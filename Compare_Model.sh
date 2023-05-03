#!/bin/bash
#SBATCH -J CompareModel_%j
#SBATCH -o ./Output/Log/outputCompareModel_%j.out
#SBATCH -e ./Output/Log/errorCompareModel_%j.err
#SBATCH --mem=8G
#SBATCH -c 16
#SBATCH -p long

#Purge any previous modules
module purge
source ~/.bashrc

#Load Conda
conda activate /shared/projects/untwist/Env/Pycaret/

#Launch script

time python Untwist-TuneAll.py


