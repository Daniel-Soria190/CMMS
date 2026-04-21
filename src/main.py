from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from src.db.database import *

from src.services.auth import router as auth_router

# Inicialización de la API y Pool SQL
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando API...")
    await init_db()
    print("DB lista:", pool is not None)

    yield

    print("Cerrando API...")
    await close_db()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}