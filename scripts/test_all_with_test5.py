import os
import sys
from short_template_beep_detector import ShortTemplateBeepDetector

def test_all_including_test5():
    """Test the improved short template beep detector on all samples including test5"""
    
    reference_beep = "go.mp3"
    test_files = ["test.wav", "test2.wav", "test3.wav", "test4.wav", "test5.wav"]
    
    # Known correct answers (in milliseconds)
    correct_answers = {
        "test.wav": 15998,
        "test2.wav": 22000,
        "test3.wav": 22389,
        "test4.wav": 17255,
        "test5.wav": 248282  # 4:08.282
    }
    
    if not os.path.exists(reference_beep):
        print(f"Error: Reference beep file '{reference_beep}' not found!")
        return
    
    results = []
    
    print("=" * 80)
    print("🎵 IMPROVED SHORT TEMPLATE BEEP DETECTOR - ALL SAMPLES INCLUDING TEST5")
    print("=" * 80)
    print("💡 Strategy: Use only the first 0.5 seconds of go.mp3 as template")
    print("🔧 Improvement: Higher thresholds to reduce false positives")
    print("🎯 Focus on onset portion for more precise timing detection")
    print("=" * 80)
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"Skipping {test_file} - file not found")
            continue
        
        print(f"\n🔍 Testing {test_file}...")
        print("-" * 60)
        
        try:
            # Create short template detector
            detector = ShortTemplateBeepDetector(reference_beep, test_file, template_duration=0.5)
            
            # Process audio and detect beeps
            beep_times = detector.process_audio()
            
            if beep_times:
                detected_time = beep_times[0]  # Take the best detection
                correct_time = correct_answers[test_file]
                error = abs(detected_time - correct_time)
                error_percentage = (error / correct_time) * 100
                
                # Determine status based on error
                if error < 50:
                    status = 'EXCELLENT'
                    emoji = '🏆'
                elif error < 100:
                    status = 'VERY_GOOD'
                    emoji = '🥇'
                elif error < 200:
                    status = 'GOOD'
                    emoji = '✅'
                elif error < 300:
                    status = 'TARGET_MET'
                    emoji = '✅'
                else:
                    status = 'NEEDS_WORK'
                    emoji = '⚠️'
                
                results.append({
                    'file': test_file,
                    'detected': detected_time,
                    'correct': correct_time,
                    'error_ms': error,
                    'error_percent': error_percentage,
                    'status': status,
                    'total_detections': len(beep_times)
                })
                
                print(f"{emoji} Detected: {detected_time:.2f} ms")
                print(f"📍 Correct:  {correct_time:.2f} ms")
                print(f"📊 Error:    {error:.2f} ms ({error_percentage:.3f}%)")
                print(f"🎯 Status:   {status}")
                print(f"🔢 Total detections: {len(beep_times)}")
                
                if error < 300:
                    print(f"🎉 SUCCESS: Achieved <300ms target!")
                else:
                    print(f"❌ FAILED: Exceeded 300ms target")
                    
            else:
                results.append({
                    'file': test_file,
                    'detected': 'NO_DETECTION',
                    'correct': correct_answers[test_file],
                    'error_ms': float('inf'),
                    'error_percent': float('inf'),
                    'status': 'FAILED',
                    'total_detections': 0
                })
                
                print(f"❌ No beeps detected")
                print(f"🎯 Status: FAILED")
            
        except Exception as e:
            print(f"❌ Error processing {test_file}: {e}")
            results.append({
                'file': test_file,
                'detected': 'ERROR',
                'correct': correct_answers[test_file],
                'error_ms': float('inf'),
                'error_percent': float('inf'),
                'status': 'ERROR',
                'total_detections': 0
            })
    
    # Calculate metrics
    successful_results = [r for r in results if isinstance(r['error_ms'], (int, float)) and r['error_ms'] < float('inf')]
    
    excellent_count = len([r for r in successful_results if r['error_ms'] < 50])
    very_good_count = len([r for r in successful_results if r['error_ms'] < 100])
    good_count = len([r for r in successful_results if r['error_ms'] < 200])
    target_met_count = len([r for r in successful_results if r['error_ms'] < 300])
    failed_count = len([r for r in results if r['status'] in ['FAILED', 'ERROR']])
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE PERFORMANCE SUMMARY (INCLUDING TEST5)")
    print("=" * 80)
    
    print(f"🏆 Excellent (< 50ms):      {excellent_count}/{len(test_files)} ({excellent_count/len(test_files)*100:.1f}%)")
    print(f"🥇 Very good (< 100ms):     {very_good_count}/{len(test_files)} ({very_good_count/len(test_files)*100:.1f}%)")
    print(f"✅ Good (< 200ms):          {good_count}/{len(test_files)} ({good_count/len(test_files)*100:.1f}%)")
    print(f"✅ Target met (< 300ms):    {target_met_count}/{len(test_files)} ({target_met_count/len(test_files)*100:.1f}%)")
    print(f"⚠️  Needs work (≥ 300ms):   {len(test_files)-target_met_count-failed_count}/{len(test_files)}")
    print(f"❌ Failed/Error:           {failed_count}/{len(test_files)}")
    
    if successful_results:
        errors = [r['error_ms'] for r in successful_results]
        avg_error = sum(errors) / len(errors)
        max_error = max(errors)
        min_error = min(errors)
        
        print(f"\n📊 ERROR STATISTICS:")
        print(f"   Average error: {avg_error:.2f} ms")
        print(f"   Maximum error: {max_error:.2f} ms")
        print(f"   Minimum error: {min_error:.2f} ms")
    
    # Detailed results table
    print(f"\n📋 DETAILED RESULTS TABLE")
    print("-" * 80)
    print(f"{'File':<12} {'Detected':<12} {'Correct':<10} {'Error(ms)':<10} {'Error%':<8} {'Detections':<11} {'Status':<12}")
    print("-" * 80)
    
    for result in results:
        detected_str = f"{result['detected']:.2f}" if isinstance(result['detected'], (int, float)) else str(result['detected'])
        error_str = f"{result['error_ms']:.2f}" if result['error_ms'] != float('inf') else "∞"
        error_pct_str = f"{result['error_percent']:.3f}%" if result['error_percent'] != float('inf') else "∞"
        
        print(f"{result['file']:<12} {detected_str:<12} {result['correct']:<10} {error_str:<10} {error_pct_str:<8} {result['total_detections']:<11} {result['status']:<12}")
    
    # Goal achievement
    print(f"\n🎯 GOAL ACHIEVEMENT:")
    if target_met_count == len(test_files):
        print(f"🏆 PERFECT SCORE! All {len(test_files)} samples achieved <300ms target!")
        if excellent_count >= len(test_files) * 0.6:
            print(f"🌟 OUTSTANDING! {excellent_count}/{len(test_files)} achieved <50ms precision!")
    elif target_met_count >= len(test_files) * 0.8:
        print(f"✅ EXCELLENT! {target_met_count}/{len(test_files)} samples achieved target (≥80%)")
    else:
        print(f"⚠️  NEEDS IMPROVEMENT: {target_met_count}/{len(test_files)} samples achieved target (<80%)")
    
    # Save results
    with open("comprehensive_test_results.txt", "w") as f:
        f.write("Comprehensive Short Template Beep Detector - Test Results\\n")
        f.write("=" * 60 + "\\n\\n")
        f.write(f"Template strategy: First 0.5 seconds of go.mp3\\n")
        f.write(f"Improvements: Higher thresholds (70% correlation, 50% spectral)\\n")
        f.write(f"Target: All errors < 300ms\\n")
        f.write(f"Tests run: {len(test_files)}\\n")
        f.write(f"Target achieved: {target_met_count}/{len(test_files)} ({target_met_count/len(test_files)*100:.1f}%)\\n\\n")
        
        for result in results:
            f.write(f"File: {result['file']}\\n")
            f.write(f"Detected: {result['detected']}\\n")
            f.write(f"Correct: {result['correct']}\\n")
            f.write(f"Error: {result['error_ms']}\\n")
            f.write(f"Total detections: {result['total_detections']}\\n")
            f.write(f"Status: {result['status']}\\n")
            f.write("-" * 30 + "\\n")
    
    print(f"\\n💾 Results saved to comprehensive_test_results.txt")
    
    return results

if __name__ == "__main__":
    test_all_including_test5()