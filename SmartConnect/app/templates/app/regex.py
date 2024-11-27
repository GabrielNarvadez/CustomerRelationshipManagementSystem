import re

# File path to your HTML template
template_path = "index.html"

# Read the template content
with open(template_path, "r", encoding="utf-8") as file:
    content = file.read()

# Regex to find all asset references (src, href, etc.) starting with "assets/"
pattern = r'(src|href)="(assets/[^"]+)"'

# Function to wrap matched paths with `{% static %}`
def replace_static(match):
    attribute = match.group(1)  # src or href
    path = match.group(2)       # assets/... path
    return f'{attribute}="{{% static \'{path}\' %}}"'

# Replace all asset references
updated_content = re.sub(pattern, replace_static, content)

# Write back the updated content to the template file
with open(template_path, "w", encoding="utf-8") as file:
    file.write(updated_content)

print("Template updated successfully!")
