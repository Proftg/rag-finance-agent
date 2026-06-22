import io
import time
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

URL = "http://localhost:8502"
OUT = Path("assets/demo.gif")
OUT.parent.mkdir(exist_ok=True)

W, H = 880, 820
frames = []


def snap(page, pause=0):
    if pause:
        time.sleep(pause)
    data = page.screenshot(type="png", clip={"x": 0, "y": 0, "width": W, "height": H})
    frames.append(Image.open(io.BytesIO(data)).convert("RGB"))


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": W, "height": H})
    page.goto(URL)

    print("Waiting for agent to load...")
    page.get_by_role("button", name="Send").wait_for(timeout=90000)
    snap(page, 1)

    # Q1: type manually
    page.locator("input[placeholder]").fill("What is the AUC score for fraud detection?")
    snap(page, 0.8)
    page.get_by_role("button", name="Send").click()
    snap(page, 1)

    print("Waiting for response 1...")
    page.wait_for_function("document.body.innerText.includes('AUC')", timeout=60000)
    snap(page, 1)
    snap(page, 2)

    # Q2: type in French
    page.locator("input[placeholder]").fill("Quel est le taux de défaut par décile de risque ?")
    snap(page, 0.8)
    page.get_by_role("button", name="Send").click()
    snap(page, 1)

    print("Waiting for response 2...")
    page.wait_for_function(
        "document.querySelectorAll('[data-testid=\"stChatMessage\"]').length >= 4",
        timeout=60000,
    )
    snap(page, 1)

    # Scroll to show both responses
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    snap(page, 1)
    snap(page, 3)

    browser.close()

# Remove temp frames
for f in Path("assets").glob("frame_*.png"):
    f.unlink()

durations = [2000] + [900] * (len(frames) - 2) + [4000]
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
print(f"GIF: {OUT} — {OUT.stat().st_size // 1024} KB, {len(frames)} frames")
