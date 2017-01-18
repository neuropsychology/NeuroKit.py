# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def plot_polarbar(scores, labels=None, labels_size=15, colors="default", fig_size=(15, 15), show=True, save=False, path="", dpi=300):
    """
    Polar bar chart.
    Parameters
    ----------
    NA
    Returns
    ----------
    NA
    Example
    ----------
    NA
    Authors
    ----------
    Dominique Makowski
    Dependencies
    ----------
    - matplotlib
    """
    plot = plt.figure(figsize=figsize)
    if colors == "default":
        colors = ["#f44336", "#9C27B0", "#3F51B5","#03A9F4", "#009688", "#8BC34A", "#FFEB3B", "#FF9800", "#795548"]
    if labels is None:
        labels = range(scores)

    N = len(scores)
    theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    radii = scores
    width = 2 * np.pi / N

    ax = plot.add_subplot(111, polar=True)

    bars = ax.bar(theta, radii, width=width, bottom=0.0)
    ax.yaxis.set_ticks(range(11))
    ax.yaxis.set_ticklabels([])
    ax.xaxis.set_ticks(theta+1*np.pi)
    ax.xaxis.set_ticklabels(labels, fontsize=labels_size)

    for index, bar in enumerate(bars):
        bar.set_facecolor(colors[index])

    if show is True:
        plot.show()
    if save is not False:
        plot.savefig(path + save + ".png", dpi=dpi)

    return(plot)
