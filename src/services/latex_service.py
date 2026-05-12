from fastapi import HTTPException
from src.db.database import get_pool
import uuid
import subprocess
import os
import shutil
import shutil
from pathlib import Path
import re

def sanitize_latex(text: str) -> str:
    if text is None:
        return ""
    
    # Mapa de caracteres especiales de LaTeX
    latex_special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    
    # Usamos un regex para encontrar y reemplazar de forma eficiente
    regex = re.compile('|'.join(re.escape(str(key)) for key in latex_special_chars.keys()))
    return regex.sub(lambda match: latex_special_chars[match.group()], str(text))

async def search(uuids: list):
    pool = await get_pool()
    if pool is None:
        raise HTTPException(status_code=500, detail="DB no inicializada")

    uuids_parsed = [uuid.UUID(u) if isinstance(u, str) else u for u in uuids]

    sql = """
                SELECT 
            E.marca, 
            E.modelo, 
            EI."numeroSerie", 
            A.nombre AS area_nombre, 
            EI."UUID"
        FROM 
            public."EquipoInstalado" AS EI
        JOIN 
            public."Equipo" AS E ON EI."idEquipo" = E."idEquipo"
        JOIN 
            public."Area" AS A ON EI."idArea" = A."idArea"
        WHERE 
            EI."UUID" = ANY($1)  -- $1 será la lista de UUIDs que enviaremos desde Python
            AND EI."isDeleted" = FALSE 
            AND E."isDeleted" = FALSE;
    """

    rows = await pool.fetch(sql, uuids_parsed)

    
    if not rows:
        # Nota: Es mejor devolver lista vacía [] que un 404 en búsquedas, 
        # pero mantengo tu lógica si así lo prefieres.
        return []
        # raise HTTPException(status_code=404, detail= "Equipo no encontrado")

    return [dict(row) for row in rows]


async def generate_equipos_tex(data_list: list, output_path: str):
    """
    Genera el archivo .tex con las llamadas al comando \etiqueta
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for equipo in data_list:
                # Sanitizamos cada campo antes de escribirlo
                marca = sanitize_latex(equipo['marca'])
                modelo = sanitize_latex(equipo['modelo'])
                serie = sanitize_latex(equipo['numeroSerie'])
                area = sanitize_latex(equipo['area_nombre'])
                uuid_val = str(equipo['UUID']) # El UUID no suele requerir escape, pero lo tratamos como str
                
                # Escribimos la macro de LaTeX
                # \etiqueta{Marca}{Modelo}{Serie}{Area}{UUID}
                line = f"\\etiqueta{{{marca}}}{{{modelo}}}{{{serie}}}{{{area}}}{{{uuid_val}}}\n"
                f.write(line)
                
        return True
    except Exception as e:
        print(f"Error escribiendo equipos.tex: {e}")
        return False
    
    
async def compile_latex_to_pdf(master_file_path: str, output_dir: str):
    """
    Invoca a pdflatex para compilar el documento.
    master_file_path: Ruta completa al archivo .tex principal (el que tiene el \input).
    output_dir: Directorio donde queremos que quede el PDF final.
    """
    try:
        # Ejecutamos pdflatex. 
        # -output-directory: indica dónde dejar los archivos resultantes (.pdf, .log, .aux)
        # -interaction=nonstopmode: evita que el proceso se detenga por errores
        process = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                f"-output-directory={output_dir}",
                master_file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False # No lanzamos excepción aquí para manejar el error de LaTeX nosotros
        )

        # Verificamos si hubo errores críticos
        if process.returncode != 0:
            print(f"Error de compilación LaTeX:\n{process.stdout}")
            return False, process.stdout

        return True, "PDF generado con éxito"

    except Exception as e:
        print(f"Error ejecutando subprocess: {e}")
        return False, str(e)
    
BASE_DIR = Path("/app/data")
PLANTILLAS_DIR = BASE_DIR / "plantillas" / "Etiquetas"
ETIQUETAS_OUT_DIR = BASE_DIR / "etiquetas"

async def preparar_entorno_compilacion():
    """
    1. Crea un ID único para este lote de etiquetas.
    2. Crea una carpeta temporal para la compilación.
    3. Copia la plantilla maestra (master.tex) a la carpeta temporal.
    Returns: (path_trabajo, path_master_tex, id_lote)
    """
    # 1. Generar un ID único para este proceso
    id_lote = str(uuid.uuid4())
    path_trabajo = ETIQUETAS_OUT_DIR / id_lote
    
    try:
        # 2. Crear el directorio de trabajo
        # Esto creará /app/data/etiquetas/{uuid}/
        path_trabajo.mkdir(parents=True, exist_ok=True)
        
        # 3. Identificar la plantilla maestra original
        # Asumiendo que tu archivo se llama 'master.tex' en la carpeta de plantillas
        master_original = PLANTILLAS_DIR / "master.tex"
        master_destino = path_trabajo / "master.tex"
        
        if not master_original.exists():
            raise FileNotFoundError(f"No se encontró la plantilla maestra en {master_original}")
            
        # 4. Copiar la plantilla al directorio de trabajo
        shutil.copy2(master_original, master_destino)

        logo_original = PLANTILLAS_DIR / "logo.png"
        if logo_original.exists():
            shutil.copy2(logo_original, path_trabajo / "logo.png")
        
        # Retornamos las rutas necesarias para las funciones siguientes
        return {
            "status": "success",
            "id_lote": id_lote,
            "path_trabajo": path_trabajo,
            "path_master_tex": master_destino,
            "path_equipos_tex": path_trabajo / "equipos.tex"
        }

    except Exception as e:
        print(f"Error preparando el entorno: {e}")
        return {"status": "error", "message": str(e)}