from doctr.io import DocumentFile
import cv2
import numpy as np
from PIL import Image

import Settings
import helper
from Medicare import Medicare
from BlueCross import BlueCross
from Anthem import Anthem
from enums import FileType

class DocumentHandler:
    def getWordsFromPDF(fileType, filePath):
        doc = DocumentFile.from_pdf(filePath)

        if fileType == FileType.ANTHEM:
            doc = DocumentHandler.rotateDocument(doc, isClockwise=False)

        correctedDoc = DocumentHandler.deskewDocument(doc)

        if fileType == FileType.MEDICARE:
            correctedDoc = Medicare.shapeDocument(correctedDoc)
        elif fileType == FileType.BLUECROSS:
            correctedDoc = BlueCross.shapeDocument(correctedDoc)
        elif fileType == FileType.ANTHEM:
            correctedDoc = Anthem.shapeDocument(correctedDoc)

        if Settings.debug.get("makeAnalyzedPDF"):
            DocumentHandler.makePDF(correctedDoc)

        wordArray = DocumentHandler.makeWordArrayFromDoc(correctedDoc)

        lines = DocumentHandler.organizeLines(wordArray)

        textArray = []

        for line in lines:
            for word in line:
                textArray.append(word["text"])

            textArray.append("\n")

        return textArray

    def makeWordArrayFromDoc(doc):
        model = helper.setupOCR()
        pdf = model(doc)
        
        wordArray = []
        
        for i, page in enumerate(pdf.pages):
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        ((x1, y1), (x2, y2)) = word.geometry

                        wordArray.append({
                            "text": word.value,
                            "x": (x1 + x2) / 2,
                            "y": ((y1 + y2) / 2) + i,
                            "height": y2 - y1
                        })

                    # wordArray.append({
                    #     "text": "\n",
                    #     "x": -1,
                    #     "y": -1,
                    #     "height": -1
                    # })

        return wordArray

    def deskewDocument(doc):
        correctedPages = []

        for i, page in enumerate(doc):
            angle = DocumentHandler.getSkewAngle(page)

            if Settings.debug.get("printPageSkew"):
                print(f"Page {i + 1} skew angle: {angle:.2f} degrees")
            
            correctedPage = DocumentHandler.skewPage(page, angle)
            correctedPages.append(correctedPage)

        return correctedPages
    

    def skewPage(page, angle):
        (h, w) = page.shape[:2]
        center = (w / 2, h / 2)

        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        return cv2.warpAffine(page,
            matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE)

    def getSkewAngle(page):
        gray = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)

        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        lines = cv2.HoughLinesP(
            thresh,
            1,
            np.pi / 180,
            threshold = 100,
            minLineLength = 100,
            maxLineGap = 10
        )

        if lines is None:
            return 0.0

        angles = []

        for line in lines:
            x1, y1, x2, y2 = line[0]

            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))

            if abs(angle) < 10:
                angles.append(angle)

        if not angles:
            return 0.0

        return np.median(angles)

    def rotateDocument(doc, isClockwise):
        rotatedDoc = []

        if isClockwise:
            rotation = cv2.ROTATE_90_CLOCKWISE
        else:
            rotation = cv2.ROTATE_90_COUNTERCLOCKWISE

        for page in doc:
            rotatedDoc.append(cv2.rotate(page, rotation))

        return rotatedDoc

    def makePDF(doc):
        images = []

        for page in doc:
            pageRGB = cv2.cvtColor(page, cv2.COLOR_BGR2RGB)
            images.append(Image.fromarray(pageRGB))

        images[0].save(
            "document.pdf",
            save_all = True,
            append_images = images[1:]
        )

    def organizeLines(wordArray):
        wordArray.sort(key = lambda w: w["y"])
        tolerance = DocumentHandler.getTolerance(wordArray)

        lines = []

        for word in wordArray:
            if not lines:
                lines.append([word])
                continue

            currentLine = lines[-1]

            lastY = currentLine[-1]["y"]

            if abs(word["y"] - lastY) <= tolerance:
                currentLine.append(word)
            else:
                lines.append([word])


        for line in lines:
            line.sort(key = lambda w: w["x"])

        return lines

    def getTolerance(wordArray):
        averageHeight = (sum(word["height"] for word in wordArray) / len(wordArray))
        return averageHeight * .17