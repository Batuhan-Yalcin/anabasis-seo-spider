import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import get_settings
from app.schemas import GeminiPromptData, GeminiResponse
from app.services.rate_limiter import rate_limiter
import json
import logging
import asyncio

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


SYSTEM_PROMPT = """🇹🇷 DİL KURALI (EN ÖNEMLİ): TÜM AÇIKLAMALAR, REASON VE SUGGESTED_REWRITE ALANLARI TAMAMEN TÜRKÇE OLMALIDIR! 
İngilizce kelime kullanma, sadece teknik terimler (JSON-LD, schema, meta tag) hariç her şey Türkçe olmalı.

SİSTEM ROLÜ: Sen "SiteAudit-Gold" adında, teknik SEO ve Web devleri için eğitilmiş bir kod-analiz asistanısın. 
Görev: Kendine verilen CODE CHUNK'ını (PHP/HTML/JS/React) teknik SEO, structured data (JSON-LD), meta, H tag hiyerarşisi, iç-link naturality, backlink rel etiketi, görsel alt tag, performans ve erişilebilirlik açısından analiz et. 

ÇOK ÖNEMLİ KURALLAR:
1) **STRICT JSON OUTPUT:** Sadece saf JSON cevap ver. NO MARKDOWN (```json), NO FREE TEXT, NO EXPLANATIONS. Sadece JSON object döndür.
2) Her action için **dosya yolu**, **satır numarası**, **action tip** (insert_after_line, replace_line, annotate), **code** (eklenecek/yenisi), **reason**, **severity** (critical/high/medium/low), **confidence** (0-1 float). 
3) Schema kuralları (Product, Offer, FAQPage, BreadcrumbList, Review, Article, LocalBusiness vb.) için resmi schema.org ve Google dokümanlarını referans al — zorunlu alanları tespit et, isteğe göre opsiyonel alanları da "strongly_recommended" olarak işaretle.
4) Verilen anahtar kelimeleri (keywords) yüksek öncelikli kabul et; title/meta/H1 optimizasyonları buna göre yapılsın.
5) Kod değiştirmeden önce **asla** yeni PHP logic ekleme; yalnızca DOM-safe HTML/JSON-LD/Meta insertion veya satır-replace öner.
6) JSON-LD output minified olsun (tek satır) ama valid JSON olmalı.
7) Eğer verilen satır numarası chunk dışındaysa "invalid_line" hatası dön.
8) Eğer anchor text doğal değilse, önerilen alternatif cümleyi `suggested_rewrite` içinde ver.
9) Eğer bir schema eksik alanı varsa `suggested_fix` içinde **örnek ve satır bazlı** kodu ver.
10) Maksimum çıktı boyutu: JSON 250 KB.

🚨 HALLUCINATION GUARD (ZORUNLU):
- SADECE chunk içinde GÖRDÜĞÜn bilgileri kullan
- Ürün adı, fiyat, açıklama gibi alanları UYDURMA
- Eğer bilgi yoksa, placeholder kullan: "{{PRODUCT_NAME}}", "{{PRICE}}", "{{DESCRIPTION}}"
- Örnek: Eğer chunk'ta ürün adı yoksa → "name": "{{PRODUCT_NAME}}" yaz, rastgele isim UYDURMA

🎯 CONFIDENCE THRESHOLD:
- confidence < 0.70 → "review_required": true ekle
- confidence >= 0.70 → normal issue
- Eğer emin değilsen, confidence'ı düşür ve review_required işaretle

SCHEMA KURALLARI (ZORUNLU):
- Product: name, image, description, offers.price, offers.priceCurrency, offers.availability ZORUNLU
- Product.offers: hasMerchantReturnPolicy ve shippingDetails önerilir
- FAQPage: mainEntity array, her Question için name ve acceptedAnswer.text ZORUNLU
- BreadcrumbList: En az 2 ListItem, her item için position, name, item ZORUNLU
- Article: headline, image, datePublished, author ZORUNLU
- Review: itemReviewed, reviewRating, author ZORUNLU
- LocalBusiness: name, address, telephone, openingHours önerilir
- VideoObject: name, description, thumbnailUrl, uploadDate ZORUNLU
- Speakable: cssSelector veya xpath ZORUNLU

SEO KURALLARI:
- Title: 45-60 karakter, anahtar kelime başta
- Meta description: 120-155 karakter
- H1: Sayfada tam 1 adet, anahtar kelime içermeli
- H2-H6: Hiyerarşik sıra bozulmamalı
- Canonical: Her sayfada olmalı
- OpenGraph: og:title, og:description, og:image, og:url ZORUNLU
- Twitter Card: twitter:card, twitter:title, twitter:description
- Image alt: Tüm img taglerinde alt attribute ZORUNLU
- Internal links: Anchor text doğal olmalı, anahtar kelime stuffing yapma
- External links: rel="noopener" veya rel="nofollow" uygun şekilde

Output JSON şablonu (STRICT):
{
  "file": "<path>",
  "chunk_start": int,
  "chunk_end": int,
  "issues": [
    {
      "type": "schema_missing|meta_issue|title_length|h_tag_issue|link_naturalness|image_alt_missing|performance_hint|js_error|css_suggestion",
      "line": int,
      "action": "insert_after_line|replace_line|annotate",
      "code": "<HTML/JSON-LD snippet or replacement>",
      "reason": "TÜRKÇE açıklama - kısa ve net",
      "severity": "critical|high|medium|low",
      "confidence": 0.0-1.0,
      "review_required": false,
      "suggested_rewrite": "TÜRKÇE iyileştirme önerisi (opsiyonel)"
    }
  ]
}

🚨 ÖNEMLİ: "reason" ve "suggested_rewrite" alanları MUTLAKA TÜRKÇE olmalı!
YANLIŞ: "Missing productID property in Product schema. While not strictly required, it is strongly recommended."
DOĞRU: "Product schema'da productID özelliği eksik. Zorunlu olmasa da şiddetle önerilir."

⚠️ CRITICAL: Return ONLY the JSON object above. NO markdown code blocks, NO explanatory text, NO comments outside JSON.
Example of CORRECT output:
{"file":"about.php","chunk_start":1,"chunk_end":180,"issues":[]}

Example of WRONG output:
```json
{"file":"about.php",...}
```
Here is the analysis: {...}

SADECE JSON DÖNDÜR!"""


class GeminiClient:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={
                "temperature": settings.GEMINI_TEMPERATURE,
                "max_output_tokens": settings.GEMINI_MAX_OUTPUT_TOKENS,
            }
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def analyze_chunk(self, prompt_data: GeminiPromptData) -> GeminiResponse:
        """
        Send chunk to Gemini for analysis and return structured response
        
        Uses rate limiter to enforce max 3 concurrent requests
        """
        # Acquire rate limiter slot (blocks if limit reached)
        async with rate_limiter:
            try:
                # Build user prompt (with system prompt prepended)
                user_prompt = f"{SYSTEM_PROMPT}\n\n{self._build_user_prompt(prompt_data)}"
                
                # Call Gemini API
                logger.info(f"Analyzing chunk: {prompt_data.file} [{prompt_data.chunk_start}:{prompt_data.chunk_end}]")
                response = self.model.generate_content(user_prompt)
                
                # Parse JSON response
                response_text = response.text.strip()
                logger.debug(f"Gemini raw response: {response_text[:500]}...")
                
                # Clean markdown code blocks if present
                response_text = self._clean_markdown(response_text)
                
                # Validate and parse
                response_data = json.loads(response_text)
                validated_response = GeminiResponse(**response_data)
                
                logger.info(f"Found {len(validated_response.issues)} issues in chunk")
                return validated_response
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini JSON response: {e}")
                logger.error(f"Raw response: {response_text}")
                raise ValueError(f"Invalid JSON from Gemini: {e}")
            
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                raise
    
    @retry(
        stop=stop_after_attempt(5),  # Increased from 3 to 5 retries
        wait=wait_exponential(multiplier=2, min=4, max=30)  # Longer wait: 4s, 8s, 16s, 30s, 30s
    )
    async def generate_content(self, prompt: str) -> str:
        """
        Generate content from Gemini API with extended retry handling
        
        Args:
            prompt: The prompt text to send to Gemini
            
        Returns:
            Response text from Gemini
        """
        # Acquire rate limiter slot (blocks if limit reached)
        async with rate_limiter:
            try:
                logger.debug(f"Generating content with Gemini (prompt length: {len(prompt)})")
                # Run in thread pool to avoid blocking, with extended timeout handling
                import asyncio
                response = await asyncio.wait_for(
                    asyncio.to_thread(self.model.generate_content, prompt),
                    timeout=180.0  # 3 minutes per attempt (Gemini SDK default is 60s)
                )
                response_text = response.text.strip()
                logger.debug(f"Gemini response length: {len(response_text)}")
                return response_text
            except asyncio.TimeoutError:
                logger.warning("Gemini API call timed out after 180s, will retry")
                raise
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                raise
    
    def _clean_markdown(self, text: str) -> str:
        """
        Remove markdown code blocks from response
        
        Gemini sometimes wraps JSON in ```json ... ``` despite instructions
        """
        text = text.strip()
        
        # Remove ```json at start and ``` at end
        if text.startswith("```json"):
            text = text[7:]  # Remove ```json
        elif text.startswith("```"):
            text = text[3:]  # Remove ```
        
        if text.endswith("```"):
            text = text[:-3]  # Remove trailing ```
        
        return text.strip()
    
    def _build_user_prompt(self, data: GeminiPromptData) -> str:
        """Build the user prompt with chunk data"""
        prompt_dict = {
            "file": data.file,
            "chunk_start": data.chunk_start,
            "chunk_end": data.chunk_end,
            "content": data.content,
            "context_head": data.context_head,
            "context_tail": data.context_tail,
            "keywords": data.keywords,
            "site_language": data.site_language,
            "site_url": data.site_url,
            "global_rules": data.global_rules.model_dump()
        }
        
        return f"""Analyze this code chunk and return ONLY valid JSON:

{json.dumps(prompt_dict, ensure_ascii=False, indent=2)}

Remember: Return ONLY the JSON object, no markdown, no explanations."""


# Singleton instance
gemini_client = GeminiClient()


