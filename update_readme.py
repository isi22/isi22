import json
import re

json_file_path = 'projects.json'
readme_path = 'README.md'

with open(json_file_path, 'r') as f:
    projects = json.load(f)

# Generate the Markdown content
markdown_content = ""
for project in projects:
    
    # Create the project section
    markdown_content += f"""
### {project['title']}

<a href="{project['url']}" target="_blank">
  <img src="{project['thumbnail_url']}" alt="{project['title']}" width="400">
</a>

{project['blurb']}

{project['badges']}

---
"""

# Read the current README
with open(readme_path, 'r') as f:
    readme_content = f.read()

# Replace the content between the portfolio markers
new_readme_content = re.sub(
    r'(?s).*',
    f'\n{markdown_content}\n',
    readme_content
)

# Write the new content back to the README
with open(readme_path, 'w') as f:
    f.write(new_readme_content)

print("✅ README updated successfully with a single-column layout!")