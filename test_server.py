#!/usr/bin/env python3
"""
Servidor simple para probar sliders sin uvicorn
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sys
import os

# Agregar path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kernel.procesar_diputados import procesar_diputados_parquet

class SliderTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parsear URL y parámetros
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            
            # Extraer parámetros
            anio = int(params.get('anio', [2024])[0])
            sistema = params.get('sistema', ['mixto'])[0]
            mr_seats = int(params.get('mixto_mr_seats', [150])[0])
            rp_seats = int(params.get('mixto_rp_seats', [150])[0])
            magnitud = int(params.get('magnitud', [300])[0])
            
            print(f"[TEST] Recibido: sistema={sistema}, MR={mr_seats}, RP={rp_seats}, magnitud={magnitud}")
            
            # Configurar archivos
            parquet_path = "data/computos_diputados_2024.parquet"
            siglado_path = "data/siglado-diputados-2024.csv"
            partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
            
            # Procesar
            resultado = procesar_diputados_parquet(
                parquet_path, partidos_base, anio, 
                path_siglado=siglado_path, max_seats=magnitud,
                sistema=sistema, mr_seats=mr_seats, rp_seats=rp_seats,
                umbral=0.03
            )
            
            if resultado:
                # Obtener datos según sistema
                if sistema == 'mr':
                    dict_escanos = resultado.get('mr', {})
                elif sistema == 'rp':
                    dict_escanos = resultado.get('rp', {})
                else:  # mixto
                    dict_escanos = resultado.get('tot', {})
                
                dict_votos = resultado.get('votos', {})
                
                # Crear seat chart
                total_curules = sum(dict_escanos.values()) or 1
                seat_chart = []
                
                for partido, escanos in dict_escanos.items():
                    if escanos > 0:
                        votos = dict_votos.get(partido, 0)
                        seat_chart.append({
                            "party": partido,
                            "seats": escanos,
                            "percent": round(100 * (escanos / total_curules), 2),
                            "votes": votos
                        })
                
                # KPIs
                kpis = {
                    "total_seats": total_curules,
                    "gallagher": 0.0,
                    "mae_votos_vs_escanos": 0.0,
                    "total_votos": sum(dict_votos.values())
                }
                
                response_data = {
                    "seatChart": seat_chart,
                    "kpis": kpis,
                    "tabla": []
                }
                
                # Enviar respuesta
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
                
                print(f"[TEST] ✅ Enviado: {len(seat_chart)} partidos, {total_curules} escaños")
                
            else:
                raise Exception("No se obtuvo resultado")
                
        except Exception as e:
            print(f"[TEST] ❌ Error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def log_message(self, format, *args):
        return  # Silenciar logs HTTP

def run_test_server():
    server_address = ('127.0.0.1', 8001)
    httpd = HTTPServer(server_address, SliderTestHandler)
    print(f"[TEST] Servidor iniciado en http://127.0.0.1:8001")
    print(f"[TEST] Prueba: http://127.0.0.1:8001/?anio=2024&sistema=mixto&mixto_mr_seats=200&mixto_rp_seats=100")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"[TEST] Servidor detenido")
        httpd.shutdown()

if __name__ == "__main__":
    run_test_server()
