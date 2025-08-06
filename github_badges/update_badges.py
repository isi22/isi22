import json
import re
import os

BADGES_FILE = "./badges_repo/badges.json"  # New path to the central badges file
README_FILE = "README.md"


def generate_badges():
    """Reads configuration files and generates the HTML for the badges."""
    badge_list_str = os.environ.get("BADGE_LIST", "")
    if not badge_list_str:
        print("Error: No badge list provided via environment variable.")
        return ""

    project_badges = [key.strip() for key in badge_list_str.split(",") if key.strip()]

    with open(BADGES_FILE, "r") as f:
        all_badges = json.load(f)

    html_badges = []
    for badge_key in project_badges:
        badge_data = all_badges.get(badge_key)
        if badge_data:
            badge_url = badge_data["badge_url"]
            alt_text = " ".join(word.capitalize() for word in badge_key.split("-"))
            html_badges.append(f'<img alt="{alt_text}" src="{badge_url}" />')

    return f'<p>\n  {" ".join(html_badges)}\n</p>'


def update_readme(new_badges_markdown):
    """Inserts the new badges into the README.md file."""
    if not os.path.exists(README_FILE):
        print(f"Error: {README_FILE} not found.")
        return

    with open(README_FILE, "r") as f:
        readme_content = f.read()

    start_marker = "<!--- Start of badges -->"
    end_marker = "<!--- End of badges -->"

    pattern = re.compile(f"{start_marker}.*?{end_marker}", re.DOTALL)
    new_content = f"{start_marker}\n{new_badges_markdown}\n{end_marker}"

    if re.search(pattern, readme_content):
        updated_readme = re.sub(pattern, new_content, readme_content)
        with open(README_FILE, "w") as f:
            f.write(updated_readme)
        print("README.md updated successfully with new badges.")
    else:
        print("Markers not found in README.md. Please add them.")


if __name__ == "__main__":
    markdown = generate_badges()
    if markdown:
        update_readme(markdown)
