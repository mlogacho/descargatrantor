# API Descarga de Contratos - Trantor

Esta es una API desarrollada en **Python (FastAPI)** que automatiza la descarga del reporte de contratos (Excel) desde el portal ISP Luki utilizando **Playwright**.

## 🛠️ Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/mlogacho/descargatrantor.git
   cd descargatrantor
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias y los navegadores de Playwright:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

## 🚀 Uso

### 1. Ejecutar como API Servidor
Ideal para integrar con otras aplicaciones o frontends.
```bash
source venv/bin/activate
uvicorn main:app --reload
```
El servidor iniciará en `http://127.0.0.1:8000`. Puedes ingresar a `http://127.0.0.1:8000/docs` para visualizar la interfaz de **Swagger** y realizar pruebas del endpoint `POST /api/reportes/contratos`.

### 2. Ejecutar Prueba Local (Script)
Ideal para probar rápidamente o descargar el archivo manualmente a tu equipo sin levantar el servidor.
```bash
./test.sh
```
*(Este script requiere que hayas activado el entorno virtual o usará el ejecutable de `venv` automáticamente).* El Excel descargado se guardará en la carpeta `prueba_descargas/`.

## 📁 Estructura Principal
- `scraper.py`: Contiene la lógica de automatización del navegador web (login, clicks y guardado de archivo).
- `main.py`: Código del servidor FastAPI.
- `test_download.py` y `test.sh`: Scripts para automatizar la prueba de la descarga.
