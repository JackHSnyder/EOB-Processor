import pymupdf

document = pymupdf.open("eob.pdf")

for page_number, page in enumerate(document):
    text = page.get_text()

    print(f"--- PAGE {page_number + 1} ---")
    print(text)