#!/usr/bin/env python3
# 🐛 Test para identificar el bug de magnitud

import requests
import json

def test_magnitud_bug():
    """Test para reproducir el bug de magnitud reportado"""
    
    print("🐛 === TEST DEL BUG DE MAGNITUD ===\n")
    
    # Configuración de test
    url_base = "http://localhost:8001/diputados"
    
    casos_test = [
        {
            "nombre": "Caso 1: Magnitud 128 con sliders específicos",
            "params": {
                "anio": 2021,
                "modelo": "personalizado", 
                "sistema": "mixto",
                "magnitud": 128,
                "mixto_mr_seats": 64,
                "mixto_rp_seats": 64
            }
        },
        {
            "nombre": "Caso 2: Magnitud 119 (default diputados)",
            "params": {
                "anio": 2021,
                "modelo": "personalizado",
                "sistema": "mixto", 
                "magnitud": 119,
                "mixto_mr_seats": 60,
                "mixto_rp_seats": 59
            }
        },
        {
            "nombre": "Caso 3: Sin magnitud especificada (debería usar 300)",
            "params": {
                "anio": 2021,
                "modelo": "personalizado",
                "sistema": "mixto",
                "mixto_mr_seats": 150,
                "mixto_rp_seats": 150
            }
        }
    ]
    
    for caso in casos_test:
        print(f"📋 {caso['nombre']}")
        print("=" * 60)
        
        # Construir URL
        params = caso['params']
        url_params = "&".join([f"{k}={v}" for k, v in params.items()])
        url_completa = f"{url_base}?{url_params}"
        
        print(f"🌐 URL: {url_completa}")
        print(f"📊 Esperado:")
        magnitud_esperada = params.get('magnitud', 300)
        mr_esperado = params.get('mixto_mr_seats', magnitud_esperada // 2)
        rp_esperado = params.get('mixto_rp_seats', magnitud_esperada - mr_esperado)
        
        print(f"   - Magnitud total: {magnitud_esperada}")
        print(f"   - MR esperado: {mr_esperado}")
        print(f"   - RP esperado: {rp_esperado}")
        print(f"   - Suma esperada: {mr_esperado + rp_esperado}")
        
        try:
            print(f"\n📡 Haciendo petición...")
            response = requests.get(url_completa, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                
                # Analizar respuesta
                try:
                    data = response.json()
                    
                    # Buscar información de escaños en la respuesta
                    if isinstance(data, dict):
                        # Buscar claves que indiquen totales
                        claves_relevantes = [k for k in data.keys() if 'total' in k.lower() or 'escanos' in k.lower() or 'seats' in k.lower()]
                        
                        if claves_relevantes:
                            print(f"📊 Datos relevantes encontrados:")
                            for clave in claves_relevantes:
                                print(f"   - {clave}: {data[clave]}")
                        else:
                            print(f"📊 Estructura de respuesta:")
                            for k, v in list(data.items())[:5]:  # Primeros 5 items
                                if isinstance(v, (int, float, str)):
                                    print(f"   - {k}: {v}")
                                else:
                                    print(f"   - {k}: {type(v)} (tamaño: {len(v) if hasattr(v, '__len__') else 'N/A'})")
                    
                except json.JSONDecodeError:
                        print(f"📄 Respuesta (primeros 200 chars): {response.text[:200]}...")
                        
                except Exception as e:
                    print(f"❌ Error procesando respuesta: {e}")
                    
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"❌ Error: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            print(f"💡 ¿Está el servidor corriendo en localhost:8001?")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_magnitud_bug()
    
    print("🏁 CONCLUSIONES:")
    print("- Si ves magnitudes diferentes a las esperadas, hay un bug")
    print("- Si ves siempre 300 MR, el problema está en el código duplicado")
    print("- Si ves las validaciones inteligentes, significa que el bloque correcto se ejecutó")
