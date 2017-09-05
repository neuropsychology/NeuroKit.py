# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import sklearn



# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
# ==============================================================================
def feature_reduction(data, method, n_features):
    """
    Feature reduction.

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
    - sklearn
    """
    if method == "PCA":
        feature_red_method = sklearn.decomposition.PCA(n_components=n_features)
        data_processed = feature_red_method.fit_transform(data)

    elif method == "agglom":
        feature_red_method = sklearn.cluster.FeatureAgglomeration(n_clusters=n_features)
        data_processed = feature_red_method.fit_transform(data)

    elif method == "ica":
        feature_red_method = sklearn.decomposition.FastICA(n_components=n_features)
        data_processed = feature_red_method.fit_transform(data)

    elif method == "kernelPCA":
        feature_red_method = sklearn.decomposition.KernelPCA(n_components=n_features, kernel='linear')
        data_processed = feature_red_method.fit_transform(data)

    elif method == "kernelPCA":
        feature_red_method = sklearn.decomposition.KernelPCA(n_components=n_features, kernel='linear')
        data_processed = feature_red_method.fit_transform(data)

    elif method == "sparsePCA":
        feature_red_method = sklearn.decomposition.SparsePCA(n_components=n_features)
        data_processed = feature_red_method.fit_transform(data)

    elif method == "incrementalPCA":
        feature_red_method = sklearn.decomposition.IncrementalPCA(n_components=n_features)
        data_processed = feature_red_method.fit_transform(data)

    elif method == "nmf":
        if np.min(data) < 0:
            data -= np.min(data)
        feature_red_method = sklearn.decomposition.NMF(n_components=n_features)
        data_processed = feature_red_method.fit_transform(data)

    else:
        feature_red_method = None
        data_processed = data.copy()

    return(data_processed)