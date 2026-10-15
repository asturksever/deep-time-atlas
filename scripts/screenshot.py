"""Visual check: screenshot dist page at 600/240/90/0 Ma (desktop) and 240 Ma (phone).
Needs: pip install playwright && python3 -m playwright install chromium
If cdnjs is blocked in your sandbox, set D3_LOCAL=path/to/d3.min.js (npm pack d3@7.9.0)."""
import asyncio, os
from pathlib import Path
from playwright.async_api import async_playwright
root = Path(__file__).resolve().parent.parent
src = (root / "dist/deep-time-atlas.html").read_text()
if os.environ.get("D3_LOCAL"):
    src = src.replace("https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js", os.environ["D3_LOCAL"])
test = root / "build/test.html"; test.write_text(src)
SEEK = """(t)=>{const el=document.getElementById('ruler'),r=el.getBoundingClientRect();
const x=r.left+18+(600-t)/600*(r.width-36);
el.dispatchEvent(new PointerEvent('pointerdown',{clientX:x,clientY:r.top+10,pointerId:1,bubbles:true}));}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, h, name, ts in [(1280, 1100, "desk", [600, 240, 90, 0]), (390, 1100, "phone", [240])]:
            pg = await b.new_page(viewport={"width": w, "height": h}); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto(test.as_uri()); await pg.wait_for_timeout(1500)
            for t in ts:
                await pg.evaluate(SEEK, t); await pg.wait_for_timeout(400)
                await pg.screenshot(path=str(root / f"build/shot_{name}_{t}.png"), full_page=True)
            print(name, "errors:", errs, "scrollWidth:", await pg.evaluate("document.documentElement.scrollWidth"))
        await b.close()
asyncio.run(main())
