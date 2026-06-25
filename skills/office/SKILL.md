---
name: office-productivity
description: Create, edit, read, and convert Microsoft Office files including Word documents (.docx), Excel spreadsheets (.xlsx), and PowerPoint presentations (.pptx) using Python libraries.
version: 1.0.0
author: Antigravity
tags:
  - office
  - word
  - excel
  - powerpoint
  - docx
  - xlsx
  - pptx
---

# Microsoft Office File Editing & Creation Skill

This skill enables the AI agent to edit and create Microsoft Office documents (Word, Excel, PowerPoint) using Python libraries.

## Overview
This skill provides structured guidelines, templates, and Python scripts to programmatically manage Office documents. By utilizing this skill, the agent can generate report documents, analyze spreadsheets, extract text/data, and create slide decks dynamically.

## Supported Formats & Python Libraries
1. **Word Documents (`.docx`)**: Managed using `python-docx`
2. **Excel Spreadsheets (`.xlsx`)**: Managed using `openpyxl`
3. **PowerPoint Presentations (`.pptx`)**: Managed using `python-pptx`

---

## Instructions & Workflows

### 1. Working with Word Documents (`.docx`)
To create or edit a Word document, use the `docx` library in Python.

#### Example: Creating a Word Document
```python
import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = docx.Document()
doc.add_heading('Office Automation Report', level=0)

p = doc.add_paragraph('This document was generated automatically by the Antigravity agent.')
p.add_run(' Bold text can be appended.').bold = True

doc.add_heading('Data Summary Table', level=1)
table = doc.add_table(rows=1, cols=3)
hdr_cells = table.rows[0].cells
hdr_cells[0].text = 'ID'
hdr_cells[1].text = 'Item'
hdr_cells[2].text = 'Value'

# Add data rows
row_cells = table.add_row().cells
row_cells[0].text = '1'
row_cells[1].text = 'Sample A'
row_cells[2].text = '120'

doc.save('report.docx')
```

### 2. Working with Excel Spreadsheets (`.xlsx`)
To read, write, or modify Excel sheets, use `openpyxl`.

#### Example: Creating/Editing an Excel Spreadsheet
```python
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Financial Summary"

# Setup headers
headers = ["Date", "Category", "Amount", "Status"]
ws.append(headers)

# Apply styling to headers
header_font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
header_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')

for col_num in range(1, 5):
    cell = ws.cell(row=1, column=col_num)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal='center')

# Add data
data = [
    ["2026-06-01", "Software License", 1200, "Approved"],
    ["2026-06-02", "Hardware", 4500, "Pending"],
    ["2026-06-03", "Office Supplies", 150, "Approved"]
]

for row in data:
    ws.append(row)

# Add formula
ws['C5'] = "=SUM(C2:C4)"
ws['C5'].font = Font(bold=True)

# Adjust column widths
for col in ws.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = openpyxl.utils.get_column_letter(col[0].column)
    ws.column_dimensions[col_letter].width = max(max_len + 3, 10)

wb.save('finances.xlsx')
```

### 3. Working with PowerPoint Slides (`.pptx`)
To create or modify PowerPoint decks, use `python-pptx`.

#### Example: Creating a PowerPoint Presentation
```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
title_slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]

title.text = "Antigravity Agent Platform"
subtitle.text = "Automated Presentation Generation"

# Add a bullet point slide
bullet_slide_layout = prs.slide_layouts[1]
slide2 = prs.slides.add_slide(bullet_slide_layout)
shapes = slide2.shapes

title_shape = shapes.title
title_shape.text = "Key Benefits"

body_shape = shapes.placeholders[1]
tf = body_shape.text_frame
tf.text = "Autonomous execution of tasks"

p = tf.add_paragraph()
p.text = "Integration with editor and terminal"
p.level = 1

prs.save('presentation.pptx')
```

---

## Rules & Constraints
- Always verify if the relevant package (`python-docx`, `openpyxl`, `python-pptx`) is installed before running scripts.
- When editing existing documents, perform a backup copy first to avoid accidental data loss.
- Ensure appropriate file locks are handled when working with spreadsheets in parallel.
- Try to use relative paths for files created in the workspace.
