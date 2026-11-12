import markdown
from bs4 import BeautifulSoup

# 1. Read Markdown file (utf-8-sig strips hidden BOM if present)
with open("report.md", "r", encoding="utf-8-sig") as f:
    md_text = f.read()

# 2. Convert Markdown to raw HTML DOM
raw_html = markdown.markdown(md_text, extensions=["extra"])
soup = BeautifulSoup(raw_html, "html.parser")

body_blocks = []

# --- Extract & Wrap Header (<div class="header">) ---
h1_tag = soup.find("h1")
if h1_tag:
    date_text = ""
    next_tag = h1_tag.find_next_sibling()
    if next_tag and next_tag.name == "p" and next_tag.find("em"):
        date_text = next_tag.get_text().strip()
        next_tag.decompose()
    
    header_html = '<div class="header">\n'
    header_html += f'  <h1>{h1_tag.get_text().strip()}</h1>\n'
    if date_text:
        header_html += f'  <p class="date">{date_text}</p>\n'
    header_html += '</div>'
    
    body_blocks.append(header_html)
    h1_tag.decompose()

# --- Group Sections into <div class="section"> & convert --- to page-break ---
current_section = []

for element in list(soup.children):
    if element.name == "h2":
        if current_section:
            body_blocks.append('<div class="section">\n' + "".join(str(e) for e in current_section) + '</div>')
            current_section = []
        current_section.append(element)
    elif element.name == "hr":
        if current_section:
            body_blocks.append('<div class="section">\n' + "".join(str(e) for e in current_section) + '</div>')
            current_section = []
        body_blocks.append('<!-- PAGE BREAK FOR EXACT 2-PAGE LAYOUT -->\n<div class="page-break"></div>')
    else:
        if current_section:
            current_section.append(element)
        elif str(element).strip():
            body_blocks.append(str(element))

if current_section:
    body_blocks.append('<div class="section">\n' + "".join(str(e) for e in current_section) + '</div>')

body_content = "\n\n".join(body_blocks)

# 3. Full HTML Document Template
full_html = f"""<style>
  @page {{
    size: A4;
    margin: 15mm 18mm;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #2d3748;
    font-size: 10pt;
    line-height: 1.45;
    background: #fff;
  }}
  .header {{
    border-bottom: 2px solid #2b6cb0;
    padding-bottom: 6px;
    margin-bottom: 16px;
  }}
  h1 {{
    color: #1a365d;
    font-size: 18pt;
    margin: 0 0 4px 0;
    font-weight: 700;
  }}
  .date {{
    color: #718096;
    font-size: 9.5pt;
    font-style: italic;
    margin: 0;
  }}
  .section {{
    break-inside: avoid;
    page-break-inside: avoid;
    margin-bottom: 14px;
    background: #f8fafc;
    border-left: 3px solid #3182ce;
    padding: 8px 12px;
    border-radius: 0 4px 4px 0;
  }}
  h2 {{
    color: #2b6cb0;
    font-size: 11.5pt;
    margin: 0 0 6px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  p {{
    margin: 0 0 4px 0;
  }}
  p:last-child {{
    margin-bottom: 0;
  }}
  strong {{
    color: #1a202c;
  }}
  a {{
    color: #2b6cb0;
    text-decoration: underline;
  }}
  .page-break {{
    break-before: page;
    page-break-before: always;
  }}
</style>

{body_content}
"""

with open("output.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Successfully generated output.html with exact section card styling!")
