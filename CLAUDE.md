# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a specialized audio processing system for detecting beep sounds in Japan Drone League (JDL) live streams. The core purpose is to automatically identify timing markers (beeps) in long video recordings and generate YouTube timestamp links for synchronization with live events.

## Environment Setup

```bash
# Modern approach: Create environment and install dependencies (2025 uv method)
uv sync

# Alternative: Step-by-step setup
uv venv
uv pip install -e .
```

## Core Architecture

### Primary Detection Engine
- **Main Algorithm**: `scripts/short_template_beep_detector.py` - The `ShortTemplateBeepDetector` class
- **Key Innovation**: Uses only the first 0.5 seconds of a reference beep template for higher timing precision
- **Processing Pipeline**: Template matching → Correlation analysis → Spectral validation → Sub-sample refinement

### Critical Detection Parameters
- **Correlation Threshold**: 80% (optimized to reduce false positives)
- **Spectral Validation**: 60% (prevents non-beep audio from being detected)
- **Sample Rate**: 22,050 Hz (balanced for speed vs precision)
- **Duplicate Removal**: 100ms window (allows detection of closely spaced beeps)

### Template System
- **Primary Template**: `templates/go.mp3` - Main reference beep sound
- **Alternative Template**: `templates/go_01.wav` - Secondary option for different beep types
- **Template Processing**: Automatically trims to first 0.5s and removes silence from onset

## Common Commands

```bash
# Run full JDL video detection (main production use)
uv run python scripts/jdl_beep_detector.py

# Generate YouTube timestamp links from detection results
uv run python scripts/create_youtube_links.py

# Run comprehensive validation on all test samples
uv run python scripts/test_all_with_test5.py

# Test single audio file (for debugging)
uv run python scripts/test_single.py test3.wav 22389  # filename and expected_time_ms

# Detect beeps in custom audio file
uv run python -c "
from scripts.short_template_beep_detector import ShortTemplateBeepDetector
detector = ShortTemplateBeepDetector('templates/go.mp3', 'your_audio.wav')
beeps = detector.process_audio()
print(f'Found {len(beeps)} beeps at: {beeps}')
"
```

## Test Suite & Validation

### Test Audio Files
- `tests/test.wav` through `tests/test6.wav` - Validated reference samples with known correct timings
- **Ground Truth Values**: test.wav(15998ms), test2.wav(22000ms), test3.wav(22389ms), test4.wav(17255ms), test5.wav(248282ms), test6.wav(25970ms & 256490ms)
- **Success Criteria**: All detections must be within 300ms of ground truth (current system achieves <150ms average)

### Validation Architecture
The system maintains 100% success rate on test samples through:
1. **Multi-stage filtering**: Correlation → Spectral validation → Confidence ranking
2. **False positive elimination**: High thresholds prevent spurious detections
3. **Sub-sample precision**: Parabolic interpolation for timing refinement

## Development Evolution

The `archive/` directory contains the complete development history showing algorithm evolution:
1. **Basic cross-correlation** → **Master detector** (multi-template) → **Ultimate detector** (bias correction) → **World-class detector** (over-engineered, failed) → **Short template detector** (current winner)

The short template approach succeeded where complex methods failed by focusing on the onset portion of beeps rather than full waveforms.

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
- **Template Selection**: go.mp3 performs slightly better than go_01.wav for most cases
- **Memory Management**: Large files are processed in-memory; ensure sufficient RAM for video processing