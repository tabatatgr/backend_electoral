import duckdb

con = duckdb.connect()

# Verificar todos los modelos disponibles
query1 = "SELECT DISTINCT modelo FROM 'data/resumen-modelos-votos-escanos-diputados.parquet'"
modelos_dip = con.execute(query1).fetchall()
print('Modelos diputados:', [m[0] for m in modelos_dip])

query2 = "SELECT DISTINCT modelo FROM 'data/senado-resumen-modelos-votos-escanos.parquet'"
modelos_sen = con.execute(query2).fetchall()
print('Modelos senado:', [m[0] for m in modelos_sen])

con.close()
