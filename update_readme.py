import json
import re
import os
from playwright.sync_api import sync_playwright

# --- Configuration ---
CARD_WIDTH = 400
DISPLAY_WIDTH = 300
CARD_HEIGHT = 550
BADGES_PADDING = 15
CARD_BORDER_RADIUS = 15
CARD_BG_COLOR = "rgba(245, 245, 245, 1)"
BLURB_PADDING = 30
SCALE_FACTOR = 2

# --- Font and Color Customization (UPDATED) ---
TITLE_FONT_FAMILY = "Arial, sans-serif"
TITLE_COLOR = "#424141"
TITLE_FONT_SIZE = "20px"
BLURB_FONT_FAMILY = "Arial, sans-serif"
BLURB_COLOR = "#6e6e6e"
BLURB_FONT_SIZE = "14px"

# --- File Paths & Setup ---
IMAGE_OUTPUT_DIR = "portfolio_cards"
JSON_FILE_PATH = "projects.json"
README_PATH = "README.md"
os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

# --- Markers and Patterns for Parsing ---
START_MARKER = "<!-- Start of Project Grid -->"
END_MARKER = "<!-- End of Project Grid -->"
BLOCK_PATTERN = re.compile(
    f"{re.escape(START_MARKER)}(.*?){re.escape(END_MARKER)}", re.DOTALL
)

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

        html_template = f"""
        <div id="card" style="width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px; background-color: {CARD_BG_COLOR}; border-radius: {CARD_BORDER_RADIUS}px; overflow: hidden; display: inline-block; text-align: left; vertical-align: top;">
            <a href="{project['url']}" target="_blank">
                <img src="{project['thumbnail_url']}" alt="{project['title']}" style="width: 100%; border-radius: {CARD_BORDER_RADIUS}px {CARD_BORDER_RADIUS}px 0 0;">
            </a>
            <div style="padding: {BADGES_PADDING}px {BADGES_PADDING}px 0 {BADGES_PADDING}px;">
                {badges_html}
            </div>
            <div style="padding: 0 {BLURB_PADDING}px 0 {BLURB_PADDING}px;">
                <h3 style="font-family: {TITLE_FONT_FAMILY}; color: {TITLE_COLOR}; font-size: {TITLE_FONT_SIZE}; margin-bottom: 10px;">{project['title']}</h3>
                <p style="font-family: {BLURB_FONT_FAMILY}; color: {BLURB_COLOR}; font-size: {BLURB_FONT_SIZE}; line-height: 1.8;">{project['blurb']}</p>
            </div>
        </div>
        """

        page.set_content(html_template, wait_until="load")

        page.locator("#card").screenshot(
            path=f"{IMAGE_OUTPUT_DIR}/{image_filename}", omit_background=True
        )

        # UPDATED: Added style="margin: 15px;" to the img tag
        card_markdown = f'<a href="{project["url"]}" target="_blank"><img src="{IMAGE_OUTPUT_DIR}/{image_filename}" alt="{project["title"]}" width="{DISPLAY_WIDTH}" style="margin: 15px;"></a>'
        all_cards_markdown += card_markdown
        print(f"  -> Generated {image_filename}")

    browser.close()

# Note: The .strip() is removed and we add a newline to the markdown to help with wrapping
final_markdown = f'<p align="center">\n{all_cards_markdown}\n</p>'

# --- Read and inject into README ---
with open(README_PATH, "r", encoding="utf-8") as f:
    readme_content = f.read()

replacement_block = f"{START_MARKER}\n{final_markdown}\n{END_MARKER}"

new_readme_content, num_replacements = re.subn(
    BLOCK_PATTERN, replacement_block, readme_content
)

if num_replacements > 0:
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_readme_content)
    print("✅ README updated successfully!")
else:
    print(
        "⚠️  Could not find portfolio placeholders ...in README.md. No changes were made."
    )
