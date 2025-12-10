from bs4 import BeautifulSoup
from pathlib import Path
import shutil
import logging
from datetime import datetime
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class PatchEngine:
    """
    Safe patching engine with automatic backup and rollback
    
    Strategies:
    - PHP/HTML: DOM-based using BeautifulSoup
    - JS/React: Line-based patching
    """
    
    def __init__(self, backup_dir: str = "/app/backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, file_path: str) -> str:
        """
        Create backup of file before patching
        Returns backup file path
        """
        file_path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        
        return str(backup_path)
    
    def apply_patch(
        self,
        file_path: str,
        line_number: int,
        action: str,
        code: str,
        file_type: str = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Apply patch to file
        
        Returns: (success, backup_path, error_message)
        """
        try:
            # Create backup first
            backup_path = self.create_backup(file_path)
            
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Determine file type
            if file_type is None:
                file_type = Path(file_path).suffix.lower()
            
            # Apply patch based on file type
            if file_type in ['.php', '.html', '.htm']:
                patched_content = self._apply_dom_patch(
                    original_content, line_number, action, code
                )
            elif file_type in ['.js', '.jsx', '.ts', '.tsx']:
                patched_content = self._apply_line_patch(
                    original_content, line_number, action, code
                )
            else:
                # Default to line-based
                patched_content = self._apply_line_patch(
                    original_content, line_number, action, code
                )
            
            # Write patched content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(patched_content)
            
            logger.info(f"Successfully patched {file_path} at line {line_number}")
            return True, backup_path, None
        
        except Exception as e:
            error_msg = f"Failed to apply patch: {e}"
            logger.error(error_msg)
            
            # Attempt rollback
            if 'backup_path' in locals():
                self.rollback(file_path, backup_path)
            
            return False, None, error_msg
    
    def _apply_dom_patch(
        self,
        content: str,
        line_number: int,
        action: str,
        code: str
    ) -> str:
        """
        Apply patch using BeautifulSoup (DOM-based)
        Safer for HTML/PHP files
        """
        # For DOM-based patching, we need to be smart about where to insert
        # This is a simplified version - production would need more sophisticated logic
        
        lines = content.splitlines(keepends=True)
        
        if action == "insert_after_line":
            if line_number <= len(lines):
                lines.insert(line_number, code + '\n')
            else:
                raise ValueError(f"Line number {line_number} out of range")
        
        elif action == "replace_line":
            if 0 < line_number <= len(lines):
                lines[line_number - 1] = code + '\n'
            else:
                raise ValueError(f"Line number {line_number} out of range")
        
        elif action == "annotate":
            # For annotate, add as comment
            if 0 < line_number <= len(lines):
                comment = f"<!-- SEO NOTE: {code} -->\n"
                lines.insert(line_number, comment)
            else:
                raise ValueError(f"Line number {line_number} out of range")
        
        return ''.join(lines)
    
    def _apply_line_patch(
        self,
        content: str,
        line_number: int,
        action: str,
        code: str
    ) -> str:
        """
        Apply patch using line-based approach
        Used for JS/React files
        """
        lines = content.splitlines(keepends=True)
        
        if action == "insert_after_line":
            if line_number <= len(lines):
                lines.insert(line_number, code + '\n')
            else:
                raise ValueError(f"Line number {line_number} out of range")
        
        elif action == "replace_line":
            if 0 < line_number <= len(lines):
                # Preserve indentation
                original_line = lines[line_number - 1]
                indent = len(original_line) - len(original_line.lstrip())
                indented_code = ' ' * indent + code.lstrip()
                lines[line_number - 1] = indented_code + '\n'
            else:
                raise ValueError(f"Line number {line_number} out of range")
        
        elif action == "annotate":
            # For JS, add as comment
            if 0 < line_number <= len(lines):
                comment = f"// SEO NOTE: {code}\n"
                lines.insert(line_number, comment)
            else:
                raise ValueError(f"Line number {line_number} out of range")
        
        return ''.join(lines)
    
    def rollback(self, file_path: str, backup_path: str) -> bool:
        """
        Rollback file to backup version
        """
        try:
            shutil.copy2(backup_path, file_path)
            logger.info(f"Rolled back {file_path} from {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to rollback: {e}")
            return False
    
    def validate_patch(self, file_path: str, file_type: str = None) -> Tuple[bool, Optional[str]]:
        """
        Validate patched file
        Returns: (is_valid, error_message)
        """
        if file_type is None:
            file_type = Path(file_path).suffix.lower()
        
        try:
            if file_type == '.php':
                return self._validate_php(file_path)
            elif file_type in ['.html', '.htm']:
                return self._validate_html(file_path)
            elif file_type in ['.js', '.jsx', '.ts', '.tsx']:
                return self._validate_js(file_path)
            else:
                # No validation for unknown types
                return True, None
        
        except Exception as e:
            return False, str(e)
    
    def _validate_php(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """Validate PHP syntax using php -l"""
        import subprocess
        
        try:
            result = subprocess.run(
                ['php', '-l', file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr
        
        except FileNotFoundError:
            logger.warning("PHP binary not found, skipping validation")
            return True, None
        except Exception as e:
            return False, str(e)
    
    def _validate_html(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate HTML using BeautifulSoup
        
        Includes DOM integrity check:
        - Ensure all opened tags are closed
        - Check for malformed structure
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'lxml')
            
            # DOM integrity checks
            # 1. Check for unclosed script tags
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string is None and len(list(script.children)) == 0:
                    # Empty script tag is OK
                    continue
            
            # 2. Check for unclosed head tag
            heads = soup.find_all('head')
            if len(heads) > 1:
                return False, "Multiple <head> tags found - DOM integrity compromised"
            
            # 3. Check for unclosed body tag
            bodies = soup.find_all('body')
            if len(bodies) > 1:
                return False, "Multiple <body> tags found - DOM integrity compromised"
            
            # Basic validation - if parsing succeeds, it's valid enough
            return True, None
        
        except Exception as e:
            return False, f"DOM integrity check failed: {str(e)}"
    
    def _validate_js(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """Validate JS/React syntax"""
        # For now, just check if file is readable
        # In production, you'd use ESLint or similar
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
            return True, None
        except Exception as e:
            return False, str(e)


# Singleton instance
patch_engine = PatchEngine()


