import argparse
import os
import sys

import pandas as pd

sys.path.append(os.getcwd())

from scripts.utils.make_dirs import make_dirs


def merge_gas_mint_verify(raw_gas_mint: pd.DataFrame, raw_gas_verify: pd.DataFrame) -> pd.DataFrame:
    gas = pd.DataFrame(columns=["gas_mint", "gas_verify"])
    gas["gas_mint"] = raw_gas_mint["gas_mint"]
    gas["gas_verify"] = raw_gas_verify["gas_verify"].astype(dtype=pd.Int64Dtype())
    gas.index += 1

    return gas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="merge the raw gas data of mint and verify")
    parser.add_argument(
        "raw_gas_mint_csv_path",
        type=str,
        help="path to the CSV file containing the mint raw gas data",
    )
    parser.add_argument(
        "raw_gas_verify_csv_path",
        type=str,
        help="path to the CSV file containing the verify raw gas data",
    )
    parser.add_argument(
        "out_csv_path",
        type=str,
        help="path to the output CSV file",
    )
    args = parser.parse_args()

    raw_gas_mint = pd.read_csv(args.raw_gas_mint_csv_path)
    raw_gas_verify = pd.read_csv(args.raw_gas_verify_csv_path)

    gas = merge_gas_mint_verify(raw_gas_mint, raw_gas_verify)
    make_dirs(args.out_csv_path)
    gas.to_csv(args.out_csv_path, index=True)
