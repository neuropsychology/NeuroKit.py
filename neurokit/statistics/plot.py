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
def plot_polarbar(scores, labels=None, labels_size=15, colors="default", distribution_means=None, distribution_sds=None, treshold=1.28, fig_size=(15, 15)):
    """
    Polar bar chart.

    Parameters
    ----------
    scores : list or dict
        Scores to plot.
    labels : list
        List of labels to be used for ticks.
    labels_size : int
        Label's size.
    colors : list or str
        List of colors or "default".
    distribution_means : int or list
        List of means to add a range ribbon.
    distribution_sds : int or list
        List of SDs to add a range ribbon.
    treshold : float
        Limits of the range ribbon (in terms of standart deviation from mean).
    fig_size : tuple
        Figure size.


    Returns
    ----------
    plot : matplotlig figure
        The figure.

    Example
    ----------
    >>> import neurokit as nk
    >>> fig = nk.plot_polarbar(scores=[1, 2, 3, 4, 5], labels=["A", "B", "C", "D", "E"], distribution_means=3, distribution_sds=1)
    >>> fig.show()

    Notes
    ----------
    *Authors*

    - `Dominique Makowski <https://dominiquemakowski.github.io/>`_

    *Dependencies*

    - matplotlib
    - numpy
    """


    # Sanity check
    if isinstance(scores, dict):
        if labels is None:
            labels = list(scores.keys())
        try:
            scores = [scores[key] for key in labels]
        except KeyError:
            print("NeuroKit Error: plot_polarbar(): labels and scores keys not matching. Recheck them.")



    # Parameters
    if colors == "default":
        if len(scores) < 9:
            colors = ["#f44336", "#9C27B0", "#3F51B5","#03A9F4", "#009688", "#8BC34A", "#FFEB3B", "#FF9800", "#795548"]
        else:
            colors = None
    if labels is None:
        labels = range(len(scores))

    N = len(scores)
    theta = np.linspace(0.0, -2 * np.pi, N, endpoint=False)
    width = 2 * np.pi / N



    # Main
    plot = plt.figure(figsize=fig_size)

    layer1 = plot.add_subplot(111, projection="polar")
    bars1 = layer1.bar(theta+np.pi/len(scores), scores, width=width, bottom=0.0)

    layer1.yaxis.set_ticks(range(11))
    layer1.yaxis.set_ticklabels([])

    layer1.xaxis.set_ticks(theta+np.pi/len(scores))
    layer1.xaxis.set_ticklabels(labels, fontsize=labels_size)

    for index, bar in enumerate(bars1):
        if colors is not None:
            bar.set_facecolor(colors[index])
        bar.set_alpha(1)

    # Layer 2
    if distribution_means is not None and distribution_sds is not None:

        # Sanity check
        if isinstance(distribution_means, int):
            distribution_means = [distribution_means]*N
        if isinstance(distribution_sds, int):
            distribution_sds = [distribution_sds]*N

        # TODO: add convertion if those parameter are dict


        bottoms, tops = normal_range(np.array(distribution_means), np.array(distribution_sds), treshold=treshold)
        tops = tops - bottoms

        layer2 = plot.add_subplot(111, polar=True)
        bars2 = layer2.bar(theta, tops, width=width, bottom=bottoms, linewidth=0)
        layer2.xaxis.set_ticks(theta+np.pi/len(scores))
        layer2.xaxis.set_ticklabels(labels, fontsize=labels_size)

        for index, bar in enumerate(bars2):
            bar.set_facecolor("#607D8B")
            bar.set_alpha(0.3)

    return(plot)
