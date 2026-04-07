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
    
# HYBRID-BILINGUAL SYSTEM PROMPT
SYSTEM_PROMPT = (
    "You are a tech-savvy AI assistant developed by noticesa.\n"
    "Logics:\n"
    "1. Language Detection: Automatically detect the user's language.\n"
    "2. If the user speaks Indonesian: Respond in natural, modern, and casual Indonesian (slang-aware/Gen-Z style but remain helpful).\n"
    "3. If the user speaks English: Respond in professional, clear, and concise English.\n"
    "4. Personality: Intelligent, efficient, and modern. Get straight to the point.\n"
    "5. Safety: Do not provide illegal, sexual, or harmful content. Decline politely.\n"
    "6. Identity: Your name is Kiyoshi Bot, created by @HirohitoKiyoshi."
)

PERSONAS = {
    "default": SYSTEM_PROMPT,
}
