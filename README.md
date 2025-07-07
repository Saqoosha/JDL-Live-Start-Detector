# JDL Live Start Detector

🎬 **Japan Drone League 2025 Beep Detection System**

Automatically detects beep audio timings in JDL live streams for synchronization purposes.

**🆕 NEW**: Now includes a configurable hybrid detection system that eliminates hard-coding while maintaining proven performance.

## 🎯 Project Overview

This project successfully detects beep sounds in the "JAPAN DRONE LEAGUE 2025 Round4 Semi Final & Final" video with high precision, creating YouTube timestamp links for easy navigation.

The latest version features both the original proven system and a new configurable hybrid system that works with any audio file.

## 📁 Project Structure

```
jdl-live-start-detector/
├── results/              # Final detection results
│   ├── JDL_beep_detection_results.txt
│   ├── JDL_beep_timings.csv
│   └── JDL_YouTube_Links.*
├── scripts/              # Detection systems
│   ├── short_template_beep_detector.py  # Original proven system
│   ├── hybrid_configurable_detector.py  # NEW: Configurable system
│   ├── use_hybrid_detector.py           # NEW: Easy CLI interface
│   ├── jdl_beep_detector.py            # JDL video processor
│   ├── create_youtube_links.py         # Link generator
│   └── test_all_with_test5.py          # Comprehensive testing
├── tests/                # Test audio files
│   ├── test.wav, test2.wav, ... test6.wav
│   └── test*.pkf
├── templates/            # Audio templates
│   ├── go.mp3           # Primary template
│   └── go_01.wav        # Alternative template
├── archive/              # Previous versions
└── JAPAN DRONE LEAGUE...m4a  # Source video
```

## 🚀 Quick Start

1. **Setup Environment (2025 uv method):**
   ```bash
   # Modern approach: Create environment and install dependencies
   uv sync
   
   # Alternative: Step-by-step setup
   uv venv
   uv pip install -e .
   ```

2. **Detect Beeps (Multiple Options):**
   ```bash
   # Standard JDL detection (proven original system)
   uv run python scripts/jdl_beep_detector.py
   
   # Any audio file with original settings (NEW)
   uv run python scripts/use_hybrid_detector.py audio.wav --config original
   
   # Noisy live recording with BGM (NEW)
   uv run python scripts/use_hybrid_detector.py audio.wav --config noisy_live
   
   # Maximum sensitivity for difficult audio (NEW)
   uv run python scripts/use_hybrid_detector.py audio.wav --correlation 0.4 --spectral 0.15
   ```

3. **Generate YouTube Links:**
   ```bash
   # With uv (recommended)
   uv run python scripts/create_youtube_links.py
   ```

## 🎵 Detection Results

### Original System
**Successfully detected 14 beeps** with high accuracy:
- Average error: <150ms
- 100% success rate on test samples
- Processing time: 37.8 seconds for 135-minute video

### NEW: Hybrid Configurable System
**Maintains identical performance with flexibility**:
- **Original config**: 14 beeps ✅ (100% match with original)
- **Sensitive config**: 18 beeps (more detections)
- **Aggressive config**: 30+ beeps (maximum sensitivity)
- **Noisy live config**: 19 beeps (optimized for BGM interference)

## 🔧 Technical Specifications

### Core Algorithm
- **Method**: Short Template Matching (first 0.2-1.0s of reference, configurable)
- **Sample Rate**: 22,050 Hz (optimized for speed vs precision)
- **Frequency Analysis**: Adaptive FFT-based bandpass filtering
- **Refinement**: Parabolic interpolation for sub-sample precision

### Configurable Parameters (NEW)
- **Correlation Threshold**: 40%-90% (default 80%)
- **Spectral Validation**: 15%-80% (default 60%)
- **Minimum Distance**: 0.1-20 seconds (default 0.5s)
- **Template Duration**: 0.2-1.0 seconds (default 0.5s)
- **Frequency Range**: ±50-300Hz (adaptive, default ±120Hz)

## 📊 Performance Metrics

| Test Sample | Error (ms) | Status |
|-------------|------------|---------|
| test.wav    | 249.81     | ✅ Target Met |
| test2.wav   | 6.57       | 🏆 Excellent |
| test3.wav   | 199.16     | ✅ Good |
| test4.wav   | 187.74     | ✅ Good |
| test5.wav   | 81.96      | 🥇 Very Good |
| test6.wav   | 50.35, 218.85 | ✅ Multiple Beeps |

## 🎵 Template Performance Comparison

Both audio templates achieve excellent results with the short template strategy:

| Template | Average Error | Best Performance | Samples Won |
|----------|---------------|------------------|-------------|
| go.mp3 | 129.27 ms | Long samples (test5-6) | 3/6 |
| go_01.wav | 131.97 ms | Short samples (test1-3) | 3/6 |

**Key Findings:**
- **Equivalent Performance**: Only 2.7ms average difference
- **Template Flexibility**: Both achieve <300ms target on all samples  
- **Short Template Strategy**: First 0.5s approach works optimally for both
- **Production Ready**: Either template can be used based on preference

## 🎬 YouTube Integration

All detected beep timings are converted to direct YouTube links:
- Open `results/JDL_YouTube_Links.html` for clickable navigation
- Use CSV files for spreadsheet integration
- Links format: `https://www.youtube.com/live/Z7sjETGD-dg?t=<seconds>`

## 📝 Usage Examples

### Original System (Python API)
```python
from scripts.short_template_beep_detector import ShortTemplateBeepDetector

# Detect beeps with proven original system
detector = ShortTemplateBeepDetector("templates/go.mp3", "your_audio.wav")
beep_times = detector.process_audio()
print(f"Found {len(beep_times)} beeps at: {beep_times}")
```

### NEW: Hybrid Configurable System (Command Line)
```bash
# Use proven original settings
uv run python scripts/use_hybrid_detector.py audio.wav --config original

# High-quality studio recording
uv run python scripts/use_hybrid_detector.py audio.wav --config studio_quality

# Noisy live recording with BGM
uv run python scripts/use_hybrid_detector.py audio.wav --config noisy_live

# Custom ultra-sensitive settings
uv run python scripts/use_hybrid_detector.py audio.wav --correlation 0.4 --spectral 0.15

# Conservative detection (fewer false positives)
uv run python scripts/use_hybrid_detector.py audio.wav --config conservative
```

### NEW: Hybrid System (Python API)
```python
from scripts.hybrid_configurable_detector import HybridConfigurableDetector, HybridConfig

# Original proven settings
config = HybridConfig()  # Uses original defaults
detector = HybridConfigurableDetector("templates/go.mp3", "audio.wav", config)
beeps = detector.process_audio()

# Custom settings for noisy audio
noisy_config = HybridConfig(
    correlation_threshold=0.4,
    spectral_threshold=0.15,
    min_distance_seconds=2
)
detector = HybridConfigurableDetector("templates/go.mp3", "noisy_audio.wav", noisy_config)
beeps = detector.process_audio()
```

## 🧪 Testing

Run comprehensive tests on all samples:
```bash
# With uv (recommended)
uv run python scripts/test_all_with_test5.py

# Or with activated environment
python scripts/test_all_with_test5.py
```

## 📜 Development History

1. **Original System**: Short template detector with fixed parameters (proven, 14 beeps)
2. **Failed Attempt**: Complete algorithm rewrite (0 detections)
3. **Hybrid Success**: Parameter-only changes to proven algorithms (14-19+ beeps configurable)

**Key Insight**: Smart parameterization of proven algorithms often outperforms complete rewrites.

## 🏆 Key Achievements

### Original System
- ✅ 100% test success rate (all samples <300ms error)
- ⚡ High-speed processing (135min video in 37.8s)
- 🎯 False positive elimination
- 🔗 Direct YouTube integration

### NEW: Hybrid System
- ✅ 100% backward compatibility (identical results with original config)
- 🎛️ No hard-coding (works with any audio file)
- 📈 Scalable detection (14-30+ beeps depending on sensitivity)
- 🎵 Optimized for different audio conditions (studio, live, noisy)
- 🔧 Easy parameter tuning via command line

## 👥 Contributors

- **Saqoosha** - Project requirements and testing
- **Claude Code** - Algorithm development and optimization

---
*Generated by JDL Beep Detection System - Optimized for live event synchronization*
