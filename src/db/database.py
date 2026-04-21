import asyncpg
import traceback

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