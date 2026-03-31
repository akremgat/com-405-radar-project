# COM-405 Radar Project

**Course:** COM-405  
**Team:** Mohamed Habib Ben Amor, Julien Gretillat, Rania Haffar, Mohamed Akrem El Guet

---

## Project Description
Radar-based system that classifies student attention levels using mmWave FMCW radar.
We classify 3 behavioral states: Attentive, Distracted, and Active.

---

## Project Structure
```
radar-project/
  src/
    capture/       → data capture scripts
    processing/    → signal processing (Range FFT, phase extraction)
    ml/            → machine learning models (Week 4-6)
  data/            → captured radar data per experiment
  results/         → plots and outputs
  scripts/         → Lua scripts for radar configuration
  utils/           → radar utility functions
```
