#!/usr/bin/env python3
"""
Servidor de test simple para sliders
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar función de simulación del main
from main import simulacion

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test_sliders")
def test_sliders(
    anio: int = 2024,
    camara: str = "diputados",
    modelo: str = "personalizado",
    magnitud: int = 300,
    sistema: str = "mixto",
    mixto_mr_seats: int = 200,
    mixto_rp_seats: int = 100
):
    try:
        # Llamar función de simulación con valores por defecto para parámetros faltantes
        resultado = simulacion(
            anio=anio,
            camara=camara,
            modelo=modelo,
            magnitud=magnitud,
            sobrerrepresentacion=None,
            umbral=None,
            regla_electoral=None,
            mixto_mr_seats=mixto_mr_seats,
            mixto_rp_seats=mixto_rp_seats,
            sistema=sistema,
            quota_method='hare',
            divisor_method='dhondt',
            max_seats_per_party=None,
            primera_minoria=True,
            limite_escanos_pm=None
        )
        
        # Si el resultado es JSONResponse, extraer el contenido
        if hasattr(resultado, 'body'):
            import json
            content = json.loads(resultado.body)
            return content
        else:
            return resultado
            
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
