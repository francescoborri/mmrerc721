import argparse
import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.getcwd())

import pandas as pd

from scripts.utils.custom_help_formatter import CustomHelpFormatter
from scripts.utils.make_dirs import make_dirs

DELTA_ROUND_FIX = timedelta(days=3, hours=1)


def round_ts(dt: int, period: timedelta) -> int:
    dt = datetime.fromtimestamp(dt).replace(microsecond=0)
    rounded_dt = dt - timedelta(seconds=((dt + DELTA_ROUND_FIX).timestamp() % period.total_seconds()))

    return int(rounded_dt.timestamp())


def timedelta_type(timedelta_str: str) -> timedelta:
    result = None

    try:
        result = pd.Timedelta(timedelta_str).to_pytimedelta()
    except ValueError as exception:
        raise argparse.ArgumentTypeError(f"Invalid timedelta value: {timedelta_str}") from exception

    return result


def derive_collection_gas(
    gas_data: pd.DataFrame, transfers_data: pd.DataFrame, period: timedelta = timedelta(days=7)
) -> pd.DataFrame:
    first_transfer = transfers_data.iloc[0]
    if first_transfer["fromId"] != 0:
        raise argparse.ArgumentTypeError("The first row in the transfers CSV file must be a mint")

    row = {
        "ts": round_ts(first_transfer["timestamp"], period),
        "num_tokens": 1,
        "num_transfers": 0,
        "total_num_tokens": 1,
        "total_num_transfers": 0,
        "gas_mint": gas_data["gas_mint"][1],
        "gas_verify": 0,
        "total_gas_mint": gas_data["gas_mint"][1],
        "total_gas_verify": 0,
    }

    transfers_iter = transfers_data.iterrows()
    next(transfers_iter)  # Skip the first row because already processed

    collection_gas = pd.DataFrame(columns=row.keys())

    for _, transfer in transfers_iter:
        new_ts = round_ts(transfer["timestamp"], period)

        # If the period has changed, save the current row and start a new one
        if new_ts != row["ts"]:
            collection_gas.loc[len(collection_gas)] = row.values()

            row["ts"] = new_ts
            row["num_tokens"] = row["num_transfers"] = 0
            row["gas_mint"] = row["gas_verify"] = 0

        # The transfer is a mint
        if transfer["fromId"] == 0:
            gas = gas_data["gas_mint"][row["total_num_tokens"] + 1]

            row["num_tokens"] += 1
            row["total_num_tokens"] += 1

            row["gas_mint"] += gas
            row["total_gas_mint"] += gas
        # The transfer is not a mint, therefore account the verify gas
        elif transfer["toId"] != 0:
            gas = gas_data["gas_verify"][row["total_num_tokens"]]

            row["num_transfers"] += 1
            row["total_num_transfers"] += 1

            row["gas_verify"] += gas
            row["total_gas_verify"] += gas

    # Save the last row
    collection_gas.loc[len(collection_gas)] = row.values()

    return collection_gas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="calculate the gas consumption of mint and verify operations in relation to a NFT collection over time",
        formatter_class=CustomHelpFormatter,
    )
    parser.add_argument(
        "gas_csv_path",
        type=str,
        help="path to mint and verify gas data CSV file",
    )
    parser.add_argument(
        "transfers_csv_path",
        type=str,
        help="path to the NFT transfers CSV file",
    )
    parser.add_argument(
        "out_csv_path",
        type=str,
        help="""path to the output CSV file, containing for each period:\n
            - 'ts': the timestamp at the beginning of the period\n
            - 'num_tokens': the number of minted tokens in that period\n
            - 'num_transfers': the number of transfers in that period\n
            - 'total_num_tokens': the total number of minted tokens up to that period\n
            - 'total_num_transfers': the total number of transfers up to that period\n
            - 'gas_mint': the gas consumption of mint operations in that period\n
            - 'gas_verify': the gas consumption of verify operations in that period\n
            - 'total_gas_mint': the total gas consumption of mint operations up to that period\n
            - 'total_gas_verify': the total gas consumption of verify operations up to that period)""",
    )
    parser.add_argument(
        "--period",
        type=timedelta_type,
        help="the period of aggregation; it is parsed according to\nhttps://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Timedelta.html",
        metavar="p",
        default=timedelta(weeks=1),
    )
    args = parser.parse_args()

    gas_data = pd.read_csv(args.gas_csv_path, dtype=pd.Int64Dtype(), index_col=0)
    transfers_data = pd.read_csv(args.transfers_csv_path)

    collection_gas = derive_collection_gas(gas_data, transfers_data, args.period)
    make_dirs(args.out_csv_path)
    collection_gas.to_csv(args.out_csv_path, index=False)
