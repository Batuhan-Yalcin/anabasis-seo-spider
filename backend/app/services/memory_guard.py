import os
from pathlib import Path
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class MemoryGuard:
    """
    Memory pressure guard for job extraction
    
    Rules:
    - Hard limit: 500MB per extracted job
    - Abort job if exceeded
    - Prevents memory exhaustion
    """
    
    # 500MB hard limit
    MAX_EXTRACTED_SIZE_BYTES = 500 * 1024 * 1024  # 500MB
    
    def __init__(self):
        logger.info(
            f"MemoryGuard initialized: max_size={self.format_size(self.MAX_EXTRACTED_SIZE_BYTES)}"
        )
    
    def check_directory_size(self, directory: str) -> Tuple[bool, int, str]:
        """
        Check if directory size exceeds limit
        
        Returns: (is_within_limit, total_size_bytes, formatted_size)
        """
        try:
            total_size = 0
            directory_path = Path(directory)
            
            # Calculate total size recursively
            for item in directory_path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
                    
                    # Early exit if exceeded
                    if total_size > self.MAX_EXTRACTED_SIZE_BYTES:
                        logger.error(
                            f"🔴 MEMORY LIMIT EXCEEDED: {directory} "
                            f"size={self.format_size(total_size)} "
                            f"limit={self.format_size(self.MAX_EXTRACTED_SIZE_BYTES)}"
                        )
                        return False, total_size, self.format_size(total_size)
            
            logger.info(
                f"✅ Memory check passed: {directory} "
                f"size={self.format_size(total_size)}"
            )
            return True, total_size, self.format_size(total_size)
        
        except Exception as e:
            logger.error(f"Failed to check directory size: {e}")
            raise
    
    def check_file_size(self, file_path: str) -> Tuple[bool, int]:
        """
        Check if single file exceeds limit
        
        Returns: (is_within_limit, file_size_bytes)
        """
        try:
            file_size = Path(file_path).stat().st_size
            
            if file_size > self.MAX_EXTRACTED_SIZE_BYTES:
                logger.error(
                    f"🔴 File too large: {file_path} "
                    f"size={self.format_size(file_size)}"
                )
                return False, file_size
            
            return True, file_size
        
        except Exception as e:
            logger.error(f"Failed to check file size: {e}")
            raise
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


# Singleton instance
memory_guard = MemoryGuard()
