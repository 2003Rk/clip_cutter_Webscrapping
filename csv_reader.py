"""
CSV Reader Utility for ClipScutter Automation
=============================================

This module handles reading and parsing the clip ranges CSV file,
providing utilities for grouping clips by YouTube URL for efficient processing.

Author: Automated ClipScutter Bot
Version: 1.0
"""

import csv
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ClipData:
    """Data class to store clip information"""
    start_time: str
    end_time: str
    youtube_url: str
    row_number: int = 0
    
    def __str__(self) -> str:
        return f"Clip #{self.row_number}: {self.start_time}-{self.end_time} from {self.youtube_url}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'youtube_url': self.youtube_url,
            'row_number': self.row_number
        }

class CSVReader:
    """Utility class for reading and processing clip CSV files"""
    
    def __init__(self, csv_path: str):
        """
        Initialize CSV reader
        
        Args:
            csv_path (str): Path to the CSV file
        """
        self.csv_path = csv_path
        self.clips: List[ClipData] = []
        self.grouped_clips: Dict[str, List[ClipData]] = {}
        
    def validate_time_format(self, time_str: str) -> bool:
        """
        Validate time format (HH:MM:SS)
        
        Args:
            time_str (str): Time string to validate
            
        Returns:
            bool: True if valid format
        """
        try:
            parts = time_str.split(':')
            if len(parts) != 3:
                return False
            
            hours, minutes, seconds = parts
            if not (hours.isdigit() and minutes.isdigit() and seconds.isdigit()):
                return False
            
            if int(minutes) >= 60 or int(seconds) >= 60:
                return False
                
            return True
        except Exception:
            return False
    
    def validate_youtube_url(self, url: str) -> bool:
        """
        Validate YouTube URL format
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid YouTube URL
        """
        youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
        return any(domain in url for domain in youtube_domains) and url.startswith('http')
    
    def read_csv(self) -> List[ClipData]:
        """
        Read and parse the CSV file
        
        Returns:
            List[ClipData]: List of validated clip data
        """
        clips = []
        invalid_rows = []
        
        try:
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                
                for row_num, row in enumerate(csv_reader, 1):
                    if len(row) < 3:
                        invalid_rows.append((row_num, "Insufficient columns", row))
                        continue
                    
                    start_time = row[0].strip()
                    end_time = row[1].strip()
                    youtube_url = row[2].strip()
                    
                    # Validate data
                    if not self.validate_time_format(start_time):
                        invalid_rows.append((row_num, "Invalid start time format", row))
                        continue
                    
                    if not self.validate_time_format(end_time):
                        invalid_rows.append((row_num, "Invalid end time format", row))
                        continue
                    
                    if not self.validate_youtube_url(youtube_url):
                        invalid_rows.append((row_num, "Invalid YouTube URL", row))
                        continue
                    
                    # Create clip data
                    clip = ClipData(
                        start_time=start_time,
                        end_time=end_time,
                        youtube_url=youtube_url,
                        row_number=row_num
                    )
                    clips.append(clip)
                    logger.debug(f"Valid row {row_num}: {clip}")
            
            self.clips = clips
            
            # Log results
            logger.info(f"Successfully loaded {len(clips)} valid clips from CSV")
            if invalid_rows:
                logger.warning(f"Found {len(invalid_rows)} invalid rows:")
                for row_num, reason, row_data in invalid_rows:
                    logger.warning(f"  Row {row_num}: {reason} - {row_data}")
            
            return clips
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def group_clips_by_url(self, clips: List[ClipData] = None) -> Dict[str, List[ClipData]]:
        """
        Group clips by YouTube URL for efficient processing
        
        Args:
            clips (List[ClipData], optional): List of clips to group. If None, uses self.clips
            
        Returns:
            Dict[str, List[ClipData]]: Clips grouped by YouTube URL
        """
        if clips is None:
            clips = self.clips
        
        grouped = defaultdict(list)
        
        for clip in clips:
            grouped[clip.youtube_url].append(clip)
        
        # Convert to regular dict and sort clips within each group by row number
        result = {}
        for url, url_clips in grouped.items():
            # Sort clips by row number to maintain order
            url_clips.sort(key=lambda x: x.row_number)
            result[url] = url_clips
        
        self.grouped_clips = result
        
        # Log grouping results
        logger.info(f"Grouped {len(clips)} clips into {len(result)} different YouTube URLs:")
        for url, url_clips in result.items():
            logger.info(f"  {url}: {len(url_clips)} clips (rows {url_clips[0].row_number}-{url_clips[-1].row_number})")
        
        return result
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the loaded clips
        
        Returns:
            Dict: Statistics dictionary
        """
        if not self.clips:
            return {"error": "No clips loaded"}
        
        total_clips = len(self.clips)
        unique_urls = len(set(clip.youtube_url for clip in self.clips))
        
        # Calculate total duration (approximation)
        total_duration = 0
        for clip in self.clips:
            try:
                start_parts = [int(x) for x in clip.start_time.split(':')]
                end_parts = [int(x) for x in clip.end_time.split(':')]
                
                start_seconds = start_parts[0] * 3600 + start_parts[1] * 60 + start_parts[2]
                end_seconds = end_parts[0] * 3600 + end_parts[1] * 60 + end_parts[2]
                
                clip_duration = end_seconds - start_seconds
                if clip_duration > 0:
                    total_duration += clip_duration
            except Exception:
                continue
        
        return {
            "total_clips": total_clips,
            "unique_youtube_urls": unique_urls,
            "total_duration_seconds": total_duration,
            "total_duration_formatted": f"{total_duration // 3600:02d}:{(total_duration % 3600) // 60:02d}:{total_duration % 60:02d}",
            "average_clip_duration": total_duration / total_clips if total_clips > 0 else 0
        }
    
    def export_grouped_clips(self, output_path: str) -> None:
        """
        Export grouped clips to a new CSV file organized by URL
        
        Args:
            output_path (str): Path for the output CSV file
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write header
                writer.writerow(['youtube_url', 'start_time', 'end_time', 'original_row'])
                
                for url, clips in self.grouped_clips.items():
                    for clip in clips:
                        writer.writerow([clip.youtube_url, clip.start_time, clip.end_time, clip.row_number])
            
            logger.info(f"Exported grouped clips to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export grouped clips: {e}")
            raise

def main():
    """Test the CSV reader functionality"""
    import os
    
    # Setup logging for testing
    logging.basicConfig(level=logging.INFO)
    
    csv_path = "/Users/rahul/Desktop/FREELANCING/20$_clipcut/clip_ranges.csv"
    
    if not os.path.exists(csv_path):
        logger.error(f"Test CSV file not found: {csv_path}")
        return
    
    # Test CSV reader
    reader = CSVReader(csv_path)
    
    # Read clips
    clips = reader.read_csv()
    logger.info(f"Loaded {len(clips)} clips")
    
    # Group clips
    grouped = reader.group_clips_by_url()
    logger.info(f"Grouped into {len(grouped)} URLs")
    
    # Show statistics
    stats = reader.get_statistics()
    logger.info(f"Statistics: {stats}")
    
    # Export grouped clips for verification
    output_path = "/Users/rahul/Desktop/FREELANCING/20$_clipcut/grouped_clips.csv"
    reader.export_grouped_clips(output_path)

if __name__ == "__main__":
    main()