#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 17:43:06 2023

Utility functions for numeric stuff
"""
import numpy as np


def numericalOrder(nSteps, err):
    """
    Help function to compute numerical order from error and nSteps vectors 

    Parameters
    ----------
    nSteps : np.1darray
        Different number of steps to compute the error.
    err : np.1darray
        Diffenrent error values associated to the number of steps.

    Returns
    -------
    beta : float
        Order coefficient computed through linear regression.
    rmse : float
        The root mean square error of the linear regression.
    """
    x, y = np.log10(1/nSteps), np.log10(err)

    # Compute regression coefficients and rmse
    xMean = x.mean()
    yMean = y.mean()
    sX = ((x-xMean)**2).sum()
    sXY = ((x-xMean)*(y-yMean)).sum()

    beta = sXY/sX
    alpha = yMean - beta*xMean

    yHat = alpha + beta*x
    rmse = ((y-yHat)**2).sum()**0.5
    rmse /= x.size**0.5

    return beta, rmse
