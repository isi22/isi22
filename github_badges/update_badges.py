import json
import re
from pathlib import Path
from typing import List
import sys

# --- Configuration ---
# Using Path objects is still good practice for handling paths correctly.
BADGES_FILE = (
    "./badges_repo/github_badges/badges.json"  # New path to the central badges file
)

# --- Markers and Patterns ---
START_MARKER = "<!--- Start of badges -->"
END_MARKER = "<!--- End of badges -->"

# [FIX] The regex pattern should not be enclosed in forward slashes (/) in Python.
# Using a raw string (r"...") is also best practice for regex patterns.
BADGE_LIST_COMMENT_PATTERN = re.compile(r"<!-- Badges: (.*?) -->")

# Regex to find the entire block to be replaced.
BADGE_BLOCK_PATTERN = re.compile(
    f"({re.escape(START_MARKER)}.*?{re.escape(END_MARKER)})", re.DOTALL
)


def generate_badges_html(badge_keys: List[str]) -> str:
    """
    Generates the HTML for the badges based on the provided keys and the
    central JSON file.
    """
    if not badge_keys:
        return ""

    try:
        # Use the standard `with open()` for compatibility.
        with open(BADGES_FILE, "r", encoding="utf-8") as f:
            all_badges = json.load(f)
    except FileNotFoundError:
        print(f"Error: {BADGES_FILE} not found.")
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

    return f'<p align="left">{" ".join(html_badges)}</p>' if html_badges else ""


def update_file(file_path_str: str):
    """
    Reads a specific file, finds the badge keys, generates new badge HTML,
    and updates the file.
    """
    target_file = Path(file_path_str)
    try:
        # Using with open(...) is a robust way to handle file reading.
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()

        match = BADGE_LIST_COMMENT_PATTERN.search(content)

        if not match:
            # Corrected the error message to show the expected pattern accurately.
            print("Error: Badge list comment `<!-- Badges: ... -->` not found in File.")
            return

        # This line is useful for debugging to see what the regex matched.
        print(f"Found badge comment: {match.group(0)}")

        badge_comment_line = match.group(0)  # The full comment <!-- Badges: ... -->
        badge_list_str = match.group(1).strip()  # The content of the capturing group
        badge_keys = [key.strip() for key in badge_list_str.split(",") if key.strip()]

        # [NEW] Sort the badge keys alphabetically.
        badge_keys.sort()

        new_badges_html = generate_badges_html(badge_keys)

        if not new_badges_html:
            print("No new badges were generated. File will not be updated.")
            return

        # Construct the new content block that will replace the old one.
        new_block_content = (
            f"{START_MARKER}\n"
            f"{badge_comment_line}\n\n"
            f"{new_badges_html}\n"
            f"{END_MARKER}"
        )

        # Check if the start/end markers exist to replace the block.
        if BADGE_BLOCK_PATTERN.search(content):
            updated_file = BADGE_BLOCK_PATTERN.sub(new_block_content, content)
        else:
            print(
                f"Error: Markers `{START_MARKER}` and `{END_MARKER}` not found in File."
            )
            return

        # Write the updated content back to the file.
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(updated_file)

        print("File updated successfully with new badges.")

    except FileNotFoundError:
        print(f"Error: {target_file} not found.")
    except Exception as e:
        # Catch other potential errors, like permissions issues.
        print(f"An unexpected error occurred: {e}")


def main():
    """Main execution function."""
    if len(sys.argv) > 1:
        file_to_update = sys.argv[1]
        print(f"Attempting to update badges in: {file_to_update}")
        update_file(file_to_update)
    else:
        print("Error: No file path provided.")


if __name__ == "__main__":
    main()
