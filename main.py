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
	quota_method: str = Query('hare'),
	divisor_method: str = Query('dhondt')
):
	# Si modelo personalizado, procesar datos reales
	if modelo.lower() == "personalizado":
		camara_lower = camara.lower()
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
			try:
				seat_chart_raw = procesar_diputados_parquet(
					parquet_path, partidos_base, anio, path_siglado=siglado_path, max_seats=max_seats
				)
				# Unificar formato de seat_chart
				total_curules = sum([p['curules'] for p in seat_chart_raw if 'curules' in p]) or 1
				seat_chart = [
					{
						"party": p["partido"],
						"seats": int(p["curules"]),
						"color": PARTY_COLORS.get(p["partido"], "#888"),
						"percent": round(100 * (p["curules"] / total_curules), 2),
						"votes": int(p["votos"])
					}
					for p in seat_chart_raw if int(p["curules"]) > 0
				]
				# Aplicar sobrerrepresentación solo para Diputados
				import logging
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
				votos = [p['votes'] for p in seat_chart if 'votes' in p]
				curules = [p['seats'] for p in seat_chart if 'seats' in p]
				kpis = {
					"total_seats": total_curules,
					"mae_votos_vs_escanos": safe_mae(votos, curules),
					"gallagher": safe_gallagher(votos, curules),
					"total_votos": sum(votos)
				}
			except Exception as e:
				import traceback
				print(f"[ERROR] Procesando diputados: {e}")
				traceback.print_exc()
				seat_chart = []
				kpis = {'error': 'Fallo el procesamiento de diputados. Revisa logs y archivos.'}
		elif camara.lower() == "senado":
			if anio == 2018:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
				parquet_path = "data/computos_senado_2018.parquet"
				siglado_path = "data/ine_cg2018_senado_siglado_long.csv"
			elif anio == 2024:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
				parquet_path = "data/computos_senado_2024.parquet"
				siglado_path = "data/siglado-senado-2024.csv"
			else:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
				parquet_path = "data/computos_senado_2024.parquet"
				siglado_path = "data/siglado_senado_2024.parquet"
			senado_res = procesar_senadores_parquet(
				parquet_path, partidos_base, anio, path_siglado=siglado_path,
				total_rp_seats=32, umbral=0.03, quota_method=quota_method, divisor_method=divisor_method
			)
			seat_chart_raw = senado_res['salida']
			total_escanos = sum([p['escanos'] if 'escanos' in p else p.get('curules', 0) for p in seat_chart_raw]) or 1
			seat_chart = [
				{
					"party": p["partido"],
					"seats": int(p.get("escanos", p.get("curules", 0))),
					"color": PARTY_COLORS.get(p["partido"], "#888"),
					"percent": round(100 * (p.get("escanos", p.get("curules", 0)) / total_escanos), 2),
					"votes": int(p["votos"]) if 'votos' in p else 0
				}
				for p in seat_chart_raw if int(p.get("escanos", p.get("curules", 0))) > 0
			]
			votos = [p['votos'] for p in seat_chart_raw if 'votos' in p]
			escanos = [p.get('escanos', p.get('curules', 0)) for p in seat_chart_raw]
			kpis = {
				"total_seats": total_escanos,
				"mae_votos_vs_escanos": safe_mae(votos, escanos),
				"gallagher": safe_gallagher(votos, escanos),
				"total_votos": sum(votos)
			}
		else:
			return JSONResponse(
				content={"error": "Cámara no soportada"},
				status_code=400,
				headers={"Access-Control-Allow-Origin": "*"},
			)
			tv = sum(v); ts = sum(s)
			if tv == 0 or ts == 0: return 0
			v = [x/tv for x in v]
			s = [x/ts for x in s]
			return (sum((a-b)**2 for a,b in zip(v,s))/2)**0.5

		# Solo partidos (sin CI)
	# kpis ya calculados arriba
		return JSONResponse(
			content={
				"seatChart": seat_chart,
				"kpis": kpis,
				"tabla": seat_chart
			},
			headers={"Access-Control-Allow-Origin": "*"},
			status_code=200
		)

	# Selecciona el archivo Parquet según la cámara (ruta relativa)
	if camara.lower() == "senado":
		parquet_path = "data/senado-resumen-modelos-votos-escanos.parquet"
	else:
		parquet_path = "data/resumen-modelos-votos-escanos-diputados.parquet"

	# Determina la magnitud
	if modelo.lower() == "personalizado" and magnitud is not None:
		magnitud_camara = magnitud
	else:
		magnitud_camara = get_magnitud(camara, modelo)

	con = duckdb.connect()
	query = f'''
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

