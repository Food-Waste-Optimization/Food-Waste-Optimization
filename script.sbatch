#!/bin/sh
#SBATCH --job-name=FoodWaste_pred
#SBATCH -M ukko
#SBATCH -o logs/%x_%j.out
#SBATCH -e logs/%x_%j.err
#SBATCH -c 4
#SBATCH -t 2-00:00:00
#SBATCH --mem=64G
#SBATCH -p gpu
#SBATCH --constraint=v100
#SBATCH --gres=gpu:1
#SBATCH --chdir=/home/hoanghu/foodwaste-prediction/


module purge
module load Mamba cuDNN

date


/home/hoanghu/foodwaste-prediction/py/bin/python run.py



date

