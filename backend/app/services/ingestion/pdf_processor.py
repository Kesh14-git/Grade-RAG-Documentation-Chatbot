import fitz  # PyMuPDF
import re
import base64
from typing import List, Dict, Any
from app.services.llm.factory import llm_factory

class PDFProcessor:
    def __init__(self):
        pass

    def extract_text_and_metadata(self, file_path: str, document_id: str, document_name: str) -> List[Dict[str, Any]]:
        """
        Extracts text from a PDF, preserving paragraph boundaries and page numbers.
        Returns a list of 'chunks' which are essentially paragraphs or structural blocks.
        """
        doc = fitz.open(file_path)
        blocks_data = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            # get_text("blocks") returns a list of blocks
            # each block is a tuple: (x0, y0, x1, y1, "lines in block", block_no, block_type)
            # block_type 0 is text, 1 is image.
            blocks = page.get_text("blocks")
            
            for b in blocks:
                # We only care about text blocks (0) and image blocks (1)
                if b[6] == 0: 
                    text = b[4].strip()
                    # Basic cleanup
                    text = re.sub(r'\s+', ' ', text)
                    if len(text) > 5: # Ignore very short/empty blocks
                        blocks_data.append({
                            "document_id": document_id,
                            "document_name": document_name,
                            "page_number": page_num + 1,
                            "content": text,
                            "source_type": "pdf"
                        })
                elif b[6] == 1:
                    # Image block
                    try:
                        rect = fitz.Rect(b[:4])
                        pix = page.get_pixmap(clip=rect)
                        img_bytes = pix.tobytes("png")
                        img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                        
                        llm = llm_factory.get_llm_provider()
                        desc_prompt = "Analyze this image and describe it in extreme detail so it can be effectively indexed for a search engine. Include all visible text, numbers, charts, and structural data."
                        description = llm.generate_response(
                            system_prompt="You are a highly precise visual data extraction assistant.",
                            user_prompt=desc_prompt, 
                            images=[img_b64]
                        )
                        
                        blocks_data.append({
                            "document_id": document_id,
                            "document_name": document_name,
                            "page_number": page_num + 1,
                            "content": f"[Image Content]: {description}",
                            "source_type": "pdf_image",
                            "base64_image": img_b64
                        })
                    except Exception as e:
                        print(f"Failed to process image on page {page_num + 1}: {e}")
        return blocks_data

pdf_processor = PDFProcessor()
