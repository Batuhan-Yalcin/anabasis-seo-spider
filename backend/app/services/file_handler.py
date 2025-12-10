import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import List, Dict
import logging
import magic
import aiofiles
import os

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Handle file uploads, extraction, and inventory
    """
    
    SUPPORTED_EXTENSIONS = ['.php', '.html', '.htm', '.js', '.jsx', '.tsx', '.ts', '.css']
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_upload(self, file_content: bytes, filename: str, job_id: str) -> str:
        """
        Save uploaded file to workspace
        Returns: path to saved file
        """
        job_dir = self.workspace_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        upload_path = job_dir / filename
        
        async with aiofiles.open(upload_path, 'wb') as f:
            await f.write(file_content)
        
        logger.info(f"Saved upload: {upload_path} ({len(file_content)} bytes)")
        return str(upload_path)
    
    def extract_archive(self, archive_path: str, job_id: str) -> str:
        """
        Extract ZIP or TAR archive
        Returns: path to extraction directory
        """
        archive_path = Path(archive_path)
        extract_dir = self.workspace_dir / job_id / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Detect archive type
            if zipfile.is_zipfile(archive_path):
                logger.info(f"Extracting ZIP: {archive_path}")
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            
            elif tarfile.is_tarfile(archive_path):
                logger.info(f"Extracting TAR: {archive_path}")
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_dir)
            
            else:
                raise ValueError("Unsupported archive format")
            
            logger.info(f"Extracted to: {extract_dir}")
            return str(extract_dir)
        
        except Exception as e:
            logger.error(f"Failed to extract archive: {e}")
            raise
    
    def create_inventory(self, directory: str) -> List[Dict]:
        """
        Create inventory of all supported files in directory
        
        Returns list of file info:
        [
            {
                'file_path': str,
                'file_type': str,
                'size_bytes': int,
                'line_count': int
            }
        ]
        """
        directory = Path(directory)
        inventory = []
        
        for ext in self.SUPPORTED_EXTENSIONS:
            for file_path in directory.rglob(f'*{ext}'):
                # Skip __MACOSX and hidden files
                if '__MACOSX' in str(file_path) or any(part.startswith('.') for part in file_path.parts):
                    continue
                    
                if file_path.is_file():
                    try:
                        # Get file info
                        size_bytes = file_path.stat().st_size
                        
                        # Count lines
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            line_count = sum(1 for _ in f)
                        
                        # Get relative path from extraction directory
                        relative_path = file_path.relative_to(directory)
                        
                        file_info = {
                            'file_path': str(relative_path),
                            'absolute_path': str(file_path),
                            'file_type': ext,
                            'size_bytes': size_bytes,
                            'line_count': line_count
                        }
                        
                        inventory.append(file_info)
                        logger.debug(f"Inventoried: {relative_path} ({line_count} lines)")
                    
                    except Exception as e:
                        logger.warning(f"Failed to inventory {file_path}: {e}")
        
        logger.info(f"Created inventory: {len(inventory)} files")
        return inventory
    
    def get_file_type(self, file_path: str) -> str:
        """
        Detect file type using python-magic
        """
        try:
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file_path)
            return file_type
        except Exception as e:
            logger.warning(f"Failed to detect file type: {e}")
            return Path(file_path).suffix
    
    def cleanup_job(self, job_id: str):
        """
        Clean up job workspace
        """
        job_dir = self.workspace_dir / job_id
        if job_dir.exists():
            shutil.rmtree(job_dir)
            logger.info(f"Cleaned up job: {job_id}")


# Singleton instance will be created in main.py with config

