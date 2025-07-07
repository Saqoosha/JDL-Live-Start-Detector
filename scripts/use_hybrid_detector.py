#!/usr/bin/env python3
"""
Practical usage examples for the Hybrid Configurable Detector
Demonstrates how to use the system for different audio scenarios
"""

import sys
import argparse
from pathlib import Path
sys.path.append('scripts')

from hybrid_configurable_detector import HybridConfigurableDetector, HybridConfig

def get_preset_configs():
    """Predefined configurations for common scenarios"""
    
    return {
        "original": HybridConfig(
            correlation_threshold=0.8,
            spectral_threshold=0.6,
            min_distance_seconds=0.5,
            template_duration=0.5,
            duplicate_window_ms=100.0
        ),
        
        "conservative": HybridConfig(
            correlation_threshold=0.85,  # Higher thresholds
            spectral_threshold=0.65,
            min_distance_seconds=1.0,    # Longer gaps required
            template_duration=0.5,
            max_detections=15            # Limit results
        ),
        
        "sensitive": HybridConfig(
            correlation_threshold=0.7,   # Lower thresholds
            spectral_threshold=0.5,
            min_distance_seconds=0.3,    # Closer spacing allowed
            template_duration=0.5,
            max_detections=25
        ),
        
        "aggressive": HybridConfig(
            correlation_threshold=0.6,   # Much lower
            spectral_threshold=0.4,
            min_distance_seconds=0.2,
            template_duration=0.5,
            max_detections=30
        ),
        
        "studio_quality": HybridConfig(
            correlation_threshold=0.85,  # High quality audio
            spectral_threshold=0.7,      # Strong spectral matching
            min_distance_seconds=0.8,
            template_duration=0.4,       # Shorter template for precision
            freq_range_hz=100.0          # Tighter frequency range
        ),
        
        "noisy_live": HybridConfig(
            correlation_threshold=0.65,  # Background noise tolerance
            spectral_threshold=0.45,     # Relaxed spectral matching
            min_distance_seconds=0.4,
            template_duration=0.6,       # Longer template for robustness
            freq_range_hz=150.0          # Wider frequency range
        )
    }

def detect_beeps(audio_file, template_file, config_name="original", custom_config=None):
    """
    Detect beeps with specified configuration
    
    Args:
        audio_file: Path to audio file
        template_file: Path to template beep file
        config_name: Preset configuration name
        custom_config: Custom HybridConfig object (overrides config_name)
    
    Returns:
        List of beep times in milliseconds
    """
    
    # Validate files
    if not Path(audio_file).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not Path(template_file).exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")
    
    # Get configuration
    if custom_config:
        config = custom_config
        config_desc = "Custom"
    else:
        presets = get_preset_configs()
        if config_name not in presets:
            raise ValueError(f"Unknown preset: {config_name}. Available: {list(presets.keys())}")
        config = presets[config_name]
        config_desc = config_name.title()
    
    print(f"🎛️  HYBRID DETECTOR - {config_desc} Configuration")
    print("=" * 60)
    print(f"Audio: {audio_file}")
    print(f"Template: {template_file}")
    print(f"Correlation ≥ {config.correlation_threshold:.1%}")
    print(f"Spectral ≥ {config.spectral_threshold:.1%}")
    print(f"Min distance: {config.min_distance_seconds}s")
    if config.max_detections:
        print(f"Max results: {config.max_detections}")
    print("=" * 60)
    
    # Run detection
    detector = HybridConfigurableDetector(
        template_path=template_file,
        target_path=audio_file,
        config=config
    )
    
    beeps = detector.process_audio()
    
    return beeps

def save_results(beeps, output_file, audio_file, config_name):
    """Save detection results to CSV"""
    
    with open(output_file, 'w') as f:
        f.write(f"# Beep Detection Results\n")
        f.write(f"# Audio: {audio_file}\n")
        f.write(f"# Configuration: {config_name}\n")
        f.write(f"# Total beeps: {len(beeps)}\n")
        f.write("Beep_Number,Time_MS,Time_Seconds,Time_MM_SS,Notes\n")
        
        for i, time_ms in enumerate(beeps):
            time_seconds = int(time_ms / 1000)
            mins = time_seconds // 60
            secs = time_seconds % 60
            time_format = f"{mins:02d}:{secs:02d}"
            
            f.write(f"{i+1},{time_ms:.2f},{time_seconds},{time_format},Hybrid-{config_name}\n")
    
    print(f"💾 Results saved to: {output_file}")

def main():
    """Command-line interface"""
    
    parser = argparse.ArgumentParser(description="Hybrid Configurable Beep Detector")
    parser.add_argument("audio_file", help="Audio file to analyze")
    parser.add_argument("--template", default="templates/go.mp3", help="Template beep file")
    parser.add_argument("--config", default="original", 
                       choices=list(get_preset_configs().keys()),
                       help="Preset configuration")
    parser.add_argument("--output", help="Output CSV file (auto-generated if not specified)")
    
    # Custom configuration options
    parser.add_argument("--correlation", type=float, help="Custom correlation threshold (0.0-1.0)")
    parser.add_argument("--spectral", type=float, help="Custom spectral threshold (0.0-1.0)")
    parser.add_argument("--min-distance", type=float, help="Minimum distance between beeps (seconds)")
    parser.add_argument("--max-results", type=int, help="Maximum number of results")
    
    args = parser.parse_args()
    
    # Create custom config if parameters provided
    custom_config = None
    if any([args.correlation, args.spectral, args.min_distance, args.max_results]):
        base_config = get_preset_configs()[args.config]
        custom_config = HybridConfig(
            correlation_threshold=args.correlation or base_config.correlation_threshold,
            spectral_threshold=args.spectral or base_config.spectral_threshold,
            min_distance_seconds=args.min_distance or base_config.min_distance_seconds,
            max_detections=args.max_results or base_config.max_detections,
            template_duration=base_config.template_duration,
            duplicate_window_ms=base_config.duplicate_window_ms,
            freq_filter_enabled=base_config.freq_filter_enabled,
            freq_range_hz=base_config.freq_range_hz
        )
    
    # Generate output filename if not specified
    if args.output:
        output_file = args.output
    else:
        audio_path = Path(args.audio_file)
        config_suffix = "custom" if custom_config else args.config
        output_file = f"{audio_path.stem}_beeps_{config_suffix}.csv"
    
    try:
        # Run detection
        beeps = detect_beeps(
            audio_file=args.audio_file,
            template_file=args.template,
            config_name=args.config,
            custom_config=custom_config
        )
        
        if beeps:
            # Save results
            save_results(beeps, output_file, args.audio_file, 
                        "custom" if custom_config else args.config)
            
            print(f"\n✅ SUCCESS: Found {len(beeps)} beeps")
            print(f"📊 Configuration: {args.config}" + (" (customized)" if custom_config else ""))
            
            # Show sample results
            print(f"\n📍 Sample detections:")
            for i, time_ms in enumerate(beeps[:5]):
                mins = int(time_ms / 60000)
                secs = (time_ms % 60000) / 1000
                print(f"   {i+1}. {mins:2d}:{secs:06.3f}")
            if len(beeps) > 5:
                print(f"   ... and {len(beeps)-5} more")
                
        else:
            print("❌ No beeps detected")
            print("💡 Try a more sensitive configuration:")
            print("   --config sensitive")
            print("   --config aggressive")
            print("   --correlation 0.6 --spectral 0.4")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def demo_different_scenarios():
    """Demonstrate different usage scenarios"""
    
    print("🎭 HYBRID DETECTOR USAGE SCENARIOS")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "High-Quality Studio Recording",
            "config": "studio_quality",
            "description": "Clean audio, need precise detection with minimal false positives"
        },
        {
            "name": "Noisy Live Stream",
            "config": "noisy_live", 
            "description": "Background noise, need robust detection"
        },
        {
            "name": "Conservative Detection",
            "config": "conservative",
            "description": "Only most confident detections, avoid false positives"
        },
        {
            "name": "Aggressive Detection",
            "config": "aggressive",
            "description": "Find everything possible, some false positives OK"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}")
        print(f"   Config: {scenario['config']}")
        print(f"   Use case: {scenario['description']}")
        print(f"   Command: python use_hybrid_detector.py audio.wav --config {scenario['config']}")
    
    print(f"\n🔧 Custom Configuration Examples:")
    print("   # Extra sensitive detection")
    print("   python use_hybrid_detector.py audio.wav --correlation 0.6 --spectral 0.4")
    print()
    print("   # Very conservative, only top 10 results")
    print("   python use_hybrid_detector.py audio.wav --correlation 0.9 --max-results 10")
    print()
    print("   # Allow very close beeps")
    print("   python use_hybrid_detector.py audio.wav --min-distance 0.1")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        demo_different_scenarios()
    else:
        main()