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

# Mapea colores por partido
PARTY_COLORS = {
	"MORENA": "#8B2231",
	"PAN": "#0055A5",
	"PRI": "#0D7137",
	"PT": "#D52B1E",
	"PVEM": "#1E9F00",
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
from kernel.wrapper_tablero import procesar_diputados_tablero as procesar_diputados_parquet
from kernel.asignacion_por_estado import procesar_diputados_por_estado
from kernel.procesar_senadores import procesar_senadores_parquet
from kernel.plan_c import procesar_plan_c_diputados
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
	max_seats_per_party: int = Query(None),
	primera_minoria: bool = Query(True),  # Parámetro para senado
	limite_escanos_pm: int = Query(None)  # Límite de escaños para primera minoría
):
	import logging
	camara_lower = camara.lower()
	
	# Inicializar variables por defecto
	seat_chart = []
	kpis = {"total_seats": 0, "gallagher": 0, "mae_votos_vs_escanos": 0, "total_votos": 0}
	
	# Verificar si se debe usar Plan C precomputado para diputados
	if camara_lower == "diputados" and modelo.lower() == "plan c":
		seat_chart, kpis = procesar_plan_c_diputados(anio)
		if seat_chart is None or kpis is None:
			kpis = {'error': 'Fallo el procesamiento de Plan C precomputado. Revisa logs y archivos.'}
			seat_chart = []
	
	# Si modelo personalizado, procesar datos reales
	if modelo.lower() == "personalizado":
		# Nuevo: tope máximo de escaños por partido (puede venir como parámetro, si no, None)
		logging.debug(f"[DEBUG] max_seats_per_party recibido en petición: {max_seats_per_party}")
		
		if camara_lower == "diputados":
			# Lógica existente para diputados personalizado
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
			
			# ✨ VALIDACIONES INTELIGENTES Y ROBUSTAS ✨
			print(f"[INFO] Aplicando validaciones inteligentes...")
			
			# === 1. VALIDAR QUE LA SUMA NO EXCEDA EL TOTAL ===
			if mixto_mr_seats is not None and mixto_rp_seats is not None:
				suma_total = mixto_mr_seats + mixto_rp_seats
				if suma_total != max_seats:
					print(f"[ERROR] Suma inválida: MR({mixto_mr_seats}) + RP({mixto_rp_seats}) = {suma_total} ≠ {max_seats} total")
					# AJUSTE INTELIGENTE: Si se especificaron ambos pero no suman bien, ajustar RP
					if suma_total > max_seats:
						mixto_rp_seats = max_seats - mixto_mr_seats
						print(f"[FIX] Auto-ajustando RP: {mixto_rp_seats} para que sume {max_seats}")
					elif suma_total < max_seats:
						mixto_rp_seats = max_seats - mixto_mr_seats  
						print(f"[FIX] Auto-completando RP: {mixto_rp_seats} para que sume {max_seats}")
			
			# === 2. SLIDERS INTELIGENTES (si solo se especifica uno) ===
			elif mixto_mr_seats is not None and mixto_rp_seats is None:
				# Usuario movió slider MR → ajustar RP automáticamente
				mixto_rp_seats = max_seats - mixto_mr_seats
				print(f"[AUTO]  Slider inteligente: MR={mixto_mr_seats} → RP auto-ajustado a {mixto_rp_seats}")
				
			elif mixto_rp_seats is not None and mixto_mr_seats is None:
				# Usuario movió slider RP → ajustar MR automáticamente  
				mixto_mr_seats = max_seats - mixto_rp_seats
				print(f"[AUTO]  Slider inteligente: RP={mixto_rp_seats} → MR auto-ajustado a {mixto_mr_seats}")
			
			# === 3. VALIDACIONES DE RANGOS SENSATOS ===
			if mixto_mr_seats is not None:
				# Validar que MR esté en rango sensato (mínimo 10%, máximo 90%)
				min_mr = max(1, max_seats // 10)  # Mínimo 10% pero al menos 1
				max_mr = max_seats - max(1, max_seats // 10)  # Máximo 90%
				
				if mixto_mr_seats < min_mr:
					print(f"[WARN]  mixto_mr_seats={mixto_mr_seats} muy bajo (min {min_mr}), ajustando...")
					mixto_mr_seats = min_mr
					mixto_rp_seats = max_seats - mixto_mr_seats
				elif mixto_mr_seats > max_mr:
					print(f"[WARN]  mixto_mr_seats={mixto_mr_seats} muy alto (max {max_mr}), ajustando...")
					mixto_mr_seats = max_mr
					mixto_rp_seats = max_seats - mixto_mr_seats
			
			if mixto_rp_seats is not None:
				# Validar que RP esté en rango sensato (mínimo 10%, máximo 90%)
				min_rp = max(1, max_seats // 10)
				max_rp = max_seats - max(1, max_seats // 10)
				
				if mixto_rp_seats < min_rp:
					print(f"[WARN]  mixto_rp_seats={mixto_rp_seats} muy bajo (min {min_rp}), ajustando...")
					mixto_rp_seats = min_rp
					mixto_mr_seats = max_seats - mixto_rp_seats
				elif mixto_rp_seats > max_rp:
					print(f"[WARN]  mixto_rp_seats={mixto_rp_seats} muy alto (max {max_rp}), ajustando...")
					mixto_rp_seats = max_rp
					mixto_mr_seats = max_seats - mixto_rp_seats
			
			# === 4. VALIDACIÓN FINAL: ASEGURAR QUE SUMA SEA EXACTA ===
			if mixto_mr_seats is not None and mixto_rp_seats is not None:
				suma_final = mixto_mr_seats + mixto_rp_seats
				if suma_final != max_seats:
					# Esto no debería pasar, pero por seguridad
					print(f"[ERROR] Suma final incorrecta: {suma_final} ≠ {max_seats}")
					mixto_rp_seats = max_seats - mixto_mr_seats
					print(f"[FIX] Forzando corrección: RP = {mixto_rp_seats}")
			
			print(f"[RESULT] Validaciones completadas: MR={mixto_mr_seats}, RP={mixto_rp_seats}, Total={max_seats}")
			
			# Determinar sistema y escaños MR/RP
			sistema_tipo = sistema.lower() if sistema else 'mixto'
			mr_seats = mixto_mr_seats if mixto_mr_seats is not None else (max_seats // 2 if sistema_tipo == 'mixto' else (max_seats if sistema_tipo == 'mr' else 0))
			rp_seats = mixto_rp_seats if mixto_rp_seats is not None else (max_seats - mr_seats if sistema_tipo == 'mixto' else (max_seats if sistema_tipo == 'rp' else 0))
			print(f"[DEBUG] sistema: {sistema_tipo}, MR: {mr_seats}, RP: {rp_seats}, Total: {max_seats}")
			try:
				resultado_asignadip = procesar_diputados_parquet(
					parquet_path, partidos_base, anio, path_siglado=siglado_path, max_seats=max_seats,
					sistema=sistema_tipo, mr_seats=mr_seats, rp_seats=rp_seats,
					regla_electoral=regla_electoral, quota_method=quota_method, divisor_method=divisor_method, umbral=umbral, max_seats_per_party=max_seats_per_party
				)
				# Validación robusta del tipo de resultado_asignadip
				if not isinstance(resultado_asignadip, dict):
					raise ValueError(f"Error interno: el resultado de asignación de escaños no es un diccionario. Tipo recibido: {type(resultado_asignadip)}. Valor: {resultado_asignadip}")
				
				# Selecciona el dict correcto según sistema
				if sistema_tipo == 'mr':
					dict_escanos = resultado_asignadip.get('mr', {})
					dict_votos = resultado_asignadip.get('votos', {})
				elif sistema_tipo == 'rp':
					dict_escanos = resultado_asignadip.get('rp', {})
					dict_votos = resultado_asignadip.get('votos', {})
				else:
					dict_escanos = resultado_asignadip.get('tot', {})
					dict_votos = resultado_asignadip.get('votos', {})
				
				if not isinstance(dict_escanos, dict):
					raise ValueError(f"Error interno: el resultado de escaños para el sistema '{sistema_tipo}' no es un diccionario. Tipo recibido: {type(dict_escanos)}. Valor: {dict_escanos}")
				
				total_curules = sum(dict_escanos.values()) or 1
				seat_chart = [
					{
						"party": partido,
						"seats": int(escanos),
						"color": PARTY_COLORS.get(partido, "#888"),
						"percent": round(100 * (escanos / total_curules), 2),
						"votes": dict_votos.get(partido, 0)
					}
					for partido, escanos in dict_escanos.items() if int(escanos) > 0
				]
				
				# Aplicar filtro de umbral si está definido
				logging.debug(f"[DEBUG] umbral recibido en petición: {umbral}")
				if umbral is not None and umbral > 0:
					logging.debug(f"[DEBUG] Aplicando filtro de umbral: {umbral}")
					seat_chart = aplicar_umbral(seat_chart, umbral)
					# Validar suma de votos tras filtros
					total_votos_filtrados = sum([p.get('votes', 0) for p in seat_chart])
					if total_votos_filtrados == 0:
						logging.error("[ERROR] La suma de votos tras aplicar umbral es cero. No se pueden calcular escaños.")
						return JSONResponse(
							content={
								"error": "La suma de votos tras aplicar el umbral es cero. No se pueden calcular escaños.",
								"seatChart": [],
								"kpis": {},
								"tabla": []
							},
							headers={"Access-Control-Allow-Origin": "*"},
							status_code=400
						)
				else:
					logging.debug("[DEBUG] No se aplica filtro de umbral (None, vacío o 0)")
				
				# Aplicar límite de sobrerrepresentación solo para Diputados
				print(f"[DEBUG] ⚖️ SOBRERREPRESENTACIÓN recibida en petición: {sobrerrepresentacion}")
				if camara_lower == "diputados":
					if sobrerrepresentacion is not None and sobrerrepresentacion > 0:
						print(f"[DEBUG] Aplicando sobrerrepresentación para DIPUTADOS")
						limite_sobre = sobrerrepresentacion
						if limite_sobre >= 1:
							print(f"[WARN] El límite de sobrerrepresentación recibido es {limite_sobre}, se interpreta como porcentaje: {limite_sobre/100}")
							limite_sobre = limite_sobre / 100
						print(f"[DEBUG] Aplicando límite de sobrerrepresentación: {limite_sobre}")
						seat_chart_antes = [{'party': p['party'], 'seats': p['seats']} for p in seat_chart[:3]]
						print(f"[DEBUG] ANTES sobrerrepresentación: {seat_chart_antes}")
						seat_chart = aplicar_limite_sobrerrepresentacion(seat_chart, limite_sobre)
						seat_chart_despues = [{'party': p['party'], 'seats': p['seats']} for p in seat_chart[:3]]
						print(f"[DEBUG] DESPUÉS sobrerrepresentación: {seat_chart_despues}")
					else:
						print(f"[DEBUG] No se aplica límite de sobrerrepresentación (valor={sobrerrepresentacion})")
				else:
					print(f"[DEBUG] No se aplica límite de sobrerrepresentación para cámara: {camara_lower}")
				
				# Aplicar tope de escaños por partido si está definido (solo para Diputados)
				if camara_lower == "diputados":
					print(f"[DEBUG] TOPE DE ESCAÑOS max_seats_per_party: {max_seats_per_party}")
					if max_seats_per_party is not None and max_seats_per_party > 0:
						print(f"[DEBUG] Aplicando TOPE DE ESCAÑOS por partido: {max_seats_per_party}")
						sobrantes = 0
						# 1. Recortar partidos que superan el tope y acumular sobrantes
						seat_chart_antes_tope = [{'party': p['party'], 'seats': p['seats']} for p in seat_chart[:3]]
						print(f"[DEBUG] ANTES tope escaños: {seat_chart_antes_tope}")
						for p in seat_chart:
							if p['seats'] > max_seats_per_party:
								sobrantes += p['seats'] - max_seats_per_party
								print(f"[WARN] Tope de escaños aplicado: {p['party']} tenía {p['seats']} → {max_seats_per_party}")
								p['seats'] = max_seats_per_party
						# 2. Reasignar sobrantes proporcionalmente a los partidos que no han alcanzado el tope
						while sobrantes > 0:
							elegibles = [p for p in seat_chart if p['seats'] < max_seats_per_party]
							if not elegibles:
								break
							total_votos_elegibles = sum(p.get('votes', 0) for p in elegibles)
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
								prop = p.get('votes', 0) / total_votos_elegibles
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
						total_curules_after_cap = sum(p['seats'] for p in seat_chart)
						ajuste = total_curules_after_cap - max_seats
						if ajuste != 0:
							if ajuste > 0:
								for p in sorted(seat_chart, key=lambda x: -x['seats']):
									quitar = min(ajuste, p['seats'])
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
					else:
						print(f"[DEBUG] No se aplica tope de escaños (valor={max_seats_per_party})")
				else:
					print(f"[DEBUG] No se aplica tope de escaños para cámara: {camara_lower}")
				
				# Recalcular totales finales después de aplicar TODOS los filtros
				total_curules = sum([p["seats"] for p in seat_chart]) or 1
				print(f"[DEBUG] RESULTADO FINAL después de sobrerrepresentación y tope:")
				final_top3 = [{'party': p['party'], 'seats': p['seats']} for p in seat_chart[:3]]
				print(f"[DEBUG] Top 3 final: {final_top3}, Total escaños: {total_curules}")
				
				# Recalcular porcentajes después de todos los filtros
				for p in seat_chart:
					p["percent"] = round(100 * (p["seats"] / total_curules), 2)
				
				# Calcular KPIs finales
				votos = [p.get('votes', 0) for p in seat_chart]
				curules = [p.get('seats', 0) for p in seat_chart]
				
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
		
		elif camara_lower == "senado":
			# Nueva lógica para senado personalizado
			# Define partidos base según año
			if anio == 2018:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
			elif anio == 2021:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","RSP","FXM"]
			elif anio == 2024:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
			else:
				partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
			
			# Selecciona archivos de senado
			if anio == 2018:
				parquet_path = "data/computos_senado_2018.parquet"
				siglado_path = "data/ine_cg2018_senado_siglado_long_corregido.csv"
			elif anio == 2021:
				parquet_path = "data/computos_senado_2021.parquet"  # Puede no existir
				siglado_path = "data/siglado-senado-2021.csv"       # Puede no existir
			elif anio == 2024:
				parquet_path = "data/computos_senado_2024.parquet" 
				siglado_path = "data/siglado-senado-2024.csv"
			else:
				parquet_path = "data/computos_senado_2018.parquet"
				siglado_path = "data/ine_cg2018_senado_siglado_long_corregido.csv"
			
			# Para senado, magnitud normalmente es 128, pero puede venir del frontend
			max_seats = magnitud if magnitud is not None else 128
			total_rp_seats = mixto_rp_seats if mixto_rp_seats is not None else 32  # 32 escaños de RP en senado
			total_mr_seats = mixto_mr_seats if mixto_mr_seats is not None else None  # MR puede limitarse con slider
			umbral_senado = umbral if umbral is not None else 0.03  # 3% por defecto para senado
			
			print(f"[DEBUG] Senado - magnitud: {max_seats}, RP seats: {total_rp_seats}, MR seats: {total_mr_seats}, umbral: {umbral_senado}")
			print(f"[DEBUG] Senado - primera_minoria: {primera_minoria}")
			
			try:
				resultado_asignasen = procesar_senadores_parquet(
					parquet_path, partidos_base, anio, path_siglado=siglado_path, 
					total_rp_seats=total_rp_seats, total_mr_seats=total_mr_seats, umbral=umbral_senado,
					quota_method=quota_method, divisor_method=divisor_method,
					primera_minoria=primera_minoria, limite_escanos_pm=limite_escanos_pm
				)
				
				# Validación del resultado
				if not isinstance(resultado_asignasen, dict):
					raise ValueError(f"Error interno: el resultado de asignación de senadores no es un diccionario. Tipo recibido: {type(resultado_asignasen)}")
				
				# Para senado, normalmente se usa el total
				dict_escanos = resultado_asignasen.get('tot', {})
				dict_votos = resultado_asignasen.get('votos', {})
				
				# Si primera_minoria es False, ajustar los resultados eliminando PM
				if not primera_minoria:
					logging.debug("[DEBUG] Eliminando escaños de Primera Minoría (PM)")
					mr_escanos = resultado_asignasen.get('mr', {})
					rp_escanos = resultado_asignasen.get('rp', {})
					pm_escanos = resultado_asignasen.get('pm', {})
					
					# Nuevo total sin PM: solo MR + RP
					dict_escanos = {}
					for partido in mr_escanos.keys() | rp_escanos.keys():
						dict_escanos[partido] = mr_escanos.get(partido, 0) + rp_escanos.get(partido, 0)
					
					logging.debug(f"[DEBUG] Escaños sin PM - MR: {mr_escanos}, RP: {rp_escanos}, Total: {dict_escanos}")
				else:
					logging.debug("[DEBUG] Incluyendo Primera Minoría (PM) en el cálculo")
				
				if not isinstance(dict_escanos, dict):
					raise ValueError(f"Error interno: el resultado de escaños para senado no es un diccionario. Tipo recibido: {type(dict_escanos)}")
				
				# Validar y ajustar magnitud si es necesario
				total_escanos_calculados = sum(dict_escanos.values())
				if total_escanos_calculados != max_seats:
					logging.warning(f"[WARN] Total de escaños calculados ({total_escanos_calculados}) difiere de magnitud especificada ({max_seats})")
					if max_seats < total_escanos_calculados:
						# Necesitamos reducir escaños proporcionalmente
						factor = max_seats / total_escanos_calculados
						for partido in dict_escanos:
							dict_escanos[partido] = int(dict_escanos[partido] * factor)
						# Ajuste final para llegar exacto
						diferencia = max_seats - sum(dict_escanos.values())
						partidos_ordenados = sorted(dict_escanos.keys(), key=lambda x: dict_escanos[x], reverse=True)
						for i in range(abs(diferencia)):
							if diferencia > 0:
								dict_escanos[partidos_ordenados[i % len(partidos_ordenados)]] += 1
							elif diferencia < 0 and dict_escanos[partidos_ordenados[i % len(partidos_ordenados)]] > 0:
								dict_escanos[partidos_ordenados[i % len(partidos_ordenados)]] -= 1
					logging.debug(f"[DEBUG] Escaños ajustados a magnitud {max_seats}: {dict_escanos}")
				
				total_curules = sum(dict_escanos.values()) or 1
				seat_chart = [
					{
						"party": partido,
						"seats": int(escanos),
						"color": PARTY_COLORS.get(partido, "#888"),
						"percent": round(100 * (escanos / total_curules), 2),
						"votes": dict_votos.get(partido, 0)
					}
					for partido, escanos in dict_escanos.items() if int(escanos) > 0
				]
				
				# Para senado, no se aplica sobrerrepresentación ni límite por partido
				# Solo umbral (ya aplicado en procesar_senadores_parquet)
				
				# Calcular KPIs finales
				votos = [p.get('votes', 0) for p in seat_chart]
				curules = [p.get('seats', 0) for p in seat_chart]
				
				kpis = {
					"total_seats": total_curules,
					"mae_votos_vs_escanos": safe_mae(votos, curules),
					"gallagher": safe_gallagher(votos, curules),
					"total_votos": sum(votos)
				}
				
			except Exception as e:
				import traceback
				print(f"[ERROR] Procesando senadores: {e}")
				traceback.print_exc()
				seat_chart = []
				kpis = {'error': 'Fallo el procesamiento de senadores. Revisa logs y archivos.'}
	else:
		# Lógica para modelos vigente, rp, mr, mixto usando archivos resumen
		try:
			# Selecciona el archivo Parquet según la cámara (ruta relativa)
			if camara.lower() == "senado":
				parquet_path = "data/senado-resumen-modelos-votos-escanos.parquet"
				magnitud_camara = 128  # Senado tiene 128 escaños
			else:
				parquet_path = "data/resumen-modelos-votos-escanos-diputados.parquet"
				magnitud_camara = magnitud if magnitud is not None else 500  # Diputados por defecto
			
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

			# KPIs (toma el primer registro, todos tienen el mismo total)
			kpi_row = df.iloc[0] if not df.empty else None
			
			# Manejar total_votos que puede ser "NA"
			total_votos_val = 0
			if kpi_row is not None:
				tv = kpi_row["total_votos"]
				if tv != "NA" and str(tv).strip() != "NA":
					try:
						total_votos_val = int(float(tv) if isinstance(tv, str) else tv)
					except (ValueError, TypeError):
						total_votos_val = 0
			
			# Determinar el total de escaños correcto
			if modelo.lower() == "plan c":
				total_seats_actual = 300  # Plan C tiene 300 escaños
			else:
				total_seats_actual = int(magnitud_camara)
			
			kpis = {
				"total_seats": total_seats_actual,
				"gallagher": float(kpi_row["indice_gallagher"]) if kpi_row is not None else 0,
				"mae_votos_vs_escanos": float(kpi_row["mae_votos_vs_escanos"]) if kpi_row is not None else 0,
				"total_votos": total_votos_val,
			}
			
		except Exception as e:
			import traceback
			print(f"[ERROR] Procesando modelo {modelo}: {e}")
			traceback.print_exc()
			return JSONResponse(
				content={"error": str(e)},
				status_code=500,
				headers={"Access-Control-Allow-Origin": "*"}
			)

	# Devuelve respuesta con seatChart y KPIs
	return JSONResponse(
		content={
			"seatChart": seat_chart,
			"kpis": kpis,
			"tabla": seat_chart
		},
		headers={"Access-Control-Allow-Origin": "*"},
		status_code=200
	)


