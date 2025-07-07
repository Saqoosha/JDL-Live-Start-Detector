#!/usr/bin/env python3
"""
Hybrid Configurable Detector - Uses proven algorithms from ShortTemplateBeepDetector
but makes key parameters configurable. No reinventing the wheel!
"""

import librosa
import numpy as np
import scipy.signal
from scipy.signal import find_peaks, correlate, hilbert
from dataclasses import dataclass
from typing import List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class HybridConfig:
    """Configuration that makes proven algorithms tunable"""
    
    # Core detection thresholds (from proven working values)
    correlation_threshold: float = 0.8      # 80% of max correlation (proven)
    spectral_threshold: float = 0.6         # 60% spectral similarity (proven)
    
    # Template processing
    template_duration: float = 0.5          # Use first 0.5s (proven optimal)
    silence_threshold: float = 0.02         # 2% for silence removal
    
    # Frequency filtering
    freq_filter_enabled: bool = True        # Enable adaptive frequency filtering
    freq_range_hz: float = 120.0           # ±120Hz from dominant frequency
    min_freq_hz: float = 100.0             # Absolute minimum frequency
    max_freq_hz: float = 8000.0            # Absolute maximum frequency
    
    # Peak detection
    min_distance_seconds: float = 0.5       # Minimum gap between detections
    duplicate_window_ms: float = 100.0      # Duplicate removal window
    
    # Advanced settings
    target_sample_rate: int = 22050         # Proven optimal sample rate
    filter_order: int = 6                   # Butterworth filter order
    parabolic_refinement: bool = True       # Enable sub-sample refinement
    
    # Output settings
    max_detections: Optional[int] = None    # Limit number of results
    min_confidence: float = 0.0             # Minimum confidence to include

class HybridConfigurableDetector:
    """
    Hybrid detector using proven ShortTemplateBeepDetector algorithms
    with configurable parameters. ULTRATHINK: Don't reinvent, parameterize!
    """
    
    def __init__(self, template_path: str, target_path: str, config: HybridConfig = None):
        self.template_path = template_path
        self.target_path = target_path
        self.config = config or HybridConfig()
        
        # Audio data (will be loaded)
        self.template_audio = None
        self.target_audio = None
        self.sample_rate = self.config.target_sample_rate
        
        # Analysis results
        self.dominant_frequencies = None
        self.filter_range = None
        
    def load_and_process_template(self):
        """
        EXACT template processing from original - proven to work
        """
        print(f"🎵 Loading template: {self.template_path}")
        
        # Load original template
        template_raw, orig_sr = librosa.load(self.template_path, sr=None)
        print(f"   Original: {len(template_raw)} samples at {orig_sr} Hz")
        
        # Trim to desired duration (PROVEN: 0.5s is optimal)
        template_samples = int(self.config.template_duration * orig_sr)
        if len(template_raw) > template_samples:
            template_raw = template_raw[:template_samples]
        print(f"   Trimmed to {self.config.template_duration}s: {len(template_raw)} samples")
        
        # CRITICAL: Remove silence using Hilbert envelope (FROM ORIGINAL)
        template_trimmed = self._trim_silence_hilbert(template_raw, orig_sr)
        
        # Resample to target rate
        if orig_sr != self.sample_rate:
            print(f"   Resampling: {orig_sr} Hz -> {self.sample_rate} Hz")
            template_trimmed = librosa.resample(
                template_trimmed, orig_sr=orig_sr, target_sr=self.sample_rate
            )
        
        self.template_audio = template_trimmed
        print(f"   Final template: {len(self.template_audio)} samples ({len(self.template_audio)/self.sample_rate:.3f}s)")
    
    def _trim_silence_hilbert(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        EXACT silence trimming from original using Hilbert envelope
        """
        envelope = np.abs(hilbert(audio))
        
        # Smooth envelope (FROM ORIGINAL)
        window_size = max(1, len(envelope) // 50)
        if window_size > 1:
            envelope = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')
        
        # Find energy above threshold
        max_energy = np.max(envelope)
        above_threshold = envelope > (max_energy * self.config.silence_threshold)
        
        indices = np.where(above_threshold)[0]
        if len(indices) == 0:
            return audio
        
        start_idx = indices[0]
        end_idx = indices[-1] + 1
        
        # Keep 5ms buffer before onset (FROM ORIGINAL)
        buffer = int(0.005 * sr)
        start_idx = max(0, start_idx - buffer)
        
        trimmed = audio[start_idx:end_idx]
        print(f"   Silence removed: {len(audio)} -> {len(trimmed)} samples")
        return trimmed
    
    def analyze_template_frequencies(self):
        """
        EXACT frequency analysis from original - finds dominant frequencies
        """
        print("🔍 Analyzing template frequencies...")
        
        # FFT analysis (FROM ORIGINAL)
        fft = np.fft.fft(self.template_audio)
        freqs = np.fft.fftfreq(len(fft), 1/self.sample_rate)
        magnitude = np.abs(fft)
        
        # Find peaks (FROM ORIGINAL LOGIC)
        half_len = len(magnitude) // 2
        peaks, _ = find_peaks(
            magnitude[:half_len], 
            height=np.max(magnitude) * 0.15,  # ORIGINAL threshold
            distance=5
        )
        
        if len(peaks) > 0:
            peak_magnitudes = magnitude[peaks]
            top_peak_indices = np.argsort(peak_magnitudes)[-3:]  # Top 3 peaks
            self.dominant_frequencies = freqs[peaks[top_peak_indices]]
            
            # ORIGINAL filter range calculation
            primary_freq = self.dominant_frequencies[-1]
            min_freq = max(self.config.min_freq_hz, primary_freq - self.config.freq_range_hz)
            max_freq = min(self.config.max_freq_hz, primary_freq + self.config.freq_range_hz)
        else:
            # Fallback (FROM ORIGINAL)
            min_freq = 800
            max_freq = 1300
            self.dominant_frequencies = np.array([1000])
        
        self.filter_range = (min_freq, max_freq)
        print(f"   Dominant frequencies: {self.dominant_frequencies}")
        print(f"   Filter range: {min_freq:.1f} - {max_freq:.1f} Hz")
        
        return min_freq, max_freq
    
    def apply_frequency_filter(self, audio: np.ndarray) -> np.ndarray:
        """
        EXACT frequency filtering from original - critical for success
        """
        if not self.config.freq_filter_enabled:
            return audio
            
        min_freq, max_freq = self.filter_range
        print(f"🎛️  Applying bandpass filter: {min_freq:.1f}-{max_freq:.1f} Hz")
        
        # ORIGINAL filter implementation
        nyquist = self.sample_rate / 2
        low_norm = max(0.001, min(0.999, min_freq / nyquist))
        high_norm = max(0.001, min(0.999, max_freq / nyquist))
        
        if low_norm >= high_norm:
            low_norm = 0.05
            high_norm = 0.3
        
        try:
            # EXACT same filter as original
            b, a = scipy.signal.butter(self.config.filter_order, [low_norm, high_norm], btype='band')
            filtered_audio = scipy.signal.filtfilt(b, a, audio)
            
            # Safety check (FROM ORIGINAL)
            if np.any(np.isnan(filtered_audio)) or np.any(np.isinf(filtered_audio)):
                print("   ⚠️  Filter failed, using original audio")
                return audio
            
            return filtered_audio
        except Exception as e:
            print(f"   ⚠️  Filter error: {e}")
            return audio
    
    def load_target_audio(self):
        """Load and prepare target audio"""
        print(f"🎵 Loading target: {self.target_path}")
        self.target_audio, _ = librosa.load(self.target_path, sr=self.sample_rate)
        print(f"   Loaded: {len(self.target_audio)} samples ({len(self.target_audio)/self.sample_rate:.1f}s)")
    
    def perform_template_matching(self, filtered_audio: np.ndarray) -> List[dict]:
        """
        EXACT template matching from original - proven correlation method
        """
        print("🔍 Performing template matching...")
        
        # ORIGINAL normalization method - critical!
        reference_norm = self.template_audio / np.max(np.abs(self.template_audio))
        target_norm = filtered_audio / np.max(np.abs(filtered_audio))
        
        # ORIGINAL correlation
        correlation = correlate(target_norm, reference_norm, mode='valid')
        
        if len(correlation) == 0:
            print("   ❌ No valid correlation")
            return []
        
        # ORIGINAL peak finding
        max_corr = np.max(correlation)
        threshold = max_corr * self.config.correlation_threshold
        min_distance_samples = int(self.config.min_distance_seconds * self.sample_rate)
        
        peaks, _ = find_peaks(
            correlation,
            height=threshold,
            distance=min_distance_samples
        )
        
        print(f"   Found {len(peaks)} correlation peaks above {self.config.correlation_threshold:.1%}")
        
        # Convert to detections
        detections = []
        for peak in peaks:
            time_ms = (peak / self.sample_rate) * 1000
            confidence = correlation[peak] / max_corr
            
            detections.append({
                'time_ms': time_ms,
                'confidence': confidence,
                'peak_idx': peak,
                'correlation_value': correlation[peak]
            })
            
        return detections, correlation
    
    def refine_with_parabolic_interpolation(self, detections: List[dict], correlation: np.ndarray) -> List[dict]:
        """
        EXACT parabolic refinement from original - sub-sample precision
        """
        if not self.config.parabolic_refinement:
            return detections
            
        print("🔧 Refining with parabolic interpolation...")
        
        refined = []
        for detection in detections:
            peak_idx = detection['peak_idx']
            
            # ORIGINAL parabolic interpolation
            if 0 < peak_idx < len(correlation) - 1:
                y1, y2, y3 = correlation[peak_idx-1], correlation[peak_idx], correlation[peak_idx+1]
                a = (y1 - 2*y2 + y3) / 2
                b = (y3 - y1) / 2
                
                if abs(a) > 1e-10:
                    x_offset = -b / (2*a)
                    x_offset = np.clip(x_offset, -0.5, 0.5)  # ORIGINAL limit
                    precise_peak = peak_idx + x_offset
                    refined_time_ms = (precise_peak / self.sample_rate) * 1000
                    
                    refined.append({
                        'time_ms': refined_time_ms,
                        'confidence': detection['confidence'],
                        'original_time_ms': detection['time_ms'],
                        'refined': True
                    })
                    print(f"   Refined: {detection['time_ms']:.2f} -> {refined_time_ms:.2f} ms")
                else:
                    refined.append({
                        'time_ms': detection['time_ms'],
                        'confidence': detection['confidence'],
                        'refined': False
                    })
            else:
                refined.append({
                    'time_ms': detection['time_ms'],
                    'confidence': detection['confidence'],
                    'refined': False
                })
        
        return refined
    
    def validate_spectral_similarity(self, detections: List[dict], filtered_audio: np.ndarray) -> List[dict]:
        """
        EXACT spectral validation from original - FFT correlation method
        """
        print("🔍 Validating spectral similarity...")
        
        validated = []
        for detection in detections:
            time_ms = detection['time_ms']
            start_sample = int((time_ms / 1000) * self.sample_rate)
            end_sample = start_sample + len(self.template_audio)
            
            if 0 <= start_sample < len(filtered_audio) and end_sample <= len(filtered_audio):
                audio_segment = filtered_audio[start_sample:end_sample]
                
                # ORIGINAL spectral validation method
                is_valid, spectral_score = self._validate_spectrum_fft(audio_segment)
                
                if is_valid:
                    final_confidence = detection['confidence'] * spectral_score
                    
                    validated.append({
                        'time_ms': time_ms,
                        'confidence': final_confidence,
                        'correlation_confidence': detection['confidence'],
                        'spectral_score': spectral_score,
                        'refined': detection.get('refined', False)
                    })
                    print(f"   ✅ VALIDATED: {time_ms:.2f} ms (final: {final_confidence:.3f})")
        
        return validated
    
    def _validate_spectrum_fft(self, audio_segment: np.ndarray) -> Tuple[bool, float]:
        """
        EXACT spectral validation from original using FFT correlation
        """
        if len(audio_segment) < len(self.template_audio) // 2:
            return False, 0.0
        
        try:
            # Ensure same length (FROM ORIGINAL)
            min_len = min(len(audio_segment), len(self.template_audio))
            seg = audio_segment[:min_len]
            ref = self.template_audio[:min_len]
            
            # FFT (FROM ORIGINAL)
            seg_fft = np.fft.fft(seg)
            ref_fft = np.fft.fft(ref)
            
            # Magnitude correlation (FROM ORIGINAL)
            seg_mag = np.abs(seg_fft)
            ref_mag = np.abs(ref_fft)
            
            if np.max(seg_mag) > 0 and np.max(ref_mag) > 0:
                seg_norm = seg_mag / np.max(seg_mag)
                ref_norm = ref_mag / np.max(ref_mag)
                
                spectral_similarity = np.corrcoef(seg_norm, ref_norm)[0, 1]
                
                if np.isnan(spectral_similarity):
                    spectral_similarity = 0.0
                
                # ORIGINAL threshold
                is_valid = spectral_similarity > self.config.spectral_threshold
                return is_valid, max(0.0, spectral_similarity)
        
        except Exception:
            pass
        
        return False, 0.0
    
    def remove_duplicates(self, detections: List[dict]) -> List[dict]:
        """
        EXACT duplicate removal from original - 100ms window
        """
        if not detections:
            return []
            
        print("🧹 Removing duplicates...")
        
        # Sort by confidence (FROM ORIGINAL)
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        # ORIGINAL duplicate removal logic
        final_detections = []
        for detection in detections:
            is_duplicate = False
            for existing in final_detections:
                if abs(detection['time_ms'] - existing['time_ms']) < self.config.duplicate_window_ms:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                final_detections.append(detection)
        
        print(f"   Removed {len(detections) - len(final_detections)} duplicates")
        return final_detections
    
    def process_audio(self) -> List[float]:
        """
        Main processing pipeline - combines all proven algorithms
        """
        print("🚀 HYBRID CONFIGURABLE DETECTOR")
        print("=" * 50)
        print(f"Template: {self.template_path}")
        print(f"Target: {self.target_path}")
        print(f"Config: corr≥{self.config.correlation_threshold:.1%}, spec≥{self.config.spectral_threshold:.1%}")
        print("=" * 50)
        
        # Step 1: Load and process template (PROVEN)
        self.load_and_process_template()
        
        # Step 2: Analyze template frequencies (PROVEN)
        self.analyze_template_frequencies()
        
        # Step 3: Load target audio
        self.load_target_audio()
        
        # Step 4: Apply frequency filtering (CRITICAL)
        filtered_audio = self.apply_frequency_filter(self.target_audio)
        
        # Step 5: Template matching (PROVEN)
        detections, correlation = self.perform_template_matching(filtered_audio)
        
        if not detections:
            print("❌ No detections found")
            return []
        
        # Step 6: Refine with parabolic interpolation (PROVEN)
        refined_detections = self.refine_with_parabolic_interpolation(detections, correlation)
        
        # Step 7: Spectral validation (PROVEN)
        validated_detections = self.validate_spectral_similarity(refined_detections, filtered_audio)
        
        # Step 8: Remove duplicates (PROVEN)
        final_detections = self.remove_duplicates(validated_detections)
        
        # Step 9: Apply limits and filters
        if self.config.min_confidence > 0:
            final_detections = [d for d in final_detections if d['confidence'] >= self.config.min_confidence]
        
        if self.config.max_detections:
            final_detections = final_detections[:self.config.max_detections]
        
        # Sort by time
        final_detections.sort(key=lambda x: x['time_ms'])
        
        # Extract times
        beep_times = [d['time_ms'] for d in final_detections]
        
        print(f"\n✅ FINAL RESULT: {len(beep_times)} beeps detected")
        for i, detection in enumerate(final_detections):
            mins = int(detection['time_ms'] / 60000)
            secs = (detection['time_ms'] % 60000) / 1000
            refined_marker = " (refined)" if detection.get('refined') else ""
            print(f"  {i+1}. {mins:2d}:{secs:06.3f} | Conf: {detection['confidence']:.3f}{refined_marker}")
        
        return beep_times

if __name__ == "__main__":
    # Test different configurations
    print("🎛️  HYBRID CONFIGURABLE DETECTOR TEST")
    
    # Conservative config (closer to original proven settings)
    conservative_config = HybridConfig(
        correlation_threshold=0.8,  # ORIGINAL
        spectral_threshold=0.6,     # ORIGINAL
        min_distance_seconds=0.5,   # ORIGINAL
        template_duration=0.5       # ORIGINAL
    )
    
    # More sensitive config
    sensitive_config = HybridConfig(
        correlation_threshold=0.7,  # Slightly lower
        spectral_threshold=0.5,     # Slightly lower
        min_distance_seconds=0.3,   # Closer spacing allowed
        template_duration=0.5
    )
    
    detector = HybridConfigurableDetector(
        template_path="templates/go.mp3",
        target_path="tests/test3.wav",  # Start with known test
        config=conservative_config
    )
    
    beeps = detector.process_audio()