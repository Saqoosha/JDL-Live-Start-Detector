# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a specialized audio processing system for detecting beep sounds in Japan Drone League (JDL) live streams. The core purpose is to automatically identify timing markers (beeps) in long video recordings and generate YouTube timestamp links for synchronization with live events.

**NEW**: Now includes a configurable hybrid detection system that eliminates hard-coding while maintaining proven performance.

## Environment Setup

```bash
# Modern approach: Create environment and install dependencies (2025 uv method)
uv sync

# Alternative: Step-by-step setup
uv venv
uv pip install -e .
```

## Detection Systems

### 1. Original Proven System
- **Algorithm**: `scripts/short_template_beep_detector.py` - The `ShortTemplateBeepDetector` class
- **Performance**: 14 beeps detected on JDL audio with <150ms average error
- **Use Case**: Reference implementation with proven results

### 2. Hybrid Configurable System (NEW)
- **Algorithm**: `scripts/hybrid_configurable_detector.py` - The `HybridConfigurableDetector` class
- **Innovation**: Uses EXACT algorithms from original system but makes parameters configurable
- **Advantage**: No hard-coding, works with any audio file, maintains 100% original performance
- **CLI Tool**: `scripts/use_hybrid_detector.py` - Easy command-line interface

### Template System
- **Primary Template**: `templates/go.mp3` - Main reference beep sound
- **Template Processing**: Adaptive trimming (0.2-1.0s configurable) with Hilbert envelope silence removal
- **Frequency Analysis**: Automatic FFT-based bandpass filter adaptation

## Common Commands

### Original System
```bash
# Run full JDL video detection (main production use)
uv run python scripts/jdl_beep_detector.py

# Generate YouTube timestamp links from detection results
uv run python scripts/create_youtube_links.py

# Run comprehensive validation on all test samples
uv run python scripts/test_all_with_test5.py

# Detect beeps in custom audio file (original system)
uv run python -c "
from scripts.short_template_beep_detector import ShortTemplateBeepDetector
detector = ShortTemplateBeepDetector('templates/go.mp3', 'your_audio.wav')
beeps = detector.process_audio()
print(f'Found {len(beeps)} beeps at: {beeps}')
"
```

### NEW: Hybrid Configurable System
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

# Maximum sensitivity (up to 25+ detections)
uv run python scripts/use_hybrid_detector.py audio.wav --correlation 0.4 --spectral 0.15 --min-distance 2
```

## Test Suite & Validation

### Test Audio Files
- `tests/test.wav` through `tests/test6.wav` - Validated reference samples with known correct timings
- **Ground Truth Values**: test.wav(15998ms), test2.wav(22000ms), test3.wav(22389ms), test4.wav(17255ms), test5.wav(248282ms), test6.wav(25970ms & 256490ms)
- **Success Criteria**: All detections must be within 300ms of ground truth (both templates achieve this)
- **Template Performance**: go.mp3 avg 129.27ms, go_01.wav avg 131.97ms (equivalent performance)

### Validation Architecture
Both systems maintain 100% success rate on test samples through:
1. **Multi-stage filtering**: Correlation → Spectral validation → Confidence ranking
2. **False positive elimination**: Configurable thresholds prevent spurious detections
3. **Sub-sample precision**: Parabolic interpolation for timing refinement

## Configuration Presets (Hybrid System)

- **original**: 80% correlation, 60% spectral (matches proven system exactly)
- **conservative**: 85% correlation, 65% spectral (fewer false positives)
- **sensitive**: 70% correlation, 50% spectral (more detections)
- **aggressive**: 60% correlation, 40% spectral (maximum sensitivity)
- **studio_quality**: 85% correlation, 70% spectral (clean audio)
- **noisy_live**: 65% correlation, 45% spectral (background noise tolerance)

## Development Evolution

1. **Original System**: Short template detector with fixed parameters (proven, 14 beeps)
2. **Failed Attempt**: Complete algorithm rewrite (0 detections)
3. **Hybrid Success**: Parameter-only changes to proven algorithms (14-19+ beeps configurable)

## Output Formats

The system generates multiple output formats for different use cases:
- **results/JDL_beep_detection_results.txt**: Human-readable detailed report
- **results/JDL_beep_timings.csv**: Spreadsheet-compatible data
- **results/JDL_YouTube_Links.html**: Clickable web interface for video navigation
- **results/JDL_YouTube_Links.csv**: Programmatic access to YouTube URLs

## Performance Characteristics

- **Processing Speed**: ~37.8 seconds for 135-minute video (21x real-time)
- **Memory Usage**: Processes large files (179M samples) efficiently through streaming
- **Accuracy**: <150ms average error, 100% success rate on validation samples
- **Scalability**: Template matching scales linearly with video length

## Audio Processing Pipeline

1. **Template Preparation**: Load reference beep → Trim to 0.5s → Remove silence → Resample to target rate
2. **Target Processing**: Load video audio → Resample to 22,050 Hz → Apply bandpass filter
3. **Detection**: Cross-correlation → Peak finding → Refinement → Validation
4. **Output**: Sort by confidence → Remove duplicates → Format results

## Critical Implementation Notes

- **Path Handling**: Scripts expect to run from project root; templates and results use relative paths
- **Audio Formats**: Supports any format librosa can load (wav, mp3, m4a, etc.)
- **System Choice**: Use original system for proven results, hybrid system for flexibility
- **Parameter Tuning**: Lower thresholds for noisy audio, higher for clean studio recordings
- **Memory Management**: Large files are processed in-memory; ensure sufficient RAM for video processing

## Quick Start Examples

```bash
# Standard JDL detection (proven)
uv run python scripts/jdl_beep_detector.py

# Any audio file with original settings
uv run python scripts/use_hybrid_detector.py my_audio.wav

# Noisy live stream with BGM
uv run python scripts/use_hybrid_detector.py live_stream.wav --config noisy_live

# Maximum sensitivity for difficult audio
uv run python scripts/use_hybrid_detector.py difficult.wav --correlation 0.4 --spectral 0.15 --min-distance 2
```