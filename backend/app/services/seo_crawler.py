"""
SEO Crawler Service using Playwright
Crawls a single URL and extracts all necessary SEO data
"""
import asyncio
import time
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from urllib.parse import urlparse, urljoin
import re
import httpx

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

from app.schemas.seo_schemas import CrawlResult

logger = logging.getLogger(__name__)


class SEOCrawler:
    """Playwright-based SEO crawler"""
    
    def __init__(self, screenshot_dir: str = "workspace/screenshots"):
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def crawl(self, url: str, analysis_id: str) -> CrawlResult:
        """
        Crawl a single URL and extract SEO data
        
        Args:
            url: URL to crawl
            analysis_id: Analysis ID for file naming
            
        Returns:
            CrawlResult with HTML content and metadata
        """
        logger.info(f"Starting crawl for URL: {url}")
        start_time = time.time()
        
        try:
            if not self.browser:
                raise RuntimeError("Browser not initialized. Use context manager.")
            
            # Create new page
            page = await self.browser.new_page(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (compatible; AIAnabasisSEOBot/1.0; +https://aianabasis.com/seobot)'
            )
            
            try:
                # Navigate to URL (very long timeout - 10 minutes)
                response = await page.goto(
                    url,
                    wait_until='networkidle',
                    timeout=600000  # 10 minutes - effectively no timeout
                )
                
                if not response:
                    raise Exception("No response received from URL")
                
                status_code = response.status
                
                # Wait for page to be fully loaded
                await page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(2)  # Additional wait for JS rendering
                
                # Get HTML content
                html_content = await page.content()
                
                # Extract title and meta description
                page_title = await page.title()
                meta_description = await page.evaluate("""
                    () => {
                        const meta = document.querySelector('meta[name="description"]');
                        return meta ? meta.getAttribute('content') : null;
                    }
                """)
                
                # Count visible H1 tags using Playwright (more accurate than HTML parsing)
                # Only count H1s that are actually visible in the viewport and in main content area
                visible_h1_count = await page.evaluate("""
                    () => {
                        const h1s = document.querySelectorAll('h1');
                        let visibleCount = 0;
                        const viewportHeight = window.innerHeight;
                        const viewportWidth = window.innerWidth;
                        const bodyHeight = document.body.scrollHeight;
                        const mainContentThreshold = bodyHeight * 0.8; // First 80% of page is main content
                        
                        h1s.forEach(h1 => {
                            const style = window.getComputedStyle(h1);
                            const rect = h1.getBoundingClientRect();
                            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                            const absoluteTop = rect.top + scrollTop;
                            
                            // Skip if hidden by CSS
                            if (style.display === 'none' || 
                                style.visibility === 'hidden' || 
                                parseFloat(style.opacity) === 0) {
                                return;
                            }
                            
                            // Skip if no dimensions
                            if (rect.width === 0 || rect.height === 0) {
                                return;
                            }
                            
                            // Skip if completely outside viewport (with some tolerance)
                            if (rect.bottom < -50 || rect.top > viewportHeight + 50 || 
                                rect.right < -50 || rect.left > viewportWidth + 50) {
                                return;
                            }
                            
                            // Skip if in footer area (last 20% of page) - likely duplicate/navigation H1
                            if (absoluteTop > mainContentThreshold) {
                                return;
                            }
                            
                            // Skip if inside common hidden containers (modals, dropdowns, nav menus, etc.)
                            let parent = h1.parentElement;
                            let isInHiddenContainer = false;
                            while (parent && parent !== document.body) {
                                const parentStyle = window.getComputedStyle(parent);
                                const parentRect = parent.getBoundingClientRect();
                                
                                // Check if parent is hidden
                                if (parentStyle.display === 'none' || 
                                    parentStyle.visibility === 'hidden' ||
                                    parseFloat(parentStyle.opacity) === 0 ||
                                    parentRect.width === 0 || parentRect.height === 0) {
                                    isInHiddenContainer = true;
                                    break;
                                }
                                
                                // Check for common hidden/navigation container classes/attributes
                                const classes = (parent.className || '').toLowerCase();
                                const id = (parent.id || '').toLowerCase();
                                const tagName = parent.tagName.toLowerCase();
                                
                                // Skip if in navigation, footer, sidebar, modal, etc.
                                if (tagName === 'nav' || 
                                    tagName === 'footer' ||
                                    tagName === 'aside' ||
                                    classes.includes('modal') || 
                                    classes.includes('dropdown') || 
                                    classes.includes('hidden') ||
                                    classes.includes('sr-only') ||
                                    classes.includes('visually-hidden') ||
                                    classes.includes('navigation') ||
                                    classes.includes('menu') ||
                                    classes.includes('sidebar') ||
                                    id.includes('modal') ||
                                    id.includes('popup') ||
                                    id.includes('nav') ||
                                    id.includes('menu')) {
                                    // Check if this container is actually visible and in viewport
                                    if (parentRect.width === 0 || parentRect.height === 0 ||
                                        parentRect.bottom < 0 || parentRect.top > viewportHeight) {
                                        isInHiddenContainer = true;
                                        break;
                                    }
                                }
                                
                                parent = parent.parentElement;
                            }
                            
                            if (!isInHiddenContainer) {
                                visibleCount++;
                            }
                        });
                        
                        return visibleCount;
                    }
                """)
                
                logger.info(f"Playwright detected {visible_h1_count} visible H1 tags in main content area")
                
                # Take screenshot
                screenshot_path = self.screenshot_dir / f"{analysis_id}.png"
                await page.screenshot(path=str(screenshot_path), full_page=True)
                
                load_time = time.time() - start_time
                
                logger.info(f"Successfully crawled {url} in {load_time:.2f}s")
                
                return CrawlResult(
                    url=url,
                    html_content=html_content,
                    screenshot_path=str(screenshot_path),
                    page_title=page_title,
                    meta_description=meta_description,
                    status_code=status_code,
                    load_time=load_time,
                    visible_h1_count=visible_h1_count
                )
                
            finally:
                await page.close()
                
        except PlaywrightTimeout as e:
            logger.error(f"Timeout while crawling {url}: {str(e)}")
            return CrawlResult(
                url=url,
                html_content="",
                status_code=408,
                error=f"Timeout: {str(e)}"
            )
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return CrawlResult(
                url=url,
                html_content="",
                status_code=500,
                error=str(e)
            )
    
    async def check_robots_txt(self, base_url: str) -> Dict[str, Any]:
        """Check if robots.txt exists and parse it"""
        try:
            parsed = urlparse(base_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            if not self.browser:
                return {"exists": False, "error": "Browser not initialized"}
            
            page = await self.browser.new_page()
            try:
                response = await page.goto(robots_url, timeout=600000)  # 10 minutes
                if response and response.status == 200:
                    content = await page.content()
                    # Extract text from HTML
                    soup = BeautifulSoup(content, 'html.parser')
                    robots_text = soup.get_text()
                    
                    return {
                        "exists": True,
                        "content": robots_text[:1000],  # First 1000 chars
                        "has_sitemap": "sitemap:" in robots_text.lower()
                    }
                else:
                    return {"exists": False, "status_code": response.status if response else None}
            finally:
                await page.close()
                
        except Exception as e:
            logger.warning(f"Error checking robots.txt: {str(e)}")
            return {"exists": False, "error": str(e)}
    
    async def check_sitemap(self, base_url: str) -> Dict[str, Any]:
        """Check if sitemap.xml exists"""
        try:
            parsed = urlparse(base_url)
            sitemap_urls = [
                f"{parsed.scheme}://{parsed.netloc}/sitemap.xml",
                f"{parsed.scheme}://{parsed.netloc}/sitemap_index.xml",
            ]
            
            if not self.browser:
                return {"exists": False, "error": "Browser not initialized"}
            
            for sitemap_url in sitemap_urls:
                page = await self.browser.new_page()
                try:
                    response = await page.goto(sitemap_url, timeout=600000)  # 10 minutes
                    if response and response.status == 200:
                        content = await page.content()
                        return {
                            "exists": True,
                            "url": sitemap_url,
                            "valid": "<?xml" in content and "urlset" in content.lower()
                        }
                finally:
                    await page.close()
            
            return {"exists": False}
            
        except Exception as e:
            logger.warning(f"Error checking sitemap: {str(e)}")
            return {"exists": False, "error": str(e)}
    
    async def check_broken_links(self, links: List[str], max_checks: int = 20) -> Dict[str, Any]:
        """
        Check if links are broken (return 404, 500, etc.)
        
        Args:
            links: List of URLs to check
            max_checks: Maximum number of links to check (to avoid timeout)
            
        Returns:
            Dict with broken_links list and count
        """
        broken_links = []
        checked_count = 0
        
        # No timeout for broken link checking - wait as long as needed
        async with httpx.AsyncClient(timeout=None, follow_redirects=True) as client:
            for link in links[:max_checks]:
                try:
                    # No timeout - wait as long as needed
                    response = await client.get(link, timeout=None)
                    if response.status_code >= 400:
                        broken_links.append({
                            'url': link,
                            'status_code': response.status_code
                        })
                except Exception as e:
                    # Connection error, etc. (but no timeout errors)
                    # Only mark as broken if it's a real error, not just slow
                    error_str = str(e)
                    if 'timeout' not in error_str.lower():
                        broken_links.append({
                            'url': link,
                            'status_code': None,
                            'error': error_str
                        })
                
                checked_count += 1
                
                # Small delay to avoid overwhelming server
                await asyncio.sleep(0.1)
        
        return {
            "broken_links": broken_links,
            "broken_count": len(broken_links),
            "checked_count": checked_count,
            "total_links": len(links)
        }


class HTMLAnalyzer:
    """Analyze HTML content for SEO metrics"""
    
    def __init__(self, html_content: str, url: str):
        self.html = html_content
        self.url = url
        self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def extract_schemas(self) -> list[str]:
        """Extract Schema.org types from page"""
        schemas = []
        
        # JSON-LD schemas
        for script in self.soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and '@type' in data:
                    schemas.append(data['@type'])
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and '@type' in item:
                            schemas.append(item['@type'])
            except:
                pass
        
        # Microdata schemas
        for elem in self.soup.find_all(itemtype=True):
            itemtype = elem.get('itemtype', '')
            if 'schema.org' in itemtype:
                schema_type = itemtype.split('/')[-1]
                schemas.append(schema_type)
        
        return list(set(schemas))
    
    def analyze_headings(self, visible_h1_count: Optional[int] = None) -> Dict[str, Any]:
        """Analyze heading structure - use Playwright count if available, otherwise filter visible headings"""
        # Find all headings
        all_h1_tags = self.soup.find_all('h1')
        all_h2_tags = self.soup.find_all('h2')
        all_h3_tags = self.soup.find_all('h3')
        
        # If Playwright visible H1 count is available, use it (most accurate)
        if visible_h1_count is not None:
            h1_count = visible_h1_count
            # Get H1 texts from visible ones (approximate by filtering)
            visible_h1_tags = self._filter_visible_headings(all_h1_tags)
            h1_texts = [h.get_text(strip=True) for h in visible_h1_tags[:h1_count]]  # Limit to count
        else:
            # Fallback: Filter visible headings using CSS detection
            visible_h1_tags = self._filter_visible_headings(all_h1_tags)
            h1_count = len(visible_h1_tags)
            h1_texts = [h.get_text(strip=True) for h in visible_h1_tags]
        
        visible_h2_tags = self._filter_visible_headings(all_h2_tags)
        visible_h3_tags = self._filter_visible_headings(all_h3_tags)
        
        return {
            "h1_count": h1_count,
            "h2_count": len(visible_h2_tags),
            "h3_count": len(visible_h3_tags),
            "h1_texts": h1_texts,
            "has_multiple_h1": h1_count > 1,
            "has_no_h1": h1_count == 0,
            # Also return total counts for debugging
            "total_h1_count": len(all_h1_tags),
            "total_h2_count": len(all_h2_tags),
            "total_h3_count": len(all_h3_tags)
        }
    
    def _filter_visible_headings(self, tags) -> List:
        """Filter out hidden headings (display:none, visibility:hidden, or inside hidden parents)"""
        def is_visible(tag):
            """Check if a tag is visible (not hidden by CSS)"""
            # Check if tag itself has hidden style
            style = tag.get('style', '')
            if 'display:none' in style.replace(' ', '') or 'display: none' in style:
                return False
            if 'visibility:hidden' in style.replace(' ', '') or 'visibility: hidden' in style:
                return False
            
            # Check parent elements for hidden classes/attributes
            parent = tag.parent
            while parent and parent.name:
                # Check for common hidden classes
                classes = parent.get('class', [])
                if isinstance(classes, list):
                    classes = ' '.join(classes)
                if any(hidden_class in str(classes).lower() for hidden_class in ['hidden', 'd-none', 'sr-only', 'visually-hidden']):
                    return False
                
                # Check parent style
                parent_style = parent.get('style', '')
                if 'display:none' in parent_style.replace(' ', '') or 'display: none' in parent_style:
                    return False
                if 'visibility:hidden' in parent_style.replace(' ', '') or 'visibility: hidden' in parent_style:
                    return False
                
                parent = parent.parent
            
            return True
        
        return [h for h in tags if is_visible(h)]
    
    def analyze_links(self) -> Dict[str, Any]:
        """Analyze internal and external links"""
        links = self.soup.find_all('a', href=True)
        
        internal_links = []
        external_links = []
        broken_links = []
        nofollow_links = []
        anchor_texts = []  # For natural anchor text analysis
        
        parsed_url = urlparse(self.url)
        base_domain = parsed_url.netloc
        
        for link in links:
            href = link.get('href', '')
            rel = link.get('rel', [])
            anchor_text = link.get_text(strip=True)
            
            # Collect anchor texts for analysis
            if anchor_text:
                anchor_texts.append({
                    'text': anchor_text,
                    'href': href,
                    'is_nofollow': 'nofollow' in rel
                })
            
            # Check nofollow
            if 'nofollow' in rel:
                nofollow_links.append(href)
            
            # Resolve relative URLs
            full_url = urljoin(self.url, href)
            link_domain = urlparse(full_url).netloc
            
            # Classify as internal or external
            if link_domain == base_domain or not link_domain:
                internal_links.append(full_url)
            else:
                external_links.append(full_url)
        
        return {
            "total_links": len(links),
            "internal_count": len(internal_links),
            "external_count": len(external_links),
            "nofollow_count": len(nofollow_links),
            "internal_links": internal_links[:50],  # Limit to first 50
            "external_links": external_links[:50],
            "nofollow_links": nofollow_links[:20],
            "anchor_texts": anchor_texts[:100]  # For natural anchor text analysis
        }
    
    def analyze_images(self) -> Dict[str, Any]:
        """Analyze images and alt attributes"""
        images = self.soup.find_all('img')
        
        images_without_alt = []
        for img in images:
            alt = img.get('alt', '').strip()
            if not alt:
                src = img.get('src', 'unknown')
                images_without_alt.append(src)
        
        return {
            "total_images": len(images),
            "images_without_alt": len(images_without_alt),
            "missing_alt_srcs": images_without_alt[:20]
        }
    
    def calculate_word_count(self) -> int:
        """Calculate visible text word count"""
        # Remove script and style elements
        for script in self.soup(["script", "style", "noscript"]):
            script.decompose()
        
        text = self.soup.get_text()
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def calculate_keyword_density(self, keywords: list[str]) -> Dict[str, float]:
        """Calculate keyword density"""
        # Get visible text
        for script in self.soup(["script", "style", "noscript"]):
            script.decompose()
        
        text = self.soup.get_text().lower()
        words = re.findall(r'\b\w+\b', text)
        total_words = len(words)
        
        if total_words == 0:
            return {kw: 0.0 for kw in keywords}
        
        densities = {}
        for keyword in keywords:
            kw_lower = keyword.lower()
            count = text.count(kw_lower)
            density = (count / total_words) * 100
            densities[keyword] = round(density, 2)
        
        return densities

