"""
SEO Analysis Service
Analyzes HTML content using Gemini AI and generates SEO recommendations
"""
import json
import logging
from typing import List, Dict, Any, Optional
import re

from app.services.gemini_client import GeminiClient
from app.services.seo_crawler import HTMLAnalyzer
from app.schemas.seo_schemas import (
    GeminiSEOResponse,
    GeminiSEOIssue,
    GeminiKeywordScore,
    SEOIssueType,
    SEOIssueSeverity,
    HTMLChunk
)

logger = logging.getLogger(__name__)


class SEOHTMLChunker:
    """Chunk HTML content for Gemini analysis"""
    
    def __init__(self, max_chunk_size: int = 200000):  # 200K for production - reduces chunks significantly
        self.max_chunk_size = max_chunk_size
    
    def chunk_html(self, html_content: str) -> List[HTMLChunk]:
        """
        Split HTML into manageable chunks for Gemini
        
        IMPORTANT: Head section (title, meta, schema) is included in FIRST chunk only
        to reduce chunk count while ensuring Gemini sees critical SEO elements.
        
        Args:
            html_content: Full HTML content
            
        Returns:
            List of HTMLChunk objects
        """
        chunks = []
        
        # Extract head section (title, meta, schema, etc.)
        head_match = re.search(r'<head[^>]*>.*?</head>', html_content, re.DOTALL | re.IGNORECASE)
        head_section = head_match.group(0) if head_match else ""
        
        # Extract body content
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
        if body_match:
            body_content = body_match.group(1)
        else:
            # No body tag found, use entire content as body
            body_content = html_content.replace(head_section, "") if head_section else html_content
        
        # If content is small enough, return as single chunk
        if len(html_content) <= self.max_chunk_size:
            return [HTMLChunk(
                chunk_id=0,
                content=html_content,
                start_pos=0,
                end_pos=len(html_content)
            )]
        
        # Split body by character limit (not by every div - that creates too many chunks)
        # Only split if body is very large
        body_size = len(body_content) if body_content else 0
        
        # Ensure we always have at least one chunk
        if body_size == 0:
            # Empty body, return head only as single chunk
            return [HTMLChunk(
                chunk_id=0,
                content=head_section if head_section else html_content,
                start_pos=0,
                end_pos=0
            )]
        
        # Calculate chunk size: reserve space for HTML tags/wrapper
        # Head is only in first chunk, so other chunks can use full size
        chunk_size = self.max_chunk_size - 500  # Reserve 500 chars for HTML tags/wrapper
        chunk_size = max(chunk_size, 50000)  # Ensure minimum 50K for production quality
        
        if body_size <= chunk_size:
            # Single chunk with head
            if body_match:
                full_chunk = head_section + "\n<body>\n" + body_content + "\n</body>"
            else:
                full_chunk = head_section + "\n" + body_content if head_section else body_content
            return [HTMLChunk(
                chunk_id=0,
                content=full_chunk,
                start_pos=0,
                end_pos=len(body_content)
            )]
        
        # Split body into chunks by character limit
        chunk_id = 0
        start_pos = 0
        
        for i in range(0, body_size, chunk_size):
            chunk_body = body_content[i:i + chunk_size]
            
            # Add head only to first chunk
            if chunk_id == 0:
                if body_match:
                    full_chunk = head_section + "\n<body>\n" + chunk_body + "\n</body>"
                else:
                    full_chunk = head_section + "\n" + chunk_body if head_section else chunk_body
            else:
                if body_match:
                    full_chunk = "<body>\n" + chunk_body + "\n</body>"
                else:
                    full_chunk = chunk_body
            
            chunks.append(HTMLChunk(
                chunk_id=chunk_id,
                content=full_chunk,
                start_pos=start_pos,
                end_pos=start_pos + len(chunk_body)
            ))
            chunk_id += 1
            start_pos += len(chunk_body)
        
        # Ensure at least one chunk was created
        if len(chunks) == 0:
            # Fallback: create single chunk with all content
            chunks.append(HTMLChunk(
                chunk_id=0,
                content=html_content,
                start_pos=0,
                end_pos=len(html_content)
            ))
        
        logger.info(f"Split HTML into {len(chunks)} chunks (head section in first chunk only)")
        return chunks
    
    def _split_by_sections(self, html: str) -> List[str]:
        """Split HTML by major sections - DEPRECATED, using character-based splitting instead"""
        # This method is no longer used - we split by character limit instead
        # to avoid creating too many chunks
        return [html]


class SEOAnalyzer:
    """Main SEO analysis service using Gemini AI"""
    
    def __init__(self, gemini_client: GeminiClient):
        self.gemini = gemini_client
        self.chunker = SEOHTMLChunker()
    
    async def analyze_html(
        self,
        html_content: str,
        url: str,
        keywords: List[str],
        anchor_texts: Optional[List[Dict[str, Any]]] = None,
        real_data: Optional[Dict[str, Any]] = None
    ) -> GeminiSEOResponse:
        """
        Analyze HTML content for SEO issues
        
        Args:
            html_content: Full HTML content
            url: Page URL
            keywords: Target keywords
            anchor_texts: Anchor text data for analysis
            real_data: Real extracted data from HTMLAnalyzer (headings, schemas, etc.)
            
        Returns:
            Combined SEO analysis results
        """
        logger.info(f"Starting SEO analysis for {url}")
        
        # Extract head section for reference in all chunks
        head_match = re.search(r'<head[^>]*>.*?</head>', html_content, re.DOTALL | re.IGNORECASE)
        head_section = head_match.group(0) if head_match else ""
        
        # Chunk HTML
        chunks = self.chunker.chunk_html(html_content)
        logger.info(f"Analyzing {len(chunks)} chunks")
        
        # Limit chunks to prevent timeout but analyze enough for accuracy
        # Production: Analyze up to 20 chunks for comprehensive analysis
        max_chunks_to_analyze = 20
        if len(chunks) > max_chunks_to_analyze:
            logger.warning(f"Too many chunks ({len(chunks)}), analyzing first {max_chunks_to_analyze} for comprehensive coverage")
            chunks = chunks[:max_chunks_to_analyze]
        else:
            logger.info(f"Analyzing all {len(chunks)} chunks for complete analysis")
        
        # Analyze each chunk
        all_issues = []
        all_keyword_scores = {}
        
        for chunk in chunks:
            try:
                chunk_result = await self._analyze_chunk(chunk, url, keywords, anchor_texts, head_section, real_data)
                all_issues.extend(chunk_result.issues)
                
                # Merge keyword scores (take max scores)
                for kw, score in chunk_result.keyword_scores.items():
                    if kw not in all_keyword_scores:
                        all_keyword_scores[kw] = score
                    else:
                        # Take higher scores
                        existing = all_keyword_scores[kw]
                        all_keyword_scores[kw] = GeminiKeywordScore(
                            presence_score=max(existing.presence_score, score.presence_score),
                            prominence=max(existing.prominence, score.prominence),
                            recommendation=score.recommendation if score.presence_score > existing.presence_score else existing.recommendation
                        )
            except Exception as e:
                logger.error(f"Error analyzing chunk {chunk.chunk_id}: {str(e)}")
                continue
        
        # Deduplicate issues
        unique_issues = self._deduplicate_issues(all_issues)
        
        logger.info(f"Analysis complete: {len(unique_issues)} unique issues found")
        
        return GeminiSEOResponse(
            issues=unique_issues,
            keyword_scores=all_keyword_scores
        )
    
    async def _analyze_chunk(
        self,
        chunk: HTMLChunk,
        url: str,
        keywords: List[str],
        anchor_texts: Optional[List[Dict[str, Any]]] = None,
        head_section: str = "",
        real_data: Optional[Dict[str, Any]] = None
    ) -> GeminiSEOResponse:
        """Analyze a single HTML chunk"""
        
        prompt = self._build_analysis_prompt(chunk.content, url, keywords, anchor_texts, head_section, real_data)
        
        try:
            response_text = await self.gemini.generate_content(prompt)
            
            # Parse JSON response
            result = self._parse_gemini_response(response_text)
            return result
            
        except Exception as e:
            logger.error(f"Error in Gemini analysis: {str(e)}")
            # Return empty result on error
            return GeminiSEOResponse(
                issues=[],
                keyword_scores={kw: GeminiKeywordScore(
                    presence_score=0,
                    prominence=0,
                    recommendation="Analiz hatası"
                ) for kw in keywords}
            )
    
    def _build_analysis_prompt(self, html_content: str, url: str, keywords: List[str], anchor_texts: Optional[List[Dict[str, Any]]] = None, head_section: str = "", real_data: Optional[Dict[str, Any]] = None) -> str:
        """Build Gemini analysis prompt"""
        
        keywords_str = ", ".join(keywords)
        
        # Add anchor texts info if available
        anchor_text_info = ""
        if anchor_texts:
            anchor_text_info = f"\n\n**İç Link Anchor Text'leri (Doğallık Analizi İçin):**\n"
            for i, anchor in enumerate(anchor_texts[:30], 1):  # Limit to 30 for prompt size
                anchor_text_info += f"{i}. \"{anchor['text']}\" -> {anchor['href']} (nofollow: {anchor.get('is_nofollow', False)})\n"
        
        # Add head section reference if available
        head_info = ""
        if head_section:
            head_info = f"\n\n**ÖNEMLİ: Sayfanın <head> bölümü (title, meta, schema burada):**\n```html\n{head_section[:2000]}\n```\n\nBu head section'ı dikkate alarak analiz yap!"
        
        # Add real extracted data to prevent false positives
        real_data_info = ""
        if real_data:
            real_data_info = "\n\n**🚨 GERÇEK VERİLER (HTMLAnalyzer'dan tespit edildi - BU VERİLERİ KULLAN!):**\n"
            if 'h1_count' in real_data:
                real_data_info += f"- H1 Sayısı: {real_data['h1_count']} (Gerçek sayı - HTML'de {real_data['h1_count']} adet <h1> etiketi VAR!)\n"
                if real_data.get('h1_texts'):
                    real_data_info += f"- H1 Metinleri: {', '.join(real_data['h1_texts'][:5])}\n"
            if 'schemas' in real_data:
                schemas_list = real_data['schemas'] if isinstance(real_data['schemas'], list) else []
                if schemas_list:
                    real_data_info += f"- Mevcut Schema Türleri: {', '.join(schemas_list)} (Bu schemalar VAR, eksik olarak işaretleme!)\n"
                else:
                    real_data_info += "- Mevcut Schema Türleri: YOK (Schema eksik issue oluşturabilirsin)\n"
            if 'title' in real_data and real_data['title']:
                real_data_info += f"- Title: {real_data['title'][:100]} (VAR - sadece optimizasyon kontrolü yap!)\n"
            if 'meta_description' in real_data and real_data['meta_description']:
                real_data_info += f"- Meta Description: {real_data['meta_description'][:100]} (VAR - sadece optimizasyon kontrolü yap!)\n"
            real_data_info += "\n⚠️ BU VERİLER DOĞRU! HTML'i tekrar kontrol etmeden bu verilere göre analiz yap!\n"
        
        prompt = f"""Sen "AI Anabasis SEO Auditor" isimli üst seviye bir teknik SEO uzmanısın.
Çıktı sadece JSON olacak. Dil: Türkçe. Uydurma/hallucination yok.
Eksik veri varsa "{{{{PLACEHOLDER}}}}" yaz.

🚨 KRİTİK KURALLAR:
1. {real_data_info if real_data_info else "Gerçek veri yok, HTML'i dikkatli analiz et!"}
2. HTML içeriğini ÇOK DİKKATLİ oku! Mevcut olan şeyleri gözden kaçırma!
3. Eğer yukarıdaki GERÇEK VERİLER'de bir şey VAR ise, o şey için "missing" veya "issue" oluşturma!
4. Sadece GERÇEKTEN eksik veya yanlış olan şeyler için issue oluştur!

{head_info}
Aşağıdaki HTML içeriğini teknik SEO açısından analiz et.
URL: {url}
Anahtar Kelimeler: {keywords_str}

HTML İçerik:
```html
{html_content[:50000]}
```

NOT: HTML içeriği büyük olabilir, önemli kısımları (head, h1-h6, schema script'leri) öncelikle kontrol et!
{anchor_text_info}

Aşağıdaki konularda DETAYLI analiz yap:

1. **Schema.org Yapılandırılmış Veri Analizi:**
   - 🚨 ÖNEMLİ: GERÇEK VERİLER'de schema listesi varsa, MUTLAKA o listeyi kullan! HTML'i tekrar arama!
   - Eğer GERÇEK VERİLER'de schema listesi VARSA ve boş değilse (örn: ["Organization", "WebSite"] gibi), "schema_missing" issue oluşturma! Sadece eksik schema türlerini belirt (örn: Article, Product eksikse onları belirt)!
   - Eğer GERÇEK VERİLER'de schema listesi YOKSA veya boşsa, o zaman "schema_missing" issue oluştur!
   - Sadece GERÇEKTEN eksik olan schema türlerini belirle (Organization, WebSite, WebPage, BreadcrumbList, Article, Product, vb.)
   - Her eksik schema için ZORUNLU alanları listele (örn: Organization için name, url, logo ZORUNLU)
   - Mevcut schemalarda eksik alanları tespit et ve öner

2. **Title ve Meta Description Analizi:**
   - GERÇEK VERİLER'de title ve meta description varsa, onları kullan! HTML'i tekrar arama!
   - Eğer GERÇEK VERİLER'de title VARSA, "title_issue" oluşturma! Sadece uzunluk/optimizasyon kontrolü yap!
   - Eğer GERÇEK VERİLER'de meta description VARSA, "meta_issue" oluşturma! Sadece uzunluk/optimizasyon kontrolü yap!
   - Title uzunluğu: 50-60 karakter ideal (varsa uzunluk kontrolü yap)
   - Meta description uzunluğu: 150-160 karakter ideal (varsa uzunluk kontrolü yap)
   - Anahtar kelime uyumu kontrolü
   - Google snippet'te nasıl görüneceğini değerlendir

3. **Heading Yapısı (H1-H2-H3) Analizi:**
   - 🚨 ÖNEMLİ: GERÇEK VERİLER'de H1 sayısı varsa, MUTLAKA o sayıyı kullan! HTML'i tekrar sayma!
   - Eğer GERÇEK VERİLER'de H1 sayısı = 1 ise, "heading_issue" oluşturma! (Tek H1 normaldir)
   - Eğer GERÇEK VERİLER'de H1 sayısı > 1 ise, SADECE BİR KERE "heading_issue" oluştur (critical severity ile)!
   - Eğer GERÇEK VERİLER'de H1 sayısı = 0 ise, "heading_issue" oluştur (H1 eksik)!
   - H1 sayısı (sadece 1 olmalı, birden fazla ise sorun)
   - Hiyerarşik yapı kontrolü (H1 > H2 > H3 sırası)
   - Anahtar kelimelerin heading'lerde kullanımı
   - Heading'lerde anahtar kelime stuffing var mı?

4. **İç Link Analizi:**
   - Kırık link kontrolü (404, 500, vb. hatalar)
   - Dofollow/nofollow dağılımı
   - Anchor text doğallığı: Anchor text'ler doğal mı yoksa spam gibi mi görünüyor?
   - Anahtar kelime stuffing var mı? (örn: "toplantı kabini toplantı kabini toplantı kabini" gibi)
   - İç linkler mantıklı bağlamda mı verilmiş?

5. **Görsel ALT Etiketleri:**
   - Eksik veya boş alt etiketleri tespit et
   - Alt etiketlerinde anahtar kelime kullanımı (doğal mı?)

6. **Semantic Density (Anlamsal Yoğunluk) Analizi:**
   - Anahtar kelime yoğunluğu: İdeal %1-3 arası
   - Keyword stuffing var mı? (%5 üzeri riskli)
   - İçerik doğal mı yoksa zorla mı eklenmiş?

7. **Word Count (Kelime Sayısı):**
   - Minimum 300 kelime önerilir
   - İçerik yeterli mi?

8. **Google Snippet Uyumluluğu:**
   - Title ve description snippet'te nasıl görünecek?
   - Rich snippet için schema yeterli mi?
   - FAQ, Review, Product gibi rich snippet şemaları var mı?

9. **Robots.txt ve Sitemap.xml:**
   - Robots.txt mevcut mu? Doğru yapılandırılmış mı?
   - Sitemap.xml mevcut mu? Geçerli mi?

10. **Nofollow/Dofollow Analizi:**
    - Nofollow linkler doğal dağılımda mı? (Tüm linkler nofollow ise sorun)
    - Dış linklerde nofollow kullanımı uygun mu?
    - İç linklerde gereksiz nofollow var mı?

11. **Anahtar Kelime Öne Çıkma Analizi:**
    - Anahtar kelimeler title'da mı? (Google'da öne çıkma için kritik)
    - H1'de kullanılmış mı?
    - İlk 100 kelimede geçiyor mu?
    - URL'de var mı?
    - Meta description'da var mı?
    - Bu faktörlere göre Google'da öne çıkma potansiyelini % olarak hesapla (0-100)

12. **Teknik Hatalar:**
    - Eksik meta etiketleri
    - Duplicate content riski
    - Canonical tag eksik mi?
    - Open Graph etiketleri var mı?

Çıktı formatı *zorunlu* olarak şu JSON olacaktır:
{{
  "issues": [
    {{
      "type": "schema_missing|title_issue|meta_issue|heading_issue|broken_link|nofollow_issue|anchor_spam|semantic_density_low|wordcount_low|image_alt_missing|robots_issue|sitemap_issue|snippet_issue|technical_error",
      "line": null,
      "reason": "Sorunun detaylı açıklaması",
      "recommendation": "Düzeltme önerisi",
      "example_fix": "Örnek kod veya düzeltme",
      "severity": "critical|high|medium|low",
      "confidence": 0.95
    }}
  ],
  "keyword_scores": {{
    "{keywords[0] if keywords else 'keyword'}": {{
      "presence_score": 75,
      "prominence": 60,
      "recommendation": "Title ve H1'de kullanımı artırın. Google'da öne çıkma potansiyeli: %60. Title'da kullanıldığı için iyi, ancak H1'de de kullanılmalı."
    }}
  }}
  
ÖNEMLİ NOTLAR:
- "prominence" değeri Google'da öne çıkma potansiyelini temsil eder (0-100)
- Bu skor şu faktörlere göre hesaplanmalı: Title'da kullanım (+30), H1'de kullanım (+25), İlk 100 kelimede (+15), URL'de (+10), Meta description'da (+10), Heading'lerde (+10)
- Schema eksik alanları için "example_fix" alanında JSON-LD örneği ver
- Anchor text doğallığı için "anchor_spam" tipinde issue oluştur ve "recommendation" alanında doğal alternatif öner
}}

ÖNEMLİ: Sadece JSON çıktısı ver, başka açıklama ekleme. JSON geçerli olmalı."""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> GeminiSEOResponse:
        """Parse Gemini JSON response"""
        
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_str = None
            
            # Strategy 1: Look for ```json code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Strategy 2: Look for ``` code blocks (without json)
                json_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                    # Remove "json" if it's at the start
                    if json_str.startswith('json'):
                        json_str = json_str[4:].strip()
                else:
                    # Strategy 3: Find first { and last } to extract JSON object
                    first_brace = response_text.find('{')
                    last_brace = response_text.rfind('}')
                    if first_brace >= 0 and last_brace > first_brace:
                        json_str = response_text[first_brace:last_brace + 1]
                    else:
                        raise ValueError("No JSON found in response")
            
            if not json_str:
                raise ValueError("No JSON found in response")
            
            # Clean and fix common JSON issues
            json_str = self._fix_json_string(json_str)
            
            # Try to parse
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error after fix: {str(e)}")
                logger.debug(f"JSON string (first 1000 chars): {json_str[:1000]}")
                raise
            
            # Parse issues
            issues = []
            for issue_data in data.get('issues', []):
                try:
                    issue = GeminiSEOIssue(
                        type=SEOIssueType(issue_data['type']),
                        line=issue_data.get('line'),
                        reason=issue_data['reason'],
                        recommendation=issue_data['recommendation'],
                        example_fix=issue_data.get('example_fix', ''),
                        severity=SEOIssueSeverity(issue_data['severity']),
                        confidence=float(issue_data['confidence'])
                    )
                    issues.append(issue)
                except Exception as e:
                    logger.warning(f"Error parsing issue: {str(e)}")
                    continue
            
            # Parse keyword scores
            keyword_scores = {}
            for kw, score_data in data.get('keyword_scores', {}).items():
                try:
                    score = GeminiKeywordScore(
                        presence_score=float(score_data['presence_score']),
                        prominence=float(score_data['prominence']),
                        recommendation=score_data['recommendation']
                    )
                    keyword_scores[kw] = score
                except Exception as e:
                    logger.warning(f"Error parsing keyword score for {kw}: {str(e)}")
                    continue
            
            return GeminiSEOResponse(
                issues=issues,
                keyword_scores=keyword_scores
            )
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            logger.debug(f"Response text (first 2000 chars): {response_text[:2000]}")
            logger.debug(f"Response text (last 500 chars): {response_text[-500:]}")
            # Return empty result instead of raising to prevent complete failure
            return GeminiSEOResponse(
                issues=[],
                keyword_scores={}
            )
    
    def _fix_json_string(self, json_str: str) -> str:
        """
        Fix common JSON issues in Gemini responses - IMPROVED VERSION
        
        Handles:
        - Unterminated strings
        - Unescaped quotes in strings
        - Control characters
        - Trailing commas
        """
        try:
            # First, try to parse as-is
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError as e:
            error_msg = str(e)
            error_pos = getattr(e, 'pos', None)
            logger.warning(f"JSON parse error at pos {error_pos}: {error_msg}")
            
            # Strategy 1: Fix unterminated strings more intelligently
            if 'Unterminated string' in error_msg and error_pos:
                try:
                    # Find the opening quote by going backwards from error position
                    start_pos = error_pos - 1
                    # Skip escaped characters
                    while start_pos >= 0:
                        if json_str[start_pos] == '"':
                            # Check if it's escaped
                            escape_count = 0
                            check_pos = start_pos - 1
                            while check_pos >= 0 and json_str[check_pos] == '\\':
                                escape_count += 1
                                check_pos -= 1
                            if escape_count % 2 == 0:  # Not escaped, this is the opening quote
                                break
                        start_pos -= 1
                    
                    if start_pos >= 0:
                        # Find where the string should end by looking for structural characters
                        # Look ahead for comma, }, or ] that's not inside quotes
                        search_start = error_pos
                        search_end = min(error_pos + 500, len(json_str))  # Limit search
                        
                        in_quotes = True
                        for i in range(search_start, search_end):
                            char = json_str[i]
                            if char == '"' and (i == 0 or json_str[i-1] != '\\'):
                                # Toggle quote state
                                in_quotes = not in_quotes
                            elif not in_quotes and char in [',', '}', ']']:
                                # Found end of string value
                                # Escape the content properly
                                content = json_str[start_pos + 1:i]
                                # Escape unescaped quotes and newlines
                                content = content.replace('\\', '\\\\')  # Escape backslashes first
                                content = content.replace('"', '\\"')
                                content = content.replace('\n', '\\n')
                                content = content.replace('\r', '\\r')
                                content = content.replace('\t', '\\t')
                                # Fix double escaping
                                content = content.replace('\\\\\\\\', '\\\\')
                                
                                json_str = json_str[:start_pos + 1] + content + '"' + json_str[i:]
                                break
                        else:
                            # No structural character found, close at safe position
                            safe_pos = min(error_pos + 200, len(json_str))
                            content = json_str[start_pos + 1:safe_pos]
                            # Escape properly
                            content = content.replace('\\', '\\\\')
                            content = content.replace('"', '\\"')
                            content = content.replace('\n', '\\n')
                            content = content.replace('\r', '\\r')
                            content = content.replace('\t', '\\t')
                            content = content.replace('\\\\\\\\', '\\\\')
                            json_str = json_str[:start_pos + 1] + content + '"' + json_str[safe_pos:]
                except Exception as fix_error:
                    logger.warning(f"Could not fix unterminated string: {fix_error}")
            
            # Strategy 2: Remove trailing commas
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            # Strategy 3: Try parsing again after fixes
            try:
                json.loads(json_str)
                logger.info("JSON fixed successfully")
                return json_str
            except json.JSONDecodeError as e2:
                logger.warning(f"JSON fix failed, attempting to extract valid portion. Error: {str(e2)}")
                
                # Strategy 4: Extract largest valid JSON substring
                # Try to find where JSON becomes invalid and extract up to that point
                for end_pos in range(len(json_str), max(100, len(json_str) - 2000), -100):
                    try:
                        test_json = json_str[:end_pos]
                        # Close any open braces/brackets
                        open_braces = test_json.count('{') - test_json.count('}')
                        open_brackets = test_json.count('[') - test_json.count(']')
                        
                        # Remove trailing comma before closing
                        test_json = re.sub(r',(\s*)$', r'\1', test_json)
                        test_json += '}' * open_braces + ']' * open_brackets
                        
                        parsed = json.loads(test_json)
                        logger.info(f"Extracted valid JSON from first {end_pos} characters")
                        return test_json
                    except:
                        continue
                
                # Strategy 5: Try to extract just the issues array if it exists
                issues_match = re.search(r'"issues"\s*:\s*\[(.*?)\]', json_str, re.DOTALL)
                keyword_scores_match = re.search(r'"keyword_scores"\s*:\s*\{.*?\}', json_str, re.DOTALL)
                
                if issues_match or keyword_scores_match:
                    # Try to construct minimal valid JSON
                    issues_json = issues_match.group(0) if issues_match else '"issues": []'
                    keyword_json = keyword_scores_match.group(0) if keyword_scores_match else '"keyword_scores": {}'
                    minimal_json = '{' + issues_json + ', ' + keyword_json + '}'
                    try:
                        json.loads(minimal_json)
                        logger.info("Extracted minimal valid JSON")
                        return minimal_json
                    except:
                        pass
                
                # Last resort: return empty but valid JSON
                logger.error("Could not fix JSON, returning empty result")
                return '{"issues": [], "keyword_scores": {}}'
    
    def _deduplicate_issues(self, issues: List[GeminiSEOIssue]) -> List[GeminiSEOIssue]:
        """Remove duplicate issues - improved version"""
        
        seen = set()
        unique_issues = []
        
        for issue in issues:
            # Create unique key based on type, severity, and normalized reason
            # Normalize reason by removing extra whitespace and taking first 50 chars
            normalized_reason = ' '.join(issue.reason.split())[:50].lower()
            key = f"{issue.type.value}:{issue.severity.value}:{normalized_reason}"
            
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
            else:
                # If duplicate found, keep the one with higher confidence
                for i, existing in enumerate(unique_issues):
                    existing_key = f"{existing.type.value}:{existing.severity.value}:{' '.join(existing.reason.split())[:50].lower()}"
                    if existing_key == key and issue.confidence > existing.confidence:
                        unique_issues[i] = issue
                        break
        
        return unique_issues
    
    def calculate_overall_score(
        self,
        issues: List[GeminiSEOIssue],
        keyword_scores: Dict[str, GeminiKeywordScore]
    ) -> Dict[str, float]:
        """
        Calculate overall SEO scores
        
        Returns:
            Dict with overall_score, technical_score, content_score
        """
        
        # Start with perfect score
        technical_score = 100.0
        content_score = 100.0
        
        # Deduct points for issues
        technical_issue_types = [
            SEOIssueType.SCHEMA_MISSING,
            SEOIssueType.TITLE_ISSUE,
            SEOIssueType.META_ISSUE,
            SEOIssueType.HEADING_ISSUE,
            SEOIssueType.BROKEN_LINK,
            SEOIssueType.ROBOTS_ISSUE,
            SEOIssueType.SITEMAP_ISSUE,
            SEOIssueType.TECHNICAL_ERROR
        ]
        
        content_issue_types = [
            SEOIssueType.SEMANTIC_DENSITY_LOW,
            SEOIssueType.WORDCOUNT_LOW,
            SEOIssueType.IMAGE_ALT_MISSING,
            SEOIssueType.ANCHOR_SPAM,
            SEOIssueType.NOFOLLOW_ISSUE,
            SEOIssueType.SNIPPET_ISSUE
        ]
        
        severity_penalties = {
            SEOIssueSeverity.CRITICAL: 15,
            SEOIssueSeverity.HIGH: 10,
            SEOIssueSeverity.MEDIUM: 5,
            SEOIssueSeverity.LOW: 2
        }
        
        for issue in issues:
            penalty = severity_penalties.get(issue.severity, 5)
            
            if issue.type in technical_issue_types:
                technical_score -= penalty
            elif issue.type in content_issue_types:
                content_score -= penalty
            else:
                # Split penalty between both
                technical_score -= penalty / 2
                content_score -= penalty / 2
        
        # Ensure scores don't go below 0
        technical_score = max(0, technical_score)
        content_score = max(0, content_score)
        
        # Calculate overall score (weighted average)
        overall_score = (technical_score * 0.6) + (content_score * 0.4)
        
        # Bonus for good keyword scores
        if keyword_scores:
            avg_keyword_score = sum(
                (s.presence_score + s.prominence) / 2 
                for s in keyword_scores.values()
            ) / len(keyword_scores)
            
            # Add up to 10 bonus points for excellent keyword optimization
            keyword_bonus = min(10, (avg_keyword_score - 70) / 3) if avg_keyword_score > 70 else 0
            overall_score = min(100, overall_score + keyword_bonus)
        
        return {
            "overall_score": round(overall_score, 1),
            "technical_score": round(technical_score, 1),
            "content_score": round(content_score, 1)
        }

