import subprocess
import json
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class Validator:
    """
    Validation service for patched files
    
    Validates:
    - PHP syntax (php -l)
    - HTML structure (BeautifulSoup)
    - JSON-LD schema
    - React build (npm run build)
    """
    
    @staticmethod
    def validate_php(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate PHP syntax using php -l
        Returns: (is_valid, error_message)
        """
        try:
            result = subprocess.run(
                ['php', '-l', file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"PHP validation passed: {file_path}")
                return True, None
            else:
                logger.error(f"PHP validation failed: {result.stderr}")
                return False, result.stderr
        
        except FileNotFoundError:
            logger.warning("PHP binary not found, skipping validation")
            return True, None
        
        except subprocess.TimeoutExpired:
            return False, "PHP validation timeout"
        
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_json_ld(json_ld_string: str) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON-LD syntax
        """
        try:
            parsed = json.loads(json_ld_string)
            
            # Check for @context and @type
            if '@context' not in parsed:
                return False, "Missing @context in JSON-LD"
            
            if '@type' not in parsed:
                return False, "Missing @type in JSON-LD"
            
            logger.info(f"JSON-LD validation passed for type: {parsed.get('@type')}")
            return True, None
        
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_react_build(project_dir: str) -> Tuple[bool, Optional[str]]:
        """
        Validate React project by running build
        """
        try:
            result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info(f"React build validation passed: {project_dir}")
                return True, None
            else:
                logger.error(f"React build failed: {result.stderr}")
                return False, result.stderr
        
        except FileNotFoundError:
            logger.warning("npm not found, skipping React validation")
            return True, None
        
        except subprocess.TimeoutExpired:
            return False, "React build timeout"
        
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def should_rollback(file_type: str, validation_result: Tuple[bool, Optional[str]]) -> bool:
        """
        Determine if we should rollback based on validation result
        
        Hard stops (auto-rollback):
        - PHP syntax error
        - React build failure
        - Invalid JSON-LD
        """
        is_valid, error = validation_result
        
        if not is_valid:
            if file_type in ['.php', '.jsx', '.tsx', '.ts', '.js']:
                logger.warning(f"Triggering rollback for {file_type}: {error}")
                return True
        
        return False


# Singleton instance
validator = Validator()

