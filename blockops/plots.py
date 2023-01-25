#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 09:15:53 2022

@author: cpf5546
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker


def plotAccuracyContour(reLam, imLam, err, stab=None,
                        eMin=-7, eMax=0, nLevels=22,
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

    plt.figure(figName)
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


def plotContour(reLam, imLam, val, nLevels=-1, figName=None):
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
    nLevels : int, optional
        Number of level to show on the contour plot.
    figName : str, optional
        Name for the generated figure. The default is None.
    """
    coords = np.meshgrid(reLam.ravel(), imLam.ravel(), indexing='ij')
    if nLevels == -1:
        levels = np.arange(np.max(val) + 2) - 1
    else:
        levels = np.arange(nLevels + 2) - 1

    plt.figure(figName)
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
