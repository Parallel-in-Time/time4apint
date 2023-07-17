import numpy as np
from blockops.problem import BlockProblem

import matplotlib.pyplot as plt
from matplotlib import ticker

import plotly.io as io
io.renderers.default='browser'
import plotly.graph_objects as go

class Plotly():
    
    @staticmethod
    def plotAccuracyContour(reLam, imLam, err, stab=None,
                            eMin=-6, eMax=0):
        
        ticks = [i for i in range(eMin, eMax + 1)]
        
        fig = go.Figure()
        colorbar = {
            "tickvals": ticks,
            "ticktext": [f"1e{t}" for t in ticks]
        }
        errContour = go.Contour(
            z=np.log10(err).T,
            x=reLam, y=imLam,
            colorscale='viridis',
            contours=dict(start=eMin, end=eMax, size=0.5),
            colorbar=colorbar,
            line_smoothing=0.85,
            hovertemplate =
                "<b>Re</b>: %{x}<br>" +
                "<b>Im</b>: %{y}<br>" +
                "<b>err</b>: 10^(%{z:.1f})<extra></extra>",
        )
        fig.add_trace(errContour)
        if stab is not None:
            stabContour = go.Contour(
                z=stab.T,
                x=reLam, y=imLam,
                colorscale=[(0, 'black'), (1, 'black')],
                contours=dict(start=1, end=1, size=0, coloring='lines'),
                line_width=2,
                line_smoothing=0.85,
                line_dash="dash",
                hoverinfo='skip',
                colorbar_showticklabels=False,
            )
            fig.add_trace(stabContour)
        
        fig.add_hline(y=0, line_width=1)
        fig.add_vline(x=0, line_width=1)
        
        fig.update_xaxes(
            constrain="domain"
        )
        fig.update_yaxes(
            constrain="domain",
            scaleanchor="x",
            scaleratio=1,
        )
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0), height=450)
        return fig
    

class Matplotlib():
    
    @staticmethod
    def plotAccuracyContour(reLam, imLam, err, stab=None,
                            eMin=-6, eMax=0, nLevels=13,
                            figName=None):
        """
        2D contour plot of an error given in parameters for many complex values
    
        Parameters
        ----------
        reLam : 1darray (nR,)
            The values for real part of lambda
        imLam : 1darray (nI,)
            The values for imaginary part of lambda.
        err : 2darray (nR, nI)
            The error values for each lambda
        stab : 2darray (nR, nI), optional
            Amplification factor associated to the error. The default is None.
        eMin : int, optional
            Minimum exponent to be shown for the error. The default is -7.
        eMax : int, optional
            Maximum exponent to be shown for the error. The default is 0.
        nLevels : int, optional
            Number of level to show on the contour plot. The default is 22.
        figName : str, optional
            Name for the generated figure. The default is None.
        """
        coords = np.meshgrid(reLam.ravel(), imLam.ravel(), indexing='ij')
        levels = np.logspace(eMin, eMax, num=nLevels)
        err[err < 10 ** eMin] = 10 ** eMin
        err[err > 10 ** eMax] = 10 ** eMax
        ticks = [10 ** (i) for i in range(eMin, eMax + 1)]
    
        fig = plt.figure(figName)
        plt.title(figName)
        plt.contourf(*coords, err, levels=levels, locator=ticker.LogLocator())
        plt.colorbar(ticks=ticks, format=ticker.LogFormatter())
        plt.contour(*coords, err, levels=ticks,
                    colors='k', linestyles='--', linewidths=0.75)
        plt.contour(*coords, stab, levels=[1], colors='gray')
        plt.hlines(0, coords[0].min(), coords[0].max(),
                   colors='black', linestyles='--')
        plt.vlines(0, coords[1].min(), coords[1].max(),
                   colors='black', linestyles='--')
        plt.gca().set_aspect('equal', 'box')
        plt.xlabel(r'$Re(\lambda\Delta{T})$')
        plt.ylabel(r'$Im(\lambda\Delta{T})$')
        plt.tight_layout()
        return fig

    
    @staticmethod
    def plotContour(reLam, imLam, val, levels=21, figName=None):
        """
        Individual 2D contour plot
    
        Parameters
        ----------
        reLam : 1darray (nR,)
            The values for real part of lambda
        imLam : 1darray (nI,)
            The values for imaginary part of lambda.
        val : 2darray (nR, nI)
            The values for each lambda
        levels : int, optional
            Number of level to show on the contour plot.
        figName : str, optional
            Name for the generated figure. The default is None.
        """
        coords = np.meshgrid(reLam.ravel(), imLam.ravel(), indexing='ij')
        if levels is None:
            levels = np.unique(val)
        elif isinstance(levels, int):
            levels = np.linspace(np.min(val), np.max(val), num=levels)
    
        fig = plt.figure(figName)
        plt.title(figName)
        plt.contourf(*coords, val, levels=levels)
        plt.colorbar(ticks=levels[1:])
        plt.contour(*coords, val, levels=levels,
                    colors='black', linestyles='--', linewidths=0.75)
        plt.hlines(0, coords[0].min(), coords[0].max(),
                   colors='black', linestyles='--')
        plt.vlines(0, coords[1].min(), coords[1].max(),
                   colors='black', linestyles='--')
        plt.gca().set_aspect('equal', 'box')
        plt.xlabel(r'$Re(\lambda)$')
        plt.ylabel(r'$Im(\lambda)$')
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plotIterations2D(prob: BlockProblem, algoName: str, nIter=4, figName=None):
        """Plot the 2D solution for a PinT algorithm applied on one given problem"""
    
        # Compute sequential and exact solution
        uSeq = prob.getSolution('fine', initSol=True)
        uExact = prob.getSolution('exact', initSol=True)
    
        # Compute discretization error (for printing in console)
        errDiscr = prob.getError('fine', 'exact')
    
        # Plot exact and sequential solution
        fig = plt.figure(figName)
        plt.plot(uExact.ravel().real, uExact.ravel().imag, '^-', label='Exact')
        plt.plot(uSeq.ravel().real, uSeq.ravel().imag, 's-', label='Sequential', ms=12)
    
        algo = prob.getBlockIteration(algoName)
    
        uNum = algo(nIter=nIter, initSol=True)
    
        print(f'max discretization error : {errDiscr.max()}')
    
        for k in range(nIter):
            plt.plot(uNum[k].ravel().real, uNum[k].ravel().imag, 'o-',
                      label=f'Iter{k}')
            err = prob.getError(uNum[k][1:], 'fine')
            print(f'iter {k}, max PinT error : {err.max()}')
        plt.legend()
        return fig
