#!/usr/bin/python3

import numpy as np
import argparse
import matplotlib.pyplot as plt
from matplotlib import cm
from lib import kpca, kerneltorho, kerneltodis
from lib import get_cluster_size, get_cluster_properties
from lib import DBCluster, sklearn_DB

def main(fkmat, ftags, prefix, kpca_d, pc1, pc2):

    # if it has been computed before we can simply load it
    try:
        eva = np.genfromtxt(fkmat, dtype=float)
    except: raise ValueError('Cannot load the kernel matrix')

    print("loaded",fkmat)
    if (ftags != 'none'): 
        tags = np.loadtxt(ftags, dtype="str")
        ndict = len(tags)

    # charecteristic difference in k_ij
    sigma_kij = np.std(eva[:,:])
    # do a low dimensional projection to visualize the data
    proj = kpca(eva,kpca_d)

    # now we do the clustering
    # option 1: do on the projected coordinates
    #trainer = sklearn_DB('euclidean')
    #do_clustering = DBCluster(sigma_kij, 5, trainer)
    #do_clustering.fit(proj)
    # option 2: do directly on kernel matrix.
    dmat = kerneltodis(eva)
    trainer = sklearn_DB('precomputed')
    do_clustering = DBCluster(sigma_kij, 5, trainer)
    do_clustering.fit(dmat)
    #
    labels_db = do_clustering.get_cluster_labels()
    n_clusters = do_clustering.get_n_cluster()

    # save
    np.savetxt(prefix+"-cluster-label.dat", labels_db, fmt='%d')

    [ unique_labels, cluster_size ]  = get_cluster_size(labels_db[:])
    # center of each cluster
    [ unique_labels, cluster_x ]  = get_cluster_properties(labels_db[:],proj[:,pc1],'mean')
    [ unique_labels, cluster_y ]  = get_cluster_properties(labels_db[:],proj[:,pc2],'mean')

    # color scheme
    plotcolor = labels_db
    [ plotcolormin, plotcolormax ] = [ 0, n_clusters ]
    colorlabel = 'a total of' + str(n_clusters) + ' clusters'

    # make plot
    fig, ax = plt.subplots()
    pcaplot = ax.scatter(proj[:,pc1],proj[:,pc2],c=plotcolor[:],
                    cmap=cm.gnuplot,vmin=plotcolormin, vmax=plotcolormax)
    cbar = fig.colorbar(pcaplot, ax=ax)
    cbar.ax.set_ylabel(colorlabel)

    # plot the clusters with size propotional to population
    for k in unique_labels:
        if (k >=0):
            ax.plot(cluster_x[k],cluster_y[k], 'o', markerfacecolor='none',
                markeredgecolor='gray', markersize=10.0*(np.log(cluster_size[k])))

    # project the known structures
    if (ftags != 'none'):
        for i in range(ndict):
            ax.scatter(proj[i,pc1],proj[i,pc2],marker='^',c='black')
            ax.annotate(tags[i], (proj[i,pc1], proj[i,pc2]))

    plt.title('KPCA and clustering for: '+prefix)
    plt.xlabel('pc1')
    plt.ylabel('pc2')
    fig.set_size_inches(18.5, 10.5)
    plt.show()
    fig.savefig('Clustering_4_'+prefix+'.png')
##########################################################################################
##########################################################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-kmat', type=str, required=True, help='Location of kernel matrix file. You can use gen_kmat.py to compute it.')
    parser.add_argument('-tags', type=str, default='none', help='Location of tags for the first M samples')
    parser.add_argument('--prefix', type=str, default='ASAP', help='Filename prefix')
    parser.add_argument('--d', type=int, default=10, help='number of the principle components to keep')
    parser.add_argument('--pc1', type=int, default=0, help='Plot the projection along which principle axes')
    parser.add_argument('--pc2', type=int, default=1, help='Plot the projection along which principle axes')
    args = parser.parse_args()

    main(args.kmat, args.tags, args.prefix, args.d, args.pc1, args.pc2)

