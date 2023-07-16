import pkgutil
import numpy as np
from typing import Dict

from blockops.utils.params import ParamClass, setParams
from blockops.utils.params import PositiveInteger, MultipleChoices
from blockops.utils.poly import NodesGenerator, NODE_TYPES, QUAD_TYPES
from blockops.utils.poly import LagrangeApproximation
from blockops.block import BlockOperator


def getTransferMatrices(nodesFine, nodesCoarse, vectorized=False):
    # Build polynomial approximations
    polyApproxFine = LagrangeApproximation(nodesFine)
    polyApproxCoarse = LagrangeApproximation(nodesCoarse)
    # Compute interpolation matrix
    TFtoC = polyApproxFine.getInterpolationMatrix(nodesCoarse)
    TCtoF = polyApproxCoarse.getInterpolationMatrix(nodesFine)
    if vectorized:
        TFtoC.shape = (1, *TFtoC.shape)
        TCtoF.shape = (1, *TCtoF.shape)
    return TFtoC, TCtoF


@setParams(
    nPoints=PositiveInteger(latexName='$M$'),
    ptsType=MultipleChoices(*NODE_TYPES, latexName="Point Distribution"), 
    quadType=MultipleChoices(*QUAD_TYPES, latexName="Quadrature Type"),
    form=MultipleChoices('Z2N', 'N2N')
)
class BlockScheme(ParamClass):
    """
    Base class for a block scheme (build the block time points)

    Parameters
    ----------
    nPoints : int
        Number of time points in the block. Ignored if a custom list of points
        is given for `ptsType`.
    ptsType : str of list of float, optional
        Type of points distribution (EQUID, LEGENDRE, ...). Possibilities are :

        - `EQUID` : equidistant point uniformly distributed on the block
        - `LEGENDRE` : points distribution from Legendre polynomials
        - `CHEBY-{i}` : points distribution from Chebychev polynomials of the
          `i`'th kind (`i in [1,2,3,4]`).

    quadType : str, optional
        Quadrature type used for the points in [0, 1]:

        - `LOBATTO` : 0 and 1 are included
        - `GAUSS` : neither 0 nor 1 are included
        - `RADAU-RIGHT` : only 1 is included
        - `RADAU-LEFT` : only 0 is included

    form : str, optional
        Used formulation, can be either :

        - `Z2N` : zeros-to-nodes formulation, i.e the `chi` operator produces
          a vector of the form :math:`[u_0, u_0, ..., u_0]` and `phi` represents
          the integration from :math:`u_{0}` to each block time points (nodes).
        - `N2N` : node-to-node formulation, i.e the `chi` operator produces
          a vector of the form :math:`[u_0, 0, ..., 0]` and `phi` represents
          the integration from one time point (node) to the next one.
    """
    def __init__(self, nPoints, ptsType='EQUID', quadType='LOBATTO', form='Z2N'):

        # Initialize parameters
        self.initialize(locals())

        # Time-points for the block discretization
        if isinstance(ptsType, str):
            points = NodesGenerator(ptsType, quadType).getNodes(nPoints)
            points += 1
            points /= 2
        points = np.around(np.ravel(points), 14)
        deltas = np.array(
            [tauR-tauL for tauL, tauR in zip([0]+list(points)[:-1], list(points))])
        deltas = deltas[:, None]

        # Store main attributes
        self.points = points
        self.deltas = deltas

        # Eventually update parameter values
        self.PARAMS['nPoints'].value = self.nPoints
        self.PARAMS['quadType'].value = self.quadType

    @property
    def quadType(self):
        """str: quadrature type of the block time points"""
        leftIsNode = (self.points[0] == 0)
        rightIsNode = (self.points[-1] == 1)
        if leftIsNode and rightIsNode:
            return 'LOBATTO'
        elif leftIsNode:
            return 'RADAU-LEFT'
        elif rightIsNode:
            return 'RADAU-RIGHT'
        else:
            return 'GAUSS'

    @property
    def nPoints(self):
        """int: number of time points in the block"""
        return len(self.points)

    def getBlockOperators(self, lamDt, phiName, chiName) -> [BlockOperator, BlockOperator]:
        r"""
        Generate the :math:`\phi` and :math:`\chi` block operators

        Parameters
        ----------
        lamDt : scalar or 1D vector
            The value of :math:`\lambda\Delta{T}` for the block.
        phiName : str
            The symbol name for the :math:`\phi` operator.
        chiName : Tstr
            The symbol name for the :math:`\chi` operator.

        Returns
        -------
        phi : BlockOperator
            The BlockOperator object for :math:`\phi`.
        chi : TYPE
            The BlockOperator object for :math:`\chi`.
        """

        # Eventually generate matrices for several lamDt
        lamDt = np.ravel(lamDt)[None, :]

        # Generate block matrices
        phi, chi = self.getBlockMatrices(lamDt)

        # Transpose and eventually squeeze
        phi = phi.transpose((2,0,1))
        chi = chi.transpose((2,0,1))
        if lamDt.size == 1:
            phi = phi.squeeze(axis=0)
            chi = chi.squeeze(axis=0)

        # Get block costs
        costPhi, costChi = self.getBlockCosts()

        phi = BlockOperator(phiName, matrix=phi, cost=costPhi)
        chi = BlockOperator(chiName, matrix=chi, cost=costChi)

        return phi, chi

    def getBlockMatrices(self, lamDt) -> [np.ndarray, np.ndarray]:
        """
        Generate matrices for the :math:`\phi` and :math:`\chi` block operators.

        Parameters
        ----------
        lamDt : scalar or 1D vector
            The value of :math:`\lambda\Delta{T}` for the block.

        Returns
        -------
        phi : np.ndarray
            The matrix for :math:`\phi`.
        chi : np.ndarray
            The matrix for :math:`\chi`.
        """
        raise NotImplementedError('cannot use BlockScheme class (abstract)')

    def getBlockCosts(self) -> [float, float]:
        """
        Generate costs fpr the :math:`\phi` and :math:`\chi` block operators.

        Returns
        -------
        costPhi : float
            The (estimated) cost for :math:`\phi`.
        costChi : float
            The (estimated) cost for :math:`\chi`.
        """
        raise NotImplementedError('cannot use BlockScheme class (abstract)')

# Dictionnary to store all the BlockScheme implementations
SCHEMES: Dict[str, BlockScheme] = {}

def register(cls: BlockScheme) -> BlockScheme:
    SCHEMES[cls.__name__] = cls
    return cls

# Import submodules to register BlockScheme classes in SCHEMES
__all__ = [name for name in locals().keys() if not name.startswith('__')]
for loader, moduleName, _ in pkgutil.walk_packages(__path__):
    __all__.append(moduleName)
    __import__(__name__+'.'+moduleName)
