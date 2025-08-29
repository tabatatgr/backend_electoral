#!/usr/bin/env python3
"""
Test Senado 2018 - Sistema RP Estatal Propuesto
96 senadores, 3 por estado, elegidos por representación proporcional con listas estatales

Características del sistema:
- 96 senadores totales (32 estados × 3 senadores)
- Representación proporcional pura por estado  
- Listas estatales
- Sin mayoría relativa, sin primera minoría
- Datos 2018
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_senado_rp_estatal_2018():
    """
    Test del sistema propuesto de senado con RP estatal
    """
    print("🏛️ TEST SENADO RP ESTATAL 2018")
    print("=" * 60)
    print("📋 Sistema propuesto:")
    print("  • 96 senadores totales")
    print("  • 3 senadores por estado (32 estados)")
    print("  • Representación proporcional pura")
    print("  • Listas estatales")
    print("  • Sin mayoría relativa, sin primera minoría")
    
    try:
        # Verificar si tenemos datos de senado
        ruta_senado = 'data/computos_senado_2018.parquet'
        
        # Intentar usar función de senado existente
        from kernel.procesar_senadores import procesar_senadores_parquet
        
        PARTIDOS_BASE = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA']
        
        print(f"\n🔧 Parámetros del sistema:")
        parametros_senado_rp = {
            'anio': 2018,
            'total_senadores': 96,       # 32 estados × 3
            'por_estado': 3,             # 3 senadores por estado
            'sistema': 'rp',             # RP puro
            'mr_por_estado': 0,          # Sin MR
            'primera_minoria': False,    # Sin primera minoría  
            'rp_nacional': False,        # Sin RP nacional
            'rp_estatal': True,          # RP por estado
            'umbral': 0.03,              # 3% umbral por estado
            'quota_method': 'hare',
            'divisor_method': 'dhondt'
        }
        
        for key, value in parametros_senado_rp.items():
            print(f"  {key}: {value}")
        
        print(f"\n📊 Procesando senado RP estatal...")
        
        # Intentar procesar con función de senado
        try:
            resultado = procesar_senadores_parquet(
                ruta_senado,
                PARTIDOS_BASE,
                **parametros_senado_rp
            )
            
            # Mostrar resultados
            print(f"\n🏆 RESULTADOS POR ESTADO Y PARTIDO:")
            print(f"Estado             Senadores  Distribución")
            print("=" * 50)
            
            total_por_partido = {p: 0 for p in PARTIDOS_BASE}
            total_general = 0
            
            # Si el resultado tiene información por estado
            if isinstance(resultado, dict) and 'por_estado' in resultado:
                for estado, datos in resultado['por_estado'].items():
                    senadores_estado = sum(datos.values())
                    distribucion = ", ".join([f"{p}:{v}" for p, v in datos.items() if v > 0])
                    print(f"{estado:<16} {senadores_estado:10}  {distribucion}")
                    
                    for p in PARTIDOS_BASE:
                        total_por_partido[p] += datos.get(p, 0)
                    total_general += senadores_estado
            
            # Mostrar totales nacionales
            print("=" * 50)
            print(f"{'TOTAL NACIONAL':<16} {total_general:10}")
            
            print(f"\n📊 RESUMEN NACIONAL:")
            print(f"Partido   Senadores  %Total")
            print("-" * 30)
            
            for partido in sorted(PARTIDOS_BASE, key=lambda p: total_por_partido[p], reverse=True):
                senadores = total_por_partido[partido]
                porcentaje = (senadores / total_general * 100) if total_general > 0 else 0
                if senadores > 0:
                    print(f"{partido:<8}  {senadores:8}  {porcentaje:5.1f}%")
            
            print("-" * 30)
            print(f"{'TOTAL':<8}  {total_general:8}  {100.0:5.1f}%")
            
            # Verificaciones
            print(f"\n✅ VERIFICACIONES:")
            print(f"  • Total senadores: {total_general}/96 {'✓' if total_general == 96 else '✗'}")
            print(f"  • Estados procesados: {len(resultado.get('por_estado', {}))}/32")
            print(f"  • Promedio por estado: {total_general/32:.1f} (esperado: 3.0)")
            
            return {
                'exito': True,
                'total_senadores': total_general,
                'distribucion': total_por_partido
            }
            
        except Exception as e:
            print(f"⚠️ Error con función de senado específica: {e}")
            print(f"💡 Intentando con función genérica...")
            
            # Fallback: usar función de diputados adaptada para senado
            from kernel.asignacion_por_estado import asignar_rp_por_estado
            
            # Cargar datos de senado
            print(f"📁 Cargando datos: {ruta_senado}")
            df = pd.read_parquet(ruta_senado)
            
            print(f"📊 Datos cargados:")
            print(f"  Filas: {len(df)}")
            print(f"  Columnas: {df.columns.tolist()}")
            
            # Normalizar columnas
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Verificar estructura de datos de senado
            if 'ENTIDAD' in df.columns:
                print(f"  Estados únicos: {df['ENTIDAD'].nunique()}")
                
                # Usar asignación RP por estado con 3 senadores por estado
                resultado_rp = asignar_rp_por_estado(
                    df, PARTIDOS_BASE, 
                    quota_method='hare', 
                    divisor_method='dhondt', 
                    umbral=0.03
                )
                
                # Mostrar resultados
                print(f"\n🏆 RESULTADOS RP ESTATAL:")
                total_senadores = sum(resultado_rp['rp'].values())
                
                for partido in sorted(PARTIDOS_BASE, key=lambda p: resultado_rp['rp'][p], reverse=True):
                    senadores = resultado_rp['rp'][partido]
                    porcentaje = (senadores / total_senadores * 100) if total_senadores > 0 else 0
                    if senadores > 0:
                        print(f"{partido}: {senadores} senadores ({porcentaje:.1f}%)")
                
                print(f"Total: {total_senadores} senadores")
                
                return {
                    'exito': True,
                    'total_senadores': total_senadores,
                    'distribucion': resultado_rp['rp']
                }
            else:
                print(f"❌ No se encontró columna ENTIDAD en datos de senado")
                return {'exito': False, 'error': 'Estructura de datos no compatible'}
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return {'exito': False, 'error': str(e)}

if __name__ == "__main__":
    test_senado_rp_estatal_2018()
