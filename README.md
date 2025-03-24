DAMO-610-6

Group Assignment - Operations Analytics (DAMO-610-6)

Project Title: Optimizing Public Bus Network Scheduling

📘 Project Overview

This repository contains the Python implementation of the project titled Optimizing Public Bus Network Scheduling, developed as part of the Operations Analytics course (DAMO-610-6) at the University of Niagara Falls. The project explores linear programming techniques to optimize the allocation of buses across 93 urban routes and four daily shifts, addressing a total daily demand of approximately 640,000 passengers.

🛠️ Models Implemented

Filename

Corresponding Model in the Report

Description

Berhan_bus_original_small.py

Small-Scale Prototype (Original Model)

A faithful replication of the Berhan et al. (2014) model on a small dataset.

Berhan_bus_extendedl_small.py

Small-Scale Prototype (Extended Model)

Adds a third bus type to test feasibility improvements at small scale.

Berhan_bus_original_full.py

Full Model (Original)

Applies the original model to all 93 routes using imputed data – infeasible.

Berhan_bus_extended_full.py

Full Model (Extended)

Adds the third bus type to the full dataset – still infeasible.

✨ Features

Demand and fleet constraints modeled using Google OR-Tools (Linear Solver)

Models include demand fulfillment, trip factor, shift coverage, and proportional allocation constraints

Includes both sample test data and full synthetic dataset for experimentation

Models aim to minimize total trips while meeting operational constraints

📂 Repository Structure

├── Berhan_bus_original_small.py     # Original model on reduced dataset (8 routes)
├── Berhan_bus_extendedl_small.py    # Extended model with third bus type on 6 routes
├── Berhan_bus_original_full.py      # Full original model (93 routes) – infeasible
├── Berhan_bus_extended_full.py      # Full extended model (93 routes) – still infeasible
├── README.md                        # Project documentation
└── /data                            # Input files and data sources (if applicable)

🚀 How to Run

Clone the repository

Install dependencies: pip install -r requirements.txt

Run the desired script using Python 3.10+:

python Berhan_bus_original_small.py

👥 Contributors

Nelson Benitz 

Fabio dos Santos Prumucena 

Gustavo Paula
