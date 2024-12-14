import locale

import matplotlib
import matplotlib.pyplot as plt
import scienceplots


def set_pgfplot_style():
    locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")
    plt.style.use(["science", "grid"])
    matplotlib.use("pgf")
    matplotlib.rcParams.update(
        {
            "pgf.texsystem": "pdflatex",
            "font.family": "serif",
            "text.usetex": True,
            "pgf.rcfonts": False,
        }
    )


def compute_plot_size(textwidth, aspect_ratio, scale=1.0):
    width = textwidth * scale
    height = width * aspect_ratio

    return (width, height)
