# EOL Power Battery Recycling

> **Important**: All code and data are located in the `main` branch

## Overview
This repository contains computational tools supporting the research:  
**"Reducing the environmental impacts of battery recycling through spatial and technological alignment"**

The framework consists of:
1. **Prediction Module**: Forecasts battery retirement volumes for:
   - Electric Vehicles (EV)
   - Commercial Electric Vehicles (CEV)
2. **Simulation Module**: Evaluates environmental impacts across 52 scenarios (4 supply-side × 13 demand-side)

## System Requirements

### Minimum Hardware
- Processor: Intel Core i5 or equivalent
- RAM: 8GB
- Storage: 500MB free space
- Graphics: Integrated GPU (for spatial visualizations)

### Supported Operating Systems
| OS              | Tested Versions |
|-----------------|-----------------|
| Windows         | 10, 11          |
| macOS           | Monterey (12.0+) |
| Linux (Ubuntu)  | 20.04 LTS, 22.04 LTS |

### Software Dependencies
**Core Packages** (automatically installed via requirements.txt):
```python
pandas == 1.5.3           # Data manipulation
numpy == 1.23.5           # Numerical computing
scikit-learn == 1.2.2     # Machine learning models
keras == 2.11.0           # LSTM implementation
tensorflow == 2.11.0      # Neural network backend
mlxtend == 0.21.0         # Stacked regressors
scipy == 1.10.1           # Statistical functions
geopandas == 0.12.2       # Spatial analysis
rasterio == 1.3.7         # Geospatial raster I/O
matplotlib == 3.7.1       # Visualization

Tested Python Versions:
Python 3.8.16 (recommended)
Python 3.9.18
Python 3.10.12

## License
This work is licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). When using this code, please cite the original publication.

## Contact
For technical inquiries and collaboration:

Prof. Fanran Meng: f.meng@sheffield.ac.uk

Prof. Xi Tian: tianxi@ncu.edu.cn

MS. Fei Peng: pengfei24@email.ncu.edu.cn

Academic affiliations: University of Sheffield (UK) and Nanchang University (China)
