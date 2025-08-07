import json
import re
import sys
from pathlib import Path
from typing import List

# --- Markers and Patterns ---
START_MARKER = "<!--- Start of badges -->"
END_MARKER = "<!--- End of badges -->"
BADGE_LIST_COMMENT_PATTERN = re.compile(r"<!-- Badges: (.*?) -->")
BADGE_BLOCK_PATTERN = re.compile(
    f"({re.escape(START_MARKER)}.*?{re.escape(END_MARKER)})", re.DOTALL
)
# --- Configuration ---
# Using Path objects is still good practice for handling paths correctly.
BADGES_FILE = "./self/github_badges/badges.json"  # New path to the central badges file


def generate_badges_html(badge_keys: List[str]) -> str:
    """
    Generates the HTML for the badges based on the provided keys and the
    central JSON file.
    """
    if not badge_keys:
        return ""

    try:
        with open(BADGES_FILE, "r", encoding="utf-8") as f:
            all_badges = json.load(f)
    except FileNotFoundError:
        print(f"Error: Badges file not found at {BADGES_FILE}")
        return ""
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {BADGES_FILE}.")
        return ""

    html_badges = []
    for key in badge_keys:
        badge_data = all_badges.get(key)
        if badge_data and "badge_url" in badge_data:
            alt_text = key.replace("_", " ").replace("-", " ").title()
            html_badges.append(
                f'<img alt="{alt_text}" src="{badge_data["badge_url"]}" />\n'
            )
        else:
            print(
                f"Warning: Badge key '{key}' not found or is missing 'badge_url' in {BADGES_FILE}."
            )

    return f'<p align="left">\n{" ".join(html_badges)}</p>' if html_badges else ""


def update_file(file_to_update: Path):
    """
    Reads a specific file, finds badge keys, generates new HTML,
    and updates the file.
    """
    try:
        if not file_to_update.exists():
            print(f"Error: Target file not found: {file_to_update}")
            return

        content = file_to_update.read_text(encoding="utf-8")
        match = BADGE_LIST_COMMENT_PATTERN.search(content)

        if not match:
            print(
                f"Info: Badge list comment not found in {file_to_update.name}. Skipping."
            )
            return

        print(f"Found badge comment in {file_to_update.name}")

        badge_comment_line = match.group(0)
        badge_list_str = match.group(1).strip()
        badge_keys = [key.strip() for key in badge_list_str.split(",") if key.strip()]
        badge_keys.sort()

        new_badges_html = generate_badges_html(badge_keys)

        if not new_badges_html:
            print(f"No badges generated for {file_to_update.name}. Skipping update.")
            return

        new_block_content = (
            f"{START_MARKER}\n"
            f"{badge_comment_line}\n\n"
            f"{new_badges_html}\n\n"
            f"{END_MARKER}"
        )

        if BADGE_BLOCK_PATTERN.search(content):
            updated_content = BADGE_BLOCK_PATTERN.sub(new_block_content, content)
        else:
            print(
                f"Error: Markers not found in {file_to_update.name}. Skipping update."
            )
            return

        if content == updated_content:
            print(f"No changes needed for {file_to_update.name}. Skipping commit.")
            return

        file_to_update.write_text(updated_content, encoding="utf-8")
        print(f"{file_to_update.name} updated successfully with new badges.")

    except Exception as e:
        print(
            f"An unexpected error occurred while processing {file_to_update.name}: {e}"
        )


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Error: No file paths provided.")
        sys.exit(1)

    # Loop through all file paths provided as command-line arguments.
    for file_path_str in sys.argv[1:]:
        target_file_path = Path(file_path_str)
        print(f"--- Processing {target_file_path} ---")
        update_file(target_file_path)


if __name__ == "__main__":
    main()
