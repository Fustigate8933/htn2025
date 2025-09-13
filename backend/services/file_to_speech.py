from pptx import Presentation
from PyPDF2 import PdfReader
from generate_speech import generate_speech

class PPTProcessor:
    def __init__(self):
        pass

    def extract_ppt_text(self, ppt_path):
        prs = Presentation(ppt_path)
        slides_text = []
        
        for i, slide in enumerate(prs.slides, start=1):
            slide_content = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_content.append(shape.text.strip())
            if slide_content:
                slides_text.append(f"Slide {i}: " + " | ".join(slide_content))
        return "\n".join(slides_text)
    
    def extract_pdf_text(self, pdf_path):
        text = []
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            for i, page in enumerate(reader.pages, start=1):
                content = page.extract_text()
                if content and content.strip():
                    text.append(f"Page {i}: {content.strip()}")
        return "\n".join(text)

    def build_prompt(self, ppt_text):
        """
        Build the prompt send to cohere api based on the extracted text
        """
        prompt = (
            "Please rewrite the following PPT or PDF outline into a speech draft。\n\n"
            f"{ppt_text}\n\n"
            "Please output the complete speech draft. Don't just summarize。"
        )
        return prompt



"""
Usage:
    ppt_processor = file_to_speech.PPTProcessor()

    ppt_path = "./test.pptx"
    pdf_path = "./test.pdf"

    ppt_text = ppt_processor.extract_ppt_text(ppt_path)
    pdf_text = ppt_processor.extract_pdf_text(pdf_path)
    
    prompt = ppt_processor.build_prompt(pdf_text)

    speech_text = generate_speech(prompt)
"""