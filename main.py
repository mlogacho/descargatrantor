import os
import uuid
import shutil
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import scraper

load_dotenv()

app = FastAPI(
    title="API Descarga Contratos CRM Luki",
    description="Descarga reportes del CRM Luki y sincroniza suscriptores al CMS LukiPlay",
)


# ─── DTOs ────────────────────────────────────────────────────

class DownloadRequest(BaseModel):
    username: str
    password: str


class SyncRequest(BaseModel):
    # Credenciales CRM — si se omiten se usan las variables de entorno
    crm_username: Optional[str] = None
    crm_password: Optional[str] = None
    # CMS destino — si se omiten se usan las variables de entorno
    cms_url: Optional[str] = None
    # Token directo (opcional — si no se pasa se hace login automático)
    cms_token: Optional[str] = None
    # Credenciales CMS para login automático
    cms_email: Optional[str] = None
    cms_password: Optional[str] = None
    # ID del plan de suscripción a asignar (string, ej: "plan-lukiplay")
    subscription_plan_id: Optional[str] = "plan-lukiplay"


# ─── Helpers ─────────────────────────────────────────────────

async def get_cms_token(cms_url: str, email: str, password: str) -> str:
    """Hace login al CMS y devuelve el access token."""
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.post(
            f"{cms_url}/auth/cms/login",
            json={"email": email, "password": password, "deviceId": "sync-service"},
        )
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Credenciales CMS incorrectas.")
    if response.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Error al hacer login en el CMS (HTTP {response.status_code}): {response.text[:200]}",
        )
    data = response.json()
    token = data.get("accessToken")
    if not token:
        raise HTTPException(status_code=502, detail="El CMS no devolvió un accessToken.")
    return token


# ─── Endpoints ───────────────────────────────────────────────

@app.post("/api/reportes/contratos")
async def get_reporte_contratos(req: DownloadRequest):
    """Descarga el Excel de contratos del CRM Luki y lo devuelve como archivo."""
    download_dir = os.path.join(os.getcwd(), "downloads", str(uuid.uuid4()))
    try:
        filepath = await scraper.download_contratos_report(
            req.username, req.password, download_dir
        )
        if not filepath or not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="El archivo no se descargó correctamente.")

        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el scraping: {str(e)}")


@app.post("/api/sync")
async def sync_subscribers(req: SyncRequest = SyncRequest()):
    """
    Descarga el Excel del CRM Luki e importa los suscriptores al CMS LukiPlay.

    Credenciales resueltas en orden: body → variables de entorno.
    El token CMS se obtiene automáticamente con CMS_EMAIL + CMS_PASSWORD
    si no se pasa cms_token directamente.
    """
    crm_username = req.crm_username or os.getenv("CRM_USERNAME")
    crm_password = req.crm_password or os.getenv("CRM_PASSWORD")
    cms_url      = (req.cms_url or os.getenv("CMS_URL", "")).rstrip("/")
    cms_token    = req.cms_token or os.getenv("CMS_TOKEN")
    cms_email    = req.cms_email or os.getenv("CMS_EMAIL")
    cms_password = req.cms_password or os.getenv("CMS_PASSWORD")
    subscription_plan_id = req.subscription_plan_id or os.getenv("SUBSCRIPTION_PLAN_ID", "plan-lukiplay")

    if not crm_username or not crm_password:
        raise HTTPException(status_code=422, detail="Credenciales CRM requeridas (CRM_USERNAME / CRM_PASSWORD).")
    if not cms_url:
        raise HTTPException(status_code=422, detail="URL del CMS requerida (CMS_URL).")

    # Auto-login si no hay token directo
    if not cms_token:
        if not cms_email or not cms_password:
            raise HTTPException(
                status_code=422,
                detail="Se requiere cms_token o CMS_EMAIL + CMS_PASSWORD para autenticar con el CMS.",
            )
        cms_token = await get_cms_token(cms_url, cms_email, cms_password)

    download_dir = os.path.join(os.getcwd(), "downloads", str(uuid.uuid4()))
    try:
        # 1. Descargar Excel del CRM
        filepath = await scraper.download_contratos_report(
            crm_username, crm_password, download_dir
        )
        if not filepath or not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="No se pudo descargar el Excel del CRM.")

        # 2. Enviar Excel al CMS
        async with httpx.AsyncClient(timeout=120) as client:
            with open(filepath, "rb") as f:
                files   = {"file": (os.path.basename(filepath), f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                headers = {"Authorization": f"Bearer {cms_token}"}
                data    = {"subscriptionPlanId": subscription_plan_id}

                response = await client.post(
                    f"{cms_url}/admin/users/import-excel",
                    files=files,
                    data=data,
                    headers=headers,
                )

        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Token CMS inválido o expirado.")
        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"CMS rechazó la importación (HTTP {response.status_code}): {response.text[:300]}",
            )

        return {
            "ok":      True,
            "source":  "crm-luki",
            "cms_url": cms_url,
            "result":  response.json(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la sincronización: {str(e)}")
    finally:
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir, ignore_errors=True)
