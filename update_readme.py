import json
import re
import os
from playwright.sync_api import sync_playwright

# --- Configuration ---
CARD_WIDTH = 400
DISPLAY_WIDTH = 400
CARD_HEIGHT = 550
# Margin is no longer needed for the screenshot itself
# CARD_MARGIN = 15
BADGES_PADDING = 15
CARD_BORDER_RADIUS = 15
CARD_BG_COLOR = "rgba(245, 245, 245, 1)"
BLURB_PADDING = 30
TITLE_FONT_FAMILY = "Arial"
TITLE_COLOR = "#424141"
TITLE_FONT_SIZE = "20px"
BLURB_FONT_FAMILY = "Arial"
BLURB_COLOR = "#6e6e6e"
BLURB_FONT_SIZE = "14px"
SCALE_FACTOR = 2

# --- File Paths & Setup ---
IMAGE_OUTPUT_DIR = "portfolio_cards"
JSON_FILE_PATH = "projects.json"
README_PATH = "README.md"
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
    projects = json.load(f)

all_cards_markdown = ""
print(f"Found {len(projects)} projects. Starting Playwright to generate images...")

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(
        device_scale_factor=SCALE_FACTOR,
        viewport={"width": CARD_WIDTH, "height": CARD_HEIGHT},
    )
    page = context.new_page()

    for project in projects:
        badges_html = project.get("badges", "")
        safe_title = re.sub(r"[^a-zA-Z0-9_-]", "", project["title"]).lower()
        image_filename = f"{safe_title}.png"

        # Note: id="card" is added, margin is removed, and 'px' units are added for clarity.
        html_template = f"""
        <div id="card" style="width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px; background-color: {CARD_BG_COLOR}; border-radius: {CARD_BORDER_RADIUS}px; overflow: hidden; display: inline-block; text-align: left; vertical-align: top;">
            <a href="{project['url']}" target="_blank">
                <img src="{project['thumbnail_url']}" alt="{project['title']}" style="width: 100%; border-radius: {CARD_BORDER_RADIUS}px {CARD_BORDER_RADIUS}px 0 0;">
            </a>
            <div style="padding: {BADGES_PADDING}px {BADGES_PADDING}px 0 {BADGES_PADDING}px;">
                {badges_html}
            </div>
            <div style="padding: 0 {BLURB_PADDING}px 0 {BLURB_PADDING}px;">
                <h3 style="font-family: {TITLE_FONT_FAMILY}; color: {TITLE_COLOR}; font-size: {TITLE_FONT_SIZE};">{project['title']}</h3>
                <p style="font-family: {BLURB_FONT_FAMILY}; color: {BLURB_COLOR}; font-size: {BLURB_FONT_SIZE};">{project['blurb']}</p>   
            </div>
        </div>
        """

        page.set_content(html_template, wait_until="load")

        # **THE FIX**: Locate the card by its ID and screenshot just that element.
        page.locator("#card").screenshot(
            path=f"{IMAGE_OUTPUT_DIR}/{image_filename}", omit_background=True
        )

        card_markdown = f'<a href="{project["url"]}" target="_blank"><img src="{IMAGE_OUTPUT_DIR}/{image_filename}" alt="{project["title"]}" width="{DISPLAY_WIDTH}"></a>'
        all_cards_markdown += card_markdown + " "
        print(f"  -> Generated {image_filename}")

    browser.close()

final_markdown = f'<p align="center">\n{all_cards_markdown.strip()}\n</p>'

# --- Read and inject into README (using safe placeholders is recommended) ---
# This part assumes you've added ...to your README
with open(README_PATH, "r", encoding="utf-8") as f:
    readme_content = f.read()

replacement_block = f"\n{final_markdown}\n"

new_readme_content, num_replacements = re.subn(
    r"(?s).*", replacement_block, readme_content
)

if num_replacements > 0:
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_readme_content)
    print("✅ README updated successfully!")
else:
    print("⚠️  Could not find portfolio placeholders in README.md. No changes made.")
