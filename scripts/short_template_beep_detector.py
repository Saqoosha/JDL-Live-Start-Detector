import librosa
import numpy as np
import scipy.signal
from scipy.signal import find_peaks, correlate, hilbert
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from pydub import AudioSegment
import os
import warnings
warnings.filterwarnings('ignore')

class ShortTemplateBeepDetector:
    """
    Beep detector using only the first 0.5 seconds of the reference template
    This approach focuses on the onset portion for more precise timing
    """
    
    def __init__(self, reference_beep_path, target_audio_path, template_duration=0.5):
        self.reference_beep_path = reference_beep_path
        self.target_audio_path = target_audio_path
        self.template_duration = template_duration  # seconds
        self.reference_audio = None
        self.target_audio = None
        self.reference_sr = None
        self.target_sr = None
        self.beep_timings = []
        self.reference_spectrum = None
        self.dominant_frequencies = None
        
    def load_and_trim_template(self):
        """Load reference beep and use only the first 0.5 seconds"""
        print("Loading and trimming reference template...")
        
        # Load reference beep
        self.reference_audio, self.reference_sr = librosa.load(self.reference_beep_path, sr=None)
        print(f"Original reference: {len(self.reference_audio)} samples at {self.reference_sr} Hz")
        print(f"Original duration: {len(self.reference_audio)/self.reference_sr:.3f} seconds")
        
        # Calculate samples for desired duration
        template_samples = int(self.template_duration * self.reference_sr)
        
        # Trim to first 0.5 seconds
        if len(self.reference_audio) > template_samples:
            self.reference_audio = self.reference_audio[:template_samples]
            print(f"Trimmed to first {self.template_duration}s: {len(self.reference_audio)} samples")
        else:
            print(f"Reference audio is shorter than {self.template_duration}s, using full audio")
        
        print(f"Template duration: {len(self.reference_audio)/self.reference_sr:.3f} seconds")
        
    def trim_silence_from_template(self, audio, threshold=0.02):
        """Remove silence from the beginning and end of template"""
        envelope = np.abs(hilbert(audio))
        
        # Smooth envelope
        window_size = max(1, len(envelope) // 50)
        if window_size > 1:
            envelope = np.convolve(envelope, np.ones(window_size)/window_size, mode='same')
        
        # Find where energy exceeds threshold
        max_energy = np.max(envelope)
        above_threshold = envelope > (max_energy * threshold)
        
        indices = np.where(above_threshold)[0]
        if len(indices) == 0:
            return audio, 0
        
        start_idx = indices[0]
        end_idx = indices[-1] + 1
        
        # Keep some buffer before onset
        buffer = int(0.005 * self.reference_sr)  # 5ms buffer
        start_idx = max(0, start_idx - buffer)
        
        trimmed = audio[start_idx:end_idx]
        
        print(f"Silence trimming: {len(audio)} -> {len(trimmed)} samples (removed {start_idx} from start)")
        return trimmed, start_idx
        
    def load_audio_files(self):
        """Load and process audio files"""
        # Load and trim template
        self.load_and_trim_template()
        
        # Further trim silence
        self.reference_audio, trim_offset = self.trim_silence_from_template(self.reference_audio)
        
        # Load target audio
        target_sr = 22050
        print(f"Loading target audio (resampling to {target_sr} Hz)...")
        self.target_audio, self.target_sr = librosa.load(self.target_audio_path, sr=target_sr)
        print(f"Target audio loaded: {len(self.target_audio)} samples at {self.target_sr} Hz")
        print(f"Target audio duration: {len(self.target_audio)/self.target_sr:.1f} seconds")
        
        # Resample reference to match target
        if self.reference_sr != self.target_sr:
            print(f"Resampling reference from {self.reference_sr} Hz to {self.target_sr} Hz")
            self.reference_audio = librosa.resample(self.reference_audio, 
                                                    orig_sr=self.reference_sr, 
                                                    target_sr=self.target_sr)
            self.reference_sr = self.target_sr
        
        print(f"Final template: {len(self.reference_audio)} samples ({len(self.reference_audio)/self.reference_sr:.3f}s)")
    
    def analyze_template_characteristics(self):
        """Analyze frequency characteristics of the short template"""
        print("Analyzing short template characteristics...")
        
        # Compute FFT
        fft = np.fft.fft(self.reference_audio)
        freqs = np.fft.fftfreq(len(fft), 1/self.reference_sr)
        magnitude = np.abs(fft)
        self.reference_spectrum = magnitude
        
        # Find peak frequencies
        half_len = len(magnitude) // 2
        peaks, properties = find_peaks(magnitude[:half_len], 
                                       height=np.max(magnitude) * 0.15,
                                       distance=5)
        
        if len(peaks) > 0:
            peak_magnitudes = magnitude[peaks]
            top_peak_indices = np.argsort(peak_magnitudes)[-3:]
            self.dominant_frequencies = freqs[peaks[top_peak_indices]]
            
            primary_freq = self.dominant_frequencies[-1]
            min_freq = max(100, primary_freq - 120)
            max_freq = min(8000, primary_freq + 120)
        else:
            min_freq = 800
            max_freq = 1300
            self.dominant_frequencies = np.array([1000])
        
        print(f"Template dominant frequencies: {self.dominant_frequencies} Hz")
        print(f"Filter range: {min_freq:.1f} - {max_freq:.1f} Hz")
        
        return min_freq, max_freq
    
    def apply_frequency_filter(self, audio, low_freq, high_freq):
        """Apply bandpass filter"""
        nyquist = self.target_sr / 2
        low_norm = max(0.001, min(0.999, low_freq / nyquist))
        high_norm = max(0.001, min(0.999, high_freq / nyquist))
        
        if low_norm >= high_norm:
            low_norm = 0.05
            high_norm = 0.3
        
        try:
            b, a = scipy.signal.butter(6, [low_norm, high_norm], btype='band')
            filtered_audio = scipy.signal.filtfilt(b, a, audio)
            
            if np.any(np.isnan(filtered_audio)) or np.any(np.isinf(filtered_audio)):
                return audio
            
            return filtered_audio
        except:
            return audio
    
    def template_matching_correlation(self, filtered_audio):
        """Perform template matching with short template"""
        print("Performing template matching with short template...")
        
        # Normalize signals
        reference_norm = self.reference_audio / np.max(np.abs(self.reference_audio))
        target_norm = filtered_audio / np.max(np.abs(filtered_audio))
        
        # Cross-correlation
        correlation = correlate(target_norm, reference_norm, mode='valid')
        
        if len(correlation) == 0:
            print("No valid correlation computed")
            return []
        
        # Find peaks with adaptive threshold
        max_corr = np.max(correlation)
        threshold = max_corr * 0.8  # 80% of maximum - even higher to reduce false positives
        
        peaks, properties = find_peaks(correlation, 
                                       height=threshold,
                                       distance=int(self.target_sr * 0.5))  # Min 0.5s apart
        
        print(f"Found {len(peaks)} correlation peaks above threshold")
        
        detections = []
        for peak in peaks:
            time_ms = (peak / self.target_sr) * 1000
            confidence = correlation[peak] / max_corr
            
            detections.append({
                'time_ms': time_ms,
                'confidence': confidence,
                'correlation_value': correlation[peak]
            })
            
            print(f"Detection at {time_ms:.2f} ms (confidence: {confidence:.3f})")
        
        return detections
    
    def parabolic_interpolation(self, correlation, peak_idx):
        """Parabolic interpolation for sub-sample precision"""
        if peak_idx <= 0 or peak_idx >= len(correlation) - 1:
            return peak_idx, correlation[peak_idx] if peak_idx < len(correlation) else 0
        
        y1, y2, y3 = correlation[peak_idx-1], correlation[peak_idx], correlation[peak_idx+1]
        a = (y1 - 2*y2 + y3) / 2
        b = (y3 - y1) / 2
        
        if abs(a) > 1e-10:
            x_offset = -b / (2*a)
            x_offset = np.clip(x_offset, -0.5, 0.5)  # Limit offset
            y_peak = y2 - b*b/(4*a)
            x_precise = peak_idx + x_offset
            return x_precise, y_peak
        else:
            return peak_idx, y2
    
    def refine_detections(self, detections, correlation):
        """Refine detection timing with sub-sample precision"""
        refined_detections = []
        
        for detection in detections:
            time_ms = detection['time_ms']
            peak_sample = int((time_ms / 1000) * self.target_sr)
            
            # Apply parabolic interpolation
            if 0 < peak_sample < len(correlation) - 1:
                precise_peak, precise_value = self.parabolic_interpolation(correlation, peak_sample)
                refined_time_ms = (precise_peak / self.target_sr) * 1000
                
                refined_detections.append({
                    'time_ms': refined_time_ms,
                    'confidence': detection['confidence'],
                    'method': 'short_template_refined'
                })
                
                print(f"Refined: {time_ms:.2f} -> {refined_time_ms:.2f} ms")
            else:
                refined_detections.append({
                    'time_ms': time_ms,
                    'confidence': detection['confidence'],
                    'method': 'short_template'
                })
        
        return refined_detections
    
    def validate_detections(self, detections, filtered_audio):
        """Validate detections using spectral similarity"""
        validated_detections = []
        
        for detection in detections:
            time_ms = detection['time_ms']
            start_sample = int((time_ms / 1000) * self.target_sr)
            end_sample = start_sample + len(self.reference_audio)
            
            if 0 <= start_sample < len(filtered_audio) and end_sample <= len(filtered_audio):
                audio_segment = filtered_audio[start_sample:end_sample]
                
                # Simple spectral validation
                is_valid, spectral_score = self.validate_spectrum(audio_segment)
                
                if is_valid:
                    final_confidence = detection['confidence'] * spectral_score
                    validated_detections.append({
                        'time_ms': time_ms,
                        'confidence': final_confidence,
                        'spectral_score': spectral_score,
                        'method': detection['method']
                    })
                    
                    print(f"VALIDATED: {time_ms:.2f} ms (final confidence: {final_confidence:.3f})")
        
        return validated_detections
    
    def validate_spectrum(self, audio_segment):
        """Simple spectral validation"""
        if len(audio_segment) < len(self.reference_audio) // 2:
            return False, 0.0
        
        try:
            # Ensure same length
            min_len = min(len(audio_segment), len(self.reference_audio))
            seg = audio_segment[:min_len]
            ref = self.reference_audio[:min_len]
            
            # FFT
            seg_fft = np.fft.fft(seg)
            ref_fft = np.fft.fft(ref)
            
            # Magnitude correlation
            seg_mag = np.abs(seg_fft)
            ref_mag = np.abs(ref_fft)
            
            if np.max(seg_mag) > 0 and np.max(ref_mag) > 0:
                seg_norm = seg_mag / np.max(seg_mag)
                ref_norm = ref_mag / np.max(ref_mag)
                
                spectral_similarity = np.corrcoef(seg_norm, ref_norm)[0, 1]
                
                if np.isnan(spectral_similarity):
                    spectral_similarity = 0.0
                
                return spectral_similarity > 0.6, spectral_similarity  # Even higher threshold to reduce false positives
        
        except Exception:
            pass
        
        return False, 0.0
    
    def process_audio(self):
        """Main processing function"""
        # Load audio files
        self.load_audio_files()
        
        # Analyze template characteristics
        min_freq, max_freq = self.analyze_template_characteristics()
        
        # Apply frequency filter
        print("Applying frequency filter...")
        filtered_audio = self.apply_frequency_filter(self.target_audio, min_freq, max_freq)
        
        # Template matching
        detections = self.template_matching_correlation(filtered_audio)
        
        if not detections:
            print("No detections found")
            return []
        
        # Refine timing with sub-sample precision
        correlation = correlate(filtered_audio / np.max(np.abs(filtered_audio)), 
                                self.reference_audio / np.max(np.abs(self.reference_audio)), 
                                mode='valid')
        refined_detections = self.refine_detections(detections, correlation)
        
        # Validate detections
        validated_detections = self.validate_detections(refined_detections, filtered_audio)
        
        # Sort by confidence and select best
        validated_detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Remove duplicates within 100ms
        final_detections = []
        for detection in validated_detections:
            is_duplicate = False
            for existing in final_detections:
                if abs(detection['time_ms'] - existing['time_ms']) < 100:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                final_detections.append(detection)
        
        beep_times = [d['time_ms'] for d in final_detections]
        
        print(f"\nShort template results: {len(beep_times)} beeps detected")
        for i, detection in enumerate(final_detections):
            print(f"  Beep {i+1}: {detection['time_ms']:.2f} ms "
                  f"(confidence: {detection['confidence']:.3f})")
        
        self.beep_timings = beep_times
        return beep_times
    
    def save_results(self, output_file="short_template_beep_timings.txt"):
        """Save results"""
        with open(output_file, 'w') as f:
            f.write("Short Template Beep Detection Results\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Reference beep: {self.reference_beep_path}\n")
            f.write(f"Template duration: {self.template_duration} seconds\n")
            f.write(f"Target audio: {self.target_audio_path}\n")
            f.write(f"Total beeps detected: {len(self.beep_timings)}\n\n")
            f.write("Beep timings (milliseconds):\n")
            for i, time_ms in enumerate(self.beep_timings):
                f.write(f"  Beep {i+1}: {time_ms:.2f} ms\n")
        
        print(f"Results saved to {output_file}")

def main():
    reference_beep = "go.mp3"
    target_audio = "test.wav"
    
    if not os.path.exists(reference_beep):
        print(f"Error: Reference beep file '{reference_beep}' not found!")
        return
    
    if not os.path.exists(target_audio):
        print(f"Error: Target audio file '{target_audio}' not found!")
        return
    
    # Test with 0.5 second template
    detector = ShortTemplateBeepDetector(reference_beep, target_audio, template_duration=0.5)
    
    try:
        beep_times = detector.process_audio()
        detector.save_results()
        print(f"\nShort template processing complete! Found {len(beep_times)} beeps.")
        
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()