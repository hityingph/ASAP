'''
I adapt some of the suff from:
Copyright 2017 Alexandre Day
'''

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patheffects as PathEffects
from .plot_colors import COLOR_PALETTE
import math

def set_nice_font(size = 18, usetex=False):
    font = {'family' : 'serif', 'size'   : size}
    plt.rc('font', **font)
    if usetex is True:
        plt.rc('text', usetex=True)
    
def plot_density_map(X, z,
                xlabel=None, ylabel=None, clabel=None, label=None,
                centers=None,
                psize=20,
                out_file=None, title=None, show=True, cmap='coolwarm',
                remove_tick=False,
                use_perc=False,
                rasterized = True,
                fontsize = 15,
                vmax = None,
                vmin = None
                ):
    """Plots a 2D density map given x,y coordinates and an intensity z for
    every data point

    Parameters
    ----------
    X : array-like, shape=[n_samples,2]
        Input points.
    z : array-like, shape=[n_samples]
        Density at every point

    Returns
    -------
    None
    """
    x, y = X[:,0], X[:,1]
    
    fontsize = fontsize

    if use_perc :
        n_sample = len(x)
        outlier_window = int(0.05 * n_sample)

        argz = np.argsort(z)
        bot_outliers = argz[:outlier_window]
        top_outliers = argz[-outlier_window:]
        typical = argz[outlier_window:-outlier_window]

        # plot typical
        plt.scatter(x[typical],y[typical],c=z[typical],cmap=cmap,s=psize, alpha=1.0,rasterized=rasterized)
        cb=plt.colorbar()
        # plot bot outliers (black !)
        plt.scatter(x[bot_outliers],y[bot_outliers],c='black',s=psize,alpha=1.0,rasterized=rasterized)
        # plot top outliers (orange !)
        plt.scatter(x[top_outliers],y[top_outliers],c='red',s=psize,alpha=1.0,rasterized=rasterized)

    else:
        if label is not None:
            plt.scatter(x,y,c=z,cmap=cmap,s=psize,alpha=1.0,rasterized=rasterized,label=label,vmax=vmax,vmin=vmin)
        else:
            plt.scatter(x,y,c=z,cmap=cmap,s=psize,alpha=1.0,rasterized=rasterized, vmax=vmax,vmin=vmin)
    
        cb=plt.colorbar()
    
    if remove_tick:
        plt.tick_params(labelbottom='off',labelleft='off')
    
    if xlabel is not None:
        plt.xlabel(xlabel,fontsize=fontsize)
    if ylabel is not None:
        plt.ylabel(ylabel,fontsize=fontsize)
    if clabel is not None:
        cb.set_label(label=clabel,labelpad=10)
    if title is not None:
        plt.title(title,fontsize=fontsize)
    if label is not None:
        plt.legend(loc='best')
        
    if centers is not None:
        plt.scatter(centers[:,0],centers[:,1], c='lightgreen', marker='*',s=200, edgecolor='black',linewidths=0.5)
    
    if out_file is not None:
        plt.savefig(out_file)
    if show:
        plt.show()

def plot_scatter_w_label(x, y, z, psize=20, label = None):
    """Plots a 2D scatter plot given x,y coordinates and a label z for
    every data point

    Parameters
    ----------
    x,y : array-like, shape=[n_samples]
        Input points.
    z : array-like, shape=[n_samples]
        label for every point

    This plot style only looks nice when there're limited type of labels
    """
    unique_z=np.sort(np.unique(z.flatten()))
    mycol = COLOR_PALETTE()

    plt.subplots(figsize=(8,6))

    for i, zval in enumerate(unique_z):
        pos=(z.flatten()==zval)
        if label is not None:
            plt.scatter(x[pos],y[pos],s=psize,c=mycol[i], label=label[i], rasterized=True)
        else:
            plt.scatter(x[pos],y[pos],s=psize,c=mycol[i], rasterized=True)
    
    if label is not None:
        plt.legend(loc='best',fontsize=12)

    plt.tight_layout()
    plt.show()

######################################################

def plot_cluster_w_size(X, y, c,
                      xlabel=None, ylabel=None, clabel=None, title=None, 
                      w_size = True, w_label = False,
                      circle_size = 20, alpha=0.7, edgecolors=None,
                      cmap='coolwarm', vmax = None,vmin = None, psize = 2, 
                      show=True, savefile = None, fontsize =15, 
                      figsize=None,rasterized = True, remove_tick=True,
                      dpi=200, outlier=True):

    """Plots a 2D clustering plot given x,y coordinates and a label z for
    every data point

    Parameters
    ----------
    X : array-like, shape=[n_samples,2]
        Input points.
    y : array-like, shape=[n_samples]
        label for every point
    c : array-like, shape=[n_samples]
        color for every point
    """
    # get the cluster size and mean position
    from ..cluster import get_cluster_size, get_cluster_properties
    y_unique_ = np.unique(y)
    [ _, cluster_size ]  = get_cluster_size(y)
    [ _, cluster_mx ]  = get_cluster_properties(y,X[:,0],'mean')
    [ _, cluster_my ]  = get_cluster_properties(y,X[:,1],'mean')
    # remove outliers
    if outlier is True:
        y_unique = y_unique_[y_unique_ > -1]
    else:
        y_unique = y_unique_

    # start the plots
    fig, ax = plt.subplots()

    # first do a scatter plot for all samples
    cset1 = ax.scatter(X[:,0], X[:,1],  c=c[:],
            cmap=cmap, vmin=vmin, vmax=vmax, marker='o', s=psize,rasterized=rasterized)
    cbar=fig.colorbar(cset1, ax=ax)
    cbar.ax.set_ylabel(clabel)

    # the noisy points
    if outlier is True:
        # Black used for noise.
        col = [0, 0, 0, 1]
        class_member_mask = ( y == -1 )
        xy = X[class_member_mask]
        ax.plot(xy[:,0], xy[:,1], 'x', markerfacecolor=tuple(col), alpha=alpha,
             markeredgecolor='k', markersize=0.1*psize)

    for k in y_unique:
        if (cluster_size[k]>2): # we set a cutoff here
            ax.plot(cluster_mx[k],cluster_my[k], 'o', markerfacecolor='none',
                markeredgecolor='gray', markersize=10.0*(np.log(cluster_size[k])))

    if w_label is True:
        for k in y_unique:
            # Position of each label.
            txt = ax.annotate(str(k),xy=(cluster_mx[k],cluster_my[k]),
            xytext=(0,0), textcoords='offset points',
            fontsize=fontsize,horizontalalignment='center', verticalalignment='center'
            )
            txt.set_path_effects([
                PathEffects.Stroke(linewidth=5, foreground='none'),
                PathEffects.Normal()])


    xmin,xmax = plt.xlim()
    ymin,ymax = plt.ylim()
    dx = xmax - xmin
    dy = ymax - ymin
    plt.xticks([])
    plt.yticks([])
    
    if remove_tick:
        plt.tick_params(labelbottom='off',labelleft='off')
    
    if xlabel is not None:
        plt.xlabel(xlabel,fontsize=fontsize)
    if ylabel is not None:
        plt.ylabel(ylabel,fontsize=fontsize)
    if title is not None:
        plt.title(title,fontsize=fontsize)

    plt.tight_layout()
    if savefile is not None:
        if dpi is None:
            plt.savefig(savefile)
        else:
            plt.savefig(savefile,dpi=dpi)

    if show is True:
        plt.show()
        plt.clf()
        plt.close()

    return fig, ax


######################################################

def plot_cluster_w_label(X, y, Xcluster=None, 
                      show=True, savefile = None, fontsize =15, psize = 20, 
                      title=None, w_label = True, figsize=None,
                      dpi=200, alpha=0.7, edgecolors=None, cp_style=1, w_legend=False, outlier=True):
    """Plots a 2D clustering plot given x,y coordinates and a label z for
    every data point

    Parameters
    ----------
    X : array-like, shape=[n_samples,2]
        Input points.
    y : array-like, shape=[n_samples]
        label for every point
    Xcluster: center of each cluster
    """
    
    if figsize is not None:
        plt.figure(figsize=figsize)
    y_unique_ = np.unique(y)
    
    palette = COLOR_PALETTE(style=cp_style)
    idx_centers = []
    ax = plt.subplot(111)
    all_idx = np.arange(len(X))
    
    if outlier is True:
        y_unique = y_unique_[y_unique_ > -1]
    else:
        y_unique = y_unique_
    n_center = len(y_unique)

    for i, yu in enumerate(y_unique):
        pos=(y==yu)
        Xsub = X[pos]
        plt.scatter(Xsub[:,0],Xsub[:,1],c=palette[i], s=psize, rasterized=True, alpha=alpha, edgecolors=edgecolors, label = yu)
        
        if Xcluster is not None:
            Xmean = Xcluster[i]
        else:
            Xmean = np.mean(Xsub, axis=0)
        #Xmean = np.mean(Xsub,axis=0)
        idx_centers.append(all_idx[pos][np.argmin(np.linalg.norm(Xsub - Xmean, axis=1))])

    if outlier is True:
        color_out = {-3 : '#ff0050', -2 : '#9eff49', -1 : 'gray'}
        for yi in [-3, -2, -1]:
            pos = (y == yi)
            if np.count_nonzero(pos) > 0:
                Xsub = X[pos]
                plt.scatter(Xsub[:,0],Xsub[:,1],c=color_out[yi], s=psize, rasterized=True, alpha=alpha, marker="2",edgecolors=edgecolors, label = yi)
            

    if w_label is True:
        centers = X[idx_centers]
        for xy, i in zip(centers, y_unique) :
            # Position of each label.
            txt = ax.annotate(str(i),xy,
            xytext=(0,0), textcoords='offset points',
            fontsize=fontsize,horizontalalignment='center', verticalalignment='center'
            )
            txt.set_path_effects([
                PathEffects.Stroke(linewidth=5, foreground="w"),
                PathEffects.Normal()])
        
    
    xmin,xmax = plt.xlim()
    ymin,ymax = plt.ylim()
    dx = xmax - xmin
    dy = ymax - ymin
    plt.xticks([])
    plt.yticks([])
    
    if title is not None:
        plt.title(title,fontsize=fontsize)
    if w_legend is True:
        plt.legend(loc='best')

    plt.tight_layout()
    if savefile is not None:
        if dpi is None:
            plt.savefig(savefile)
        else:
            plt.savefig(savefile,dpi=dpi)

    if show is True:
        plt.show()
        plt.clf()
        plt.close()

    return ax

def plot_outlier_scatter(x, y, z, ax):

    cmap = plt.get_cmap('coolwarm')
    
    argz = np.argsort(z)

    n_sample = len(x)
    bot_5 = round(n_sample*0.05)
    top_5 = round(n_sample*0.95)
    mid = argz[bot_5:top_5]
    bot = argz[:bot_5]
    top = argz[top_5:]

    x_mid = x[mid]
    y_mid = y[mid]
    z_mid = z[mid]

    x_bot = x[bot]
    y_bot = y[bot]
    z_bot = z[bot]

    x_top = x[top]
    y_top = y[top]
    z_top = z[top]

    ax.scatter(x_mid, y_mid, c = z_mid, cmap = cmap, s=6)
    ax.scatter(x_bot, y_bot, c = "purple", s=4)
    ax.scatter(x_top, y_top, c = "#00FF00",s=4)
