#!/usr/bin/env python3
"""
Investigar MC en el siglado de diputados 2018
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def investigar_mc_diputados_2018():
    """Investiga MC en diputados 2018"""
    print("=" * 80)
    print("INVESTIGACIÓN: MC EN SIGLADO DIPUTADOS 2018")
    print("=" * 80)
    
    # Leer siglado de diputados 2018
    siglado_file = "data/siglado-diputados-2018.csv"
    
    if not os.path.exists(siglado_file):
        print(f"❌ No encontrado: {siglado_file}")
        return
    
    print(f"📄 Leyendo: {siglado_file}")
    df = pd.read_csv(siglado_file)
    
    print(f"📊 Total filas: {len(df)}")
    print(f"📋 Columnas: {list(df.columns)}")
    print()
    
    # 1. Buscar MC explícitamente
    print("🔍 BÚSQUEDA DE MC:")
    print("-" * 40)
    
    # Buscar en grupo_parlamentario
    mc_grupo = df[df['grupo_parlamentario'].str.contains('MC', na=False, case=False)]
    print(f"MC en grupo_parlamentario: {len(mc_grupo)} registros")
    
    # Buscar en partido_origen
    mc_origen = df[df['partido_origen'].str.contains('MC', na=False, case=False)]
    print(f"MC en partido_origen: {len(mc_origen)} registros")
    
    # Buscar variaciones
    mc_movimiento = df[df['grupo_parlamentario'].str.contains('MOVIMIENTO', na=False, case=False)]
    print(f"'MOVIMIENTO' en grupo_parlamentario: {len(mc_movimiento)} registros")
    
    mc_ciudadano = df[df['grupo_parlamentario'].str.contains('CIUDADANO', na=False, case=False)]
    print(f"'CIUDADANO' en grupo_parlamentario: {len(mc_ciudadano)} registros")
    
    # Mostrar resultados si los hay
    if len(mc_grupo) > 0:
        print("\n📋 Registros con MC en grupo_parlamentario:")
        print(mc_grupo.head(10).to_string())
    
    if len(mc_movimiento) > 0:
        print("\n📋 Registros con MOVIMIENTO:")
        print(mc_movimiento.head(10).to_string())
    
    if len(mc_ciudadano) > 0:
        print("\n📋 Registros con CIUDADANO:")
        print(mc_ciudadano.head(10).to_string())
    
    print()
    
    # 2. Analizar coalición "POR MEXICO AL FRENTE"
    print("🤝 ANÁLISIS COALICIÓN 'POR MEXICO AL FRENTE':")
    print("-" * 50)
    
    frente = df[df['coalicion'].str.contains('POR MEXICO AL FRENTE', na=False, case=False)]
    print(f"Total registros 'Por México al Frente': {len(frente)}")
    
    if len(frente) > 0:
        # Partidos en esta coalición
        partidos_frente = frente['grupo_parlamentario'].value_counts()
        print("\nPartidos en 'Por México al Frente':")
        for partido, count in partidos_frente.items():
            print(f"  {partido}: {count} registros")
        
        # Mostrar muestra
        print("\nMuestra de registros:")
        print(frente.head(15).to_string())
    
    print()
    
    # 3. Todos los grupos parlamentarios únicos
    print("🏛️ TODOS LOS GRUPOS PARLAMENTARIOS:")
    print("-" * 40)
    
    grupos_unicos = df['grupo_parlamentario'].value_counts()
    print("Grupos parlamentarios encontrados:")
    for grupo, count in grupos_unicos.items():
        print(f"  {grupo}: {count} registros")
    
    print()
    
    # 4. Análisis por coalición
    print("🤝 ANÁLISIS POR COALICIÓN:")
    print("-" * 30)
    
    coaliciones = df['coalicion'].value_counts()
    print("Coaliciones encontradas:")
    for coalicion, count in coaliciones.items():
        print(f"  {coalicion}: {count} registros")
    
    print()
    
    # 5. Verificar si MC está "escondido" en algún lugar
    print("🕵️ BÚSQUEDA EXHAUSTIVA DE MC:")
    print("-" * 35)
    
    # Buscar en todas las columnas de texto
    columnas_texto = ['coalicion', 'grupo_parlamentario', 'partido_origen']
    
    for col in columnas_texto:
        if col in df.columns:
            # Buscar MC, MOVIMIENTO, CIUDADANO
            terminos = ['MC', 'MOVIMIENTO', 'CIUDADANO']
            for termino in terminos:
                matches = df[df[col].str.contains(termino, na=False, case=False)]
                if len(matches) > 0:
                    print(f"'{termino}' encontrado en {col}: {len(matches)} registros")
                    # Mostrar algunos ejemplos
                    ejemplos = matches[col].unique()[:5]
                    for ejemplo in ejemplos:
                        print(f"    Ejemplo: {ejemplo}")
    
    print()
    
    # 6. Conclusión
    print("📋 CONCLUSIÓN:")
    print("-" * 15)
    
    total_mc = len(mc_grupo) + len(mc_origen) + len(mc_movimiento) + len(mc_ciudadano)
    
    if total_mc == 0:
        print("❌ MC NO ENCONTRADO en el siglado de diputados 2018")
        print("   Esto explica por qué no aparece en los resultados")
        print("   Posibles causas:")
        print("   • MC no ganó distritos MR en 2018")
        print("   • MC está registrado con otro nombre/código")
        print("   • Problema en el archivo de siglado")
    else:
        print(f"✅ MC ENCONTRADO: {total_mc} registros totales")
        print("   MC debería aparecer en los cálculos")

if __name__ == "__main__":
    investigar_mc_diputados_2018()
