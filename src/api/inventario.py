from fastapi import APIRouter,Query,Depends
from fastapi import HTTPException
from fastapi.responses import Response
from src.models.inventario import inventarioRequest,InventarioParams,InventarioUpdate,InventarioResponse,SearchResponse,SearchParams
from src.services.inventario_service import set_inventario,get_invent,search,update,join_inventario
from src.services.auth_service import require_role

router = APIRouter(prefix="/inventario", tags=["inventario"])

@router.get("/search",response_model=list[SearchResponse])
async def join_invent(
    filters: SearchParams=Depends(),
    limit: int = Query(10, ge=1, le=50),
    page: int = Query(1, ge=1),
    current_user: dict = Depends(require_role(5)) 
):
    offset = (page - 1) * limit
    
    # Convertimos el modelo a dict filtrando los None
    query_data = filters.model_dump(exclude_none=True)

    return await join_inventario(query_data,limit, offset)


#==========================================================
@router.get ( "/",response_model=list [InventarioResponse])
async def buscar_inventario (
    filters: InventarioParams = Depends(), 
    limit: int = Query(10, ge=1, le=50), # Validamos min 1, max 50
    page: int = Query(1, ge=1),           # Página actual
    current_user: dict = Depends(require_role(5))
):
    # Calculamos el offset (ej: página 1 -> offset 0, página 2 -> offset 10)
    offset = (page - 1) * limit
    
    # Convertimos el modelo a dict filtrando los None
    query_data = filters.model_dump(exclude_none=True)

    return await search(query_data,limit, offset)
#=========================================================================================

@router.get("/{idInventario}")
async def obtener_inventario (idInventario:int,
        current_user: dict = Depends(require_role(5))
        ):
    return await get_invent(idInventario)

#=================================================================================

@router.patch ("/{idInventario}")
async def update_inventario(idInventario:int ,
        filter:InventarioUpdate=Depends(),
        current_user: dict = Depends(require_role(5))
                      ):
    query_data= filter.model_dump(exclude_none=True)
    return await update(idInventario ,query_data)

#=========================================================================

@router.post ("/")
async def inventario(invent: inventarioRequest,
        current_user: dict = Depends(require_role(5))
                     ):
    return await set_inventario(invent)