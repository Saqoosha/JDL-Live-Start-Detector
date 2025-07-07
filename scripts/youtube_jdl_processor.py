#!/usr/bin/env python3
"""
YouTube JDL Processor - Complete YouTube download and pattern detection pipeline

Downloads audio from YouTube URLs and automatically runs COUNT→GO pattern detection
to generate CSV and Markdown files with race start timing data.

Author: Claude Code
Date: 2025
"""

import argparse
import os
import sys
import subprocess
import re
import time
import signal
from pathlib import Path
from typing import Optional, Tuple, List, Dict

# Global variables for process management
download_process = None
detection_running = False

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    global download_process, detection_running
    print("\n🛑 Interrupt received. Cleaning up...")
    
    if download_process and download_process.poll() is None:
        print("   Terminating download process...")
        download_process.terminate()
        try:
            download_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            download_process.kill()
    
    if detection_running:
        print("   Detection interrupted (results may be incomplete)")
    
    print("   Cleanup completed.")
    sys.exit(1)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem compatibility"""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'[\s]+', ' ', filename)
    filename = filename.strip()
    
    if len(filename) > 200:
        filename = filename[:200].rsplit(' ', 1)[0]
    
    return filename

def get_video_info(url: str) -> Tuple[str, str]:
    """Get video title and ID from YouTube URL"""
    try:
        cmd = ['yt-dlp', '--get-title', '--get-id', url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        
        if len(lines) >= 2:
            title = lines[0]
            video_id = lines[1]
            return title, video_id
        else:
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

def download_youtube_audio(url: str, output_dir: str = ".") -> Optional[str]:
    """Download audio from YouTube URL in M4A format"""
    global download_process
    
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
    
    # Check if file already exists
    expected_file = os.path.join(output_dir, f"{sanitized_title} [{video_id}].m4a")
    if os.path.exists(expected_file):
        file_size = os.path.getsize(expected_file)
        size_mb = file_size / (1024 * 1024)
        print(f'✅ File already exists: {expected_file} ({size_mb:.1f} MB)')
        return expected_file
    
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
        '--audio-quality', '0',
        '--output', output_path,
        '--no-playlist',
        url
    ]
    
    try:
        print('⬇️ Starting download...')
        download_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Monitor download progress
        for line in iter(download_process.stdout.readline, ''):
            if line:
                line = line.strip()
                if '[download]' in line and '%' in line:
                    # Extract progress percentage
                    if 'ETA' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part.endswith('%'):
                                percentage = part.rstrip('%')
                                try:
                                    pct = float(percentage)
                                    if pct % 10 == 0 or pct > 95:  # Show every 10% or final stages
                                        print(f'   Progress: {percentage}%')
                                except ValueError:
                                    pass
        
        download_process.wait()
        
        if download_process.returncode == 0:
            if os.path.exists(expected_file):
                file_size = os.path.getsize(expected_file)
                size_mb = file_size / (1024 * 1024)
                print(f'✅ Download successful: {expected_file} ({size_mb:.1f} MB)')
                return expected_file
            else:
                print(f'❌ Downloaded file not found at expected location: {expected_file}')
                return None
        else:
            print(f'❌ Download failed with return code: {download_process.returncode}')
            return None
            
    except subprocess.CalledProcessError as e:
        print(f'❌ Download failed: {e}')
        return None
    except FileNotFoundError:
        print('❌ yt-dlp not found. Please install with: pip install yt-dlp')
        return None
    finally:
        download_process = None

def run_pattern_detection(audio_file: str, output_base_name: str = None, video_id: str = None) -> Optional[List[Dict]]:
    """Run COUNT→GO pattern detection on audio file"""
    global detection_running
    
    print()
    print('🎯 Running COUNT→GO Pattern Detection...')
    print('-' * 50)
    
    detection_running = True
    
    try:
        from pattern_enhanced_detector import PatternEnhancedDetector, PatternConfig
        
        # Use optimized configuration
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
        
        print(f'🎵 Processing: {audio_file}')
        start_time = time.time()
        
        patterns = detector.detect_patterns(audio_file)
        
        processing_time = time.time() - start_time
        
        if patterns:
            print(f'✅ Found {len(patterns)} COUNT→GO patterns!')
            print(f'⏱️  Processing time: {processing_time:.1f} seconds')
            
            # Generate results filename based on input
            if output_base_name is None:
                base_name = Path(audio_file).stem
            else:
                base_name = output_base_name
                
            files = detector.save_results(patterns, base_name, video_id)
            
            print(f'\n💾 Results saved:')
            for file_type, filename in files.items():
                print(f'   {file_type.upper()}: {filename}')
            
            # Print summary
            print(f'\n📋 PATTERN SUMMARY:')
            for pattern in patterns:
                start_sec = pattern['start_time_ms'] / 1000
                minutes = int(start_sec // 60)
                seconds = start_sec % 60
                gap = pattern['gap_seconds']
                url_seconds = int(start_sec)
                print(f'   {pattern["sequence_number"]:2d}. {minutes:02d}:{seconds:06.3f} (Gap: {gap:.1f}s) → t={url_seconds}')
            
            return patterns
        else:
            print(f'❌ No COUNT→GO patterns detected')
            print(f'⏱️  Processing time: {processing_time:.1f} seconds')
            return None
            
    except ImportError as e:
        print(f'⚠️ Pattern detection not available: {e}')
        print('   Make sure you have all dependencies installed: uv sync')
        return None
    except Exception as e:
        print(f'❌ Pattern detection failed: {e}')
        return None
    finally:
        detection_running = False

def process_youtube_url(url: str, output_dir: str = ".", skip_download: bool = False) -> bool:
    """Complete processing pipeline: download + pattern detection"""
    
    print(f'🚀 YouTube JDL Processor Pipeline')
    print('=' * 60)
    print(f'🔗 URL: {url}')
    print(f'📂 Output: {output_dir}')
    print('=' * 60)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Download audio (if not skipped)
    audio_file = None
    if skip_download:
        # Try to find existing audio file
        title, video_id = get_video_info(url)
        sanitized_title = sanitize_filename(title)
        potential_file = os.path.join(output_dir, f"{sanitized_title} [{video_id}].m4a")
        if os.path.exists(potential_file):
            audio_file = potential_file
            print(f'📁 Using existing file: {audio_file}')
        else:
            print(f'❌ Existing file not found: {potential_file}')
            return False
    else:
        audio_file = download_youtube_audio(url, output_dir)
    
    if not audio_file:
        print('❌ Audio download failed')
        return False
    
    # Step 2: Pattern detection
    # Generate clean base name for results
    title, video_id = get_video_info(url)
    sanitized_title = sanitize_filename(title)
    output_base_name = f"{sanitized_title}_{video_id}"
    
    patterns = run_pattern_detection(audio_file, output_base_name, video_id)
    
    if patterns:
        print('\n🎉 Pipeline completed successfully!')
        print(f'📊 Total patterns detected: {len(patterns)}')
        print(f'📂 Audio file: {audio_file}')
        print(f'📄 Results saved in: results/{output_base_name}.*')
        return True
    else:
        print('\n⚠️ Pipeline completed but no patterns detected')
        print(f'📂 Audio file: {audio_file}')
        return False

def main():
    """Main function for command line interface"""
    parser = argparse.ArgumentParser(
        description='Complete YouTube JDL processing pipeline: download + pattern detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process YouTube URL (download + detect patterns)
  python youtube_jdl_processor.py "https://www.youtube.com/watch?v=MSoaNUMg2yo"
  
  # Process with custom output directory
  python youtube_jdl_processor.py "https://www.youtube.com/watch?v=MSoaNUMg2yo" --output downloads/
  
  # Skip download and process existing file
  python youtube_jdl_processor.py "https://www.youtube.com/watch?v=MSoaNUMg2yo" --skip-download
        """
    )
    
    parser.add_argument(
        'url',
        help='YouTube URL to process'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='.',
        help='Output directory for downloaded audio (default: current directory)'
    )
    
    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Skip download and process existing audio file'
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not ('youtube.com' in args.url or 'youtu.be' in args.url):
        print('❌ Invalid YouTube URL')
        sys.exit(1)
    
    # Process the URL
    success = process_youtube_url(
        args.url,
        args.output,
        args.skip_download
    )
    
    if success:
        print('\n✅ All processing completed successfully!')
        sys.exit(0)
    else:
        print('\n❌ Processing failed or incomplete')
        sys.exit(1)

if __name__ == "__main__":
    main()