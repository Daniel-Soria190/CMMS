from fastapi import APIRouter,Query,Depends
from fastapi import HTTPException
from fastapi.responses import Response
from src.models.inventario import inventarioRequest
from src.services.inventario_service import set_inventario,get_invent#,search,get_inventario,update

router = APIRouter(prefix="/inventario", tags=["inventario"])

#@router.get ( "/")
#async def buscar_user (
#    filters: userParams = Depends(), 
#    limit: int = Query(10, ge=1, le=50), # Validamos min 1, max 50
#    page: int = Query(1, ge=1)           # Página actual
#):
#    # Calculamos el offset (ej: página 1 -> offset 0, página 2 -> offset 10)
#    offset = (page - 1) * limit
#    
#    # Convertimos el modelo a dict filtrando los None
#    query_data = filters.model_dump(exclude_none=True)
#
#    return await search(query_data,limit, offset)
#=========================================================================================

@router.get("/{idInventario}")
async def obtener_inventario (idInventario:int):
    return await get_invent(idInventario)

#=================================================================================

#@router.patch ("/{idUser}")
#async def update_user(id:int ,
#                      filter:userUpdate=Depends()):
#    query_data= filter.model_dump(exclude_none=True)
#    return await update(id,query_data)

#=========================================================================

@router.post ("/")
async def inventario(invent: inventarioRequest):
    return await set_inventario(invent)