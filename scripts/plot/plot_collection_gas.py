import argparse
import os
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(os.getcwd())

from scripts.utils.make_dirs import make_dirs
from scripts.utils.matplotlib_utils import compute_plot_size, set_pgfplot_style


def plot_mint(collection_gas: pd.DataFrame, min_gas_mint: int, width: float, height: float) -> plt.Figure:
    fig, gas_ax = plt.subplots(figsize=(width, height))
    nft_ax = gas_ax.twinx()

    gas_ax_color = "tab:blue"
    nft_ax_color = "tab:green"

    gas_ax.set_xlabel("Data")

    gas_ax.set_ylabel("Gas", color=gas_ax_color)
    gas_ax.tick_params(axis="y", labelcolor=gas_ax_color)

    nft_ax.set_ylabel("Numero di NFT", color=nft_ax_color)
    nft_ax.tick_params(axis="y", labelcolor=nft_ax_color)

    l1 = gas_ax.plot(collection_gas["total_gas_mint"], color=gas_ax_color, label="Costo totale di \\texttt{mint}")
    l2 = nft_ax.plot(collection_gas["total_num_tokens"], color=nft_ax_color, label="NFT totali")

    bottom, top = gas_ax.get_ylim()
    nft_ax.set_ylim(bottom=bottom / min_gas_mint, top=top / min_gas_mint)

    gas_ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(gas_ax.xaxis.get_major_locator()))
    fig.autofmt_xdate()

    legend = nft_ax.legend(fancybox=False, edgecolor="black", handles=l1 + l2, loc="upper left")
    legend.get_frame().set_linewidth(0.5)

    return fig


def plot_verify(collection_gas: pd.DataFrame, min_gas_verify: int, width: float, height: float) -> plt.Figure:
    fig, gas_ax = plt.subplots(figsize=(width, height))
    nft_ax = gas_ax.twinx()

    gas_ax_color = "tab:blue"
    nft_ax_color = "tab:green"

    gas_ax.set_xlabel("Data")

    gas_ax.set_ylabel("Gas", color=gas_ax_color)
    gas_ax.tick_params(axis="y", labelcolor=gas_ax_color)

    nft_ax.set_ylabel("Numero di NFT / Trasferimenti", color=nft_ax_color)
    nft_ax.tick_params(axis="y", labelcolor=nft_ax_color)

    l1 = gas_ax.plot(collection_gas["total_gas_verify"], color=gas_ax_color, label="Costo totale di \\texttt{verify}")
    l2 = nft_ax.plot(collection_gas["total_num_tokens"], color=nft_ax_color, label="NFT totali")
    l3 = nft_ax.plot(
        collection_gas["total_num_transfers"], color=nft_ax_color, label="Trafserimenti totali", linestyle="--"
    )

    bottom, top = gas_ax.get_ylim()
    nft_ax.set_ylim(bottom=bottom / min_gas_verify, top=top / min_gas_verify)

    gas_ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(gas_ax.xaxis.get_major_locator()))
    fig.autofmt_xdate()

    legend = nft_ax.legend(fancybox=False, edgecolor="black", handles=l1 + l2 + l3, loc="upper left")
    legend.get_frame().set_linewidth(0.5)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("collection_gas_csv_path", type=str)
    parser.add_argument("gas_csv_path", type=str)
    parser.add_argument("out_plot_path", type=str)
    parser.add_argument("--plot", "-p", type=str, default="both", choices=["mint", "verify", "both"])
    parser.add_argument("--textwidth", "-t", type=float, default=5.9066)
    parser.add_argument("--aspect_ratio", "-r", type=float, default=0.75)
    parser.add_argument("--scale", "-s", type=float, default=1.0)
    args = parser.parse_args()

    collection_gas = pd.read_csv(args.collection_gas_csv_path, index_col=0)
    collection_gas.set_index(pd.to_datetime(collection_gas.index, unit="s"), inplace=True)
    gas = pd.read_csv(args.gas_csv_path, index_col=0)
    width, height = compute_plot_size(args.textwidth, args.aspect_ratio, args.scale)

    set_pgfplot_style()

    if args.plot in ["mint", "both"]:
        mint_fig = plot_mint(collection_gas, gas["gas_mint"].min(), width, height)
        make_dirs(args.out_plot_path)

        if args.plot == "both":
            mint_fig.savefig("_mint".join(os.path.splitext(args.out_plot_path)))
        else:
            mint_fig.savefig(args.out_plot_path)

    if args.plot in ["verify", "both"]:
        verify_fig = plot_verify(collection_gas, gas["gas_verify"].min(), width, height)
        make_dirs(args.out_plot_path)

        if args.plot == "both":
            mint_fig.savefig("_verify".join(os.path.splitext(args.out_plot_path)))
        else:
            verify_fig.savefig(args.out_plot_path)
