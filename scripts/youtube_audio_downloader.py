#!/usr/bin/env python3
"""
YouTube Audio Downloader for JDL Pattern Detection

Downloads audio from YouTube URLs in M4A format for race start pattern analysis.
Optionally runs COUNT→GO pattern detection on downloaded audio.

Author: Claude Code
Date: 2025
"""

import argparse
import os
import sys
import subprocess
import re
from pathlib import Path
from typing import Optional, Tuple

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for filesystem compatibility
    
    Args:
        filename: Raw filename string
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'[\s]+', ' ', filename)  # Normalize whitespace
    filename = filename.strip()
    
    # Limit length to prevent filesystem issues
    if len(filename) > 200:
        filename = filename[:200].rsplit(' ', 1)[0]  # Cut at word boundary
    
    return filename

def get_video_info(url: str) -> Tuple[str, str]:
    """
    Get video title and ID from YouTube URL
    
    Args:
        url: YouTube URL
        
    Returns:
        Tuple of (title, video_id)
    """
    try:
        cmd = [
            'yt-dlp',
            '--get-title',
            '--get-id',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        
        if len(lines) >= 2:
            title = lines[0]
            video_id = lines[1]
            return title, video_id
        else:
            # Fallback: extract ID from URL
            video_id = extract_video_id(url)
            return f"YouTube_Video_{video_id}", video_id
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting video info: {e}")
        video_id = extract_video_id(url)
        return f"YouTube_Video_{video_id}", video_id

def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return "unknown"

def download_audio(url: str, output_dir: str = ".", run_detection: bool = True) -> Optional[str]:
    """
    Download audio from YouTube URL in M4A format
    
    Args:
        url: YouTube URL to download
        output_dir: Directory to save the audio file
        run_detection: Whether to run pattern detection after download
        
    Returns:
        Path to downloaded file if successful, None if failed
    """
    print(f'🎬 YouTube Audio Downloader')
    print('=' * 50)
    print(f'🔗 URL: {url}')
    print('=' * 50)
    
    # Get video information
    print('📋 Getting video information...')
    title, video_id = get_video_info(url)
    sanitized_title = sanitize_filename(title)
    
    print(f'📺 Title: {title}')
    print(f'🆔 Video ID: {video_id}')
    
    # Prepare output filename
    output_filename = f"{sanitized_title} [{video_id}].%(ext)s"
    output_path = os.path.join(output_dir, output_filename)
    
    print(f'💾 Output: {output_path}')
    print()
    
    # Download audio using yt-dlp
    cmd = [
        'yt-dlp',
        '--extract-audio',
        '--audio-format', 'm4a',
        '--audio-quality', '0',  # Best quality
        '--output', output_path,
        '--no-playlist',
        '--write-info-json',
        url
    ]
    
    try:
        print('⬇️ Downloading audio...')
        result = subprocess.run(cmd, check=True)
        
        # Find the actual downloaded file
        expected_file = output_path.replace('%(ext)s', 'm4a')
        
        if os.path.exists(expected_file):
            print(f'✅ Download successful: {expected_file}')
            
            # Get file size
            file_size = os.path.getsize(expected_file)
            size_mb = file_size / (1024 * 1024)
            print(f'📊 File size: {size_mb:.1f} MB')
            
            # Optionally run pattern detection
            if run_detection:
                run_pattern_detection(expected_file)
            
            return expected_file
        else:
            print(f'❌ Downloaded file not found at expected location: {expected_file}')
            return None
            
    except subprocess.CalledProcessError as e:
        print(f'❌ Download failed: {e}')
        return None
    except FileNotFoundError:
        print('❌ yt-dlp not found. Please install with: pip install yt-dlp')
        return None

def run_pattern_detection(audio_file: str):
    """
    Run COUNT→GO pattern detection on downloaded audio
    
    Args:
        audio_file: Path to audio file
    """
    print()
    print('🎯 Running COUNT→GO Pattern Detection...')
    print('-' * 50)
    
    try:
        # Import and run pattern detection
        from pattern_enhanced_detector import PatternEnhancedDetector, PatternConfig
        
        # Use optimized configuration for general audio
        config = PatternConfig(
            count_correlation_threshold=0.32,
            count_spectral_threshold=0.12,
            go_correlation_threshold=0.32,
            go_spectral_threshold=0.18,
            min_gap_seconds=2.0,
            max_gap_seconds=10.0,
            min_distance_seconds=3.0
        )
        
        detector = PatternEnhancedDetector(config=config)
        patterns = detector.detect_patterns(audio_file)
        
        if patterns:
            print(f'✅ Found {len(patterns)} COUNT→GO patterns!')
            
            # Generate results filename based on input
            base_name = Path(audio_file).stem
            detector.save_results(patterns, base_name)
            
            print(f'💾 Results saved to results/{base_name}.*')
        else:
            print('❌ No COUNT→GO patterns detected')
            
    except ImportError:
        print('⚠️ Pattern detection not available (missing dependencies)')
    except Exception as e:
        print(f'❌ Pattern detection failed: {e}')

def main():
    """Main function for command line interface"""
    parser = argparse.ArgumentParser(
        description='Download audio from YouTube URLs for JDL pattern analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and run pattern detection (default)
  python youtube_audio_downloader.py "https://www.youtube.com/watch?v=MSoaNUMg2yo"
  
  # Download audio only (skip detection)
  python youtube_audio_downloader.py "https://www.youtube.com/watch?v=MSoaNUMg2yo" --no-detect
  
  # Specify output directory
  python youtube_audio_downloader.py "https://www.youtube.com/watch?v=MSoaNUMg2yo" --output downloads/
        """
    )
    
    parser.add_argument(
        'url',
        help='YouTube URL to download'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='.',
        help='Output directory for downloaded audio (default: current directory)'
    )
    
    parser.add_argument(
        '--no-detect',
        action='store_true',
        help='Skip COUNT→GO pattern detection after download'
    )
    
    parser.add_argument(
        '--no-info',
        action='store_true',
        help='Skip downloading info JSON file'
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not ('youtube.com' in args.url or 'youtu.be' in args.url):
        print('❌ Invalid YouTube URL')
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Download audio (run detection by default unless --no-detect specified)
    downloaded_file = download_audio(
        args.url, 
        args.output, 
        not args.no_detect
    )
    
    if downloaded_file:
        print()
        print('🎉 Process completed successfully!')
        print(f'📂 Audio file: {downloaded_file}')
        
        if not args.no_detect:
            results_pattern = f"results/{Path(downloaded_file).stem}*"
            print(f'📊 Results: {results_pattern}')
    else:
        print('❌ Process failed')
        sys.exit(1)

if __name__ == "__main__":
    main()