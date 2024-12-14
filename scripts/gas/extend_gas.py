import argparse
import os
import sys

import pandas as pd

sys.path.append(os.getcwd())

from scripts.utils.make_dirs import make_dirs


def gas_limit_index(x: int) -> int:
    return int(2 ** ((x + 1).bit_length() - 1) - 1)


def extend_gas(gas: pd.DataFrame, max_gas_verify: pd.DataFrame):
    first_nan = gas.loc[gas["gas_verify"].isna()].index[0]

    for i in range(first_nan, gas.index.max() + 1):
        gas.loc[i, "gas_verify"] = max_gas_verify.loc[gas_limit_index(i), "max_gas_verify"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="extend the gas data of verify as the worst case scenario using the max gas verify data"
    )
    parser.add_argument("gas_csv_path", type=str, help="path to the source verify gas data CSV file")
    parser.add_argument("max_gas_verify_csv_path", type=str, help="path to the max gas verify data CSV file")
    parser.add_argument("out_csv_path", type=str, help="path to the output CSV file")
    args = parser.parse_args()

    extended_gas = pd.read_csv(args.gas_csv_path, index_col=0, dtype=pd.Int64Dtype())
    max_gas_verify = pd.read_csv(args.max_gas_verify_csv_path, index_col=0)

    extend_gas(extended_gas, max_gas_verify)

    make_dirs(args.out_csv_path)
    extended_gas.to_csv(args.out_csv_path, index=True)
