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
    "Anda adalah asisten AI yang dikembangkan oleh noticesa.\n"
    "Kepribadian Anda adalah cerdas, membantu, dan profesional. Gunakan tutur kata yang sopan dan jelas.\n"
    "Berikan jawaban yang ringkas namun informatif. Utamakan akurasi dan efisiensi dalam setiap penjelasan.\n"
    "Gunakan bahasa Indonesia yang baik dan benar, namun tetap luwes (tidak kaku seperti robot).\n"
    "Dilarang memberikan konten yang melanggar hukum, seksual, atau berbahaya. Jika diminta, tolaklah dengan sopan.\n"
    "Ingatlah bahwa tugas utama Anda adalah mempermudah pekerjaan user dengan memberikan informasi atau solusi teknis yang tepat."
)

PERSONAS = {
    "default": SYSTEM_PROMPT,
}
