import torch
import torch.nn.functional as F
from polars import DataFrame
from torch.utils.data import Dataset


class POSData(Dataset):
    def __init__(self, ds: DataFrame, theta: int = 5) -> None:
        super().__init__()

        self._ds = ds
        self.theta = theta

    def __getitem__(self, idx):
        record = self._ds.row(idx, named=True)

        restaurant = torch.tensor(record["restaurant_enc"], dtype=torch.int32)

        n = len(record["meal_id_enc"])
        n_zeros_padded = self.theta - n

        meal = F.pad(
            torch.tensor(record["meal_id_enc"], dtype=torch.float32),
            (0, n_zeros_padded),
        )
        meal_type = F.pad(
            torch.tensor(record["meal_type_enc"], dtype=torch.int32),
            (0, n_zeros_padded),
        )
        sim = F.pad(
            torch.tensor(record["sim"], dtype=torch.float32), (0, n_zeros_padded)
        )
        tgt_train = F.pad(
            torch.tensor(record["pcs_enc"], dtype=torch.float32),
            (0, n_zeros_padded),
        )
        tgt = F.pad(
            torch.tensor(record["pcs"], dtype=torch.float32), (0, n_zeros_padded)
        )

        # mask = torch.zeros((THETA, THETA), dtype=torch.float32)
        # mask[:n, :n] = 1.0
        mask = (meal == 0).clone().detach()

        date = torch.tensor(
            [
                record["weekday_sin"],
                record["weekday_cos"],
                record["day_sin"],
                record["day_cos"],
                record["month_sin"],
                record["month_cos"],
            ],
            dtype=torch.float32,
        )

        out = {
            "meal": meal,
            "meal_type": meal_type,
            "sim": sim,
            "mask": mask,
            "restaurant": restaurant,
            "date": date,
            "tgt_train": tgt_train,
            "tgt": tgt,
        }

        return out

    def __len__(
        self,
    ) -> int:
        return len(self._ds)
