# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a specialized audio processing system for detecting race start sequences in Japan Drone League (JDL) live streams. The core purpose is to automatically identify timing markers using revolutionary COUNT→GO pattern detection and generate YouTube timestamp links for race navigation.

**BREAKTHROUGH**: Uses dual-template temporal pattern matching for dramatically improved accuracy and reduced false positives.

## Environment Setup

```bash
# Modern approach: Create environment and install dependencies (2025 uv method)
uv sync

# Alternative: Step-by-step setup
uv venv
uv pip install -e .
```

## Detection System

### COUNT→GO Pattern Detection (Production System)
- **Main Script**: `scripts/jdl_detector.py` - Production interface for JDL race detection
- **Algorithm**: `scripts/pattern_enhanced_detector.py` - The `PatternEnhancedDetector` class
- **Innovation**: Revolutionary dual-template temporal pattern matching
- **Performance**: 20 race start patterns detected with ultra-high accuracy
- **Technology**: Analyzes countdown audio followed by go signals with timing validation

### Template System
- **COUNT Template**: `templates/count.mp3` - Countdown audio reference (2.5s duration)
- **GO Template**: `templates/go.mp3` - Start signal reference (0.5s duration)
- **Pattern Analysis**: Detects temporal sequences with 2-10 second gaps between count and go
- **Frequency Validation**: Automatic spectral analysis ensures frequency content matching

## Common Commands

### Production System
```bash
# Run JDL race start detection (main command)
uv run python scripts/jdl_detector.py

# Alternative: Run pattern detection directly
uv run python scripts/pattern_enhanced_detector.py
```

## Detection Parameters

The system uses carefully tuned parameters optimized for JDL live stream conditions:

### COUNT Detection Parameters
- **count_correlation_threshold: 0.35** - Ultra-sensitive for noisy live streams
- **count_spectral_threshold: 0.15** - Very permissive for background noise tolerance
- **count_template_duration: 2.5** - Full template length for comprehensive detection

### GO Detection Parameters  
- **go_correlation_threshold: 0.35** - Matches COUNT sensitivity for consistency
- **go_spectral_threshold: 0.2** - Slightly higher for go signal specificity
- **go_template_duration: 0.5** - Optimal balance of precision and timing

### Temporal Pattern Parameters
- **min_gap_seconds: 2.0** - Minimum realistic countdown-to-start interval
- **max_gap_seconds: 10.0** - Maximum realistic countdown duration
- **min_distance_seconds: 3.0** - Prevents duplicate detections
- **overlap_window_seconds: 15.0** - Pattern deduplication window

### Parameter Explanation

**Correlation Thresholds (0.0-1.0)**:
- Lower values = more sensitive detection, more false positives
- Higher values = stricter detection, fewer false positives
- 0.35 = Ultra-sensitive setting optimized for noisy conditions

**Spectral Thresholds (0.0-1.0)**:
- Validates frequency content matches template characteristics
- Lower values = accept more frequency variations
- Higher values = require closer frequency matching

**Template Durations**:
- COUNT: 2.5s full template for maximum context and accuracy
- GO: 0.5s short template for precise timing detection

**Temporal Windows**:
- Gap range: 2-10s covers realistic race start timing patterns
- Distance: 3s minimum prevents duplicate detections
- Overlap: 15s window ensures optimal pattern selection

## Output Formats

The system generates comprehensive output formats:
- **results/JAPAN DRONE LEAGUE 2025 Round4 Semi Final & Final_Z7sjETGD-dg.csv**: Race start timings with YouTube URLs
- **results/JAPAN DRONE LEAGUE 2025 Round4 Semi Final & Final_Z7sjETGD-dg_detailed.txt**: Human-readable detailed report
- **results/JAPAN DRONE LEAGUE 2025 Round4 Semi Final & Final_Z7sjETGD-dg_links.md**: Markdown navigation with YouTube links

## Performance Characteristics

- **Detection Accuracy**: 20 race start patterns with minimal false positives
- **Processing Speed**: Efficient dual-template correlation analysis
- **Memory Usage**: Optimized for large video files (135+ minute streams)
- **Temporal Precision**: Sub-second accuracy for race start timing

## Audio Processing Pipeline

1. **Template Analysis**: Load COUNT (2.5s) and GO (0.5s) templates
2. **Target Processing**: Load JDL video → Resample → Apply frequency analysis
3. **Pattern Detection**: 
   - Phase 1: Detect COUNT candidates with ultra-sensitive settings
   - Phase 2: Detect GO candidates with optimized parameters
   - Phase 3: Match COUNT→GO temporal patterns (2-10s gap)
   - Phase 4: Remove overlapping patterns (keep optimal timing)
4. **Output Generation**: CSV, detailed text, and HTML navigation files

## Critical Implementation Notes

- **File Requirements**: JDL video file and templates/count.mp3, templates/go.mp3
- **Path Handling**: Scripts run from project root with relative paths
- **Audio Formats**: Supports any format librosa can load (wav, mp3, m4a, etc.)
- **Parameter Optimization**: Values tuned specifically for JDL live stream conditions
- **Pattern Validation**: Dual-template approach eliminates single-beep false positives

## Quick Start

```bash
# Standard JDL race detection (recommended)
uv run python scripts/jdl_detector.py

# Check results
open results/JAPAN_DRONE_LEAGUE_2025_Round4_Semi_Final_&_Final_Z7sjETGD-dg_links.md
```

## Technical Innovation

The COUNT→GO pattern detection represents a breakthrough in audio event detection:

1. **Temporal Context**: Uses natural countdown→start sequence instead of isolated beeps
2. **False Positive Reduction**: Dual-template validation dramatically reduces errors  
3. **Timing Accuracy**: Pattern gaps provide additional validation of authentic race starts
4. **Live Stream Optimization**: Parameters tuned for noisy conditions with background music
5. **Scalable Architecture**: Clean separation of detection logic and configuration