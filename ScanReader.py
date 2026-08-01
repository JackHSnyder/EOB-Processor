import fitz
import pytesseract
from PIL import Image, ImageOps

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

pdf = fitz.open("EOBs/MCEOBExample.pdf")

for page_num in range(len(pdf)):
    page = pdf.load_page(page_num)

    # Render page as an image
    pix = page.get_pixmap(dpi=600)

    image = pix.pil_image()

    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image)

    # OCR the image
    text = pytesseract.image_to_string(image)

    print(f"----- Page {page_num + 1} -----")
    print(text)