import argparse
from typing import Tuple

import pandas as pd


def count_mints_transfers(transfers_data: pd.DataFrame) -> Tuple[int, int]:
    return (
        transfers_data.loc[(transfers_data["fromId"] == 0) & (transfers_data["toId"] != 0)].shape[0],
        transfers_data.loc[(transfers_data["fromId"] != 0) & (transfers_data["toId"] != 0)].shape[0],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="count the number of mints and transfers given a CSV file containing NFT transfers"
    )
    parser.add_argument(
        "transfers_csv_path",
        type=str,
        help="path to the CSV file containing the NFT transfers",
    )
    args = parser.parse_args()

    transfers_data = pd.read_csv(args.transfers_csv_path)
    mints, transfers = count_mints_transfers(transfers_data)

    print(f"Number of mints: {mints}")
    print(f"Number of real transfers (excluding mints): {transfers}")
