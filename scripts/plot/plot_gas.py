import argparse
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(os.getcwd())

from scripts.utils.matplotlib_utils import set_pgfplot_style, compute_plot_size
from scripts.utils.make_dirs import make_dirs


def plot_mint(gas: pd.DataFrame, max_gas_mint: pd.DataFrame, width: float, height: float) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlabel("Numero di NFT")
    ax.set_ylabel("Gas")
    ax.set_xscale("log")

    ax.plot(gas["gas_mint"], label="Costo di \\texttt{mint}")
    ax.plot(max_gas_mint["max_gas_mint"].dropna(), label="Costo massimale di \\texttt{mint}", drawstyle="steps")

    legend = ax.legend(fancybox=False, edgecolor="black", loc="upper left")
    legend.get_frame().set_linewidth(0.5)

    return fig


def plot_verify(gas: pd.DataFrame, max_gas_verify: pd.DataFrame, width: float, height: float) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlabel("Numero di NFT")
    ax.set_ylabel("Gas")
    ax.set_xscale("log")

    ax.plot(gas["gas_verify"], label="Costo di \\texttt{verify}")
    ax.plot(max_gas_verify["max_gas_verify"].dropna(), label="Costo massimale di \\texttt{verify}", drawstyle="steps")

    legend = ax.legend(fancybox=False, edgecolor="black", loc="upper left")
    legend.get_frame().set_linewidth(0.5)

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gas_csv_path", type=str)
    parser.add_argument("max_gas_csv_path", type=str)
    parser.add_argument("out_plot_path", type=str)
    parser.add_argument("--plot", "-p", type=str, default="both", choices=["mint", "verify", "both"])
    parser.add_argument("--textwidth", "-t", type=float, default=5.9066)
    parser.add_argument("--aspect_ratio", "-r", type=float, default=0.75)
    parser.add_argument("--scale", "-s", type=float, default=1.0)

    args = parser.parse_args()

    gas = pd.read_csv(args.gas_csv_path, index_col=0)
    max_gas = pd.read_csv(args.max_gas_csv_path, index_col=0)
    width, height = compute_plot_size(args.textwidth, args.aspect_ratio, args.scale)

    set_pgfplot_style()

    if args.plot in ["mint", "both"]:
        mint_fig = plot_mint(gas, max_gas, width, height)
        make_dirs(args.out_plot_path)

        if args.plot == "both":
            mint_fig.savefig("_mint".join(os.path.splitext(args.out_plot_path)))
        else:
            mint_fig.savefig(args.out_plot_path)

    if args.plot in ["verify", "both"]:
        verify_fig = plot_verify(gas, max_gas, width, height)
        make_dirs(args.out_plot_path)

        if args.plot == "both":
            mint_fig.savefig("_verify".join(os.path.splitext(args.out_plot_path)))
        else:
            verify_fig.savefig(args.out_plot_path)
