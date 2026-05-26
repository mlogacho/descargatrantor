import os
import asyncio
from playwright.async_api import async_playwright

async def download_contratos_report(username, password, download_dir):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        
        try:
            # 1. Navegar al Login
            await page.goto("https://isp-luki.trantortech.solutions/login")
            
            # 2. Rellenar credenciales usando los selectores correctos que encontramos
            await page.fill("input#email", username)
            await page.fill("input#password", password)
            await page.click("button[type='submit']")
            
            await page.wait_for_load_state('networkidle')
            
            # 3. Navegar directamente a la URL de Contratos
            await page.goto("https://isp-luki.trantortech.solutions/contrato-reporte")
            await page.wait_for_load_state('networkidle')
            
            # Presionar botón Consultar primero para que se habilite el Excel
            await page.get_by_text("Consultar", exact=True).first.click()
            # Esperar a que las peticiones terminen tras consultar
            await page.wait_for_load_state('networkidle')
            
            # 4. Descargar el reporte de Excel
            async with page.expect_download(timeout=60000) as download_info:
                await page.get_by_text("Excel").first.click()
                
            download = await download_info.value
            
            os.makedirs(download_dir, exist_ok=True)
            filepath = os.path.join(download_dir, download.suggested_filename)
            await download.save_as(filepath)
            
            return filepath
            
        except Exception as e:
            await page.screenshot(path="error_screenshot.png")
            raise e
        finally:
            await browser.close()
