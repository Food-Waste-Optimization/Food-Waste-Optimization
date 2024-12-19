import datetime
import sys
from pathlib import Path

import joblib
import lightning as L
import numpy as np
import polars as pl
import torch
from lightning.pytorch.callbacks import ModelCheckpoint, RichProgressBar
from torch import nn
from torch.utils.data import DataLoader

from src import LitPOSForecast, POSData

BATCH_SIZE = 128
LR = 3e-4
THETA = 5
NUM_EPOCHS = 20

MODEL_NAME = Path("idea_dl_topK")

PATH_DIR_WEIGHTS = Path("weights")
PATH_DIR_WEIGHTS.mkdir(exist_ok=True, parents=True)

PATH_DIR = Path("data/inter/idea7")
PATH_SCALER = PATH_DIR / "pcs_scaler.gz"
PATH_TRAIN = PATH_DIR / "train.parquet"
PATH_VAL = PATH_DIR / "val.parquet"
PATH_EMBDS = PATH_DIR / "meal_embds.npy"

PATH_DIR_LOGS = Path("logs")
PATH_TENSORBOARD = PATH_DIR_LOGS / "tb_logs"
PATH_WANDB = PATH_DIR_LOGS / "wandb"


def main():
    scaler_pcs = joblib.load(PATH_SCALER)
    embds = np.load(PATH_EMBDS)

    pos_train = pl.read_parquet(PATH_TRAIN)
    pos_val = pl.read_parquet(PATH_VAL)

    # Define data module, model
    params = {
        "n_meal_types": 5,
        "n_restaurants": 4,
        "n_meals": 149,
        "d_hid": 32,
        "d_raw_meal_emd": 1024,
    }

    loader_train = DataLoader(POSData(pos_train), batch_size=BATCH_SIZE, shuffle=True)
    loader_val = DataLoader(POSData(pos_val), batch_size=BATCH_SIZE)

    litmodel = LitPOSForecast(scaler_pcs, params, LR)
    litmodel.forecaster._embd_meal.weight = nn.parameter.Parameter(
        torch.tensor(embds, dtype=torch.float32), requires_grad=True
    )

    version = datetime.datetime.now().strftime("%m-%d_%H-%M-%S")
    trainer = L.Trainer(
        # devices=0,
        callbacks=[
            RichProgressBar(leave=True),
            ModelCheckpoint(
                save_top_k=2,
                monitor="rmse_val",
                mode="min",
                dirpath=PATH_DIR_WEIGHTS / MODEL_NAME / version,
                filename="{epoch:02d}-{rmse_val:.2f}",
            ),
        ],
        logger=[
            # TensorBoardLogger(PATH_TENSORBOARD, name=MODEL_NAME, version=version),
            WandbLogger(name=MODEL_NAME, version=version, save_dir=PATH_WANDB),
        ],
        gradient_clip_val=1,
        max_epochs=NUM_EPOCHS,
    )

    trainer.fit(litmodel, loader_train, loader_val)


if __name__ == "__main__":
    sys.exit(main())
