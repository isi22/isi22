import json
import re
import os

BADGES_FILE = 'badges.json'
CONFIG_FILE = '.github/badges.txt'
README_FILE = 'README.md'

def generate_badges():
    """Reads configuration files and generates the HTML for the badges."""
    badges_file_path = os.path.join(os.getcwd(), BADGES_FILE)
    config_file_path = os.path.join(os.getcwd(), CONFIG_FILE)

    if not os.path.exists(badges_file_path):
        print(f"Error: {BADGES_FILE} not found.")
        return ""
    
    if not os.path.exists(config_file_path):
        print(f"Error: {CONFIG_FILE} not found.")
        return ""

    with open(badges_file_path, 'r') as f:
        all_badges = json.load(f)

    with open(config_file_path, 'r') as f:
        project_badges = [line.strip() for line in f if line.strip()]

    html_badges = []
    for badge_key in project_badges:
        badge_data = all_badges.get(badge_key)
        if badge_data:
            badge_url = badge_data['badge_url']
            # The alt text is a user-friendly version of the key
            alt_text = ' '.join(word.capitalize() for word in badge_key.split('-'))
            html_badges.append(f'<img alt="{alt_text}" src="{badge_url}" />')
    
    # Wrap the badges in a <p> tag and join them with a space for neatness
    return f'<p>\n  {" ".join(html_badges)}\n</p>'

def update_readme(new_badges_markdown):
    """Inserts the new badges into the README.md file."""
    readme_file_path = os.path.join(os.getcwd(), README_FILE)
    if not os.path.exists(readme_file_path):
        print(f"Error: {README_FILE} not found.")
        return

    with open(readme_file_path, 'r') as f:
        readme_content = f.read()

    start_marker = '<!--- Start of badges -->'
    end_marker = '<!--- End of badges -->'
    
    # Use a regex to find the content between the markers and replace it
    pattern = re.compile(f'{start_marker}.*?{end_marker}', re.DOTALL)
    new_content = f"{start_marker}\n{new_badges_markdown}\n{end_marker}"
    
    if re.search(pattern, readme_content):
        updated_readme = re.sub(pattern, new_content, readme_content)
        with open(readme_file_path, 'w') as f:
            f.write(updated_readme)
        print("README.md updated successfully with new badges.")
    else:
        print("Markers not found in README.md. Please add them.")
        
if __name__ == "__main__":
    markdown = generate_badges()
    if markdown:
        update_readme(markdown)