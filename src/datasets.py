import torch
from polars import DataFrame
from torch.utils.data import Dataset


def _fill_none(x):
    return x if x is not None else 0


def _create_tensor(col: str, record: dict):
    return torch.tensor(
        [
            _fill_none(record[f"{col}_1"]),
            _fill_none(record[f"{col}_2"]),
            _fill_none(record[f"{col}_3"]),
            _fill_none(record[f"{col}_4"]),
        ],
        dtype=torch.float32,
    )


def _create_mask(record: dict):
    return torch.tensor(
        [
            record["dist_1"] is None,
            record["dist_2"] is None,
            record["dist_3"] is None,
            record["dist_4"] is None,
        ],
        dtype=torch.bool,
    )


class POSData(Dataset):
    def __init__(self, ds: DataFrame) -> None:
        super().__init__()

        self._ds = ds

    def __getitem__(self, idx):
        record = self._ds.row(idx, named=True)

        restaurant = torch.tensor(record["restaurant_enc"], dtype=torch.int32)

        meal = _create_tensor("meal_id_sim_enc", record).type(torch.int32)
        meal_type = _create_tensor("meal_type_enc", record).type(torch.int32)
        serv_pcn = _create_tensor("serving_percent", record)
        sim = _create_tensor("dist", record)
        tgt = _create_tensor("pcs_scaled", record)

        mask = _create_mask(record)

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
            "serv_pcn": serv_pcn,
            "tgt": tgt,
        }

        return out

    def __len__(
        self,
    ) -> int:
        return len(self._ds)
