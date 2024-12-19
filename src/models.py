import lightning as L
import torch
from sklearn.metrics import r2_score, root_mean_squared_error
from torch import Tensor, nn
from torch.nn import Module
from torch.optim import AdamW
from torchmetrics.regression import MeanSquaredError, R2Score


class POSForecast(Module):
    def __init__(
        self,
        n_meal_types: int = 5,
        n_restaurants: int = 4,
        n_meals: int = 149,
        d_hid: int = 32,
        d_raw_meal_emd: int = 1024,
    ) -> None:
        super().__init__()

        self._embd_meal_type = nn.Embedding(n_meal_types, d_hid)
        self._embd_restaurant = nn.Embedding(n_restaurants, d_hid)
        self._embd_meal = nn.Embedding(n_meals, d_raw_meal_emd)

        self.lin_date = nn.Linear(6, d_hid)
        self.lin_sim = nn.Linear(1, d_hid)
        self.lin_serv = nn.Linear(1, d_hid)
        self.lin_meal = nn.Linear(d_raw_meal_emd, d_hid)

        self.ff_combine = nn.Sequential(
            nn.Linear(d_hid * 6, d_hid * 6),
            nn.Dropout(),
            nn.Tanh(),
            nn.LayerNorm(d_hid * 6),
        )

        self.trans_encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=d_hid * 6, nhead=1, batch_first=True),
            num_layers=2,
            enable_nested_tensor=False,
        )

        self.lin_pcs = nn.Linear(d_hid * 6, 1)

    def forward(self, X: dict[str, Tensor]) -> Tensor:
        meal = X["meal"]
        meal_type = X["meal_type"]
        mask = X["mask"]
        restaurant = X["restaurant"]
        date = X["date"]
        sim = X["sim"]
        serv_pcn = X["serv_pcn"]

        # Encode
        meal_type = self._embd_meal_type(meal_type)
        restaurant = self._embd_restaurant(restaurant)
        meal = self._embd_meal(meal)
        meal = self.lin_meal(meal)

        date = self.lin_date(date)
        sim = self.lin_sim(sim.unsqueeze(-1))
        serv_pcn = self.lin_serv(serv_pcn.unsqueeze(-1))

        # Concate fields
        N = meal.shape[1]
        restaurant = torch.repeat_interleave(restaurant.unsqueeze(1), N, dim=1)
        date = torch.repeat_interleave(date.unsqueeze(1), N, dim=1)

        meals = torch.concat(
            [
                meal,
                meal_type,
                restaurant,
                date,
                sim,
                serv_pcn,
            ],
            dim=-1,
        )
        meals = self.ff_combine(meals)

        # Use Transformer Encoder
        # SEQ_LEN = mask.shape[-1]
        # mask = mask.unsqueeze(1).repeat_interleave(SEQ_LEN, dim=1)
        meals = self.trans_encoder(meals, src_key_padding_mask=mask)

        # meal_main = meals[:, 0:1]       # [bz, 1, d_hid * 4]
        # meals_other = meals[:, 1:]      # [bz, N-1, d_hid * 4]
        # S: Tensor = meal_main @ meals_other.permute(0, 2, 1)        # [bz, 1, N-1]
        # attentive_prob = nn.functional.softmax(S.masked_fill_(mask.unsqueeze(1), -1e10), dim=-1)
        # # [bz, 1, N-1]
        # h = attentive_prob @ meals_other
        # # [bz, 1, d_hid * 4]

        # meal_main = torch.concat([meal_main, h], dim=-1)
        # meal_main = self.lin2(meal_main)
        # [bz, 1, d_hid * 8]

        # Predict pos
        pos = self.lin_pcs(meals).squeeze(-1)
        # pos = F.tanh(pos)

        return pos


class LitPOSForecast(L.LightningModule):
    def __init__(
        self,
        scaler,
        params: dict,
        lr: float = 3e-4,
    ) -> None:
        super().__init__()
        self.save_hyperparameters()

        self.scaler = scaler

        self.forecaster = POSForecast(**params)
        self.lr = lr

        self.mse = MeanSquaredError()
        self.r2 = R2Score()
        self.preds_val, self.tgts_val = [], []
        self.preds_train, self.tgts_train = [], []

    def training_step(self, batch, batch_idx):
        tgt = batch["tgt"]

        pred = self.forecaster(batch)

        # pred = ((~batch['mask']).type(torch.float32) + EPS) * pred
        # tgt = ((~batch['mask']).type(torch.float32) + EPS) * tgt

        loss = nn.functional.mse_loss(pred, tgt)
        self.log("train_loss", loss, prog_bar=True, on_step=True)

        self.preds_train.append(pred)
        self.tgts_train.append(tgt)

        return loss

    def on_train_epoch_end(self) -> None:
        preds = self.scaler.inverse_transform(
            torch.concat(self.preds_train, dim=0).detach().cpu()
        ).flatten()
        tgts = self.scaler.inverse_transform(
            torch.concat(self.tgts_train, dim=0).detach().cpu()
        ).flatten()

        rmse = root_mean_squared_error(preds, tgts)
        r2 = r2_score(preds, tgts)

        self.log("rmse_train", rmse, on_epoch=True)
        self.log("r2_train", r2, on_epoch=True)

        self.preds_train, self.tgts_train = [], []

    def validation_step(self, batch, batch_idx):
        tgt = batch["tgt"]

        pred = self.forecaster(batch)

        self.preds_val.append(pred)
        self.tgts_val.append(tgt)

    def on_validation_epoch_end(self) -> None:
        preds = self.scaler.inverse_transform(
            torch.concat(self.preds_val, dim=0).detach().cpu()
        ).flatten()
        tgts = self.scaler.inverse_transform(
            torch.concat(self.tgts_val, dim=0).detach().cpu()
        ).flatten()

        rmse = root_mean_squared_error(preds, tgts)
        r2 = r2_score(preds, tgts)
        # rmse = torch.sqrt(self.mse(preds, tgts))
        # r2 = self.r2(preds, tgts)

        self.log("rmse_val", rmse, on_epoch=True)
        self.log("r2_val", r2, on_epoch=True)

        self.preds_val, self.tgts_val = [], []

    def configure_optimizers(self):
        optimizer = AdamW(self.parameters(), lr=self.lr)

        return optimizer
