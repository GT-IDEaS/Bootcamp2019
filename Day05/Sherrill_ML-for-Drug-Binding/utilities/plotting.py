"""Plotting utilities for binding curves of total energies & SAPT components"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy as sp

def sapt_bars(data, index, bar_options, plot_options, savename=None):
    """Plots SAPT breakdown of IE as a bar chart.  Can plot multiple bar groups
    side-by-side.
    
    Arguments:
    <list> data : List of Pandas Series/DataFrame objects with SAPT components to plot
    <list> index : List of <str> labels for each bar.
    <dict> bar_options : Dictionary of bar options for Matplotlib bars.
    	<key: str> 'align' : <str> Alignment of bars within group.
        <key: str> 'colors' : <list> Colors to use for bars.
    <dict> plot_options : Dictionary of plot options.
    	<key: str> 'xlim' : <list> Limits for x-axis.  If None, determined automatically.
        <key: str> 'ylim' : <list> Limits for y-axis.  If None, determined automatically.
    	<key: str> 'group_labels' : <list> Labels for bar groupings, if len(data) > 1
        <key: str> 'xlabel' : <str> x-axis label
        <key: str> 'ylabel' : <str> y-axis label
        <key: str> 'title' : <str> Plot title
    <str> savename : Filename to save plot to.  Defalut: None (show plot only)
    """
    fig = plt.figure()
    
    # Default SAPT component colors
    try:
        colors = bar_options['colors']
    except KeyError:
        colors = ['r','g','b','orange','k']
    # Error Bars?
    errorbars = False if 'errorbars' not in plot_options.keys() else True
        
    # Plot data
    for i in range(len(data)):
        if errorbars:
            if plot_options['errorbars']['emax'][i] is not None:
                yerr = [plot_options['errorbars']['emax'][i], plot_options['errorbars']['emin'][i]]
                errkw = plot_options['errorbars']['errorkw']
                if np.allclose(np.array(list(yerr[0])), np.array(list(yerr[1]))):
                        yerr = None
                        errkw = {}
            else:
                yerr = None
                errkw = {}
        else:
            yerr = None
            errkw = {}
        
        tix = np.arange(len(data[i]))
        plt.bar(tix + (i)*len(data[0]) + (i), data[i], 
                align=bar_options['align'], color=colors,
                yerr=yerr, error_kw=errkw)
        plt.hlines(0, tix[0] + i*len(data[0]) + (i-0.4), tix[-1] + i*len(data[0]) + (i+0.4), linewidth=1)
        upper = range(len(data))[-1]
    if plot_options['xlim'] is None:
        plt.xlim(-1, tix[-1] + upper*len(data[0]) + upper + 1)
    else: plt.xlim(plot_options['xlim'])
    if plot_options['ylim'] is not None: plt.ylim(plot_options['ylim'])
    # Grid?
    if plot_options['grid'] is not None:
        ax = plt.gca()
        ax.set_axisbelow(True)
        if plot_options['grid'] == 'major':
            ax.yaxis.grid(True, which='major', color='k', linestyle='-', linewidth=1)
        if plot_options['grid'] == 'minor':
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.grid(True, which='major', color='k', linestyle='-', linewidth=1)
            ax.yaxis.grid(True, which='minor', color='k', linestyle='-', linewidth=0.15)
        if plot_options['grid'] == 'both':
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator())
            ax.yaxis.grid(True, which='major', color='k', linestyle='-', linewidth=1)
            ax.yaxis.grid(True, which='minor', color='k', linestyle='-', linewidth=0.15)
    # Manual legend
    patches = []
    for i in range(len(index)):
        patches.append(mpatches.Patch(color=colors[i], label=index[i]))
    # Legend Position
    if 'lgdcols' in plot_options.keys():
        lgd = plt.legend(loc='center left', handles=patches, ncol=plot_options['lgdcols'], fancybox=True, bbox_to_anchor=(1, 0.5))
    else:
        lgd = plt.legend(loc='center left', handles=patches, ncol=1, fancybox=True, bbox_to_anchor=(1, 0.5))
    # Axis labels
    mid = (tix[-1] - tix[0]) / 2.
    tick_x = []
    for i in range(len(plot_options['group_labels'])):
        tick_x.append(mid + i*len(data[i]) + i)
    plt.xticks(tick_x, plot_options['group_labels'])
    plt.xlabel(plot_options['xlabel'])
    plt.ylabel(plot_options['ylabel'])
    if plot_options['title'] is not None: plt.title(plot_options['title'])
    if savename is not None: plt.savefig(savename, transparent=True, bbox_extra_artists=(lgd,), 
                                         bbox_inches='tight')
