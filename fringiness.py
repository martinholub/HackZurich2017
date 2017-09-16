from __future__ import division, print_function

import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt

def fringiness(data, distance_metric='cosine'):
    """Calculates the fringiness of news articles.

    The fringiness is a number between 0 and 1 that rates each news article 
    based on how well it is embedded in the context.

    Parameters
    ----------
    data : ndarray
        Matrix with every row representing a news article and every column a 
        feature.
    distance_metric : str
        Distance metric to use to compute the differences between the news 
        articles. Supports all distance metrics in sklearn [1]

    Returns
    -------
    array_like
        x coordinate of the embedding
    array_like
        y coordinate of the embedding
    array_like
        Fringiness score for each news article.

    References
    ----------
    .. [1] https://docs.scipy.org/doc/scipy/reference/spatial.distance.html#module-scipy.spatial.distance
    """
    normalised_data = (data.T / np.linalg.norm(data, axis=1)).T
    pairwise_distances = squareform(pdist(normalised_data, distance_metric))
    
    pca = PCA()
    loadings = pca.fit_transform(pairwise_distances)
    sum_sq_loadings = np.sum(loadings**2 * pca.explained_variance_ratio_, 
                             axis=1)
    sum_sq_loadings /= sum_sq_loadings.max()
    return loadings.T[0], loadings.T[1], sum_sq_loadings

import json

def to_json(x, y, s, filename=None):
    d = [{'x':xx,'y':yy,'s':ss} for xx, yy, ss in zip(x, y, s)]
    if filename is not None:
        with open(filename,'w') as f:
            json.dump(d, f)
    return d


def embedding_plot_mpl(x, y, s):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x, y, c=s, vmin=0, vmax=1)
    ax.axis('off')
    return fig

from bokeh.plotting import figure, show
from bokeh.palettes import viridis

def embedding_plot_bokeh(x, y, s):
    col_ind = np.digitize(s, np.linspace(s.min(), s.max(), 20))
    colormap = viridis(21)
    colors = [colormap[int(ind)] for ind in col_ind]
    colors[0] = 'red'

    p = figure(title="Article embedding", tools=['tap','pan','zoom_in',
        'zoom_out','wheel_zoom'])
    p.circle(x, y, fill_color=colors, line_color=colors)

    return p
