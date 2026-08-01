from doctr.io import DocumentFile
from doctr.models import ocr_predictor

model = ocr_predictor(pretrained=True)

doc = DocumentFile.from_pdf("EOBs/MCEOBExample.pdf")

result = model(doc)

for page in result.pages:
    for block in page.blocks:
        for line in block.lines:
            print(" ".join(word.value for word in line.words))