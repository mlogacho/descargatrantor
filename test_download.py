import asyncio
import os
from scraper import download_contratos_report

async def run_test():
    username = "salvear@netdigital.com.ec"
    password = "aesj1579"
    
    # Carpeta donde se guardará el archivo descargado
    download_dir = os.path.join(os.getcwd(), "prueba_descargas")
    
    print("========================================")
    print("Iniciando prueba de descarga automática")
    print(f"Usuario: {username}")
    print("========================================")
    
    try:
        filepath = await download_contratos_report(username, password, download_dir)
        print("\n✅ ¡Éxito! El archivo se descargó correctamente.")
        print(f"📂 Ruta del archivo: {filepath}")
        print("========================================")
    except Exception as e:
        print(f"\n❌ Error durante la descarga: {e}")
        print("Revisa el archivo 'error_screenshot.png' si se generó para ver dónde falló.")

if __name__ == "__main__":
    asyncio.run(run_test())
