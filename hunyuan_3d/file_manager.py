"""
File Manager for Hunyuan 3D models
Handles model storage, caching, and cleanup
"""

import os
import hashlib
import time
import glob
import re
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """
    Manages file operations for 3D models including caching and cleanup
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize file manager
        
        Args:
            base_dir: Base directory for storing models (default: current extension directory)
        """
        if base_dir is None:
            # Get extension directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.base_dir = os.path.dirname(current_dir)
        else:
            self.base_dir = base_dir
            
        self.models_dir = os.path.join(self.base_dir, "models")
        self.cache_dir = os.path.join(self.base_dir, "cache")
        
        # Create directories if they don't exist
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Create necessary directories"""
        for directory in [self.models_dir, self.cache_dir]:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"Created directory: {directory}")
                except Exception as e:
                    logger.error(f"Failed to create directory {directory}: {e}")
                    raise
                    
    def generate_filename(self, prompt: str, extension: str = "glb") -> str:
        """
        Generate unique filename based on prompt
        
        Args:
            prompt: Text prompt used for generation
            extension: File extension (default: glb)
            
        Returns:
            Unique filename
        """
        # Clean prompt for filename
        clean_prompt = re.sub(r'[^\w\s-]', '', prompt.strip())
        clean_prompt = re.sub(r'[-\s]+', '_', clean_prompt)
        clean_prompt = clean_prompt[:50]  # Limit length
        
        # Create hash for uniqueness
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        timestamp = int(time.time())
        
        filename = f"{clean_prompt}_{prompt_hash}_{timestamp}.{extension}"
        return filename
        
    def get_model_path(self, filename: str) -> str:
        """
        Get full path for model file
        
        Args:
            filename: Model filename
            
        Returns:
            Full path to model file
        """
        return os.path.join(self.models_dir, filename)
        
    def get_cache_path(self, filename: str) -> str:
        """
        Get full path for cache file
        
        Args:
            filename: Cache filename
            
        Returns:
            Full path to cache file
        """
        return os.path.join(self.cache_dir, filename)
        
    def file_exists(self, filepath: str) -> bool:
        """
        Check if file exists
        
        Args:
            filepath: Path to file
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.exists(filepath) and os.path.isfile(filepath)
        
    def get_file_size(self, filepath: str) -> int:
        """
        Get file size in bytes
        
        Args:
            filepath: Path to file
            
        Returns:
            File size in bytes, 0 if file doesn't exist
        """
        try:
            if self.file_exists(filepath):
                return os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Error getting file size for {filepath}: {e}")
        return 0
        
    def delete_file(self, filepath: str) -> bool:
        """
        Delete file safely
        
        Args:
            filepath: Path to file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if self.file_exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted file: {filepath}")
                return True
        except Exception as e:
            logger.error(f"Error deleting file {filepath}: {e}")
        return False
        
    def cleanup_old_files(self, directory: str, max_age_hours: int = 24, max_files: int = 100) -> int:
        """
        Clean up old files in directory
        
        Args:
            directory: Directory to clean
            max_age_hours: Maximum age in hours before deletion
            max_files: Maximum number of files to keep
            
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        
        try:
            if not os.path.exists(directory):
                return 0
                
            # Get all files with modification time
            files = []
            for filepath in glob.glob(os.path.join(directory, "*")):
                if os.path.isfile(filepath):
                    mtime = os.path.getmtime(filepath)
                    files.append((filepath, mtime))
                    
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x[1], reverse=True)
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            # Delete old files
            for i, (filepath, mtime) in enumerate(files):
                should_delete = False
                
                # Delete if too old
                if current_time - mtime > max_age_seconds:
                    should_delete = True
                    
                # Delete if exceeding max files limit
                if i >= max_files:
                    should_delete = True
                    
                if should_delete:
                    if self.delete_file(filepath):
                        deleted_count += 1
                        
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old files from {directory}")
                
        except Exception as e:
            logger.error(f"Error during cleanup of {directory}: {e}")
            
        return deleted_count
        
    def cleanup_models(self, max_age_hours: int = 24, max_files: int = 50) -> int:
        """
        Clean up old model files
        
        Args:
            max_age_hours: Maximum age in hours before deletion
            max_files: Maximum number of model files to keep
            
        Returns:
            Number of files deleted
        """
        return self.cleanup_old_files(self.models_dir, max_age_hours, max_files)
        
    def cleanup_cache(self, max_age_hours: int = 6, max_files: int = 20) -> int:
        """
        Clean up old cache files
        
        Args:
            max_age_hours: Maximum age in hours before deletion
            max_files: Maximum number of cache files to keep
            
        Returns:
            Number of files deleted
        """
        return self.cleanup_old_files(self.cache_dir, max_age_hours, max_files)
        
    def get_disk_usage(self) -> dict:
        """
        Get disk usage information
        
        Returns:
            Dictionary with disk usage info
        """
        usage = {
            "models_dir": self.models_dir,
            "cache_dir": self.cache_dir,
            "models_size": 0,
            "cache_size": 0,
            "models_count": 0,
            "cache_count": 0
        }
        
        try:
            # Calculate models directory usage
            for filepath in glob.glob(os.path.join(self.models_dir, "*")):
                if os.path.isfile(filepath):
                    usage["models_size"] += self.get_file_size(filepath)
                    usage["models_count"] += 1
                    
            # Calculate cache directory usage
            for filepath in glob.glob(os.path.join(self.cache_dir, "*")):
                if os.path.isfile(filepath):
                    usage["cache_size"] += self.get_file_size(filepath)
                    usage["cache_count"] += 1
                    
        except Exception as e:
            logger.error(f"Error calculating disk usage: {e}")
            
        return usage
        
    def format_size(self, size_bytes: int) -> str:
        """
        Format size in human readable format
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
        
    def get_storage_info(self) -> str:
        """
        Get formatted storage information
        
        Returns:
            Formatted storage info string
        """
        usage = self.get_disk_usage()
        
        info = f"""Storage Information:
Models Directory: {usage['models_dir']}
- Files: {usage['models_count']}
- Size: {self.format_size(usage['models_size'])}

Cache Directory: {usage['cache_dir']}
- Files: {usage['cache_count']}  
- Size: {self.format_size(usage['cache_size'])}

Total Size: {self.format_size(usage['models_size'] + usage['cache_size'])}"""
        
        return info