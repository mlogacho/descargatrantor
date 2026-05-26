from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uuid
import scraper

app = FastAPI(title="API Descarga Contratos ISP Luki", description="API para automatizar la descarga de reportes del sistema Luki")

class DownloadRequest(BaseModel):
    username: str
    password: str

@app.post("/api/reportes/contratos")
async def get_reporte_contratos(req: DownloadRequest):
    # Crear un directorio único para esta petición y evitar colisiones
    download_dir = os.path.join(os.getcwd(), "downloads", str(uuid.uuid4()))
    
    try:
        filepath = await scraper.download_contratos_report(req.username, req.password, download_dir)
        
        if not filepath or not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="El archivo no se descargó correctamente.")
            
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el scraping: {str(e)}")
