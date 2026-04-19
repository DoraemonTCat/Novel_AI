"""Google Gemini 2.5 Flash AI Provider."""
import json
import logging
import re
import time

from google import genai
from google.genai import types

from app.config import settings
from app.services.ai_providers.base import BaseAIProvider

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
BASE_RETRY_DELAY = 30  # seconds


class GeminiProvider(BaseAIProvider):
    """AI Provider using Google Gemini 2.5 Flash."""

    def __init__(self, model_name: str = None):
        super().__init__(model_name or settings.GEMINI_MODEL)
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    def _generate(self, system_prompt: str, user_prompt: str, temperature: float = 1.0, max_tokens: int = 8192) -> str:
        """Core generation method with automatic retry on rate limit."""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )
                return response.text

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    # Extract retry delay from error message
                    delay = BASE_RETRY_DELAY
                    match = re.search(r'retry in (\d+\.?\d*)', error_str, re.IGNORECASE)
                    if match:
                        delay = max(float(match.group(1)), 10) + 5  # Add 5s buffer

                    logger.warning(
                        f"⏳ Rate limited (attempt {attempt + 1}/{MAX_RETRIES}). "
                        f"Waiting {delay:.0f}s before retry..."
                    )
                    time.sleep(delay)
                else:
                    raise  # Non-rate-limit errors should fail immediately

        raise Exception(f"Failed after {MAX_RETRIES} retries due to rate limiting")

    def generate_outline(self, prompt, genre, language, num_chapters,
                         writing_style="contemporary", tone="balanced", pov="third_person") -> dict:
        """Generate a structured novel outline with Gemini."""
        system = self._get_system_prompt(language, role="outline_generator")
        
        user_prompt = f"""สร้าง outline นิยายให้หน่อย:

เรื่องย่อ: {prompt}
แนว: {genre}
จำนวนตอน: {num_chapters}
สไตล์: {writing_style}
โทน: {tone}
มุมมอง: {pov}
ภาษา: {"ไทย" if language == "th" else "English" if language == "en" else "ผสม"}

ตอบเป็น JSON format:
{{
    "title": "ชื่อเรื่อง",
    "synopsis": "เรื่องย่อ 2-3 ย่อหน้า",
    "themes": ["ธีมหลัก"],
    "chapters": [
        {{
            "number": 1,
            "title": "ชื่อตอน",
            "summary": "สรุปเนื้อหาตอนนี้",
            "key_events": ["เหตุการณ์สำคัญ"],
            "characters_involved": ["ตัวละครที่เกี่ยวข้อง"],
            "mood": "อารมณ์ของตอน"
        }}
    ]
}}"""

        result = self._generate(system, user_prompt, temperature=0.8, max_tokens=4096)
        
        # Parse JSON from response
        try:
            # Try to extract JSON from markdown code block
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except (json.JSONDecodeError, IndexError):
            logger.warning("Failed to parse outline JSON, using raw text")
            return {
                "title": "Untitled Novel",
                "synopsis": prompt,
                "chapters": [
                    {"number": i + 1, "title": f"Chapter {i + 1}", "summary": "", "key_events": [], "mood": tone}
                    for i in range(num_chapters)
                ],
            }

    def generate_chapter(self, outline, chapter_num, chapter_outline, previous_summaries,
                         language="th", writing_style="contemporary", tone="balanced",
                         pov="third_person", target_length=3000) -> str:
        """Generate a chapter with full context."""
        system = self._get_system_prompt(language, role="chapter_writer", 
                                          writing_style=writing_style, tone=tone, pov=pov)

        # Build context from previous chapters
        context = ""
        if previous_summaries:
            context = "\n\n--- สรุปตอนก่อนหน้า ---\n"
            for s in previous_summaries[-5:]:  # Last 5 chapters for context
                context += f"\nตอนที่ {s['chapter']}: {s['title']}\n{s['summary']}\n"

        user_prompt = f"""เขียนนิยายตอนที่ {chapter_num}:

--- ข้อมูลเรื่อง ---
ชื่อเรื่อง: {outline.get('title', 'Untitled')}
เรื่องย่อ: {outline.get('synopsis', '')}

--- ข้อมูลตอนนี้ ---
ชื่อตอน: {chapter_outline.get('title', f'Chapter {chapter_num}')}
เนื้อหาที่ต้องเขียน: {chapter_outline.get('summary', '')}
เหตุการณ์สำคัญ: {', '.join(chapter_outline.get('key_events', []))}
อารมณ์: {chapter_outline.get('mood', tone)}
{context}

--- คำสั่ง ---
- เขียนให้มีความยาวประมาณ {target_length} คำ
- ใช้มุมมอง {pov}
- เขียนแบบ {writing_style}
- โทนเสียง {tone}
- เริ่มต้นตอนด้วย hook ที่น่าสนใจ
- จบตอนด้วย cliffhanger หรือจุดสนใจ
- เขียนเฉพาะเนื้อหาของตอนเท่านั้น ไม่ต้องใส่หัวข้อตอนหรือหมายเลข"""

        return self._generate(system, user_prompt, temperature=1.0, max_tokens=max(target_length * 2, 8192))

    def summarize_chapter(self, content: str, language: str = "th") -> str:
        """Summarize a chapter for context management."""
        lang_text = "ไทย" if language == "th" else "English"
        system = f"You are a precise text summarizer. Respond in {lang_text}."
        prompt = f"สรุปเนื้อหาต่อไปนี้ให้กระชับใน 3-5 ประโยค โดยเน้นเหตุการณ์สำคัญ พัฒนาการตัวละคร และ plot point:\n\n{content[:3000]}"
        return self._generate(system, prompt, temperature=0.3, max_tokens=500)

    def rewrite_text(self, text: str, instruction: str, language: str = "th") -> str:
        system = self._get_system_prompt(language, role="editor")
        prompt = f"เขียนข้อความต่อไปนี้ใหม่ตามคำสั่ง:\n\nข้อความเดิม:\n{text}\n\nคำสั่ง: {instruction}"
        return self._generate(system, prompt, temperature=0.9)

    def expand_text(self, text: str, target_length: int, language: str = "th") -> str:
        system = self._get_system_prompt(language, role="editor")
        prompt = f"ขยายข้อความต่อไปนี้ให้มีความยาวประมาณ {target_length} คำ โดยเพิ่มรายละเอียด บทสนทนา และบรรยากาศ:\n\n{text}"
        return self._generate(system, prompt, temperature=1.0, max_tokens=target_length * 2)

    def suggest_continuation(self, text: str, language: str = "th") -> str:
        system = self._get_system_prompt(language, role="continuation")
        prompt = f"เขียนต่อจากข้อความนี้ให้อีก 200-300 คำ:\n\n...{text[-1000:]}"
        return self._generate(system, prompt, temperature=1.0, max_tokens=1024)

    def generate_characters(self, prompt: str, genre: str, language: str = "th") -> list:
        system = self._get_system_prompt(language, role="character_designer")
        user_prompt = f"""สร้างตัวละครสำหรับนิยายแนว {genre}:

เรื่องย่อ: {prompt}

สร้างตัวละครหลัก 3-5 ตัว ตอบเป็น JSON array:
[{{"name": "ชื่อ", "age": 25, "role": "protagonist", "appearance": "รูปลักษณ์", "personality": "นิสัย", "background": "ภูมิหลัง"}}]"""

        result = self._generate(system, user_prompt, temperature=0.8, max_tokens=2048)
        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except (json.JSONDecodeError, IndexError):
            return []
