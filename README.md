# DAMO-610-6
Group Assignment - Opertion Analytics - LP assignment -GROUP (DAMO-610-6) - 2

Optimizing Public Bus Network Scheduling - GitHub Repository README
📘 Project Overview
This repository contains the Python implementation of the project titled 'Optimizing Public Bus Network Scheduling', developed as part of the Operations Analytics course (DAMO-610-6) at the University of Niagara Falls. The project applies linear programming and constraint programming methods to optimize the assignment of buses across 93 urban routes and four shifts, serving a total daily demand of 640,000 passengers.
🛠️ Models Implemented
- **Original LP Model**: Based on the work of Berhan et al. (2014), this model minimizes the number of bus trips while satisfying demand, fleet size, and service constraints.
- **Extended CP-SAT Model with Buffer**: Introduces a buffer-based constraint relaxation mechanism to address infeasibility and enhance flexibility in trip allocations.
✨ Features
- Demand and fleet constraints modeled using Google OR-Tools (LP and CP-SAT)
- Includes both sample test data and complete synthetic dataset
- Automated loop to find minimal buffer that restores model feasibility
- Optimized assignment of two bus types (Type-I and Type-II)
📂 Repository Structure
```
├── prototype_model.py            # Initial test model using sample data
├── full_model.py                 # Original model using full dataset
├── extended_model_with_buffer.py# Enhanced CP-SAT model with buffer flexibility
├── README.md                     # Project documentation
└── /data                         # Input files (if any)
```
🚀 How to Run
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the desired model script using Python 3.10+ (e.g., `python extended_model_with_buffer.py`)
👥 Contributions
- **Nelson Benitz** – Lead author of the initial models and responsible for implementing the original LP formulation based on the referenced academic article.
- **Fabio dos Santos Prumucena** – Author of the extended model with buffer flexibility, responsible for enhancing feasibility, revising and commenting on the initial scripts, and preparing the final documentation.
- **Gustavo Paula** – Provided research support and peer-reviewed the implementations and documentation to ensure academic quality and coherence.
📄 License
This project is released for academic purposes only. Please cite the source paper and this repository if using the content.

