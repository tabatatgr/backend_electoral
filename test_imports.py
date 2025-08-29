#!/usr/bin/env python3
"""
Test de importaciones del main.py
"""

print("Probando importaciones...")

try:
    from fastapi import FastAPI, Query
    print("✅ FastAPI importado")
except Exception as e:
    print(f"❌ Error FastAPI: {e}")

try:
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ CORS importado")
except Exception as e:
    print(f"❌ Error CORS: {e}")

try:
    import duckdb
    print("✅ DuckDB importado")
except Exception as e:
    print(f"❌ Error DuckDB: {e}")

try:
    from kernel.magnitud import get_magnitud
    print("✅ kernel.magnitud importado")
except Exception as e:
    print(f"❌ Error kernel.magnitud: {e}")

try:
    from kernel.procesar_diputados import procesar_diputados_parquet
    print("✅ kernel.procesar_diputados importado")
except Exception as e:
    print(f"❌ Error kernel.procesar_diputados: {e}")

try:
    from kernel.procesar_senadores import procesar_senadores_parquet
    print("✅ kernel.procesar_senadores importado")
except Exception as e:
    print(f"❌ Error kernel.procesar_senadores: {e}")

try:
    from kernel.plan_c import procesar_plan_c_diputados
    print("✅ kernel.plan_c importado")
except Exception as e:
    print(f"❌ Error kernel.plan_c: {e}")

print("\nTodas las importaciones probadas.")
