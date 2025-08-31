import numpy as np
import librosa
from typing import Optional, Tuple
import os
from scipy.spatial.distance import euclidean

class DTWAnalyzer:
    def __init__(self, reference_audio: np.ndarray, sample_rate: int = 44100, 
                 window_size: float = 1.0,
                 window_constraint_ratio: float = 0.1, downsample_factor: int = 2):
        """
        Initialize DTW analyzer for audio pattern matching
        
        Args:
            reference_audio: Reference audio pattern as numpy array
            sample_rate: Audio sample rate in Hz
            window_size: Size of the sliding window in seconds for comparison
            window_constraint_ratio: Sakoe-Chiba window constraint as ratio of sequence length
            downsample_factor: Factor to downsample features for faster processing
        """
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.window_constraint_ratio = window_constraint_ratio
        self.downsample_factor = downsample_factor
        
        # Extract and store reference features
        self.reference_features = self.extract_features(reference_audio)
        
    
    def extract_features(self, audio_data: np.ndarray) -> np.ndarray:
        """Extract MFCC features from audio data"""
        if len(audio_data) == 0:
            return np.array([])
            
        # Ensure audio_data is float32 for librosa
        audio_data = audio_data.astype(np.float32)
        
        # Normalize to [-1, 1] range for consistent feature extraction
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            audio_data = audio_data / max_val
        else:
            return []
        
        # Extract MFCC features
        mfcc_features = librosa.feature.mfcc(
            y=audio_data, sr=self.sample_rate, n_mfcc=13, hop_length=512
        ).T  # Transpose to get time x features
        
        # Downsample features for faster processing
        if self.downsample_factor > 1:
            features = mfcc_features[::self.downsample_factor]
        else:
            features = mfcc_features
        
        # Normalize features (mean=0, std=1) for better DTW comparison
        if len(features) > 0:
            features = (features - np.mean(features, axis=0)) / (np.std(features, axis=0))
        
        return features
    
    def _dtw_distance_optimized(self, seq1: np.ndarray, seq2: np.ndarray, 
                               window_constraint: Optional[int] = None) -> float:
        """
        Optimized DTW implementation with window constraint
        """
        n, m = len(seq1), len(seq2)
        
        # Calculate window constraint
        if window_constraint is None:
            window_constraint = max(1, int(max(n, m) * self.window_constraint_ratio))
        
        # Initialize DTW matrix with infinity
        dtw_matrix = np.full((n + 1, m + 1), np.inf)
        dtw_matrix[0, 0] = 0
        
        # Fill DTW matrix with Sakoe-Chiba band constraint
        for i in range(1, n + 1):
            # Calculate window bounds
            j_start = max(1, i - window_constraint)
            j_end = min(m + 1, i + window_constraint + 1)
            
            for j in range(j_start, j_end):
                # Calculate distance between current features
                cost = euclidean(seq1[i-1], seq2[j-1])
                
                # DTW recurrence relation
                dtw_matrix[i, j] = cost + min(
                    dtw_matrix[i-1, j],      # insertion
                    dtw_matrix[i, j-1],      # deletion
                    dtw_matrix[i-1, j-1]     # match
                )
                
        return dtw_matrix[n, m]
    
    def calculate_similarity_features(self, seq1_features: np.ndarray, seq2_features: np.ndarray) -> float:
        """
        Calculate DTW similarity between two feature sequences
        
        Args:
            seq1_features: First feature sequence as numpy array
            seq2_features: Second feature sequence as numpy array
            
        Returns:
            similarity_score: Float between 0 and 1 (0 = perfect match, 1 = no similarity)
        """
        if len(seq1_features) == 0 or len(seq2_features) == 0:
            return 1.0  # Return max dissimilarity for empty sequences
        
        # Calculate DTW distance between the two feature sequences
        try:
            # Use optimized DTW with window constraint
            distance = self._dtw_distance_optimized(
                seq1_features,
                seq2_features,
            )
            
            # Normalize distance by sequence length for fair comparison
            normalized_distance = distance / (len(seq1_features) + len(seq2_features))
            
            # Convert distance to similarity score (0-1): lower distance = lower score
            # Using exponential: score = 1 - exp(-distance), approaches 1 for large distances, 0 for small distances
            similarity_score = 1 - np.exp(-normalized_distance)
            
            return similarity_score
            
        except Exception as e:
            print(f"DTW calculation error: {e}")
            return 1.0  # Return max dissimilarity on error
    
    
    def calculate_similarity(self, audio_pattern: np.ndarray) -> float:
        """
        Calculate DTW similarity between audio pattern and reference
        
        Args:
            audio_pattern: Audio pattern as numpy array
            
        Returns:
            similarity_score: Float between 0 and 1 (0 = perfect match, 1 = no similarity)
        """
        import time
        
        # Extract features from input audio pattern
        feature_start = time.time()
        pattern_features = self.extract_features(audio_pattern)
        feature_time = time.time() - feature_start
        
        # Compare with stored reference features
        dtw_start = time.time()
        similarity = self.calculate_similarity_features(pattern_features, self.reference_features)
        dtw_time = time.time() - dtw_start
        
        if os.getenv('DEBUG', '').lower() == 'true':
            print(f"  DTW breakdown: features={feature_time*1000:.1f}ms, dtw_calc={dtw_time*1000:.1f}ms")
        
        return similarity
    
