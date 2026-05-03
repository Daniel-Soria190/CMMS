from fastapi import APIRouter, Query, Depends
from fastapi import HTTPException 
from fastapi.responses import Response
from src.models.orden import ordenRequest,ordenParams,ordenUpdate
from src.services.orden_service import set_orden,search,get_orden,update
from src.models.auth import TokenResponse



router = APIRouter(prefix="/orden", tags=["orden"])

#@router.get ( "/")
#async def buscar_orden (
#    idOrden: Optional[int] = Query(None),
#    idEquipoInstall: Optional[int] = Query(None),
#    prioridad: Optional[str] = Query(None),
#    estado:Optional[str]=Query(None),
#    fechaEnt:Optional[datetime]=Query(None),
#    asignadoa:Optional[int]=Query(None),
#    creadopor:Optional[int]=Query(None),
#    ):
#    return await search (idOrden,idEquipoInstall,prioridad,estado,fechaSoli,fechaEnt,asignadoa,creadopor)


@router.get("/")
async def buscar_orden(
    filters: ordenParams = Depends(),
    limit: int = Query(10, ge=1, le=50), # Validamos min 1, max 50
    page: int = Query(1, ge=1)           # Página actual
):
    # Calculamos el offset (ej: página 1 -> offset 0, página 2 -> offset 10)
    offset = (page - 1) * limit
    
    # Convertimos el modelo a dict filtrando los None
    query_data = filters.model_dump(exclude_none=True)
    
    return await search(query_data, limit, offset)


@router.get("/{idOrden}")
async def obtener_orden (idOrden:int):
    return await get_orden(idOrden)


@router.patch ("/{idOrden}")
async def update_orden(id:int ,
                        filter:ordenUpdate=Depends()):
    data= filter.model_dump(exclude_none=True)
    return await update(id,data)


@router.post("/")
async def orden( orden:ordenRequest):
    return await set_orden(orden)