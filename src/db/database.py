import asyncpg
import traceback
from datetime import datetime
from typing import Any


from src.core.config import *

pool = None

async def init_db():
    global pool

    try:
        print("=== DEBUG DB CONNECTION ===")
        print(f"HOST: {SERVER}")
        print(f"PORT: {PORT}")
        print(f"USER: {DBUSER}")
        print(f"DATABASE: {DATABASE}")
        print("===========================")

        # Validación básica
        if not all([SERVER, PORT, DBUSER, PASSWORD, DATABASE]):
            raise ValueError("Faltan variables de entorno para la conexión a la DB")

        # Intenta la creación de la pool
        pool = await asyncpg.create_pool(
            user=DBUSER,
            password=PASSWORD,
            host=SERVER,
            port=int(PORT),
            database=DATABASE,
            min_size=1,
            max_size=10,
            timeout=10
        )

        # Test de conexión real
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 1;")
            print("DB TEST RESULT:", result)
            print(pool)

        print("Pool creado correctamente")

    except Exception as e:
        print("ERROR AL INICIALIZAR DB:")
        print(str(e))
        traceback.print_exc()

        # reestablece el pool a None en caso de fallo
        pool = None



async def close_db():
    global pool
    if pool:
        await pool.close()
        print("Pool cerrado")

async def get_pool():
    global pool
    return pool

from datetime import datetime, date
from typing import Any

def build_dynamic_query(params: dict, whitelist: list) -> tuple[str, list]:
    conditions = []
    values = []
    counter = 1
  
    for key, value in params.items():
        if key not in whitelist or value is None:
            continue

        # STR → búsqueda parcial
        if isinstance(value, str):
            conditions.append(f'"{key}" ILIKE ${counter}')
            values.append(f"%{value}%")

        # BOOL → igualdad
#        elif isinstance(value, bool):
#           conditions.append(f"{key} = ${counter}")
#            values.append(value)

        # INT / FLOAT → igualdad
        elif isinstance(value, (int, float,bool)):
            conditions.append(f'"{key}" = ${counter}')
            values.append(value)

        # DATETIME / DATE → igualdad (básico)
        elif isinstance(value, (datetime, date)):
            conditions.append(f'"{key}" = ${counter}')
            values.append(value)

        # LIST → IN (...)
#        elif isinstance(value, list) and value:
#            placeholders = []
#            for v in value:
#                placeholders.append(f"${counter}")
#                values.append(v)
#                counter += 1
#            conditions.append(f"{key} IN ({', '.join(placeholders)})")
#            continue  # ya incrementamos counter dentro

        else:
            raise ValueError(f"Tipo no soportado para {key}: {type(value)}")

        counter += 1

    where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""

    return where_clause, values

#def build_dynamic_query(params: dict, whitelist: list) -> tuple[str, list]:
#    conditions = []
#    values = []
#    counter = 1
#
#    for key, value in params.items():
#        if key in whitelist and value is not None:
#            # Usamos ILIKE para búsquedas parciales
#            conditions.append(f"{key} ILIKE ${counter}")
#            # Añadimos los % aquí para no ensuciar el endpoint
#            values.append(f"%{value}%")
#            counter += 1
#
#    where_clause = ""
#   if conditions:
#        where_clause = " WHERE " + " AND ".join(conditions)
#    
#    return where_clause, values