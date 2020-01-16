# Analysis of stochastic simulations of Genome-Scale Metabolic Models 

## Introduction

Python application for analysing Dynamic GSMM models simulated by BESS5.
Developed by Valentin Laroche

A 2-steps analysis using python 3.7 to understand where BESS5 simulations are "dying" and locate rules and elements that are wrongly simulated. Both these analyzes require the BESS5 code to work with. BESS5 code is not integrated to this repository due to code protection and only the files located in "simulation files" and "results/archive" folders can be used with the given python files.

The first step uses an original .model2 file and one of its simulation results (.poe) to arbitrarily fix new weights to the .model2 file rules.
It generated a new .model2 file with the new weights, a cytoscape network file (.sif), and annotation files for edges and nodes (.csv) to use with the network.

The second step uses an updated .model2 file, its simulation results (.poe and .por) and a node annotation file generated in the first step of the analysis.

## Requirements

To use both files, Python version 3.7 is mandatory.
It also requires the following packages, both of which normally installed with a traditional Python installation :
    1. argparse
    2. textwarp

## How to use

Both Python modules are located in "./code" directory and can be used from any terminal.
It is possible to use both analysis files with the example files, following these steps :
    
1. edit_model2.py
Example files are located in "./simulation_files" :
    1. e_coli_core.model2
    2. test_model_ecoli.poe

A command line would be :
    ```./code/edit_model2.py ./simulation_files/e_coli_core.model2 ./simulation_files/test_model_ecoli.poe```

2. analyze_model2.py :
Example files are located in "./results/archive" :
    1. e_coli_core_new.model2
    2. test_model_ecoli_new.poe
    3. test_model_ecoli_new.por
    4. annot_node.csv

A command line would be : 
    ```./code/analyze_model2.py ./results/archive/e_coli_core_new.model2 ./results/archive/test_model_ecoli_new.poe ./results/archive/test_model_ecoli_new.por ./results/archive/annot_node.csv```

All generated files will be located in "./results" for further analysis