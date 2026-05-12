from fastapi import APIRouter 
from fastapi import HTTPException
from fastapi.responses import Response
from src.models.ge import funcionResponse,riesgoResponse,ReqMtoResponse,antecedenteResponse,AreaResponse
from src.services.ge_service import get_funcion,get_riesgo,get_ReqMto,get_antecedentes,get_area
from src.models.auth import TokenResponse


router = APIRouter(prefix="/GE", tags=["GE"])

@router.get("/Area/",
            response_model=list[AreaResponse],
            summary="Areas")    
async def funcion ():
    return await get_area()

@router.get("/GeFuncion/",
            response_model=list[funcionResponse],
            summary="Funciones del equipo")    
async def funcion ():
    return await get_funcion()

@router.get("/GeRiesgo/",
            response_model=list[riesgoResponse],
            summary="Riesgo del equipo")    

async def Riesgo ():
    return await get_riesgo()

@router.get("/GeReqMto/",
            response_model=list[ReqMtoResponse],
            summary="Requisitos de mantenimieto")    

async def ReqMto ():
    return await get_ReqMto()

@router.get("/GeAntecedentes/",
            response_model=list[antecedenteResponse],
            summary="Antecedentes de fallo")    
async def Antecedentes ():
    return await get_antecedentes()