import argparse
import math
import os
import sys

import pandas as pd

sys.path.append(os.getcwd())

from scripts.utils.make_dirs import make_dirs


def derive_max_gas_mint(gas_mint: pd.DataFrame, num_tokens: int = None) -> pd.Series:
    max_gas_mint = pd.Series(dtype=pd.Int64Dtype())
    last = mean = None

    if num_tokens is None:
        num_tokens = gas_mint.index.max()

    for i in range(1, math.ceil(math.log2(num_tokens)) + 1):
        if i == 1:
            last = gas_mint.loc[2**i + 1, "gas_mint"]
        elif 2**i + 1 <= gas_mint.index.max():
            last = gas_mint.loc[2**i - 1 : 2**i + 1, "gas_mint"].max()
        else:
            if mean is None:
                mean = int(max_gas_mint.diff().mean())

            last += mean

        max_gas_mint[2**i + 1] = last

    return max_gas_mint


def derive_max_gas_verify(ext_max_gas_verify: pd.DataFrame, num_tokens: int) -> pd.Series:
    max_gas_verify = pd.Series(dtype=pd.Int64Dtype())
    last = mean = None

    for i in range(1, math.ceil(math.log2(num_tokens)) + 1):
        if 2**i + 1 <= ext_max_gas_verify.index.max():
            last = ext_max_gas_verify.loc[2**i - 1 : 2**i + 1, "gas_verify"].max()
        else:
            if mean is None:
                mean = int(max_gas_verify.diff().mean())

            last += mean

        max_gas_verify[2**i - 1] = last

    return max_gas_verify


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="compute the maximum gas at each MMR height for mint and verify operations"
    )
    parser.add_argument(
        "gas_mint_csv_path",
        type=str,
        help="path to the mint gas CSV file",
    )
    parser.add_argument(
        "ext_max_gas_verify_csv_path",
        type=str,
        help="path to the helper CSV file containing the max gas of verify at several values of 2^n - 1, 2^n, 2^n + 1",
    )
    parser.add_argument(
        "max_gas_csv_path",
        type=str,
        help="path to the output CSV file which will contain the max gas of mint, at several values of 2^n + 1, and verify, at several values of 2^n - 1",
    )
    parser.add_argument(
        "--num_tokens",
        "-n",
        type=int,
        help="number of tokens in the collection; if not provided, it will be taken as the number of rows in the mint gas CSV file",
        default=None,
    )
    args = parser.parse_args()

    gas_mint = pd.read_csv(args.gas_mint_csv_path, index_col=0)
    ext_max_gas_verify = pd.read_csv(args.ext_max_gas_verify_csv_path, index_col=0)
    num_tokens = gas_mint.index.max() if args.num_tokens is None else args.num_tokens

    max_gas_mint = derive_max_gas_mint(gas_mint, num_tokens)
    max_gas_verify = derive_max_gas_verify(ext_max_gas_verify, num_tokens)
    max_gas = (
        pd.concat([max_gas_mint, max_gas_verify], axis=1, keys=["max_gas_mint", "max_gas_verify"])
        .astype(pd.Int64Dtype())
        .sort_index()
    )

    make_dirs(args.max_gas_csv_path)
    max_gas.to_csv(args.max_gas_csv_path, index=True)
