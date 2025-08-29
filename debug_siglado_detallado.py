#!/usr/bin/env python3
"""
Análisis detallado del archivo siglado para entender 
cómo R calcula MR usando grupo_parlamentario
"""

import pandas as pd
import sys
sys.path.append('kernel')

print("🔍 ANÁLISIS DETALLADO DEL SIGLADO")
print("=" * 50)

# Leer archivo siglado
siglado_path = "data/siglado-diputados-2021.csv"
df_siglado = pd.read_csv(siglado_path)

print(f"📊 Archivo: {siglado_path}")
print(f"Filas: {len(df_siglado)}")
print(f"Columnas: {list(df_siglado.columns)}")
print()

# Mostrar primeras filas
print("🔍 PRIMERAS 10 FILAS:")
print("-" * 80)
print(df_siglado.head(10).to_string())
print()

# Verificar si hay exactamente 1 ganador por distrito
print("🏆 ANÁLISIS POR DISTRITO:")
print("-" * 30)
distritos_unicos = df_siglado.groupby(['entidad', 'distrito']).size()
print(f"Total combinaciones entidad-distrito: {len(distritos_unicos)}")
print(f"Registros por distrito - min: {distritos_unicos.min()}, max: {distritos_unicos.max()}")

# Buscar duplicados por distrito
duplicados = distritos_unicos[distritos_unicos > 1]
if len(duplicados) > 0:
    print(f"\n⚠️  DISTRITOS CON MÚLTIPLES REGISTROS: {len(duplicados)}")
    print("Primeros 10 casos:")
    for (entidad, distrito), count in duplicados.head(10).items():
        print(f"  {entidad} - Distrito {distrito}: {count} registros")
        # Mostrar detalles de estos casos
        casos = df_siglado[(df_siglado['entidad'] == entidad) & (df_siglado['distrito'] == distrito)]
        for _, row in casos.iterrows():
            print(f"    → {row['grupo_parlamentario']} ({row['coalicion']})")
    print()

# Contar ganadores por grupo parlamentario
print("🎯 CONTEO POR GRUPO PARLAMENTARIO:")
print("-" * 40)
conteo_gp = df_siglado['grupo_parlamentario'].value_counts().sort_values(ascending=False)
total_registros = conteo_gp.sum()

print("Registros en siglado:")
for partido, count in conteo_gp.items():
    print(f"  {partido}: {count}")
print(f"  TOTAL: {total_registros}")
print()

# Comparar con resultados esperados de R
print("📊 COMPARACIÓN CON RESULTADOS R:")
print("-" * 35)
resultados_r = {
    'MORENA': 144,
    'PAN': 55, 
    'PRI': 23,
    'PT': 31,
    'PVEM': 31
}

print("PARTIDO  SIGLADO  R_ESPERADO  DIFF")
print("-" * 35)
for partido in ['MORENA', 'PAN', 'PRI', 'PT', 'PVEM']:
    siglado_count = conteo_gp.get(partido, 0)
    r_count = resultados_r.get(partido, 0)
    diff = siglado_count - r_count
    print(f"{partido:<8} {siglado_count:<8} {r_count:<11} {diff:+d}")

print()

# Analizar coaliciones
print("🤝 ANÁLISIS POR COALICIÓN:")
print("-" * 30)
conteo_coalicion = df_siglado['coalicion'].value_counts()
print("Registros por coalición:")
for coalicion, count in conteo_coalicion.items():
    print(f"  {coalicion}: {count}")
print()

# Verificar si R usa solo 1 registro por distrito
print("🎯 HIPÓTESIS: R usa 1 registro por distrito")
print("-" * 45)

# Intentar simular el método de R tomando 1 por distrito
# Opción 1: Primer registro por distrito
primer_por_distrito = df_siglado.groupby(['entidad', 'distrito']).first().reset_index()
conteo_primer = primer_por_distrito['grupo_parlamentario'].value_counts().sort_values(ascending=False)

print("MÉTODO 1 - Primer registro por distrito:")
for partido, count in conteo_primer.items():
    print(f"  {partido}: {count}")
print(f"  TOTAL: {conteo_primer.sum()}")
print()

# Opción 2: Último registro por distrito  
ultimo_por_distrito = df_siglado.groupby(['entidad', 'distrito']).last().reset_index()
conteo_ultimo = ultimo_por_distrito['grupo_parlamentario'].value_counts().sort_values(ascending=False)

print("MÉTODO 2 - Último registro por distrito:")
for partido, count in conteo_ultimo.items():
    print(f"  {partido}: {count}")
print(f"  TOTAL: {conteo_ultimo.sum()}")
print()

# Verificar si hay algún patrón en los datos
print("🔍 ANÁLISIS DE PATRONES:")
print("-" * 25)

# Verificar si partido_origen es diferente
if 'partido_origen' in df_siglado.columns:
    print("Comparación grupo_parlamentario vs partido_origen:")
    diferentes = df_siglado[df_siglado['grupo_parlamentario'] != df_siglado['partido_origen']]
    print(f"Registros donde grupo_parlamentario ≠ partido_origen: {len(diferentes)}")
    if len(diferentes) > 0:
        print("Primeros 5 casos:")
        for _, row in diferentes.head().iterrows():
            print(f"  {row['entidad']}-{row['distrito']}: GP={row['grupo_parlamentario']}, PO={row['partido_origen']}")
    print()

print("🎯 CONCLUSIÓN:")
print("-" * 15)
print("Para que los resultados coincidan con R, necesitamos identificar")
print("exactamente cómo R selecciona 1 registro por distrito del archivo siglado.")
print("Los 402 registros sugieren que hay múltiples candidatos por distrito,")
print("pero solo uno debe ser el ganador.")
