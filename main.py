from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import os

app = FastAPI()

# Permitir peticiones desde cualquier origen (útil para desarrollo local)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
)

# Mapea colores por partido (puedes agregar más)
PARTY_COLORS = {
	"MORENA": "#8B2231",
	"PAN": "#0055A5",
	"PRI": "#0D7137",
	"PT": "#D52B1E",
	"PVEM": "#5CE23D",
	"MC": "#F58025",
	"PRD": "#FFCC00",
	"PES": "#6A1B9A",
	"NA": "#00B2E3",
	"FXM": "#FF69B4",
}

from fastapi.responses import JSONResponse


from kernel.magnitud import get_magnitud
from kernel.sobrerrepresentacion import aplicar_limite_sobrerrepresentacion
from kernel.umbral import aplicar_umbral
from kernel.regla_electoral import aplicar_regla_electoral
from kernel.procesar_diputados import procesar_diputados_parquet
from kernel.procesar_senadores import procesar_senadores_parquet
from kernel.kpi_utils import kpis_votos_escanos

def safe_mae(v, s):
	v = [x for x in v if x is not None]
	s = [x for x in s if x is not None]
	if not v or not s or len(v) != len(s): return 0
	return sum(abs(a-b) for a,b in zip(v,s)) / len(v)

def safe_gallagher(v, s):
	v = [x for x in v if x is not None]
	s = [x for x in s if x is not None]
	if not v or not s or len(v) != len(s): return 0
	return (0.5 * sum((100*(a/(sum(v) or 1)) - 100*(b/(sum(s) or 1)))**2 for a,b in zip(v,s)))**0.5

@app.get("/simulacion")
def simulacion(
	anio: int,
	camara: str,
	modelo: str,
	magnitud: int = Query(None),
	sobrerrepresentacion: float = Query(None),
	umbral: float = Query(None),
	regla_electoral: str = Query(None),
	mixto_mr_seats: int = Query(None),
	mixto_rp_seats: int = Query(None),
	sistema: str = Query('mixto'),
	quota_method: str = Query('hare'),
	divisor_method: str = Query('dhondt'),
	max_seats_per_party: int = Query(None)
):
	import logging
	camara_lower = camara.lower()
	# Si modelo personalizado, procesar datos reales
	if modelo.lower() == "personalizado":
		# Nuevo: tope máximo de escaños por partido (puede venir como parámetro, si no, None)
		logging.debug(f"[DEBUG] max_seats_per_party recibido en petición: {max_seats_per_party}")
		if camara_lower == "diputados":
			# Define partidos base según año
			if anio == 2018:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
			elif anio == 2021:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","RSP","FXM"]
			elif anio == 2024:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
			else:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
			# Selecciona archivo y siglado
			if anio == 2018:
				parquet_path = "data/computos_diputados_2018.parquet"
				siglado_path = "data/siglado-diputados-2018.csv"
			elif anio == 2021:
				parquet_path = "data/computos_diputados_2021.parquet"
				siglado_path = "data/siglado-diputados-2021.csv"
			elif anio == 2024:
				parquet_path = "data/computos_diputados_2024.parquet"
				siglado_path = "data/siglado-diputados-2024.csv"
			else:
				parquet_path = "data/computos_diputados_2021.parquet"
				siglado_path = "data/siglado-diputados-2021.csv"
			# Determina magnitud (número de escaños) si viene del frontend
			print(f"[DEBUG] magnitud recibida en petición: {magnitud}")
			print(f"[DEBUG] umbral recibido en petición: {umbral}")
			max_seats = magnitud if magnitud is not None else 300
			# Determinar sistema y escaños MR/RP
			sistema_tipo = sistema.lower() if sistema else 'mixto'
			mr_seats = mixto_mr_seats if mixto_mr_seats is not None else (max_seats // 2 if sistema_tipo == 'mixto' else (max_seats if sistema_tipo == 'mr' else 0))
			rp_seats = mixto_rp_seats if mixto_rp_seats is not None else (max_seats - mr_seats if sistema_tipo == 'mixto' else (max_seats if sistema_tipo == 'rp' else 0))
			print(f"[DEBUG] sistema: {sistema_tipo}, MR: {mr_seats}, RP: {rp_seats}, Total: {max_seats}")
			try:
				resultado_asignadip = procesar_diputados_parquet(
					parquet_path, partidos_base, anio, path_siglado=siglado_path, max_seats=max_seats,
					sistema=sistema_tipo, mr_seats=mr_seats, rp_seats=rp_seats,
					regla_electoral=regla_electoral, quota_method=quota_method, divisor_method=divisor_method
				)
				# Validación robusta del tipo de resultado_asignadip
				if not isinstance(resultado_asignadip, dict):
					raise ValueError(f"Error interno: el resultado de asignación de escaños no es un diccionario. Tipo recibido: {type(resultado_asignadip)}. Valor: {resultado_asignadip}")
				# Selecciona el dict correcto según sistema
				if sistema_tipo == 'mr':
					dict_escanos = resultado_asignadip.get('mr', {})
				elif sistema_tipo == 'rp':
					dict_escanos = resultado_asignadip.get('rp', {})
				else:
					dict_escanos = resultado_asignadip.get('tot', {})
				if not isinstance(dict_escanos, dict):
					raise ValueError(f"Error interno: el resultado de escaños para el sistema '{sistema_tipo}' no es un diccionario. Tipo recibido: {type(dict_escanos)}. Valor: {dict_escanos}")
				total_curules = sum(dict_escanos.values()) or 1
				seat_chart = [
					{
						"party": partido,
						"seats": int(escanos),
						"color": PARTY_COLORS.get(partido, "#888"),
						"percent": round(100 * (escanos / total_curules), 2)
					}
					for partido, escanos in dict_escanos.items() if int(escanos) > 0
				]
				# Si quieres exponer el resultado completo para debug/frontend avanzado, puedes agregarlo:
				resultado_asignadip_v2 = resultado_asignadip
				# ...existing code...
				# Aplicar tope de escaños por partido si está definido y reasignar sobrantes
				logging.debug(f"[DEBUG] max_seats_per_party (Diputados): {max_seats_per_party}")
				if max_seats_per_party is not None and max_seats_per_party > 0:
					sobrantes = 0
					# 1. Recortar partidos que superan el tope y acumular sobrantes
					for p in seat_chart:
						if p['seats'] > max_seats_per_party:
							sobrantes += p['seats'] - max_seats_per_party
							logging.warning(f"[WARN] Tope de escaños por partido aplicado: {p['party']} tenía {p['seats']} → {max_seats_per_party}")
							p['seats'] = max_seats_per_party
					# 2. Reasignar sobrantes proporcionalmente a los partidos que no han alcanzado el tope
					while sobrantes > 0:
						elegibles = [p for p in seat_chart if p['seats'] < max_seats_per_party]
						if not elegibles:
							break
						total_votos_elegibles = sum(p['votes'] for p in elegibles)
						if total_votos_elegibles == 0:
							for p in elegibles:
								if sobrantes == 0:
									break
								p['seats'] += 1
								sobrantes -= 1
							break
						asignaciones = []
						for p in elegibles:
							asignar = min(sobrantes, max_seats_per_party - p['seats'])
							prop = p['votes'] / total_votos_elegibles
							seats_to_add = min(asignar, int(round(prop * sobrantes)))
							asignaciones.append(seats_to_add)
						total_asignados = sum(asignaciones)
						faltan = sobrantes - total_asignados
						for i, p in enumerate(elegibles):
							if faltan <= 0:
								break
							if p['seats'] + asignaciones[i] < max_seats_per_party:
								asignaciones[i] += 1
								faltan -= 1
						for i, p in enumerate(elegibles):
							p['seats'] += asignaciones[i]
							sobrantes -= asignaciones[i]
					# Ajuste final: asegurar que la suma total de escaños no cambió
					total_curules = sum(p['seats'] for p in seat_chart)
					ajuste = total_curules - (magnitud if magnitud is not None else 300)
					if ajuste != 0:
						if ajuste > 0:
							for p in sorted(seat_chart, key=lambda x: -x['seats']):
								quitar = min(ajuste, p['seats'] - 0)
								p['seats'] -= quitar
								ajuste -= quitar
								if ajuste == 0:
									break
						elif ajuste < 0:
							for p in sorted(seat_chart, key=lambda x: x['seats']):
								p['seats'] += 1
								ajuste += 1
								if ajuste == 0:
									break
				# Aplicar sobrerrepresentación solo para Diputados
				import logging
				logging.debug(f"[DEBUG] sobrerrepresentacion recibida en petición: {sobrerrepresentacion}")
				if camara_lower == "diputados":
					# Si modelo personalizado, procesar datos reales
					if modelo.lower() == "personalizado":
						if camara_lower == "diputados":
							if anio == 2018:
								partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
							elif anio == 2021:
								partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","RSP","FXM"]
							elif anio == 2024:
								partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
							else:
								partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
							if anio == 2018:
								parquet_path = "data/computos_diputados_2018.parquet"
								siglado_path = "data/siglado-diputados-2018.csv"
							elif anio == 2021:
								parquet_path = "data/computos_diputados_2021.parquet"
								siglado_path = "data/siglado-diputados-2021.csv"
							elif anio == 2024:
								parquet_path = "data/computos_diputados_2024.parquet"
								siglado_path = "data/siglado-diputados-2024.csv"
							else:
								parquet_path = "data/computos_diputados_2021.parquet"
								siglado_path = "data/siglado-diputados-2021.csv"
							max_seats = magnitud if magnitud is not None else 300
							sistema_tipo = sistema.lower() if sistema else 'mixto'
							mr_seats = mixto_mr_seats if mixto_mr_seats is not None else (max_seats // 2 if sistema_tipo == 'mixto' else (max_seats if sistema_tipo == 'mr' else 0))
							rp_seats = mixto_rp_seats if mixto_rp_seats is not None else (max_seats - mr_seats if sistema_tipo == 'mixto' else (max_seats if sistema_tipo == 'rp' else 0))
							seat_chart_raw = procesar_diputados_parquet(
								parquet_path, partidos_base, anio, path_siglado=siglado_path, max_seats=max_seats,
								sistema=sistema_tipo, mr_seats=mr_seats, rp_seats=rp_seats,
								regla_electoral=regla_electoral, quota_method=quota_method, divisor_method=divisor_method
							)
							total_curules = sum([p["curules"] for p in seat_chart_raw]) or 1
							seat_chart = [
								{
									"party": p["partido"],
									"seats": int(p["curules"]),
									"color": PARTY_COLORS.get(p["partido"], "#888"),
									"percent": round(100 * (p["curules"] / total_curules), 2),
									"votes": int(p["votos"]) if 'votos' in p else 0
								}
								for p in seat_chart_raw if int(p["curules"]) > 0
							]
							votos = [p['votes'] for p in seat_chart if 'votes' in p]
							curules = [p['seats'] for p in seat_chart if 'seats' in p]
							# Aplicar sobrerrepresentación solo para Diputados
							logging.debug(f"[DEBUG] sobrerrepresentacion recibida en petición: {sobrerrepresentacion}")
							if sobrerrepresentacion is not None and sobrerrepresentacion > 0:
								limite_sobre = sobrerrepresentacion
								if limite_sobre >= 1:
									logging.warning(f"[WARN] El límite de sobrerrepresentación recibido es {limite_sobre}, se interpreta como porcentaje: {limite_sobre/100}")
									limite_sobre = limite_sobre / 100
								logging.debug(f"[DEBUG] Aplicando límite de sobrerrepresentación: {limite_sobre}")
								seat_chart = aplicar_limite_sobrerrepresentacion(seat_chart, limite_sobre)
							else:
								logging.debug("[DEBUG] No se aplica límite de sobrerrepresentación (None, vacío o 0)")
							kpis = {
								"total_seats": total_curules,
								"mae_votos_vs_escanos": safe_mae(votos, curules),
								"gallagher": safe_gallagher(votos, curules),
								"total_votos": sum(votos)
							}
					# Si necesitas lógica para senado o modelos no personalizados, agrégala aquí
					pass
		SELECT partido, asientos_partido, pct_escanos, total_escanos, total_votos, mae_votos_vs_escanos, indice_gallagher
		FROM '{parquet_path}'
		WHERE anio = {anio}
		  AND LOWER(modelo) = '{modelo.lower()}'
	'''
	df = con.execute(query).df()
	if df.empty:
		# Devuelve respuesta vacía y CORS OK
		return JSONResponse(
			content={"seatChart": [], "kpis": {}, "tabla": []},
			headers={"Access-Control-Allow-Origin": "*"},
			status_code=200
		)
	try:
		# Selecciona el archivo Parquet según la cámara (ruta relativa)
		if camara.lower() == "senado":
			parquet_path = "data/senado-resumen-modelos-votos-escanos.parquet"
		else:
			parquet_path = "data/resumen-modelos-votos-escanos-diputados.parquet"
		con = duckdb.connect()
		query = f'''
			SELECT partido, asientos_partido, pct_escanos, total_escanos, total_votos, mae_votos_vs_escanos, indice_gallagher, pct_votos
			FROM '{parquet_path}'
			WHERE anio = {anio}
			  AND LOWER(modelo) = '{modelo.lower()}'
		'''
		df = con.execute(query).df()
		if df.empty:
			# Devuelve respuesta vacía y CORS OK
			return JSONResponse(
				content={"seatChart": [], "kpis": {}, "tabla": []},
				headers={"Access-Control-Allow-Origin": "*"},
				status_code=200
			)
		# Prepara el seat chart
		seat_chart = [
			{
				"party": row["partido"],
				"seats": int(row["asientos_partido"]),
				"color": PARTY_COLORS.get(row["partido"], "#888"),
				"percent": round(float(row["pct_escanos"]) * 100, 2),
				"votes": float(row["pct_votos"]) if "pct_votos" in row else 0.0
			}
			for _, row in df.iterrows()
			if int(row["asientos_partido"]) > 0
		]

		# Lógica robusta para umbral
		import logging
		if modelo.lower() == "personalizado":
			logging.debug(f"[DEBUG] umbral recibido en petición: {umbral}")
			if umbral is not None and umbral > 0:
				logging.debug(f"[DEBUG] Aplicando filtro de umbral: {umbral}")
				seat_chart = aplicar_umbral(seat_chart, umbral)
				# Validar suma de votos tras filtros
				total_votos_filtrados = sum([p.get('votes', 0) for p in seat_chart])
				if total_votos_filtrados == 0:
					logging.error("[ERROR] La suma de votos tras aplicar umbral y filtros es cero. No se pueden calcular escaños.")
					return JSONResponse(
						content={
							"error": "La suma de votos tras aplicar el umbral y otros filtros es cero. No se pueden calcular escaños.",
							"seatChart": [],
							"kpis": {},
							"tabla": []
						},
						headers={"Access-Control-Allow-Origin": "*"},
						status_code=400
					)
			else:
				logging.debug("[DEBUG] No se aplica filtro de umbral (None, vacío o 0). Se calcula como si no hubiera umbral.")
		# Lógica robusta para sobrerrepresentación SOLO para Diputados
		if modelo.lower() == "personalizado":
			logging.debug(f"[DEBUG] sobrerrepresentacion recibida en petición: {sobrerrepresentacion}")
			if camara_lower == "diputados":
				if sobrerrepresentacion is not None and sobrerrepresentacion > 0:
					limite_sobre = sobrerrepresentacion
					if limite_sobre >= 1:
						logging.warning(f"[WARN] El límite de sobrerrepresentación recibido es {limite_sobre}, se interpreta como porcentaje: {limite_sobre/100}")
						limite_sobre = limite_sobre / 100
					logging.debug(f"[DEBUG] Aplicando límite de sobrerrepresentación: {limite_sobre}")
					seat_chart = aplicar_limite_sobrerrepresentacion(seat_chart, limite_sobre)
				else:
					logging.debug("[DEBUG] No se aplica límite de sobrerrepresentación (None, vacío o 0)")
			else:
				logging.debug("[DEBUG] No se aplica límite de sobrerrepresentación para cámara distinta a Diputados")
		# Finalmente, si hay regla electoral, aplicar el kernel correspondiente
		if modelo.lower() == "personalizado" and regla_electoral is not None:
			seat_chart = aplicar_regla_electoral(
				seat_chart,
				regla_electoral,
				mixto_mr_seats,
				quota_method=quota_method,
				divisor_method=divisor_method
			)

		# KPIs (toma el primer registro, todos tienen el mismo total)
		kpi_row = df.iloc[0] if not df.empty else None
		kpis = {
			"total_seats": int(magnitud_camara),
			"gallagher": float(kpi_row["indice_gallagher"]) if kpi_row is not None else 0,
			"mae_votos_vs_escanos": float(kpi_row["mae_votos_vs_escanos"]) if kpi_row is not None else 0,
			"total_votos": int(kpi_row["total_votos"]) if kpi_row is not None else 0,
		}
		return JSONResponse(
			content={
				"seatChart": seat_chart,
				"kpis": kpis,
				"tabla": seat_chart
			},
			headers={"Access-Control-Allow-Origin": "*"},
			status_code=200
		)
	except Exception as e:
		return JSONResponse(
			content={"error": str(e)},
			status_code=500,
			headers={"Access-Control-Allow-Origin": "*"}
		)
	# Prepara el seat chart
	seat_chart = [
		{
			"party": row["partido"],
			"seats": int(row["asientos_partido"]),
			"color": PARTY_COLORS.get(row["partido"], "#888"),
			"percent": round(float(row["pct_escanos"]) * 100, 2)
		}
		for _, row in df.iterrows()
		if int(row["asientos_partido"]) > 0
	]
	# KPIs (toma el primer registro, todos tienen el mismo total)
	kpi_row = df.iloc[0] if not df.empty else None
	kpis = {
		"total_seats": int(kpi_row["total_escanos"]) if kpi_row is not None else 0,
		"gallagher": float(kpi_row["indice_gallagher"]) if kpi_row is not None else 0,
		"mae_votos_vs_escanos": float(kpi_row["mae_votos_vs_escanos"]) if kpi_row is not None else 0,
		"total_votos": int(kpi_row["total_votos"]) if kpi_row is not None else 0,
	}
	return JSONResponse(
		content={
			"seatChart": seat_chart,
			"kpis": kpis,
			"tabla": seat_chart
		},
		headers={"Access-Control-Allow-Origin": "*"},
		status_code=200
	)

