from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from src.db.database import init_db, close_db, get_pool

from src.api.users import router as users_router
from src.api.login import router as login_router
from src.api.equipos import router as equipos_router
from src.api.ge import router as ge_router
from src.api.websockets import router as ws_router
from src.api.ordenes import router as ordenes_router


from src.api.mantenimiento import router as mantto_router
from src.api.orden import router as orden_router
# Inicialización de la API y Pool SQL
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando API...")
    await init_db()
    pool = get_pool()
    print("DB lista:", pool is not None)

    print (pool)

    yield

    print("Cerrando API...")
    await close_db()


app = FastAPI(lifespan=lifespan)

app.include_router(ws_router)
# app.include_router(auth_router)
app.include_router(users_router)
app.include_router(login_router)
app.include_router(equipos_router)
app.include_router(ge_router)
app.include_router(ordenes_router)
app.include_router(mantto_router)
app.include_router(orden_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}