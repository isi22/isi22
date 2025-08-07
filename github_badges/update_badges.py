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
                f'<img alt="{alt_text}" src="{badge_data["badge_url"]}" />'
            )
        else:
            print(
                f"Warning: Badge key '{key}' not found or is missing 'badge_url' in {BADGES_FILE}."
            )

    return f'<p align="left">{" ".join(html_badges)}</p>' if html_badges else ""


def update_markdown_file(file_path: Path):
    """Processes a standard Markdown (.md) file."""
    content = file_path.read_text(encoding="utf-8")
    updated_content, was_changed = process_content(content)
    if was_changed:
        file_path.write_text(updated_content, encoding="utf-8")
        print(f"Successfully updated badges in {file_path.name}.")
    else:
        print(f"No changes needed for {file_path.name}.")


def update_notebook_file(file_path: Path):
    """Processes a Jupyter Notebook (.ipynb) file."""
    with open(file_path, "r", encoding="utf-8") as f:
        notebook_data = json.load(f)

    notebook_modified = False
    for cell in notebook_data.get("cells", []):
        if cell.get("cell_type") == "markdown":
            # The 'source' can be a list of strings or a single string.
            source_content = "".join(cell.get("source", []))
            updated_source, was_changed = process_content(source_content)
            if was_changed:
                # Jupyter expects the source to be a list of strings, each ending with a newline.
                cell["source"] = [line + "\n" for line in updated_source.split("\n")]
                notebook_modified = True

    if notebook_modified:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(notebook_data, f, indent=1, ensure_ascii=False)
            f.write("\n") # Add a trailing newline for POSIX compatibility
        print(f"Successfully updated badges in {file_path.name}.")
    else:
        print(f"No changes needed for {file_path.name}.")


def process_content(content: str) -> (str, bool):
    """
    Finds the badge block in a string of content, generates new badges,
    and returns the updated content and a flag indicating if changes were made.
    """
    match = BADGE_LIST_COMMENT_PATTERN.search(content)
    if not match:
        return content, False

    badge_comment_line = match.group(0)
    badge_list_str = match.group(1).strip()
    badge_keys = [key.strip() for key in badge_list_str.split(",") if key.strip()]
    badge_keys.sort()

    new_badges_html = generate_badges_html(badge_keys)
    if not new_badges_html:
        return content, False

    new_block_content = (
        f"{START_MARKER}\n"
        f"{badge_comment_line}\n\n"
        f"{new_badges_html}\n"
        f"{END_MARKER}"
    )

    if BADGE_BLOCK_PATTERN.search(content):
        updated_content = BADGE_BLOCK_PATTERN.sub(new_block_content, content)
        return updated_content, content != updated_content
    else:
        return content, False


def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Error: No file paths provided.")
        sys.exit(1)

    for file_path_str in sys.argv[1:]:
        target_file_path = Path(file_path_str)
        print(f"--- Processing {target_file_path} ---")

        if not target_file_path.exists():
            print(f"Error: File not found: {target_file_path}")
            continue

        try:
            if target_file_path.suffix == ".md":
                update_markdown_file(target_file_path)
            elif target_file_path.suffix == ".ipynb":
                update_notebook_file(target_file_path)
            else:
                print(f"Skipping unsupported file type: {target_file_path.name}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {target_file_path.name}: {e}")


if __name__ == "__main__":
    main()

