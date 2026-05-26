import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to login page...")
        await page.goto("https://isp-luki.trantortech.solutions/login")
        await page.wait_for_load_state('networkidle')
        
        print("Login page inputs:")
        inputs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll("input, button")).map(el => {
                return {
                    tag: el.tagName,
                    type: el.type,
                    name: el.name,
                    id: el.id,
                    placeholder: el.placeholder,
                    text: el.innerText
                };
            });
        }''')
        for i in inputs:
            print(i)
            
        print("Attempting login...")
        await page.fill("input[name='email']", "salvear@netdigital.com.ec")
        await page.fill("input[name='password']", "aesj1579")
        await page.click("button[type='submit']")
        
        print("Waiting for network idle...")
        await page.wait_for_load_state('networkidle')
        print("Current URL after login:", page.url)
        
        print("Menu links:")
        links = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll("a")).map(a => {
                return { text: a.innerText.trim(), href: a.href };
            });
        }''')
        for l in links:
            if l['text']:
                print(l)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
