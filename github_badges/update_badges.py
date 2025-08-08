# update_badges.py

import json
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# --- Markers and Patterns for Parsing ---
# (Patterns remain the same as the previous version)
START_BADGE_MARKER = "<!--- Start of badges -->"
END_BADGE_MARKER = "<!--- End of badges -->"
BADGE_LIST_COMMENT_PATTERN = re.compile(r"<!-- Badges: (.*?) -->")
BADGE_BLOCK_PATTERN = re.compile(f"{re.escape(START_BADGE_MARKER)}(.*?){re.escape(END_BADGE_MARKER)}", re.DOTALL)
BLURB_MARKER_PATTERN = re.compile(r"<!--- Blurb\s(.*?)-->", re.DOTALL)
START_THUMBNAIL_MARKER = "<!--- Start of Thumbnail-->"
END_THUMBNAIL_MARKER = "<!--- End of Thumbnail-->"
THUMBNAIL_BLOCK_PATTERN = re.compile(f"{re.escape(START_THUMBNAIL_MARKER)}(.*?){re.escape(END_THUMBNAIL_MARKER)}", re.DOTALL)
TITLE_PATTERN = re.compile(r"^\s*#\s+(.*)", re.MULTILINE)

# --- Configuration ---
BADGES_FILE = "./self/github_badges/badges.json"

# --- Badge Generation Logic (remains the same) ---
def generate_badges_html(badge_keys: List[str]) -> str:
    if not badge_keys: return ""
    try:
        with open(BADGES_FILE, "r", encoding="utf-8") as f:
            all_badges = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading badges file: {e}", file=sys.stderr)
        return ""
    html_badges = []
    for key in sorted(badge_keys):
        badge_data = all_badges.get(key)
        if badge_data and "badge_url" in badge_data:
            alt_text = key.replace("_", " ").replace("-", " ").title()
            html_badges.append(f'<img alt="{alt_text}" src="{badge_data["badge_url"]}" />')
    return f'<p align="left">{" ".join(html_badges)}</p>' if html_badges else ""

def process_badge_content(content: str) -> Tuple[str, str, bool]:
    match = BADGE_LIST_COMMENT_PATTERN.search(content)
    if not match: return content, "", False
    badge_comment_line = match.group(0)
    badge_keys = [key.strip() for key in match.group(1).strip().split(",") if key.strip()]
    new_badges_html = generate_badges_html(badge_keys)
    if not new_badges_html: return content, "", False
    new_block_content = f"{START_BADGE_MARKER}\n{badge_comment_line}\n\n{new_badges_html}\n{END_BADGE_MARKER}"
    if BADGE_BLOCK_PATTERN.search(content):
        updated_content = BADGE_BLOCK_PATTERN.sub(new_block_content, content)
        return updated_content, new_badges_html, content != updated_content
    return content, new_badges_html, False

# --- Project Parsing Logic (remains the same) ---
def parse_project_file(content: str, badges_html: str, file_path: Path, repo_name: str) -> Optional[Dict]:
    blurb_match = BLURB_MARKER_PATTERN.search(content)
    if blurb_match:
        blurb = blurb_match.group(1).strip()
    else:
        return None

    title_match = TITLE_PATTERN.search(content)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title =""

    thumbnail_match = THUMBNAIL_BLOCK_PATTERN.search(content)
    if thumbnail_match:
        thumbnail_html = thumbnail_match.group(1).strip()
        img_src_match = re.search(r'src="([^"]+)"', thumbnail_html)
        thumbnail_url = ""
        if img_src_match:
            relative_path = img_src_match.group(1)
            thumbnail_url = f"https://raw.githubusercontent.com/{repo_name}/main/{relative_path}"
    else:
        thumbnail_url = ""

    if file_path.suffix == ".md":
        url = f"https://github.com/{repo_name}/blob/main/{file_path.as_posix()}"
    elif file_path.suffix == ".ipynb":
        url = f"https://nbviewer.org/github/{repo_name}/blob/main/{file_path.as_posix()}"

    return {
        "title": title,
        "blurb": blurb,
        "badges": badges_html,
        "thumbnail_url": thumbnail_url,
        "url": url
    }

# --- File Processing (remains the same) ---
def process_file(file_path: Path, repo_name: str, is_private: bool) -> Optional[Dict]:

    print(f"--- Processing file: {file_path} ---", file=sys.stderr)
    project_data = None
    content = ""
    try:
        if file_path.suffix == ".md":
            content = file_path.read_text(encoding="utf-8")
            updated_content, badges_html, was_changed = process_badge_content(content)
            if was_changed:
                file_path.write_text(updated_content, encoding="utf-8")
                print(f"Updated badges in {file_path.name}.", file=sys.stderr)
        
        elif file_path.suffix == ".ipynb":
            notebook_data = json.loads(file_path.read_text(encoding="utf-8"))
            notebook_modified = False
            for cell in notebook_data.get("cells", []):
                if cell.get("cell_type") == "markdown":
                    source_content = "".join(cell.get("source", []))
                    content += source_content + "\n"
                    updated_source, badges_html, was_changed = process_badge_content(source_content)
                    if was_changed:
                        cell["source"] = [line + "\n" for line in updated_source.split("\n")]
                        notebook_modified = True
            if notebook_modified:
                file_path.write_text(json.dumps(notebook_data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
                print(f"Updated badges in {file_path.name}.", file=sys.stderr)
        else:
            return None

        if not is_private:
            project_data = parse_project_file(content, badges_html, file_path, repo_name)

    except Exception as e:
        print(f"Error processing {file_path.name}: {e}", file=sys.stderr)
    
    return project_data

def main():
    """Main execution function."""
    print("--- Python script started successfully ---", file=sys.stderr)
    parser = argparse.ArgumentParser(description="Update badges and parse project data.")
    parser.add_argument("--repo-name", required=True)
    parser.add_argument("--is-private", required=True, type=lambda v: v.lower() == 'true')
    parser.add_argument("--files", nargs='+', required=True)
    args = parser.parse_args()

    all_projects = []
    for file_path_str in args.files:
        target_file = Path(file_path_str)
        if not target_file.exists(): continue
        
        project = process_file(target_file, args.repo_name, args.is_private)
        if project:
            all_projects.append(project)

    # Print the final list as a compact JSON string to stdout
    # This is the output that the GitHub Action will capture.
    print(json.dumps(all_projects, separators=(',', ':')))

if __name__ == "__main__":
    main()