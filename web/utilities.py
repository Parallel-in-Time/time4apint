import numpy as np
from matplotlib import ticker
from matplotlib.figure import Figure

from blockops import BlockProblem


def discretization_error(scheme, n, N, M):
    reLam = np.linspace(-4, 0.5, n + 1)
    imLam = np.linspace(-3, 3, n)

    lam = reLam[:, None] + 1j * imLam[None, :]
    prob = BlockProblem(lam.ravel(),
                        N,
                        N,
                        M,
                        scheme,
                        nodes='LEGENDRE',
                        quadType='LOBATTO',
                        nStepPerNode=1,
                        form='Z2N',
                        exactProlong=False)

    uExact = prob.getSolution('exact')
    uNum = prob.getSolution('fine')
    err = np.abs(uExact - uNum)

    stab = np.abs(uNum)[0, :, -1].reshape(lam.shape)
    errMax = np.max(err, axis=(0, -1)).reshape(lam.shape)

    err = errMax
    return create_figure(reLam, imLam, err, stab)


def pint_iter(scheme_F, n, N, M, n_steps_F, n_steps_G):
    reLam = np.linspace(-4, 0.5, n + 1)
    imLam = np.linspace(-3, 3, n)

    schemeF = scheme_F
    nStepsF = n_steps_F
    schemeG = 'RK4'
    nStepsG = n_steps_G
    algoName = 'Parareal'

    lam = reLam[:, None] + 1j * imLam[None, :]
    prob = BlockProblem(lam.ravel(),
                        N,
                        N,
                        M,
                        schemeF,
                        nStepPerNode=nStepsF,
                        nodes='LEGENDRE',
                        quadType='LOBATTO',
                        form='Z2N')
    prob.setApprox(schemeG, nStepPerNode=nStepsG)

    algo = prob.getBlockIteration(algoName)

    # Compute fine solution
    uNum = prob.getSolution('fine')

    # Compute exact solution and discretization error
    uExact = prob.getSolution('exact')
    errDiscr = np.abs(uExact - uNum)
    errDiscrMax = np.max(errDiscr, axis=(0, -1)).reshape(lam.shape)
    stab = np.abs(uNum)[0, :, -1].reshape(lam.shape)

    # Compute PinT solution and error
    nIterMax = N
    uPar = algo(K=nIterMax)
    errPinT = np.abs(uNum - uPar)
    errPinTMax = np.max(errPinT,
                        axis=(1,
                              -1)).reshape((errPinT.shape[0], ) + (lam.shape))

    # Compute required number of iterations to discretization error
    nIter = -np.ones_like(errDiscrMax)
    nIter *= 2
    k = errPinT.shape[0] - 1
    for err in errPinTMax[-1::-1]:
        nIter[err < errDiscrMax] = k
        k -= 1

    coords = np.meshgrid(reLam.ravel(), imLam.ravel(), indexing='ij')
    levels = np.arange(nIterMax + 2) - 1

    fig = Figure()
    ax = fig.subplots()
    ax.contourf(*coords, nIter, levels=levels)
    # plt.colorbar(ticks=levels[1:])
    ax.contour(*coords,
               nIter,
               levels=levels,
               colors='black',
               linestyles='--',
               linewidths=0.75)
    ax.hlines(0,
              coords[0].min(),
              coords[0].max(),
              colors='black',
              linestyles='--')
    ax.vlines(0,
              coords[1].min(),
              coords[1].max(),
              colors='black',
              linestyles='--')
    # ax.set_aspect('equal', 'box')
    # ax.set_xlabel(r'$Re(\lambda)$')
    # ax.set_ylabel(r'$Im(\lambda)$')
    # ax.set_xlabel(r'`\lambda`')
    # ax.set_ylabel(r'\lambda')
    fig.tight_layout()
    return fig


def pint_error(scheme, n, N, M, n_steps_F, n_steps_G):
    reLam = np.linspace(-4, 0.5, n + 1)
    imLam = np.linspace(-3, 3, n)
    nStepsF = n_steps_F
    nStepsG = n_steps_G
    algoName = 'Parareal'

    lam = reLam[:, None] + 1j * imLam[None, :]
    prob = BlockProblem(lam.ravel(), N, N, M, scheme, nStepPerNode=nStepsF)
    prob.setApprox(scheme, nStepPerNode=nStepsG)

    algo = prob.getBlockIteration(algoName)

    uNum = prob.getSolution('fine')
    uPar = algo(K=4)

    err = np.abs(uNum - uPar)

    stab = np.abs(uPar)[-1, -1, :, -1].reshape(lam.shape)
    errMax = np.max(err[-1], axis=(0, -1)).reshape(lam.shape)

    err = errMax
    return create_figure(reLam, imLam, err, stab)


def create_figure(reLam, imLam, err, stab, eMin=-7, eMax=0, nLevels=22):
    coords = np.meshgrid(reLam.ravel(), imLam.ravel(), indexing='ij')
    levels = np.logspace(eMin, eMax, num=nLevels)
    err[err < 10**eMin] = 10**eMin
    err[err > 10**eMax] = 10**eMax
    ticks = [10**(i) for i in range(eMin, eMax + 1)]

    fig = Figure()
    ax = fig.subplots()
    ax.contourf(*coords, err, levels=levels, locator=ticker.LogLocator())
    # plt.colorbar(ticks=ticks, format=ticker.LogFormatter())
    ax.contour(*coords,
               err,
               levels=ticks,
               colors='k',
               linestyles='--',
               linewidths=0.75)
    ax.contour(*coords, stab, levels=[1], colors='gray')
    ax.hlines(0,
              coords[0].min(),
              coords[0].max(),
              colors='black',
              linestyles='--')
    ax.vlines(0,
              coords[1].min(),
              coords[1].max(),
              colors='black',
              linestyles='--')
    # ax.set_aspect('equal', 'box')
    # ax.set_xlabel(r'$Re(\lambda\Delta{T})$')
    # ax.set_ylabel(r'$Im(\lambda\Delta{T})$')
    fig.tight_layout()
    return fig