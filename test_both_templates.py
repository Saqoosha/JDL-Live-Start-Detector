import os
import sys
from scripts.short_template_beep_detector import ShortTemplateBeepDetector

def test_both_templates():
    """Test both go.mp3 and go_01.wav templates on all test samples"""
    
    # Test files and their known correct answers (in milliseconds)
    test_files = {
        "test.wav": 15998,
        "test2.wav": 22000,
        "test3.wav": 22389,
        "test4.wav": 17255,
        "test5.wav": 248282,  # 4:08.282
        "test6.wav": [25970, 256490]  # Two beeps: 25970ms, 4:16.490
    }
    
    templates = ["templates/go.mp3", "templates/go_01.wav"]
    
    print("=" * 80)
    print("🎵 TEMPLATE COMPARISON TEST - BOTH go.mp3 vs go_01.wav")
    print("=" * 80)
    print("💡 Strategy: First 0.5 seconds of each template")
    print("🎯 Goal: Compare performance on all test samples")
    print("=" * 80)
    
    results = {}
    
    for template in templates:
        template_name = os.path.basename(template)
        print(f"\n🔍 TESTING TEMPLATE: {template_name}")
        print("-" * 60)
        
        results[template_name] = {}
        
        if not os.path.exists(template):
            print(f"❌ Template {template} not found!")
            continue
        
        for test_file, correct_answer in test_files.items():
            if not os.path.exists(f"tests/{test_file}"):
                print(f"⚠️  Skipping {test_file} - file not found")
                continue
            
            print(f"\n  📁 Testing {test_file}...")
            
            try:
                # Create detector with current template
                detector = ShortTemplateBeepDetector(template, f"tests/{test_file}", template_duration=0.5)
                
                # Process audio and detect beeps
                beep_times = detector.process_audio()
                
                if beep_times:
                    detected_time = beep_times[0]  # Take the best detection
                    
                    # Handle test6 which has two beeps
                    if isinstance(correct_answer, list):
                        # Find closest match for test6
                        errors = [abs(detected_time - ans) for ans in correct_answer]
                        min_error = min(errors)
                        closest_answer = correct_answer[errors.index(min_error)]
                        error = min_error
                        print(f"     Detected: {detected_time:.2f} ms")
                        print(f"     Closest correct: {closest_answer} ms")
                        print(f"     Error: {error:.2f} ms")
                    else:
                        error = abs(detected_time - correct_answer)
                        print(f"     Detected: {detected_time:.2f} ms")
                        print(f"     Correct: {correct_answer} ms")
                        print(f"     Error: {error:.2f} ms")
                    
                    # Determine status
                    if error < 50:
                        status = 'EXCELLENT'
                    elif error < 100:
                        status = 'VERY_GOOD'
                    elif error < 200:
                        status = 'GOOD'
                    elif error < 300:
                        status = 'TARGET_MET'
                    else:
                        status = 'FAILED'
                    
                    print(f"     Status: {status}")
                    print(f"     Total detections: {len(beep_times)}")
                    
                    results[template_name][test_file] = {
                        'detected': detected_time,
                        'error': error,
                        'status': status,
                        'total_detections': len(beep_times)
                    }
                    
                else:
                    print(f"     ❌ No beeps detected")
                    results[template_name][test_file] = {
                        'detected': 'NO_DETECTION',
                        'error': float('inf'),
                        'status': 'FAILED',
                        'total_detections': 0
                    }
                    
            except Exception as e:
                print(f"     ❌ Error: {e}")
                results[template_name][test_file] = {
                    'detected': 'ERROR',
                    'error': float('inf'),
                    'status': 'ERROR',
                    'total_detections': 0
                }
    
    # Generate comparison report
    print(f"\n" + "=" * 80)
    print("📊 TEMPLATE COMPARISON RESULTS")
    print("=" * 80)
    
    # Summary table
    print(f"\n📋 DETAILED COMPARISON TABLE")
    print("-" * 90)
    print(f"{'File':<12} {'go.mp3 Error':<15} {'go_01.wav Error':<17} {'Winner':<10} {'Difference':<12}")
    print("-" * 90)
    
    go_mp3_wins = 0
    go_01_wav_wins = 0
    ties = 0
    
    for test_file in test_files.keys():
        if test_file in results.get('go.mp3', {}) and test_file in results.get('go_01.wav', {}):
            go_mp3_error = results['go.mp3'][test_file]['error']
            go_01_error = results['go_01.wav'][test_file]['error']
            
            # Format errors
            go_mp3_str = f"{go_mp3_error:.2f} ms" if go_mp3_error != float('inf') else "FAILED"
            go_01_str = f"{go_01_error:.2f} ms" if go_01_error != float('inf') else "FAILED"
            
            # Determine winner
            if go_mp3_error < go_01_error:
                winner = "go.mp3"
                go_mp3_wins += 1
                diff = go_01_error - go_mp3_error
                diff_str = f"-{diff:.2f} ms" if diff != float('inf') else "N/A"
            elif go_01_error < go_mp3_error:
                winner = "go_01.wav"
                go_01_wav_wins += 1
                diff = go_mp3_error - go_01_error
                diff_str = f"-{diff:.2f} ms" if diff != float('inf') else "N/A"
            else:
                winner = "TIE"
                ties += 1
                diff_str = "0.00 ms"
            
            print(f"{test_file:<12} {go_mp3_str:<15} {go_01_str:<17} {winner:<10} {diff_str:<12}")
    
    # Overall winner
    print(f"\n🏆 OVERALL COMPARISON:")
    print(f"   go.mp3 wins: {go_mp3_wins}")
    print(f"   go_01.wav wins: {go_01_wav_wins}")
    print(f"   Ties: {ties}")
    
    if go_mp3_wins > go_01_wav_wins:
        print(f"   🥇 Winner: go.mp3 ({go_mp3_wins}/{len(test_files)} samples)")
    elif go_01_wav_wins > go_mp3_wins:
        print(f"   🥇 Winner: go_01.wav ({go_01_wav_wins}/{len(test_files)} samples)")
    else:
        print(f"   🤝 Result: TIE")
    
    # Calculate average errors
    for template_name in ['go.mp3', 'go_01.wav']:
        if template_name in results:
            valid_errors = [data['error'] for data in results[template_name].values() 
                          if data['error'] != float('inf')]
            if valid_errors:
                avg_error = sum(valid_errors) / len(valid_errors)
                print(f"   📊 {template_name} average error: {avg_error:.2f} ms")
    
    # Save results
    with open("template_comparison_results.txt", "w") as f:
        f.write("TEMPLATE COMPARISON RESULTS\n")
        f.write("=" * 50 + "\n\n")
        f.write("Templates tested: go.mp3 vs go_01.wav\n")
        f.write("Strategy: First 0.5 seconds of each template\n\n")
        
        for template_name, template_results in results.items():
            f.write(f"\n{template_name} Results:\n")
            f.write("-" * 30 + "\n")
            for test_file, data in template_results.items():
                f.write(f"{test_file}: {data['error']:.2f} ms ({data['status']})\n")
        
        f.write(f"\nSummary:\n")
        f.write(f"go.mp3 wins: {go_mp3_wins}\n")
        f.write(f"go_01.wav wins: {go_01_wav_wins}\n")
        f.write(f"Ties: {ties}\n")
    
    print(f"\n💾 Results saved to: template_comparison_results.txt")
    print(f"✅ Template comparison complete!")

if __name__ == "__main__":
    test_both_templates()