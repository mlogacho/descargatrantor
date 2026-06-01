import os
import asyncio
from playwright.async_api import async_playwright

async def download_contratos_report(username, password, download_dir):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
        )
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()

        try:
            await page.goto("https://isp-luki.trantortech.solutions/login", wait_until='load')
            await asyncio.sleep(4)
            await page.fill("input[type='text']", username)
            await page.fill("input[type='password']", password)
            await page.click("button[type='submit']")
            await page.wait_for_load_state('load')
            await asyncio.sleep(3)

            if '/login' in page.url:
                await page.screenshot(path="error_login.png")
                raise Exception(f"Login fallido. URL: {page.url}")

            await page.goto("https://isp-luki.trantortech.solutions/contrato-reporte", wait_until='load')
            await asyncio.sleep(5)

            await page.get_by_text("Consultar", exact=True).first.click()
            await asyncio.sleep(5)

            async with page.expect_download(timeout=90000) as download_info:
                await page.get_by_text("Excel").first.click()

            download = await download_info.value
            os.makedirs(download_dir, exist_ok=True)
            filepath = os.path.join(download_dir, download.suggested_filename)
            await download.save_as(filepath)

            if os.path.getsize(filepath) < 5000:
                raise Exception(f"Excel inválido (tamaño: {os.path.getsize(filepath)} bytes)")

            return filepath

        except Exception as e:
            await page.screenshot(path="error_screenshot.png")
            raise e
        finally:
            await browser.close()
