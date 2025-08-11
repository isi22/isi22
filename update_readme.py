import json
import re
import textwrap

# --- Configuration ---
# Adjust these values to change the appearance of your cards
COLLAPSED_CARD_HEIGHT = "400px" # The strict height for the card BEFORE it's expanded
IMAGE_FRAME_HEIGHT = "200px"    # Fixed height for the image container
CARD_PADDING = "10px"
CARD_BORDER_RADIUS = "15px"
CARD_BG_COLOR = "rgba(215, 215, 215, 0.2)" # Semi-transparent grey

# --- File Paths ---
json_file_path = 'projects.json'
readme_path = 'README.md'

with open(json_file_path, 'r', encoding='utf-8') as f:
    projects = json.load(f)
# Start the main table that will hold the cards
html_content = "<table>\n<tr>\n"

for i, project in enumerate(projects):
    badges_html = project.get('badges', '')

    # The "front" of the card (visible part)
    summary_content = textwrap.dedent(f"""
    <table width="100%">
      <tr>
        <td style="height: {COLLAPSED_CARD_HEIGHT};">
          <a href="{project['url']}" target="_blank">
            <div style="height: {IMAGE_FRAME_HEIGHT}; display: flex; align-items: center; justify-content: center; overflow: hidden;">
              <img src="{project['thumbnail_url']}" alt="{project['title']}" style="max-width: 100%; max-height: 100%;">
            </div>
          </a>
          <br>
          <h3>{project['title']}</h3>
          {badges_html}
        </td>
      </tr>
    </table>
    """)
    
    # The "back" of the card (hidden blurb)
    details_content = textwrap.dedent(f"""
    <br>
    <blockquote>
      {project['blurb']}
    </blockquote>
    """)

    # Assemble the full collapsible <details> element
    card_details = textwrap.dedent(f"""
    <details>
      <summary>{summary_content.strip()}</summary>
      {details_content.strip()}
    </details>
    """).strip()

    # The outer div now ONLY handles aesthetics (background, border, padding) and has no height property.
    styled_card = textwrap.dedent(f"""
    <div style="background-color: {CARD_BG_COLOR}; border-radius: {CARD_BORDER_RADIUS}; padding: {CARD_PADDING};">
      {card_details}
    </div>
    """)

    # Add the complete styled card to a cell in our main grid
    html_content += f'<td width="50%" valign="top">{styled_card}</td>\n'

    # After every 2nd card, close the current row and start a new one
    if (i + 1) % 2 == 0 and (i + 1) < len(projects):
        html_content += "</tr>\n<tr>\n"

# Close the final row and the main table
html_content += "</tr>\n</table>"


# --- Read the existing README and inject the new content ---
with open(readme_path, 'r', encoding='utf-8') as f:
    readme_content = f.read()

new_readme_content = re.sub(
    r'(?s).*',
    f'\n{html_content}\n',
    readme_content
)

with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(new_readme_content)

print("✅ README updated! Cards now have a strict collapsed height and expand on click.")