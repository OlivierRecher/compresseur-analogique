import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import sounddevice as sd

fs = 20000  # Fréquence d'échantillonnage (10 échantillons/période pour 2kHz)
duration = 3  # Durée en secondes
f = 2000  # Fréquence du signal en Hz

t = np.linspace(0, duration, int(fs * duration), endpoint=False)
signal_float = np.sin(2 * np.pi * f * t)

print("Lecture du signal original...")
sd.play(signal_float, fs)
sd.wait()

wavfile.write('signal_original.wav', fs, (signal_float * 32767).astype(np.int16))

# Quantification à n bits
def quantize_signal(signal, bits):
    signal_normalized = (signal + 1) / 2  # Normalisation [0, 1]
    levels = 2 ** bits
    quantized = np.round(signal_normalized * (levels - 1)) / (levels - 1)
    return (quantized * 2 - 1)  # Retour à l'échelle [-1, 1]

# 1.b Quantification à 8 bits
signal_8bits = quantize_signal(signal_float, 8)

# 1.c Quantification avec différentes résolutions
resolutions = [8, 6, 4, 3, 2]
signals_quantized = {}

for bits in resolutions:
    signals_quantized[bits] = quantize_signal(signal_float, bits)
    
    # Lecture du signal quantifié
    print(f"Lecture du signal quantifié à {bits} bits...")
    sd.play(signals_quantized[bits], fs)
    sd.wait()
    
    # Sauvegarde
    wavfile.write(f'signal_{bits}bits.wav', fs, (signals_quantized[bits] * 32767).astype(np.int16))

# 1.d Quantification à 1 bit
def quantize_1bit(signal):
    """Quantification à 1 bit (seuil à 0)"""
    return np.where(signal >= 0, 1.0, -1.0)

signal_1bit = quantize_1bit(signal_float)

print("Lecture du signal à 1 bit...")
sd.play(signal_1bit, fs)
sd.wait()
wavfile.write('signal_1bit.wav', fs, (signal_1bit * 32767).astype(np.int16))

# Visualisation des résultats
plt.figure(figsize=(15, 12))

# Signal original
plt.subplot(3, 2, 1)
plt.plot(t[:1000], signal_float[:1000])  # Premier millier d'échantillons
plt.title('Signal original (float)')
plt.xlabel('Temps [s]')
plt.ylabel('Amplitude')
plt.grid(True)

# Signal 8 bits
plt.subplot(3, 2, 2)
plt.plot(t[:1000], signal_8bits[:1000])
plt.title('Signal quantifié - 8 bits')
plt.xlabel('Temps [s]')
plt.ylabel('Amplitude')
plt.grid(True)

# Signal 4 bits
plt.subplot(3, 2, 3)
plt.plot(t[:1000], signals_quantized[4][:1000])
plt.title('Signal quantifié - 4 bits')
plt.xlabel('Temps [s]')
plt.ylabel('Amplitude')
plt.grid(True)

# Signal 2 bits
plt.subplot(3, 2, 4)
plt.plot(t[:1000], signals_quantized[2][:1000])
plt.title('Signal quantifié - 2 bits')
plt.xlabel('Temps [s]')
plt.ylabel('Amplitude')
plt.grid(True)

# Signal 1 bit
plt.subplot(3, 2, 5)
plt.plot(t[:1000], signal_1bit[:1000])
plt.title('Signal quantifié - 1 bit')
plt.xlabel('Temps [s]')
plt.ylabel('Amplitude')
plt.grid(True)

# Comparaison des erreurs de quantification
plt.subplot(3, 2, 6)
errors = {}
for bits in [8, 6, 4, 3, 2]:
    error = np.abs(signal_float - signals_quantized[bits])
    errors[bits] = np.mean(error)
    plt.semilogy(t[:1000], error[:1000], label=f'{bits} bits')

plt.title('Erreur de quantification')
plt.xlabel('Temps [s]')
plt.ylabel('Erreur absolue')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('comparaison_quantification.png', dpi=300, bbox_inches='tight')
plt.show()

# Analyse des performances
print("\n=== ANALYSE DES PERFORMANCES ===")
print("Résolution | SNR (dB) | Erreur quadratique moyenne")
print("-" * 50)

for bits in [8, 6, 4, 3, 2]:
    signal_quant = signals_quantized[bits]
    mse = np.mean((signal_float - signal_quant) ** 2)
    
    # Calcul du SNR
    power_signal = np.mean(signal_float ** 2)
    power_noise = mse
    snr = 10 * np.log10(power_signal / power_noise) if power_noise > 0 else float('inf')
    
    print(f"{bits:2d} bits    | {snr:7.2f}  | {mse:.6f}")

# Analyse spécifique du cas 1 bit
mse_1bit = np.mean((signal_float - signal_1bit) ** 2)
power_signal_1bit = np.mean(signal_float ** 2)
power_noise_1bit = mse_1bit
snr_1bit = 10 * np.log10(power_signal_1bit / power_noise_1bit)

print(f" 1 bit    | {snr_1bit:7.2f}  | {mse_1bit:.6f}")
