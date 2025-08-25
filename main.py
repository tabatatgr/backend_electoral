from fastapi import FastAPI
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

@app.get("/simulacion")
def simulacion(anio: int, camara: str, modelo: str):
	# Selecciona el archivo Parquet según la cámara (ruta relativa)
	if camara.lower() == "senado":
		parquet_path = "data/senado-resumen-modelos-votos-escanos.parquet"
	else:
		parquet_path = "data/resumen-modelos-votos-escanos-diputados.parquet"
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
