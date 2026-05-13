from fastapi import (APIRouter, Query,
                     Depends, HTTPException)
from fastapi.responses import Response, FileResponse
from src.models.inventario import (inventarioRequest, InventarioParams,
                                   InventarioUpdate,InventarioResponse,
                                   SearchResponse,SearchParams)
from src.services.inventario_service import (set_inventario,get_invent,
                                             search,update, join_inventario)
from src.services.auth_service import require_role
from src.services.latex_service import (
    preparar_entorno_compilacion,
    generate_equipos_tex,
    compile_latex_to_pdf,
    search as search_uuids
)

router = APIRouter(prefix="/inventario", tags=["inventario"])

@router.get("/search",response_model=list[SearchResponse])
async def join_invent(
    filters: SearchParams=Depends(),
    limit: int = Query(10, ge=1, le=50),
    page: int = Query(1, ge=1)
    #current_user: dict = Depends(require_role(5)) 
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


@router.post("/qr")
async def generar_etiquetas(uuids: list[str]):
    """
    Endpoint para generar un PDF de etiquetas en lote basado en una lista de UUIDs.
    """
    
    # 1. Preparar el entorno (Crear carpeta única y copiar master.tex)
    entorno = await preparar_entorno_compilacion()
    if entorno["status"] == "error":
        raise HTTPException(status_code=500, detail=f"Error de infraestructura: {entorno['message']}")

    path_trabajo = entorno["path_trabajo"]
    path_master = entorno["path_master_tex"]
    path_equipos = entorno["path_equipos_tex"]

    try:
        # 2. Consultar datos en la DB
        # La función search ya devuelve una lista de diccionarios
        datos_equipos = await search_uuids(uuids)
        
        # 3. Sanitizar datos y escribir el archivo equipos.tex
        # Esta función internamente llama a sanitize_latex para cada campo
        exito_escritura = await generate_equipos_tex(datos_equipos, str(path_equipos))
        if not exito_escritura:
            raise HTTPException(status_code=500, detail="Error al procesar los datos para LaTeX")

        # 4. Compilar el PDF
        # Invocamos a pdflatex dentro de la carpeta del lote
        exito_compilacion, mensaje_latex = await compile_latex_to_pdf(str(path_master), str(path_trabajo))
        
        if not exito_compilacion:
            # En caso de error, podrías querer revisar el mensaje_latex (logs de pdflatex)
            raise HTTPException(status_code=500, detail=f"Error de compilación LaTeX: {mensaje_latex[:200]}")

        # 5. Localizar el PDF resultante
        # Por defecto, pdflatex genera el PDF con el mismo nombre que el maestro: master.pdf
        pdf_final = path_trabajo / "master.pdf"
        
        if not pdf_final.exists():
            raise HTTPException(status_code=500, detail="El PDF no se encontró tras la compilación")

        # 6. Servir el archivo directamente
        return FileResponse(
            path=pdf_final, 
            filename=f"etiquetas_lote_{entorno['id_lote'][:8]}.pdf",
            media_type='application/pdf'
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        # Aquí podrías loguear el error completo para depuración
        raise HTTPException(status_code=500, detail=f"Error inesperado en el servidor: {str(e)}")