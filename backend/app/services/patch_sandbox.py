import shutil
from pathlib import Path
from typing import Tuple, Optional
import tempfile
import logging

logger = logging.getLogger(__name__)


class PatchSandbox:
    """
    Sandbox environment for safe patch testing
    
    Strategy:
    1. Create temp copy of original file
    2. Apply patch to temp copy
    3. Validate temp copy
    4. Only if validation passes → replace original
    5. If validation fails → discard temp, keep original
    """
    
    def __init__(self, sandbox_dir: str = None):
        if sandbox_dir:
            self.sandbox_dir = Path(sandbox_dir)
        else:
            self.sandbox_dir = Path(tempfile.gettempdir()) / "seo_checker_sandbox"
        
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PatchSandbox initialized: {self.sandbox_dir}")
    
    def create_temp_copy(self, original_path: str) -> str:
        """
        Create temporary copy of file for safe patching
        
        Returns: path to temp copy
        """
        try:
            original = Path(original_path)
            
            # Create unique temp filename
            temp_name = f"{original.stem}_temp_{id(self)}{original.suffix}"
            temp_path = self.sandbox_dir / temp_name
            
            # Copy file
            shutil.copy2(original, temp_path)
            
            logger.debug(f"Created temp copy: {original} → {temp_path}")
            return str(temp_path)
        
        except Exception as e:
            logger.error(f"Failed to create temp copy: {e}")
            raise
    
    def apply_and_validate(
        self,
        original_path: str,
        patch_func: callable,
        validate_func: callable,
        *patch_args,
        **patch_kwargs
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Apply patch to temp copy and validate before replacing original
        
        Returns: (success, temp_path, error_message)
        """
        temp_path = None
        
        try:
            # Step 1: Create temp copy
            temp_path = self.create_temp_copy(original_path)
            
            # Step 2: Apply patch to temp copy
            logger.info(f"Applying patch to temp copy: {temp_path}")
            success, backup_path, error = patch_func(temp_path, *patch_args, **patch_kwargs)
            
            if not success:
                logger.error(f"Patch application failed: {error}")
                return False, temp_path, error
            
            # Step 3: Validate temp copy
            logger.info(f"Validating temp copy: {temp_path}")
            is_valid, validation_error = validate_func(temp_path)
            
            if not is_valid:
                logger.error(f"Validation failed: {validation_error}")
                return False, temp_path, validation_error
            
            # Step 4: Validation passed - replace original
            logger.info(f"Validation passed, replacing original: {original_path}")
            shutil.copy2(temp_path, original_path)
            
            logger.info(f"Successfully patched file: {original_path}")
            return True, temp_path, None
        
        except Exception as e:
            error_msg = f"Sandbox patch failed: {e}"
            logger.error(error_msg)
            return False, temp_path, error_msg
    
    def cleanup_temp(self, temp_path: str):
        """Clean up temporary file"""
        try:
            if temp_path and Path(temp_path).exists():
                Path(temp_path).unlink()
                logger.debug(f"Cleaned up temp file: {temp_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file: {e}")
    
    def cleanup_all(self):
        """Clean up entire sandbox directory"""
        try:
            if self.sandbox_dir.exists():
                shutil.rmtree(self.sandbox_dir)
                logger.info(f"Cleaned up sandbox: {self.sandbox_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup sandbox: {e}")


# Singleton instance
patch_sandbox = PatchSandbox()

