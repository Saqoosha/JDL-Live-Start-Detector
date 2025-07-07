# JDL Live Start Detector

🎬 **Japan Drone League 2025 Beep Detection System**

Automatically detects beep audio timings in JDL live streams for synchronization purposes.

## 🎯 Project Overview

This project successfully detects beep sounds in the "JAPAN DRONE LEAGUE 2025 Round4 Semi Final & Final" video with high precision, creating YouTube timestamp links for easy navigation.

## 📁 Project Structure

```
jdl-live-start-detector/
├── results/              # Final detection results
│   ├── JDL_beep_detection_results.txt
│   ├── JDL_beep_timings.csv
│   └── JDL_YouTube_Links.*
├── scripts/              # Production scripts
│   ├── short_template_beep_detector.py  # Main detector
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

2. **Run Detection on JDL Video:**
   ```bash
   # With uv (recommended - automatically uses .venv)
   uv run python scripts/jdl_beep_detector.py
   
   # Or with activated environment
   python scripts/jdl_beep_detector.py
   ```

3. **Generate YouTube Links:**
   ```bash
   # With uv (recommended)
   uv run python scripts/create_youtube_links.py
   
   # Or with activated environment  
   python scripts/create_youtube_links.py
   ```

## 🎵 Detection Results

**Successfully detected 14 beeps** with high accuracy:
- Average error: <150ms
- 100% success rate on test samples
- Processing time: 37.8 seconds for 135-minute video

## 🔧 Technical Specifications

- **Algorithm**: Short Template Matching (first 0.5s of reference)
- **Sample Rate**: 22,050 Hz
- **Correlation Threshold**: 80%
- **Spectral Validation**: 60%
- **False Positive Control**: Advanced filtering

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

```python
from scripts.short_template_beep_detector import ShortTemplateBeepDetector

# Detect beeps with go.mp3 template (recommended for long samples)
detector = ShortTemplateBeepDetector("templates/go.mp3", "your_audio.wav")
beep_times = detector.process_audio()
print(f"Found {len(beep_times)} beeps at: {beep_times}")

# Alternative: Use go_01.wav template (equivalent performance)
detector = ShortTemplateBeepDetector("templates/go_01.wav", "your_audio.wav")
beep_times = detector.process_audio()
print(f"Found {len(beep_times)} beeps at: {beep_times}")

# Compare both templates
# uv run python test_both_templates.py
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

1. **Basic Detector** - Initial cross-correlation approach
2. **Master Detector** - Multi-template with onset detection  
3. **Ultimate Detector** - Bias correction and refinement
4. **World-Class Detector** - 2024 state-of-the-art (overcomplicated)
5. **Short Template Detector** - Simplified, optimized (WINNER!)

## 🏆 Key Achievements

- ✅ 100% test success rate (all samples <300ms error)
- ⚡ High-speed processing (135min video in 37.8s)
- 🎯 False positive elimination 
- 🔗 Direct YouTube integration
- 📊 Multiple output formats

## 👥 Contributors

- **Saqoosha** - Project requirements and testing
- **Claude Code** - Algorithm development and optimization

---
*Generated by JDL Beep Detection System - Optimized for live event synchronization*
