import numpy as np
import librosa
import soundfile as sf
import tempfile
import os

SAMPLE_RATE = 44100

def generate_base_pattern():
    """Create a simple audio pattern (440Hz + 880Hz tones)"""
    duration = 1.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # Create a pattern with two tones
    pattern = (np.sin(2 * np.pi * 440 * t) + 0.5 * np.sin(2 * np.pi * 880 * t))
    max_val = np.max(np.abs(pattern))
    if max_val > 0:
        pattern /= max_val

    return pattern

def test_pattern_equivalence():
    """Test if synthetic pattern matches pattern loaded from file"""
    
    # Generate synthetic pattern
    synthetic = generate_base_pattern()
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_file.close()
    
    try:
        # Save synthetic pattern to file
        sf.write(temp_file.name, synthetic, SAMPLE_RATE)
        
        # Load back from file
        loaded, _ = librosa.load(temp_file.name, sr=SAMPLE_RATE)
        
        print("=== Audio Comparison ===")
        print(f"Synthetic shape: {synthetic.shape}, dtype: {synthetic.dtype}")
        print(f"Loaded shape: {loaded.shape}, dtype: {loaded.dtype}")
        print(f"Synthetic range: [{synthetic.min():.6f}, {synthetic.max():.6f}]")
        print(f"Loaded range: [{loaded.min():.6f}, {loaded.max():.6f}]")
        print(f"Synthetic mean: {synthetic.mean():.6f}, std: {synthetic.std():.6f}")
        print(f"Loaded mean: {loaded.mean():.6f}, std: {loaded.std():.6f}")
        
        # Direct comparison
        print("\n=== Direct Comparison ===")
        are_equal = np.allclose(synthetic, loaded, atol=1e-2)
        print(f"Arrays equal (atol=1e-5): {are_equal}")
        
        if not are_equal:
            diff = np.abs(synthetic - loaded)
            print(f"Max difference: {np.max(diff):.6f}")
            print(f"Mean difference: {np.mean(diff):.6f}")
            print(f"Std difference: {np.std(diff):.6f}")
            
            # Show first few differences
            non_zero_diffs = np.where(diff > 1e-6)[0]
            if len(non_zero_diffs) > 0:
                print(f"First 5 significant differences (indices):")
                for i in non_zero_diffs[:5]:
                    print(f"  [{i}] synthetic: {synthetic[i]:.6f}, loaded: {loaded[i]:.6f}, diff: {diff[i]:.6f}")
        
        # Test with normalization (as done in extract_features)
        print("\n=== After Normalization ===")
        
        # Normalize synthetic
        synthetic_norm = synthetic.astype(np.float32)
        max_val = np.max(np.abs(synthetic_norm))
        if max_val > 0:
            synthetic_norm = synthetic_norm / max_val
            
        # Normalize loaded
        loaded_norm = loaded.astype(np.float32)
        max_val = np.max(np.abs(loaded_norm))
        if max_val > 0:
            loaded_norm = loaded_norm / max_val
        
        print(f"Normalized synthetic range: [{synthetic_norm.min():.6f}, {synthetic_norm.max():.6f}]")
        print(f"Normalized loaded range: [{loaded_norm.min():.6f}, {loaded_norm.max():.6f}]")
        
        are_norm_equal = np.allclose(synthetic_norm, loaded_norm, atol=1e-3)
        print(f"Normalized arrays equal (atol=1e-5): {are_norm_equal}")
        
        if not are_norm_equal:
            norm_diff = np.abs(synthetic_norm - loaded_norm)
            print(f"Normalized max difference: {np.max(norm_diff):.6f}")
            print(f"Normalized mean difference: {np.mean(norm_diff):.6f}")
        
        # Test MFCC features
        print("\n=== MFCC Features Comparison ===")
        
        # Extract MFCC features manually (similar to extract_features)
        synthetic_mfcc = librosa.feature.mfcc(
            y=synthetic_norm, sr=SAMPLE_RATE, n_mfcc=13, hop_length=512
        ).T
        
        loaded_mfcc = librosa.feature.mfcc(
            y=loaded_norm, sr=SAMPLE_RATE, n_mfcc=13, hop_length=512
        ).T
        
        print(f"Synthetic MFCC shape: {synthetic_mfcc.shape}")
        print(f"Loaded MFCC shape: {loaded_mfcc.shape}")
        
        are_mfcc_equal = np.allclose(synthetic_mfcc, loaded_mfcc, atol=1e-2)
        print(f"MFCC features equal (atol=1e-3): {are_mfcc_equal}")
        
        if not are_mfcc_equal:
            mfcc_diff = np.abs(synthetic_mfcc - loaded_mfcc)
            print(f"MFCC max difference: {np.max(mfcc_diff):.6f}")
            print(f"MFCC mean difference: {np.mean(mfcc_diff):.6f}")
            
        return are_equal, are_norm_equal, are_mfcc_equal
        
    finally:
        # Clean up
        os.unlink(temp_file.name)

if __name__ == "__main__":
    print("Testing pattern equivalence between synthetic and file-loaded audio...\n")
    direct_equal, norm_equal, mfcc_equal = test_pattern_equivalence()
    
    print(f"\n=== SUMMARY ===")
    print(f"Direct comparison: {'PASS' if direct_equal else 'FAIL'}")
    print(f"Normalized comparison: {'PASS' if norm_equal else 'FAIL'}")
    print(f"MFCC features comparison: {'PASS' if mfcc_equal else 'FAIL'}")
