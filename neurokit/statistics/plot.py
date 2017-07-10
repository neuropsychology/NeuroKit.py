# -*- coding: utf-8 -*-
from .statistics import normal_range

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def plot_polarbar(scores, labels=None, labels_size=15, colors="default", distribution_means=None, distribution_sds=None, treshold=1.28, fig_size=(15, 15), show=True, save=False, path="", dpi=300):
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

    # Parameters
    if colors == "default":
        colors = ["#f44336", "#9C27B0", "#3F51B5","#03A9F4", "#009688", "#8BC34A", "#FFEB3B", "#FF9800", "#795548"]
    if labels is None:
        labels = range(scores)

    N = len(scores)
    theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    width = 2 * np.pi / N



    # Main
    plot = plt.figure(figsize=fig_size)

    layer1 = plot.add_subplot(111, polar=True)
    bars1 = layer1.bar(theta, scores, width=width, bottom=0.0)

    layer1.yaxis.set_ticks(range(11))
    layer1.yaxis.set_ticklabels([])

    layer1.xaxis.set_ticks(theta+np.pi/len(scores))
    layer1.xaxis.set_ticklabels(labels, fontsize=labels_size)

    for index, bar in enumerate(bars1):
        bar.set_facecolor(colors[index])
        bar.set_alpha(1)

    # Layer 2
    if distribution_means is not None and distribution_sds is not None:

        bottoms, tops = normal_range(np.array(distribution_means), np.array(distribution_sds), treshold=treshold)
        tops = tops - bottoms

        layer2 = plot.add_subplot(111, polar=True)
        bars2 = layer2.bar(theta, tops, width=width, bottom=bottoms, linewidth=0)
        layer2.yaxis.set_ticks(range(11))
        layer2.yaxis.set_ticklabels([])

        for index, bar in enumerate(bars2):
            bar.set_facecolor("#607D8B")
            bar.set_alpha(0.3)



    if show is True:
        plot.show()
    if save is not False:
        plot.savefig(path + save + ".png", dpi=dpi)

    return(plot)
