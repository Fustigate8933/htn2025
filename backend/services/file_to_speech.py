from pptx import Presentation
from PyPDF2 import PdfReader
from generate_speech import generate_speech
from gcp import GCSClient 
import io
import time

class PPTProcessor:
    def __init__(self):
        self.gcs = GCSClient()
        pass

    def extract_ppt_text(self, ppt_path):
        bucket_name = "hack-the-north-bucket"
        blob = self.gcs.client.bucket(bucket_name).blob(ppt_path)
        data = blob.download_as_bytes()
        
        prs = Presentation(io.BytesIO(data))    # 用 BytesIO 包装成 file-like object
        slides_text = []
        
        for i, slide in enumerate(prs.slides, start=1):
            slide_content = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_content.append(shape.text.strip())
            if slide_content:
                slides_text.append({
                    "page_num": i,
                    "text": "\n".join(slide_content)
                })
        return slides_text
    
    def extract_pdf_text(self, pdf_path):
        text = []
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            for i, page in enumerate(reader.pages, start=1):
                content = page.extract_text()
                if content and content.strip():
                    text.append({
                        "page_num": i,
                        "text": content.strip()
                    })
        return text

    def build_prompt(self, ppt_text):
        """
        Build the prompt send to cohere api based on the extracted text
        """
        prompt = (
            f"Use English to generate a speech draft for Slide/Page {ppt_text['page_num']}.\n\n"
            f"Content:\n{ppt_text['text']}\n\n"
            "Please output a clear and complete speech text for this slide/page. "
            "Do not summarize, make it ready to speak."
        )
        return prompt
    
    def file_to_speech(self, file_path: str) -> dict:
        if file_path.endswith(".pptx"):
            pages = self.extract_ppt_text(file_path)
        elif file_path.endswith(".pdf"):
            pages = self.extract_pdf_text(file_path)
        else:
            raise ValueError("Unsupported file format: Only .pptx and .pdf are supported")

        result = {}
        for page in pages:
            print(f"Processing Page {page['page_num']}...")
            prompt = self.build_prompt(page)
            speech_text = generate_speech(prompt)
            result[page["page_num"]] = speech_text
            time.sleep(7)

        return result

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