import pkgutil
import numpy as np
from typing import Dict

from blockops.utils.params import ParamClass, setParams
from blockops.utils.params import PositiveNumber, MultipleChoices, CustomPoints
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
    nPoints=PositiveNumber(),
    ptsType=MultipleChoices(*NODE_TYPES, CustomPoints()),
    quadType=MultipleChoices(*QUAD_TYPES),
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
        Either the type of points (EQUID, LEGENDRE), or a list of given time
        points in [0, 1].
    quadType : str, optional
        Quadrature type used for the points in [0, 1]:

        - LOBATTO -> 0 and 1 are included
        - GAUSS -> neither 0 nor 1 are included
        - RADAU-RIGHT -> only 1 is included
        - RADAU-LEFT -> only 0 is included

    form : str, optional
        Used formulation, either N2N (node-to-node) or Z2N (zero-to-node).    
    """
    def __init__(self, nPoints, ptsType='EQUID', quadType='LOBATTO', form='Z2N'):
        
        # Check parameters
        self.checkAndStoreParams(locals())
        
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
        return len(self.points)
        
    def getBlockOperators(self, lamDt, phiName, chiName):
        
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
        
    def getBlockMatrices(self, lamDt):
        raise NotImplementedError('cannot use BlockScheme class (abstract)')
        
    def getBlockCosts(self):
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
