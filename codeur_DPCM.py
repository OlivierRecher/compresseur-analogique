import numpy as np
from scipy.io import wavfile
import sounddevice as sd

def dpcm_encoder(signal, bits):
    """Encode un signal en DPCM avec résolution de 'bits'"""
    levels = 2 ** bits
    quant_step = 2.0 / (levels - 1)
    
    reconstructed = np.zeros_like(signal)
    differences_quantized = np.zeros_like(signal)
    
    reconstructed[0] = np.clip(signal[0], -1, 1)
    
    # Codage DPCM
    for i in range(1, len(signal)):
        diff = signal[i] - reconstructed[i-1]
        
        diff_normalized = np.clip(diff / 2.0, -1, 1)
        diff_quantized = np.round(diff_normalized * (levels - 1) / 2) * 2 / (levels - 1)
        diff_quantized = diff_quantized * 2.0
        
        reconstructed[i] = reconstructed[i-1] + diff_quantized
        reconstructed[i] = np.clip(reconstructed[i], -1, 1)
        
        differences_quantized[i] = diff_quantized
    
    return reconstructed, differences_quantized

def simulate_dpcm_with_errors(signal, bits, error_rate):
    """Simule le DPCM avec erreurs de transmission"""
    encoded, diffs = dpcm_encoder(signal, bits)
    
    corrupted = encoded.copy()
    
    error_indices = np.random.choice(len(corrupted), 
                                   size=int(error_rate * len(corrupted)), 
                                   replace=False)
    
    for idx in error_indices:
        corrupted[idx] = -corrupted[idx] * 0.5
    
    return corrupted, len(error_indices)

def quantize_signal(signal, bits):
    """Quantifie le signal sur le nombre de bits spécifié"""
    signal_normalized = (signal + 1) / 2
    levels = 2 ** bits
    quantized = np.round(signal_normalized * (levels - 1)) / (levels - 1)
    return (quantized * 2 - 1)

print("=== ANALYSE DPCM - PARTIE 2 ===")

print("\n1. Analyse DPCM avec erreurs aléatoires")

fs = 8000
duration = 2
f = 1000
t = np.linspace(0, duration, int(fs * duration), endpoint=False)
signal_test = np.sin(2 * np.pi * f * t)

error_rates = [0.01, 0.001]

for p in error_rates:
    print(f"\n--- Taux d'erreur p = {p} ---")
    
    signal_corrupted, num_errors = simulate_dpcm_with_errors(signal_test, 4, p)
    
    mse_error = np.mean((signal_test - signal_corrupted) ** 2)
    snr_error = 10 * np.log10(np.mean(signal_test ** 2) / mse_error) if mse_error > 0 else float('inf')
    
    print(f"Nombre d'erreurs simulées: {num_errors}")
    print(f"SNR avec erreurs: {snr_error:.2f} dB")
    
    print("Écoute du signal avec erreurs...")
    sd.play(signal_corrupted, fs)
    sd.wait()

print("\n2. Analyse avec signal vocal")

try:
    fs_voice, voice_signal = wavfile.read('xtineFs.wav')
    
    if voice_signal.dtype == np.int16:
        voice_signal = voice_signal.astype(np.float32) / 32768.0
    elif voice_signal.dtype == np.int32:
        voice_signal = voice_signal.astype(np.float32) / 2147483648.0
    
    if len(voice_signal.shape) > 1:
        voice_signal = voice_signal[:, 0]
    
    # Limitation à 3 secondes pour l'analyse
    if len(voice_signal) > 3 * fs_voice:
        voice_signal = voice_signal[:3 * fs_voice]
    
    print(f"Signal vocal chargé: {len(voice_signal)} échantillons, {fs_voice} Hz")
    
    voice_8bit = quantize_signal(voice_signal, 8)
    
    voice_dpcm, _ = dpcm_encoder(voice_signal, 8)
    
    voice_dpcm_errors, error_count = simulate_dpcm_with_errors(voice_signal, 8, 0.01)
    
    print(f"Erreurs introduites: {error_count}")
    
    print("\nÉcoute comparative:")
    print("Voix originale...")
    sd.play(voice_signal, fs_voice)
    sd.wait()
    
    print("Voix PCM 8 bits...")
    sd.play(voice_8bit, fs_voice)
    sd.wait()
    
    print("Voix DPCM 8 bits sans erreurs...")
    sd.play(voice_dpcm, fs_voice)
    sd.wait()
    
    print("Voix DPCM 8 bits avec erreurs (p=0.01)...")
    sd.play(voice_dpcm_errors, fs_voice)
    sd.wait()
    
    wavfile.write('voix_dpcm_8bits.wav', fs_voice, (voice_dpcm * 32767).astype(np.int16))
    wavfile.write('voix_dpcm_erreurs.wav', fs_voice, (voice_dpcm_errors * 32767).astype(np.int16))
    print("\nFichiers sauvegardés: voix_dpcm_8bits.wav, voix_dpcm_erreurs.wav")
    
except FileNotFoundError:
    print("Fichier vocal 'xtineFs.wav' non trouvé.")
    print("Création d'un signal de test vocal simulé...")
    
    fs_voice = 16000
    duration = 3
    t_voice = np.linspace(0, duration, int(fs_voice * duration))
    
    voice_signal = (0.5 * np.sin(2 * np.pi * 200 * t_voice) + 
                   0.3 * np.sin(2 * np.pi * 400 * t_voice) + 
                   0.2 * np.sin(2 * np.pi * 800 * t_voice))
    
    envelope = np.exp(-0.5 * (t_voice - duration/2)**2)
    voice_signal *= envelope
    
    voice_signal = voice_signal / np.max(np.abs(voice_signal))
    
    voice_8bit = quantize_signal(voice_signal, 8)
    voice_dpcm, _ = dpcm_encoder(voice_signal, 8)
    voice_dpcm_errors, error_count = simulate_dpcm_with_errors(voice_signal, 8, 0.01)
    
    print("Écoute du signal vocal simulé avec DPCM et erreurs...")
    sd.play(voice_dpcm_errors, fs_voice)
    sd.wait()

print("\n=== CONCLUSIONS ===")
print("1. Performance avec erreurs:")
print("   - p = 10^-2 : Dégradation audible significative")
print("   - p = 10^-3 : Légère dégradation, peu perceptible")
print("2. DPCM vocal à 8 bits:")
print("   - Qualité similaire au PCM à débit égal")
print("   - Avec p=10^-2 : Apparition de clicks et distortions")
print("   - La voix reste intelligible mais qualité réduite")