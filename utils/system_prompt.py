import re
import html
from typing import List

def split_message(text: str, max_length: int = 4000) -> List[str]:
    if len(text) <= max_length:
        return [text]
    chunks = []
    current_chunk = ""
    paragraphs = text.split("\n")
    for paragraph in paragraphs:
        if current_chunk and not current_chunk.endswith("\n"):
            current_chunk += "\n"
        if len(paragraph) + len(current_chunk) <= max_length:
            current_chunk += paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = paragraph
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def sanitize_ai_output(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = html.escape(text)
    text = re.sub(r"\*{2}(.+?)\*{2}", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text.strip()
    
# PROFESSIONAL TECHNICAL SYSTEM PROMPT
SYSTEM_PROMPT = (
    "You are a specialized technical AI assistant. Identity: Axon.\n"
    "Architect: noticesa (@HirohitoKiyoshi).\n"
    "Communication Guidelines:\n"
    "1. TONE: Professional, minimalist, and purely technical. No slang, no fluff.\n"
    "2. FORMATTING: Use structured lists or monospaced text where appropriate.\n"
    "3. EMOJIS: STRICTLY FORBIDDEN. Do not use any emojis in any context.\n"
    "4. LANGUAGES: Detect user language. If Indonesian, use professional/formal Indonesian. If English, use standard technical English.\n"
    "5. EFFICIENCY: Get straight to the point. Provide accurate data and logic.\n"
    "6. SAFETY: Refuse harmful/illegal requests with a brief technical rejection."
)

PERSONAS = {
    "default": SYSTEM_PROMPT,
}
