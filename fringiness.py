from __future__ import division, print_function

import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA

import json

import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.palettes import viridis
from bokeh.models import Span

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

def embedding_plot_bokeh(x, y, s):
    """
    Draws a Bokeh scatter plot with the color indicating the fringiness. The 
    first row is indicated in red.

    Parameters
    ----------
    x : array_like
        x coordinates of the points.
    y : array_like
        y coordinates of the points.
    s : array_like
        fringiness of the points.

    Returns
    -------
    bokeh.plotting.figure.Figure
    """
    col_ind = np.digitize(s, np.linspace(s.min(), s.max(), 20))
    colormap = viridis(21)
    colors = [colormap[int(ind)] for ind in col_ind]
    colors[0] = 'red'

    p = figure(title="Article embedding", tools=['tap','pan','zoom_in',
        'zoom_out','wheel_zoom'])
    p.circle(x, y, fill_color=colors, line_color=colors)

    return p

def histogram_bokeh(s):
    p=figure(title='Histogram')
    bins=20
    h, e = np.histogram(s, density=True, bins=bins)

    colors = viridis(bins)

    p.quad(top=h, bottom=0, left=e[:-1], right=e[1:], fill_color=colors)
    vline = Span(location=s[0], dimension='height', line_color='red', 
                 line_width=3)
    p.add_layout(vline)

    return p

def res_to_matrix(res):
    all_keys = set(res['point'])

    for env in res['environs']:
        all_keys |= env['entities'].keys()
    reference = np.array(list(all_keys))
    v = np.zeros(len(reference))
    v[np.hstack([np.where(reference==key)
                 for key in res['point']])[0]] = 1
    vs = [v]
    for env in res['environs']:
        v = np.zeros(len(reference))
        try:
            v[np.hstack([np.where(reference==key)
                         for key in env['entities']])[0]] = 1
            vs.append(v)
        except ValueError:
            pass

    vs = np.vstack(vs)
    return vs

def text_to_matrix(text):
    return res_to_matrix(run(text))
