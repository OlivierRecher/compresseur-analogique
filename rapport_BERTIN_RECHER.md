# Rapport d'Analyse PCM - DPCM

## Partie 1 : Analyse de la quantification PCM

### 1.a Création du signal de référence

**Signal généré :**
- Fréquence : 2 kHz
- Durée : 3 secondes → 2000*3 = 6 000 périodes
- Échantillonnage : 10 échantillons/période → 60 000 kHz
- Format : signal sinusoïdal pur

**Justification :** Un échantillonnage à 10 fois la fréquence du signal garantit une reconstruction fidèle selon le théorème de Shannon.

### 1.b Quantification à 8 bits

**Observation :** Le signal quantifié à 8 bits est presque identique au signal original à l'oreille et visuellement.

**Justification :** 
- La conception du quantificateur repose sur la division de l'amplitude en $2^R$ intervalles, où $R$ est le nombre de bits. L'écart de quantification est donné par $\Delta = \frac{2A}{2^R}$, avec $A=1$, soit $\Delta = \frac{2}{2^R}$. 
- À 8 bits (256 niveaux), la résolution est suffisamment fine pour qu'une sinusoïde soit représentée avec une erreur de quantification négligeable, assurant une excellente fidélité sonore.

### 1.c Quantification à résolutions réduites

**Résultats observés :**

| Résolution | Observation de la ualité audio |
|------------|--------------------------------|
| 6 bits     | Légère dégradation, peu visibles |
| 4 bits     | Dégradation notable de la qualité du signal |
| 3 bits     | Forte distorsion , signal crénelé |
| 2 bits     | Très médiocre, signal très échantillonné |

**Justification :** Plus le nombre de bits diminue, plus le bruit de quantification augmente. La relation SNR ≈ 6×n dB (pour un signal sinusoïdal) explique cette dégradation progressive.

### 1.d Quantification à 1 bit

**Observation :** Le signal devient une onde carrée. La sinusoïde originale est complètement perdue.

**Justification :** 
- Avec 1 bit, seulement 2 niveaux possibles (-1 et +1, seule le signe est conservé)
- Le quantificateur agit comme un comparateur de seuil à zéro
- La forme d'onde originale est irrécupérable, on entend que du bruits

### Conclusions

1. **Relation linéaire** : Le SNR diminue d'environ 6 dB par bit réduit, confirmant la théorie
2. **Seuil d'audibilité** : En dessous de 4 bits, la dégradation devient très perceptible
3. **Limite extrême** : À 1 bit, le système ne conserve que l'information binaire de passage par zéro
