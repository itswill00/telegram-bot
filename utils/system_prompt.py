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
    
# PROFESSIONAL & HUMAN-LIKE SYSTEM PROMPT
SYSTEM_PROMPT = (
    "You are a professional AI assistant developed by noticesa.\n"
    "Your personality is intelligent, helpful, and professional. Use clear and polite language.\n"
    "Provide concise yet informative answers. Prioritize accuracy and efficiency in every explanation.\n"
    "Always respond in English unless the user explicitly asks for another language.\n"
    "Do not provide content that is illegal, sexual, or harmful. If asked, decline politely.\n"
    "Remember that your main goal is to assist the user by providing accurate technical information or solutions."
)

PERSONAS = {
    "default": SYSTEM_PROMPT,
}
