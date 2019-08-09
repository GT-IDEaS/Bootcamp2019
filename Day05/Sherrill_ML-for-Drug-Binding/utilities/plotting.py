"""Plotting utilities for binding curves of total energies & SAPT components"""

import matplotlib.pyplot as plt
import seaborn as sns
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

def violin(df, options, saveas=None):
    fig = plt.figure(figsize=(9,6))
    ax = plt.gca()
    sns.violinplot(data=df, 
                   inner='quartile', 
                   palette='Set2',
                   scale="count"
                  )
    
    # Plot labels
    plt.ylabel(options['labels']['y axis'], size=14)
    ax.set_ylim(bottom=-15)
    plt.title(options['labels']['title'])
    
    if 'inset' in options.keys(): 
        inset = ax.inset_axes(bounds=options['inset']['bounds'])
        if options['inset']['kind'] == 'box':
            boxplot(df, axis=inset, options=options['inset']['options'])
            #df.plot(kind='box', showfliers=options['inset']['options']['fliers'], 
            #    whis=options['inset']['options']['whis'], showmeans=True, ax=inset)
        elif options['inset']['kind'] == 'violin':
            if 'keep' in options['inset']['options'].keys():
                q1 = ((100 - options['inset']['options']['keep']) / 2)
                q2 = 100 - q1
                q = [q1/100, q2/100]
                trimmed = qfilter(df, filter_on='all', q=q)
            elif 'whis' in options['inset']['options'].keys():
                q = [i / 100 for i in options['inset']['options']['whis']]
                trimmed = qfilter(df, filter_on='all', q=q)
            else:
                trimmed = df
            sns.violinplot(data=trimmed, ax=inset, 
                           inner='quartile', 
                           palette='Set2', 
                           scale="count"
                          )
    plt.tight_layout()
    if saveas is not None:
        plt.savefig(saveas, transparent=True, tight_layout=True)
    
def boxplot(df, options, axis=None, saveas=None):
    
    from numbers import Number
    # Determine whiskers if not passed explicitly
    if 'whis' not in options.keys():
        if options['keep'] == 'all' and not options['fliers']:
            options['whis'] = 'range'
        elif options['keep'] == 'all' and options['fliers']:
            options['whis'] = 1.5 # Matplotlib default
        elif isinstance(options['keep'], Number):
            options['whis'] = [float(options['keep']/100), 100-float(options['keep']/100)]
        else:
            raise Exception(f"Option `keep` should be the string 'all' or a percent value.  Instead, you passed {options['keep']}, which is a {type(options['keep'])}. Better luck next time!")
            
    fig = plt.figure(figsize=(3,2))
    df.plot(kind='box', ax=axis, showfliers=options['fliers'], whis=options['whis'], showmeans=True)
    if 'labels' in options.keys():
        plt.ylabel(options['labels']['y axis'])
        plt.title(options['labels']['title'])
    plt.tight_layout()
    if saveas is not None:
        plt.savefig(saveas, transparent=True, tight_layout=True)

def psi4_ternary_wrapper(df, dispmodel='SAPT0', systems='all', **kwargs):
    """Void function wrapping Psi4 to generate SAPT ternary plots from dataframes
    
    Parameters
    ----------
    df : pandas.DataFrame
        Data with which to generate ternary figure
    dispmodel : str, optional
        Dispersion model to use for Disp term in ternary figure
        Accepted: SAPT0, D3M, D3BJ, TT
        Default: SAPT0
    systems : str or list of str, optional
        Indicates which rows of dataframe to slice on for inclusion in ternary
        Default: all
    **kwargs : optional
        Additional arguments to be passed to psi4.driver.qcdb.mpl.ternary()
    """
    from psi4.driver.qcdb.mpl import ternary as p4tern
    import pandas as pd
    idx = pd.IndexSlice

    dispcols = {'SAPT0': 'Disp', 'D3M': 'Zero3', 'D3BJ': 'BJ', 'TT': 'TT'}
    
    # Columns multiindex?
    if isinstance(df.columns, pd.MultiIndex):
        # Get SAPT terms, zip together to pass to `tern()`
        if systems == 'all':
            elst = df.loc[:, idx[dispmodel,['Elst']]].values
            ind =  df.loc[:, idx[dispmodel,['Ind']]].values
            disp = df.loc[:, idx[dispmodel,[dispcols[dispmodel]]]].values
        else:
            elst = df.loc[idx[systems], idx[dispmodel,['Elst']]].values
            ind =  df.loc[idx[systems], idx[dispmodel,['Ind']]].values
            disp = df.loc[idx[systems], idx[dispmodel,[dispcols[dispmodel]]]].values
    else:
        # Get SAPT terms, zip together to pass to `tern()`
        if systems == 'all':
            elst = df.loc[:, idx['Elst']].values
            ind =  df.loc[:, idx['Ind']].values
            disp = df.loc[:, idx[dispcols[dispmodel]]].values
        else:
            elst = df.loc[idx[systems], idx['Elst']].values
            ind =  df.loc[idx[systems], idx['Ind']].values
            disp = df.loc[idx[systems], idx[dispcols[dispmodel]]].values
        
    # Call ternary plot
    sapt = list(zip(elst, ind, disp))
    p4tern(sapt, **kwargs)

def ternary(saptdf, title=None, labeled=True, colors='sapt', colorbar=None, saveas=None):
    """Takes array of arrays *sapt* in form [elst, indc, disp] and builds formatted
    two-triangle ternary diagrams. Either fully-readable or dotsonly depending
    on *labeled*. Saves in formats *graphicsformat*.

    """
    import hashlib
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    from matplotlib.path import Path
    import matplotlib.patches as patches
    
    idx = pd.IndexSlice

    class MidpointNormalize(mpl.colors.Normalize):
        ## class from the mpl docs:
        # https://matplotlib.org/users/colormapnorms.html
    
        def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
            self.midpoint = midpoint
            super().__init__(vmin, vmax, clip)
    
        def __call__(self, value, clip=None):
            # I'm ignoring masked values and all kinds of edge cases to make a
            # simple example...
            x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
            return np.ma.masked_array(np.interp(value, x, y))  

    # initialize plot
    fig, ax = plt.subplots(figsize=(6, 3.6))
    plt.xlim([-0.75, 1.25])
    plt.ylim([-0.18, 1.02])
    plt.xticks([])
    plt.yticks([])
    ax.set_aspect('equal')

    if labeled:
        # form and color ternary triangles
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
        pathPos = Path([(0., 0.), (1., 0.), (0.5, 0.866), (0., 0.)], codes)
        pathNeg = Path([(0., 0.), (-0.5, 0.866), (0.5, 0.866), (0., 0.)], codes)
        ax.add_patch(patches.PathPatch(pathPos, facecolor='white', lw=2))
        ax.add_patch(patches.PathPatch(pathNeg, facecolor='#fff5ee', lw=2))

        # form and color HB/MX/DD dividing lines
        ax.plot([0.667, 0.5], [0., 0.866], color='#eeb4b4', lw=0.5)
        ax.plot([-0.333, 0.5], [0.577, 0.866], color='#eeb4b4', lw=0.5)
        ax.plot([0.333, 0.5], [0., 0.866], color='#7ec0ee', lw=0.5)
        ax.plot([-0.167, 0.5], [0.289, 0.866], color='#7ec0ee', lw=0.5)

        # label corners
        ax.text(1.0, -0.15, u'Elst (\u2212)',
            verticalalignment='bottom', horizontalalignment='center',
            family='Times New Roman', weight='bold', fontsize=18)
        ax.text(0.5, 0.9, u'Ind (\u2212)',
            verticalalignment='bottom', horizontalalignment='center',
            family='Times New Roman', weight='bold', fontsize=18)
        ax.text(0.0, -0.15, u'Disp (\u2212)',
            verticalalignment='bottom', horizontalalignment='center',
            family='Times New Roman', weight='bold', fontsize=18)
        ax.text(-0.5, 0.9, u'Elst (+)',
            verticalalignment='bottom', horizontalalignment='center',
            family='Times New Roman', weight='bold', fontsize=18)

    xvals = []
    yvals = []
    cvals = []
    df = saptdf.reset_index()
    for row in df.index:
        [elst, indc, disp] = df.loc[idx[row], idx[['Elst', 'Ind', 'Disp']]].values

        # calc ternary posn and color
        Ftop = abs(indc) / (abs(elst) + abs(indc) + abs(disp))
        Fright = abs(elst) / (abs(elst) + abs(indc) + abs(disp))
        xdot = 0.5 * Ftop + Fright
        ydot = 0.866 * Ftop
        if colors == 'sapt':
            cdot = 0.5 + (xdot - 0.5) / (1. - Ftop)
            colormap = mpl.cm.jet
            vmin = 0
            vmax = 1
        if elst > 0.:
            xdot = 0.5 * (Ftop - Fright)
            ydot = 0.866 * (Ftop + Fright)

        xvals.append(xdot)
        yvals.append(ydot)

        if colors == 'error':
            if colorbar == 'symmetric':
                emin = df.loc[:, idx['Error']].min()
                emax = df.loc[:, idx['Error']].max()
                bound = (-max(abs(emin), abs(emax)), max(abs(emin), abs(emax)))
                #[vmin, vmax] = bound
                [vmin, vmax] = [-5, 5]
                norm = None
            elif colorbar == 'asymmetric':
                norm = MidpointNormalize(midpoint=0)
            
            cdot = df.loc[idx[row], idx['Error']]
            #colormap = mpl.cm.seismic
            colormap = mpl.cm.PRGn
        cvals.append(cdot)

    sc = ax.scatter(xvals, yvals, c=cvals, s=15, marker="o", \
        cmap=colormap, edgecolor='none', vmin=vmin, vmax=vmax, zorder=10, \
        norm=norm
        )

    if colorbar is not None:
        cbar = plt.colorbar(sc)
        cbar.minorticks_on()

    # remove figure outline
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.suptitle(title, family='Times New Roman', weight='bold', fontsize=24)

    # save and show
    if saveas is not None:
        plt.savefig(saveas, transparent=True, format='pdf', bbox_inches='tight',
                    frameon=False, dpi=450, edgecolor='none', pad_inches=0.0)

