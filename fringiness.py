from __future__ import division, print_function

import numpy as np
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA

import json

#import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.palettes import viridis
from bokeh.models import Span, HoverTool
from bokeh.models.sources import ColumnDataSource
import pandas as pd
from IPython.core.debugger import set_trace
import data_getter

from data_getter import *

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
    s = pairwise_distances[0] < np.mean(pairwise_distances[0])
    
    pca = PCA()
    loadings = pca.fit_transform(pairwise_distances[s,:][:,s])
    sum_sq_loadings = np.sum(loadings**2 * pca.explained_variance_ratio_, 
                             axis=1)
    sum_sq_loadings -= sum_sq_loadings.min()
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
    
def hex_color(color_float):
    # Returns Hex color code
    return str(hex(int(color_float * 255))).lstrip('0x').zfill(2).upper()

def vertohex(x, y):
    '''
    Computes distance from centroid for list of x and y coordinates and gives hex value for coloring by distance from center.
    '''
    centroid = (np.mean(x), np.mean(y))
    #X, Y = np.meshgrid(x, y)
    R = np.sqrt((x - centroid[0])**2 + (y - centroid[1])**2)
    maxR = np.amax(R)
    
    cmap_cust = (plt.cm.viridis(R / maxR))
    hex_color_codes = []
    for (v,r,d,_) in cmap_cust:
        hex_color_codes.append(''.join(['#',
                                      hex_color(v),
                                      hex_color(r),
                                      hex_color(d)]))
    dists = ["{:0.2f}".format(x/maxR) for x in R]
    return dists, hex_color_codes

def embedding_plot_bokeh(x, y, s, res):
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
    # Produce annotations
    _, idxer = res_to_matrix(res)
    (ents, tit) = res_to_annot(res, idxer)
    
    # Generate colors and some annotations
    
    if not any(s):
        centroid , colors = vertohex(x, y)
    else:
        col_ind = np.digitize(s, np.linspace(s.min(), s.max(), 20))
        colormap = viridis(21)
        colors = [colormap[int(ind)] for ind in col_ind]
        colors[0] = 'red'

    # Define tools
    toolbox = "tap, pan, wheel_zoom, box_zoom, reset, box_select, lasso_select"
    # Define hover window
    
    # create a new plot with the tools, explicit ranges and some custom design
    p = figure(plot_width= 1080, plot_height= 640, tools= [toolbox], title="Mouse over the dots")
    p.axis.visible = False
    p.ygrid.grid_line_color = None
    p.xgrid.grid_line_color = None

    # p.circle(x, y, fill_color=colors,  fill_alpha=0.6, line_color = None)
    p = plot_with_hover(p, x, y, s, colors, ents, tit)
    
    return p

def plot_with_hover(plot, x, y, f, colors, entities, title):
    '''
    Add hover over individual datapoints.
    We use dirty trick of plotting invisible scatter points so that we can use exisitng plot.
    doc, TBA
    '''

    # Compute distance from current article in terms of first two principal components
    centroid = (x[0], y[0])
    R = np.sqrt((x - centroid[0])**2 + (y - centroid[1])**2)
    maxR = np.amax(R)
    dists = ["{:0.2f}".format(x/maxR) for x in R]
    
    # Get number of entities from for each article = datapoint
    numEnts = [len(en) for en in entities]
    
    # Create dataframe holding all the data that we want to appear on the final plot, including hover
    d = {'x': x,
        'y': y,
        'f': f,
        'ents': entities,
        'numEnts': numEnts,
        'dists': dists,
        'tit': title}
    # works also for series of different length
    plot_df = dict([ (k, pd.Series(v)) for k,v in d.items() ])
    
    # Plot empty circles and specify source. This enables us to add hover.
    plot.circle('x',
                'y', 
                fill_color= colors,
                fill_alpha=0.6,
                radius = 0.025,
                line_color = None,
                source = ColumnDataSource(data = plot_df))
    
    # Add Hover tooltips    
    hover = gimmeHover()
    plot.add_tools(hover)
    
    return plot
def gimmeHover():

    cols = ['f', 'ents', 'numEnts', 'dists', 'tit']
    names = ['F', 'Entities', '# of Entities', 'Dsitance from current', 'Tile']
    ttips_pairs = [(n, '@' + v) for (n, v) in zip(names, cols)]
    
    hover = HoverTool(tooltips = """
    <div style = "max-width: 750px">
        <div>
            <span style="font-size: 28px; font-weight: bold;">F = </span>
            <span style="font-size: 28px; font-weight: bold;">@f</span>
        </div>
        <div>
            <span style="font-size: 18px; font-weight: bold;">Title:<br/></span>
            <span style="font-size: 18px;">@tit</span>
        </div>
        <div>
            <span style="font-size: 18px; font-weight: bold;">Entities:<br/></span>
            <span style="font-size: 18px;">@ents</span>
        </div>
        <div>
            <span style="font-size: 18px; font-weight: bold;">No. of Entities = </span>
            <span style="font-size: 18px;">@numEnts</span>
        </div>
        <!--
        <div>
            <span style="font-size: 12px; font-weight: bold;">Distance= </span>
            <span style="font-size: 10px;">@dists</span>
        </div>
        <div>
            <span style="font-size: 12px; font-weight: bold;">(x,y) </span>
            <span style="font-size: 10px;">($x, $y) </span>
        </div>
        -->
    </div>
    """)
    return hover
    
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

def keys(env):
    keys = set()
    keys |= env['entities'].keys()
    keys |= env['tags'].keys()
    keys |= env['topics'].keys()
    return keys

def res_to_matrix(res):
    all_keys = set()
    l = [res['point']] + res['environs']
    for env in l:
        all_keys |= keys(env)
    reference = np.array(list(all_keys))
    idxer = np.ones(len(l), dtype = bool)
    
    vs = []
    for it, env in enumerate(l):
        v = np.zeros(len(reference))
        try:
            s = np.hstack([np.where(reference==key)
                           for key in keys(env)]) 
            if np.sum(s) >= 1:
                v[s] = 1
                vs.append(v)
        except ValueError:
            idxer[it] = False;
            pass

    vs = np.vstack(vs)
    return vs, idxer

def text_to_matrix(text):
    return res_to_matrix(data_getter.run(text))

def text_to_fringiness(text):
    return fringiness(res_to_matrix(run(text)))

def random_data(n, m, sparsity=0.8, mean=2, distribution='poisson'):
    """
    Parameters
    ----------
    n : int
        number of samples
    m : int
        number of features
    sparsity : float between 0 and 1
        sets the ratio of zero values in the resulting matrix.
    distribution : str
        supported are 'poisson' and 'normal'
    """
    if distribution == 'poisson':
        r = np.random.poisson(mean, (n, m))
    elif distribution == 'normal':
        r = np.random.randn(n*m).reshape((n,m)) + mean
    p = np.random.rand(n*m).reshape((n,m))
    r[p<sparsity] = 0
    return r

def res_to_annot(res, idxer):
    # Take resources .json and extract topics and entites
    # res is a result of data_getter.run(text)
    ents = []
    tit = []
    l = [res['point']] + res['environs']
    l = [e for (id, e) in zip(idxer, l) if id]
    for env in l:
        ents.append(list(env['entities'].keys()))
        try:
            tit.append([env['title']])
        except:
            tit.append([])
    
    return (ents, tit)
