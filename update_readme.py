import json
import re

# --- Configuration ---
# You can adjust these values to change the appearance
CARD_WIDTH = "400px"            # Fixed width for each card
CARD_HEIGHT = "550px"       # The minimum height for each card (allows it to grow if needed)
CARD_MARGIN = "15px"            # Space between cards
BADGES_PADDING = "15px"
CARD_BORDER_RADIUS = "15px"
CARD_BG_COLOR = "rgba(245, 245, 245, 1)" # Semi-transparent grey for light/dark themes
BLURB_PADDING = "30px"
# --- Font and Color Customization ---
# Use web-safe fonts. 'inherit' lets GitHub's theme (light/dark) control the color.
TITLE_FONT_FAMILY = "Arial"
TITLE_COLOR = "#424141"  # or change to a hex code like '#24292f'
TITLE_FONT_SIZE = "20px"

BLURB_FONT_FAMILY = "Arial"
BLURB_COLOR = "#6e6e6e"  # or change to a hex code like '#57606a'
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

    # Create the HTML for one card with the new vertical layout
    card_html = f"""
    <div style="width: {CARD_WIDTH}; height: {CARD_HEIGHT}; margin: {CARD_MARGIN}; background-color: {CARD_BG_COLOR}; border-radius: {CARD_BORDER_RADIUS}; overflow: hidden; display: inline-block; text-align: left; vertical-align: top;">
      <a href="{project['url']}" target="_blank">
        <img src="{project['thumbnail_url']}" alt="{project['title']}" style="width: 100%; border-radius: {CARD_BORDER_RADIUS} {CARD_BORDER_RADIUS} 0 0;">
      </a>
      <div style="padding: {BADGES_PADDING} {BADGES_PADDING} 0 {BADGES_PADDING};">
        {badges_html}
      </div>
      <div style="padding: 0 {BLURB_PADDING} 0 {BLURB_PADDING};">
        <h3 style="font-family: {TITLE_FONT_FAMILY}; color: {TITLE_COLOR}; font-size: {TITLE_FONT_SIZE};">{project['title']}</h3>
        <p style="font-family: {BLURB_FONT_FAMILY}; color: {BLURB_COLOR}; font-size: {BLURB_FONT_SIZE};">{project['blurb']}</p>   
      </div>
    </div>
    """
    
    # Clean and compress the HTML string for reliability
    cleaned_card_html = ' '.join(card_html.split())

    # Add the cleaned HTML to our container
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

print("✅ README updated with full-width header images on cards!")