---
name: pdf-productivity
description: Capabilities for reading, writing, merging, splitting, rotating, and encrypting PDF files using the pypdf Python library.
version: 1.0.0
author: Antigravity
tags:
  - pdf
  - pypdf
  - merge
  - split
  - extract
---

# PDF Editing & Manipulation Skill (pypdf)

This skill enables the AI agent to read, write, merge, split, rotate, and secure PDF documents using the `pypdf` Python library.

## Overview
This skill provides guidelines and example Python scripts for manipulating PDF files. The agent can use this skill to extract text from documents, compile multiple files, secure sensitive documents, or reorganise PDF pages.

## Core Python Library
- **pypdf**: Used for all PDF parsing, creation, and manipulation tasks.

---

## Instructions & Workflows

### 1. Extracting Text from a PDF
To read text from a PDF, iterate through its pages and call `extract_text()`.

#### Example: Extracting Text
```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
print(f"Total Pages: {len(reader.pages)}")

# Extract text from the first page
first_page = reader.pages[0]
text = first_page.extract_text()
print(text)
```

### 2. Merging Multiple PDFs
To combine multiple PDF files into a single document, use the `PdfMerger` class.

#### Example: Merging PDFs
```python
from pypdf import PdfMerger

def merge_pdfs(pdf_list, output_path):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()
    print(f"Merged PDF saved to {output_path}")

merge_pdfs(["doc1.pdf", "doc2.pdf"], "combined.pdf")
```

### 3. Splitting & Extracting Pages
To extract specific pages from a PDF and save them to a new file, use `PdfReader` and `PdfWriter`.

#### Example: Splitting PDFs
```python
from pypdf import PdfReader, PdfWriter

def extract_pages(input_pdf, output_pdf, pages_to_extract):
    # pages_to_extract should be a list of 0-indexed page numbers
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    for page_num in pages_to_extract:
        writer.add_page(reader.pages[page_num])
        
    with open(output_pdf, "wb") as f:
        writer.write(f)
    print(f"Extracted pages saved to {output_pdf}")

extract_pages("document.pdf", "extracted.pdf", [0, 2, 4]) # Extracts pages 1, 3, and 5
```

### 4. Rotating PDF Pages
You can rotate pages by 90-degree increments using `.rotate()` on a page object.

#### Example: Rotating Pages
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

# Rotate the first page 90 degrees clockwise
first_page = reader.pages[0].rotate(90)
writer.add_page(first_page)

# Copy the rest of the pages unchanged
for i in range(1, len(reader.pages)):
    writer.add_page(reader.pages[i])

with open("rotated.pdf", "wb") as f:
    writer.write(f)
```

### 5. Encrypting (Securing) a PDF
You can encrypt a PDF with a password.

#### Example: Encrypting a PDF
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Encrypt the PDF with a password
writer.encrypt("secure_password123")

with open("encrypted.pdf", "wb") as f:
    writer.write(f)
```

---

## Rules & Constraints
- Ensure the `pypdf` package is installed before running scripts.
- When working with scanned PDFs (images), note that `extract_text()` may return empty or poorly formatted text. In such cases, OCR (Optical Character Recognition) tools like Tesseract would be needed.
- Always check if the input PDF is encrypted before trying to read it. Use `reader.is_encrypted` and `reader.decrypt("password")` if needed.
