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
		if camara.lower() == "diputados":
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
			seat_chart = procesar_diputados_parquet(
				parquet_path, partidos_base, anio, path_siglado=siglado_path
			)
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
			seat_chart = senado_res['salida']
			kpis = senado_res['kpis']
		else:
			return JSONResponse(
				content={"error": "Cámara no soportada"},
				status_code=400,
				headers={"Access-Control-Allow-Origin": "*"},
			)
		# KPIs robustos: MAE y Gallagher
		def safe_mae(v, s):
			v = [x for x in v if x is not None]
			s = [x for x in s if x is not None]
			if not v or not s or len(v) != len(s): return 0
			return sum(abs(a-b) for a,b in zip(v,s)) / len(v)
		def safe_gallagher(v, s):
			v = [x for x in v if x is not None]
			s = [x for x in s if x is not None]
			if not v or not s or len(v) != len(s): return 0
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

		# Si es personalizado y hay umbral, aplicar primero el kernel de umbral
		if modelo.lower() == "personalizado" and umbral is not None:
			seat_chart = aplicar_umbral(seat_chart, umbral)
		# Luego, si hay sobrerrepresentación, aplicar el kernel correspondiente
		if modelo.lower() == "personalizado" and sobrerrepresentacion is not None:
			seat_chart = aplicar_limite_sobrerrepresentacion(seat_chart, sobrerrepresentacion)
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

