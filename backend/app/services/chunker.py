from typing import List, Tuple
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


class Chunker:
    """
    Chunk files into overlapping segments for analysis
    
    Chunk size: 180 lines
    Overlap: 20 lines
    Context: 10 lines before and after each chunk
    
    SEMANTIC EXPANSION:
    - Automatically expands chunks if they split <script>, <head>, or JSON-LD blocks
    - Ensures structured data is never split mid-block
    """
    
    # Patterns for semantic block detection
    BLOCK_PATTERNS = {
        'script': (r'<script[^>]*>', r'</script>'),
        'head': (r'<head[^>]*>', r'</head>'),
        'json_ld': (r'<script\s+type=["\']application/ld\+json["\'][^>]*>', r'</script>'),
        'style': (r'<style[^>]*>', r'</style>'),
    }
    
    def __init__(self, chunk_size: int = 180, overlap: int = 20, context_lines: int = 10):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.context_lines = context_lines
    
    def chunk_file(self, file_path: str, content: str = None) -> List[dict]:
        """
        Chunk a file into overlapping segments
        
        Returns list of chunks with structure:
        {
            'file_path': str,
            'start_line': int,
            'end_line': int,
            'content': str,
            'context_head': str,
            'context_tail': str
        }
        """
        # Read file if content not provided
        if content is None:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        lines = content.splitlines()
        total_lines = len(lines)
        
        if total_lines == 0:
            logger.warning(f"Empty file: {file_path}")
            return []
        
        chunks = []
        start = 0
        
        while start < total_lines:
            # Calculate chunk boundaries
            end = min(start + self.chunk_size, total_lines)
            
            # SEMANTIC EXPANSION: Check if we're splitting a structured block
            end = self._expand_for_semantic_blocks(lines, start, end, total_lines)
            
            # Extract chunk content
            chunk_lines = lines[start:end]
            chunk_content = '\n'.join(chunk_lines)
            
            # Extract context (previous 10 lines)
            context_head_start = max(0, start - self.context_lines)
            context_head_lines = lines[context_head_start:start]
            context_head = '\n'.join(context_head_lines) if context_head_lines else None
            
            # Extract context (next 10 lines)
            context_tail_end = min(total_lines, end + self.context_lines)
            context_tail_lines = lines[end:context_tail_end]
            context_tail = '\n'.join(context_tail_lines) if context_tail_lines else None
            
            chunk = {
                'file_path': file_path,
                'start_line': start + 1,  # 1-indexed for human readability
                'end_line': end,
                'content': chunk_content,
                'context_head': context_head,
                'context_tail': context_tail,
                'line_count': len(chunk_lines)
            }
            
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.overlap
            
            # Prevent infinite loop on small files
            if start >= total_lines or end >= total_lines:
                break
        
        logger.info(f"Created {len(chunks)} chunks for {file_path} ({total_lines} lines)")
        return chunks
    
    def _expand_for_semantic_blocks(
        self,
        lines: List[str],
        start: int,
        end: int,
        total_lines: int
    ) -> int:
        """
        Expand chunk boundaries if they split semantic blocks
        
        Checks for:
        - <script> blocks (including JSON-LD)
        - <head> blocks
        - <style> blocks
        
        Returns adjusted end line
        """
        chunk_content = '\n'.join(lines[start:end])
        
        # Check each block type
        for block_name, (open_pattern, close_pattern) in self.BLOCK_PATTERNS.items():
            # Find all opening tags in chunk
            open_matches = list(re.finditer(open_pattern, chunk_content, re.IGNORECASE))
            
            for open_match in open_matches:
                # Calculate absolute line number of opening tag
                lines_before_match = chunk_content[:open_match.start()].count('\n')
                open_line = start + lines_before_match
                
                # Search for closing tag from open_line onwards
                close_line = self._find_closing_tag(
                    lines,
                    open_line,
                    close_pattern,
                    total_lines
                )
                
                if close_line is not None and close_line >= end:
                    # Block extends beyond current chunk - expand
                    new_end = close_line + 1
                    logger.debug(
                        f"Semantic expansion: {block_name} block "
                        f"[{open_line}:{close_line}] extends chunk to line {new_end}"
                    )
                    end = min(new_end, total_lines)
        
        return end
    
    def _find_closing_tag(
        self,
        lines: List[str],
        start_line: int,
        close_pattern: str,
        total_lines: int,
        max_search: int = 100
    ) -> int:
        """
        Find closing tag starting from start_line
        
        Returns line number of closing tag, or None if not found
        """
        search_end = min(start_line + max_search, total_lines)
        
        for i in range(start_line, search_end):
            if re.search(close_pattern, lines[i], re.IGNORECASE):
                return i
        
        return None
    
    def chunk_directory(self, directory: str, extensions: List[str] = None) -> dict:
        """
        Chunk all files in a directory
        
        Returns dict: {file_path: [chunks]}
        """
        if extensions is None:
            extensions = ['.php', '.html', '.htm', '.js', '.jsx', '.tsx', '.ts', '.css']
        
        directory_path = Path(directory)
        all_chunks = {}
        
        for ext in extensions:
            for file_path in directory_path.rglob(f'*{ext}'):
                if file_path.is_file():
                    try:
                        chunks = self.chunk_file(str(file_path))
                        if chunks:
                            all_chunks[str(file_path)] = chunks
                    except Exception as e:
                        logger.error(f"Failed to chunk {file_path}: {e}")
        
        total_chunks = sum(len(chunks) for chunks in all_chunks.values())
        logger.info(f"Chunked {len(all_chunks)} files into {total_chunks} total chunks")
        
        return all_chunks
    
    def get_line_content(self, file_path: str, line_number: int, context: int = 5) -> str:
        """
        Get content around a specific line number
        Useful for displaying issues in UI
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            start = max(0, line_number - context - 1)
            end = min(len(lines), line_number + context)
            
            context_lines = []
            for i in range(start, end):
                prefix = ">>> " if i == line_number - 1 else "    "
                context_lines.append(f"{prefix}{i+1:4d} | {lines[i].rstrip()}")
            
            return '\n'.join(context_lines)
        
        except Exception as e:
            logger.error(f"Failed to get line content: {e}")
            return ""


# Singleton instance
chunker = Chunker(chunk_size=180, overlap=20, context_lines=10)

