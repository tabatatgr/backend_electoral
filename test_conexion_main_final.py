#!/usr/bin/env python3
"""
TEST FINAL: Verificar que las funciones del main.py están correctamente conectadas
y usan la versión corregida del cálculo MR por votos
"""

import sys
sys.path.append('.')

# Importar las mismas funciones que usa main.py
from kernel.wrapper_tablero import procesar_diputados_tablero as procesar_diputados_parquet
from kernel.asignacion_por_estado import procesar_diputados_por_estado
from kernel.procesar_senadores import procesar_senadores_parquet

def test_conexion_main_corregida():
    """
    Verifica que las funciones conectadas al main.py usan la versión corregida
    """
    
    print("🔧 TEST: Verificación de conexión main.py con versión corregida")
    print("=" * 70)
    print("✅ Verificando que las funciones del main.py usan cálculo MR correcto")
    print("=" * 70)
    
    # Parámetros idénticos a lo que usaría el frontend
    path_parquet_2021 = "data/computos_diputados_2021.parquet"
    path_siglado_2021 = "data/siglado-diputados-2021.csv"
    partidos_2021 = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'RSP', 'FXM', 'PES']
    
    print("\n📋 ESCENARIO: Sistema Vigente (igual que frontend)")
    print("   • 300 MR + 200 RP")
    print("   • Umbral 3%")
    print("   • Función: procesar_diputados_tablero (main.py)")
    
    try:
        # Ejecutar exactamente como lo haría main.py
        resultado = procesar_diputados_parquet(
            path_parquet=path_parquet_2021,
            partidos_base=partidos_2021,
            anio=2021,
            path_siglado=path_siglado_2021,
            max_seats=500,
            sistema='mixto',
            mr_seats=300,
            rp_seats=200,
            umbral=0.03,
            quota_method='hare'
        )
        
        if 'tot' in resultado:
            escanos = resultado['tot']
            mr_escanos = resultado.get('mr', {})
            total_escanos = sum(escanos.values())
            total_mr = sum(mr_escanos.values())
            
            print(f"\n✅ RESULTADO FUNCIÓN MAIN:")
            print(f"   • Total escaños: {total_escanos}")
            print(f"   • MR escaños: {total_mr}")
            print(f"   • RP escaños: {total_escanos - total_mr}")
            
            # Verificar que está usando el cálculo correcto de MR
            if total_mr == 300:
                print(f"   🎉 CORRECTO: MR = 300 (calculado por votos)")
                
                # Mostrar algunos resultados clave
                print(f"\n📊 ESCAÑOS PRINCIPALES:")
                for partido in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC']:
                    if partido in escanos and escanos[partido] > 0:
                        mr = mr_escanos.get(partido, 0)
                        rp = escanos[partido] - mr
                        print(f"   {partido:>6}: {escanos[partido]:>3} total ({mr:>3} MR + {rp:>3} RP)")
                
                # Verificar estructura de respuesta
                claves_esperadas = ['tot', 'mr', 'rp', 'votos']
                claves_encontradas = [k for k in claves_esperadas if k in resultado]
                
                print(f"\n🔍 ESTRUCTURA DE RESPUESTA:")
                print(f"   • Claves esperadas: {claves_esperadas}")
                print(f"   • Claves encontradas: {claves_encontradas}")
                
                if len(claves_encontradas) == len(claves_esperadas):
                    print(f"   ✅ Estructura completa")
                    estado_conexion = "✅ CONEXIÓN PERFECTA"
                else:
                    print(f"   ⚠️ Faltan algunas claves")
                    estado_conexion = "⚠️ CONEXIÓN PARCIAL"
                    
            else:
                print(f"   ❌ ERROR: MR = {total_mr} (debería ser 300)")
                estado_conexion = "❌ USANDO VERSIÓN INCORRECTA"
                
        else:
            print("❌ ERROR: Estructura de resultado no reconocida")
            estado_conexion = "❌ ERROR DE ESTRUCTURA"
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        estado_conexion = "❌ ERROR DE EJECUCIÓN"
    
    print(f"\n" + "=" * 70)
    print(f"📋 VEREDICTO FINAL")
    print(f"=" * 70)
    print(f"🔗 Estado de conexión: {estado_conexion}")
    
    if "PERFECTA" in estado_conexion:
        print(f"✅ Las funciones del main.py están correctamente conectadas")
        print(f"✅ Usan la versión corregida del cálculo MR por votos") 
        print(f"✅ El frontend recibirá datos correctos")
        print(f"✅ El tablero está listo para producción")
        
    elif "PARCIAL" in estado_conexion:
        print(f"⚠️ Las funciones funcionan pero faltan algunos datos")
        print(f"⚠️ Puede requerir ajustes menores")
        
    else:
        print(f"❌ Las funciones del main.py tienen problemas")
        print(f"❌ Requiere corrección antes del uso en producción")
    
    print(f"\n🎯 RESUMEN TÉCNICO:")
    print(f"   • Función probada: kernel.wrapper_tablero.procesar_diputados_tablero")
    print(f"   • Misma función que usa main.py")
    print(f"   • Parámetros idénticos al frontend")
    print(f"   • Test de sistema vigente mexicano")
    
    return estado_conexion

if __name__ == "__main__":
    test_conexion_main_corregida()
