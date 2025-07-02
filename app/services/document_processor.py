import fitz  # PyMuPDF
from docx.api import Document
from unstructured.partition.text import partition_text
from typing import List
import os

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']

    async def extract_text(self, file_path: str, file_type: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self._extract_pdf(file_path)
        elif ext == '.docx':
            return self._extract_docx(file_path)
        elif ext == '.txt':
            return self._extract_txt(file_path)
        else:
            raise ValueError('Format non supporté')

    def _extract_pdf(self, file_path: str) -> str:
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text("text") for page in doc)  # type: ignore
        doc.close()
        return text

    def _extract_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    def _extract_txt(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    async def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    async def process_document(self, file_path: str, file_type: str) -> List[str]:
        text = await self.extract_text(file_path, file_type)
        chunks = await self.chunk_text(text)
        return chunks 