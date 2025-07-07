#!/usr/bin/env python3
"""
JDL Beep Detector - COUNT→GO Pattern Detection System

This is the production JDL beep detector that uses COUNT→GO temporal pattern
matching for race start detection in Japan Drone League live streams.

The system analyzes countdown audio followed by go signals to accurately
identify race start moments with minimal false positives.

Author: AI Assistant  
Version: 3.0
Date: 2025
"""

import os
import sys
import time
from typing import List, Dict

# Add scripts directory to path for imports
scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)

try:
    from pattern_enhanced_detector import detect_jdl_patterns_enhanced
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure pattern_enhanced_detector.py is in the scripts directory")
    sys.exit(1)

def detect_jdl_beeps() -> List[Dict]:
    """
    Detect race start patterns in JDL video using COUNT→GO temporal analysis
    
    Returns:
        List of detected race start patterns with timing information
    """
    
    # JDL video file (expected in project root)
    jdl_video = "JAPAN DRONE LEAGUE 2025 Round4 Semi Final & Final [Z7sjETGD-dg].m4a"
    
    # Verify video file exists
    if not os.path.exists(jdl_video):
        print(f"❌ Error: JDL video file '{jdl_video}' not found!")
        print("Please ensure the video file is in the current directory")
        return []
    
    # Verify template files exist
    templates = ["templates/count.mp3", "templates/go.mp3"]
    missing_templates = [t for t in templates if not os.path.exists(t)]
    
    if missing_templates:
        print(f"❌ Error: Missing template files: {missing_templates}")
        print("Please ensure template files are in the templates/ directory")
        return []
    
    print("=" * 80)
    print("🏁 JAPAN DRONE LEAGUE 2025 - RACE START DETECTION")
    print("=" * 80)
    print(f"🎵 Video: {jdl_video}")
    print("🚀 Method: COUNT→GO Temporal Pattern Matching")
    print("🎯 Goal: Detect race start sequences with high accuracy")
    print("⚙️  Templates: count.mp3 (countdown) + go.mp3 (start signal)")
    print("🔬 Technology: Dual-template temporal sequence analysis")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        print(f"\n🚀 Starting pattern detection...")
        print(f"⏱️  Processing large file - this may take several minutes...")
        print(f"🔍 Analyzing COUNT→GO temporal sequences...")
        
        # Run the enhanced pattern detection
        patterns = detect_jdl_patterns_enhanced()
        
        processing_time = time.time() - start_time
        
        if patterns:
            print(f"\n✅ Detection complete!")
            print(f"⚡ Performance: {processing_time:.1f}s processing time")
            print(f"🎯 Found {len(patterns)} race start patterns")
            
            # Calculate and display statistics
            _display_statistics(patterns)
            
            return patterns
            
        else:
            print(f"\n❌ No COUNT→GO patterns detected")
            print(f"⏱️  Processing time: {processing_time:.1f} seconds")
            print(f"\n🔧 TROUBLESHOOTING:")
            print(f"   - Verify video contains race start sequences")
            print(f"   - Check template files match expected beep types")
            print(f"   - Ensure audio quality is sufficient for detection")
            return []
            
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"\n❌ Error during detection: {e}")
        print(f"⏱️  Processing time: {processing_time:.1f} seconds")
        
        # Save error log for debugging
        _save_error_log(e)
        return []

def _display_statistics(patterns: List[Dict]) -> None:
    """Display detailed statistics about detected patterns"""
    
    if len(patterns) > 1:
        # Calculate race interval statistics
        intervals = []
        for i in range(1, len(patterns)):
            interval_ms = patterns[i]['start_time_ms'] - patterns[i-1]['start_time_ms']
            intervals.append(interval_ms)
        
        avg_interval = sum(intervals) / len(intervals)
        min_interval = min(intervals)
        max_interval = max(intervals)
        
        print(f"\n📊 RACE INTERVAL STATISTICS:")
        print(f"   Average race interval: {avg_interval/1000:.1f} seconds")
        print(f"   Minimum race interval: {min_interval/1000:.1f} seconds") 
        print(f"   Maximum race interval: {max_interval/1000:.1f} seconds")
        
        # Calculate COUNT→GO gap statistics
        gaps = [p['gap_seconds'] for p in patterns]
        avg_gap = sum(gaps) / len(gaps)
        min_gap = min(gaps)
        max_gap = max(gaps)
        
        print(f"\n⏱️  COUNT→GO TIMING ANALYSIS:")
        print(f"   Average gap: {avg_gap:.1f} seconds")
        print(f"   Gap range: {min_gap:.1f}s - {max_gap:.1f}s")
        print(f"   Gap consistency: {'Excellent' if max_gap - min_gap < 4 else 'Good' if max_gap - min_gap < 6 else 'Variable'}")

def _save_error_log(error: Exception) -> None:
    """Save error details to log file for debugging"""
    
    os.makedirs("results", exist_ok=True)
    
    with open("results/JDL_detection_error.log", 'w') as f:
        f.write(f"JDL Beep Detector Error Log\n")
        f.write(f"Time: {time.ctime()}\n")
        f.write(f"Error: {str(error)}\n\n")
        f.write("Traceback:\n")
        import traceback
        f.write(traceback.format_exc())
    
    print(f"💾 Error log saved to: results/JDL_detection_error.log")

def main():
    """Main function - simplified interface for production use"""
    
    print("JDL Race Start Detector v3.0")
    print("COUNT→GO Pattern Detection System")
    print()
    
    # Run detection
    patterns = detect_jdl_beeps()
    
    if patterns:
        print(f"\n🎉 SUCCESS! Detected {len(patterns)} race start sequences")
        print(f"📁 Results saved to results/ directory")
        print(f"🎬 Check JDL_pattern_enhanced_links.html for YouTube navigation")
    else:
        print(f"\n❌ No race start patterns detected")
        print(f"💡 Check troubleshooting suggestions above")
    
    return patterns

if __name__ == "__main__":
    main()