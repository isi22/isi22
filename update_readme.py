import json
import re
import os
from playwright.sync_api import sync_playwright

# --- Configuration ---
CARD_WIDTH = 400
DISPLAY_WIDTH = 400
CARD_HEIGHT = 550
BADGES_PADDING = 30
CARD_BORDER_RADIUS = 15
BLURB_PADDING = 30
SCALE_FACTOR = 6
SHADOW_OFFSET = 20

# --- Light & Dark Theme Styles ---
# Light Theme
CARD_BG_COLOR_LIGHT = "rgba(255, 255, 255, 1)"
TITLE_COLOR_LIGHT = "#24292f"
BLURB_COLOR_LIGHT = "#57606a"
BOX_SHADOW_LIGHT = "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);"

# Dark Theme
CARD_BG_COLOR_DARK = "rgba(25,30,35, 1)"  # A dark grey
TITLE_COLOR_DARK = "#f0f6fc"
BLURB_COLOR_DARK = "#d3d7dc"
# A subtle white "glow" for the dark mode shadow
BOX_SHADOW_DARK = (
    "0 4px 8px 0 rgba(255, 255, 255, 0.8), 0 6px 20px 0 rgba(255, 255, 255, 0.8);"
)

# --- Font Customization ---
MODERN_FONT_STACK = "Arial, sans-serif"
TITLE_FONT_FAMILY = MODERN_FONT_STACK
TITLE_FONT_SIZE = "20px"
BLURB_FONT_FAMILY = MODERN_FONT_STACK
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
    viewport_width = CARD_WIDTH + SHADOW_OFFSET * 2
    viewport_height = CARD_HEIGHT + SHADOW_OFFSET * 2
    context = browser.new_context(
        device_scale_factor=SCALE_FACTOR,
        viewport={"width": viewport_width, "height": viewport_height},
    )
    page = context.new_page()

    for project in projects:
        safe_title = re.sub(r"[^a-zA-Z0-9_-]", "", project["title"]).lower()

        # Loop through themes to generate a card for each
        for theme in ["light", "dark"]:
            if theme == "light":
                card_bg = CARD_BG_COLOR_LIGHT
                title_color = TITLE_COLOR_LIGHT
                blurb_color = BLURB_COLOR_LIGHT
                box_shadow = BOX_SHADOW_LIGHT
            else:  # dark
                card_bg = CARD_BG_COLOR_DARK
                title_color = TITLE_COLOR_DARK
                blurb_color = BLURB_COLOR_DARK
                box_shadow = BOX_SHADOW_DARK

            image_filename = f"{safe_title}-{theme}.png"
            badges_html = project.get("badges", "")

            html_template = f"""
            <body style="margin: 0; display: flex; justify-content: center; align-items: center; width: 100vw; height: 100vh;">
                <div id="card" style="width: {CARD_WIDTH}px; height: {CARD_HEIGHT}px; background-color: {card_bg}; border-radius: {CARD_BORDER_RADIUS}px; box-shadow: {box_shadow}; overflow: hidden;">
                    <a href="{project['url']}" target="_blank">
                        <img src="{project['thumbnail_url']}" alt="{project['title']}" style="width: 100%; border-radius: {CARD_BORDER_RADIUS}px {CARD_BORDER_RADIUS}px 0 0;">
                    </a>
                    <div style="padding: {BADGES_PADDING}px {BADGES_PADDING}px 0 {BADGES_PADDING}px;">{badges_html}</div>
                    <div style="padding: 0 {BLURB_PADDING}px 0 {BLURB_PADDING}px;">
                        <h3 style="font-family: {TITLE_FONT_FAMILY}; color: {title_color}; font-size: {TITLE_FONT_SIZE}; margin-bottom: 10px;">{project['title']}</h3>
                        <p style="font-family: {BLURB_FONT_FAMILY}; color: {blurb_color}; font-size: {BLURB_FONT_SIZE}; line-height: 1.6;">{project['blurb']}</p>
                    </div>
                </div>
            </body>
            """

            page.set_content(html_template, wait_until="load")
            page.screenshot(
                path=f"{IMAGE_OUTPUT_DIR}/{image_filename}", omit_background=True
            )
            print(f"  -> Generated {image_filename}")

        # Create markdown that includes both light and dark themed images
        light_img_url = f"{IMAGE_OUTPUT_DIR}/{safe_title}-light.png#gh-light-mode-only"
        dark_img_url = f"{IMAGE_OUTPUT_DIR}/{safe_title}-dark.png#gh-dark-mode-only"

        card_markdown = f"""
<a href="{project['url']}" target="_blank">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="{dark_img_url}">
        <source media="(prefers-color-scheme: light)" srcset="{light_img_url}">
        <img src="{light_img_url}" alt="{project['title']}" width="{DISPLAY_WIDTH}" style="margin: 15px;">
    </picture>
</a>"""
        all_cards_markdown += card_markdown

    browser.close()

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
        f"⚠️ Could not find portfolio placeholders between '{START_MARKER}' and '{END_MARKER}' in README.md. No changes were made."
    )
