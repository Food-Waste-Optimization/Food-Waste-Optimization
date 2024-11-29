import datetime
import sys
from pathlib import Path

import joblib
import lightning as L
import polars as pl
from lightning.pytorch.callbacks import ModelCheckpoint, RichProgressBar
from pytorch_lightning.loggers import TensorBoardLogger
from torch.utils.data import DataLoader

from src import LitPOSForecast, POSData

BATCH_SIZE = 256
LR = 9e-4
THETA = 5
NUM_EPOCHS = 20

MODEL_NAME = Path("idea5_TransEnc")

PATH_DIR_WEIGHTS = Path("weights")
PATH_DIR_WEIGHTS.mkdir(exist_ok=True, parents=True)

PATH_SCALER = Path("res/scaler.save")
PATH_TRAIN = Path("data/inter/pos_train.parquet")
PATH_VAL = Path("data/inter/pos_val.parquet")

PATH_DIR_LOGS = Path("logs")
PATH_TENSORBOARD = PATH_DIR_LOGS / "tb_logs"
PATH_WANDB = PATH_DIR_LOGS / "wandb"


def main():
    scaler = joblib.load(PATH_SCALER)

    pos_train = pl.read_parquet(PATH_TRAIN)
    pos_val = pl.read_parquet(PATH_VAL)

    loader_train = DataLoader(POSData(pos_train), batch_size=BATCH_SIZE, shuffle=True)
    loader_val = DataLoader(POSData(pos_val), batch_size=BATCH_SIZE)

    litmodel = LitPOSForecast(scaler, lr=LR)

    version = datetime.datetime.now().strftime("%m-%d_%H-%M-%S")
    trainer = L.Trainer(
        # devices=0,
        callbacks=[
            RichProgressBar(leave=True),
            ModelCheckpoint(
                save_top_k=2,
                monitor="rmse_val",
                mode="min",
                dirpath=PATH_DIR_WEIGHTS / MODEL_NAME,
                filename="{epoch:02d}-{rmse_val:.2f}",
            ),
        ],
        logger=[
            TensorBoardLogger(PATH_TENSORBOARD, name=MODEL_NAME, version=version),
            # WandbLogger(name=MODEL_NAME, version=version, save_dir=PATH_WANDB),
        ],
        # gradient_clip_val=1,
        max_epochs=NUM_EPOCHS,
    )

    trainer.fit(litmodel, loader_train, loader_val)


if __name__ == "__main__":
    sys.exit(main())
