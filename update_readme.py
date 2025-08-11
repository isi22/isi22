import json
import re

# --- Configuration ---
# You can customize these values to match your style
CARD_WIDTH = "400px"
CARD_HEIGHT = "550px"
CARD_MARGIN = "15px"
CARD_PADDING = "20px" # Adds space around the text content
CARD_BORDER_RADIUS = "15px"
CARD_BG_COLOR = "rgba(245, 245, 245, 1)" # Using the color from your example

# --- Font and Color Customization ---
TITLE_FONT_FAMILY = "Arial, sans-serif"
TITLE_COLOR = "#424141"
TITLE_FONT_SIZE = "20px"
BLURB_FONT_FAMILY = "Arial, sans-serif"
BLURB_COLOR = "#6e6e6e"
BLURB_FONT_SIZE = "14px"

# --- File Paths ---
json_file_path = 'projects.json'
readme_path = 'README.md'

with open(json_file_path, 'r', encoding='utf-8') as f:
    projects = json.load(f)

# This will hold the HTML for all the cards
all_cards_html = ""

for project in projects:
    badges_html = project.get('badges', '')

    # Create the HTML for one card
    card_html = f"""
    <div style="width: {CARD_WIDTH}; height: {CARD_HEIGHT}; margin: {CARD_MARGIN}; background-color: {CARD_BG_COLOR}; border-radius: {CARD_BORDER_RADIUS}; overflow: hidden; display: inline-block; text-align: left; vertical-align: top;">
      <a href="{project['url']}" target="_blank">
        <img src="{project['thumbnail_url']}" alt="{project['title']}" style="width: 100%; border-radius: {CARD_BORDER_RADIUS} {CARD_BORDER_RADIUS} 0 0;">
      </a>
      <div style="padding: {CARD_PADDING};">
        {badges_html}
        <h3 style="font-family: {TITLE_FONT_FAMILY}; color: {TITLE_COLOR}; font-size: {TITLE_FONT_SIZE}; margin-top: 10px; margin-bottom: 10px;">{project['title']}</h3>
        <p style="font-family: {BLURB_FONT_FAMILY}; color: {BLURB_COLOR}; font-size: {BLURB_FONT_SIZE};">{project['blurb']}</p>
      </div>
    </div>
    """
    
    # Clean and compress the HTML string to prevent formatting issues
    cleaned_card_html = ' '.join(card_html.split())
    all_cards_html += cleaned_card_html

# Wrap all the cards in a single centering div
final_html = f'<div style="text-align: center;">\n{all_cards_html}\n</div>'


# --- Read the existing README and inject the new content ---
with open(readme_path, 'r', encoding='utf-8') as f:
    readme_content = f.read()

new_readme_content = re.sub(
    r'(?s).*',
    f'\n{final_html}\n',
    readme_content
)

with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(new_readme_content)

print("✅ README updated with compressed HTML to fix display issues.")