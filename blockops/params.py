#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 16:16:27 2023

Contains utility class for scheme parameters
"""
import inspect
import typing
import numpy as np


class ParamError(Exception):

    def __init__(self, name, value, reason):
        self.reason = reason
        msg = f"{name}={value} -> {reason}"
        super().__init__(msg)


class Parameter(object):
    
    name = None
    docs = None
    default = None

    def error(self, value, reason):
        reason+= f" ({self.pType})"
        raise ParamError(self.name, value, reason)

    @property
    def pType(self):
        """str: name of the Parameter object"""
        return self.__class__.__name__

    def check(self, value):
        raise NotImplementedError('cannot use abstract classe')


class PositiveNumber(Parameter):

    def check(self, value):
        try:
            assert int(value) == value
        except (ValueError, TypeError):
            self.error(value,
                       "cannot be interpreted as integer")
        except AssertionError:
            self.error(value,
                       "is not a rounded integer")
        if value < 1:
            self.error(value,
                       "is not a strictly positive integer")
        return True


class MultipleChoices(Parameter):

    def __init__(self, *choices):
        self.pTypes = set(c for c in choices if isinstance(c, Parameter))
        self.choices = set(c for c in choices if not isinstance(c, Parameter))

    def check(self, value):
        choices = {c for c in self.choices}
        for pType in self.pTypes:
            try:
                return pType.check(value)
            except ParamError as err:
                choices.add(err.reason)
        if not isinstance(value, typing.Hashable):
            self.error(value,
                       f"is not in {[c for c in choices]}")
        if value not in self.choices:
            self.error(value,
                       f"is not in {[c for c in choices]}")
        return True

class CustomPoints(Parameter):

    def check(self, value):
        try:
            value = np.array(value, dtype=float)
            assert len(value.shape) == 1
        except (ValueError, AssertionError):
            self.error(value,
                       "cannot be interpreted as a list of float")
        if not np.all(np.sort(value) == value):
            self.error(value,
                       "points are not ordered increasingly")
        if value[0] < 0 or value[-1] > 1:
            self.error(value,
                       "points are not included in [0, 1]")
        return True


def extractParamDocs(cls, *names):
    docs = cls.__doc__
    
    if docs is None:
        raise ValueError(f'undocumented class {cls}')
    
    paramsDoc = {}
    
    for name in names:
        paramsDoc[name] = ""
        iStart = docs.find(f'\n    {name} :')
        if iStart == -1:
            raise ValueError(f'{name} parameter not in {cls} docs')
        docLines = docs[iStart:].splitlines()[2:]
        descr = []
        for line in docLines:
            if line.startswith(8*' '):
                descr.append(line.strip())
            elif line.strip() == '':
                continue
            else:
                break
        if len(descr) == 0:
            raise ValueError(f'empty documentation for {name} in {cls} docs')
        paramsDoc[name] = '\n'.join(descr)
            
    return paramsDoc


def setParams(**kwargs):

    def wrapper(cls):
        
        # Get constructor signature
        sig = inspect.signature(cls.__init__)
        
        # Add parameter object to the class parameter dictionnary
        for name, pType in kwargs.items():
            pType.name = name
            cls.PARAMS[name] = pType
        
        # Check if signature of the constructor corresponds to given parameters       
        clsParams = set(sig.parameters.keys())
        clsParams.remove('self')
        
        objParams = set(cls.PARAMS.keys())
        
        if objParams != clsParams:
            raise ValueError(
                f"object parameters set in setParams ({objParams}) are not"
                f" the same as __init__ parameters for the class ({clsParams})")
            
        # Add docs and default value for each parameters
        pDocs = extractParamDocs(cls, *kwargs.keys())
        for name, par in sig.parameters.items():
            if name == 'self':
                continue
            default = par.default if par.default != inspect._empty else None
            cls.PARAMS[name].default = default
            if name in pDocs:
                cls.PARAMS[name].docs = pDocs[name]

        return cls

    return wrapper


class ParamClass(object):

    PARAMS = {}
    
    @classmethod
    def getParamsDocs(cls):
        return {name: param.docs for name, param in cls.PARAMS.items()}
    
    @classmethod
    def getParamsDefault(cls):
        return {name: param.default for name, param in cls.PARAMS.items()}

    @classmethod
    def checkParams(cls, localVars: dict):
        for name, value in localVars.items():
            if name != 'self':
                cls.PARAMS[name].check(value)


@setParams(
    nPoints=PositiveNumber(),
    ptsType=MultipleChoices('EQUID', 'LEGENDRE', CustomPoints()),
    quadType=MultipleChoices('GAUSS', 'LOBATTO', 'RADAU-RIGHT', 'RADAU-LEFT'),
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
        self.checkParams(locals())
        # Generate nodes ...


    def generateBlockOperators(self, lamDt):
        raise NotImplementedError()


STABILITY_FUNCTIONS = {
    # First order methods
    'BE': lambda z: (1 - z)**(-1),
    'FE': lambda z: 1 + z,
    'RK21': lambda z: 1 + z + z**2,
    # Second order methods
    'TRAP': lambda z: (1 + z/2)/(1 - z/2),
    'RK2': lambda z: 1 + z + z**2/2,
    'GAUSS-LG': lambda z: (1 + z/2 + z**2/12)/(1 - z/2 + z**2/12),
    'SDIRK2': lambda z: (0.414213562373095*z + 1) /
        (0.0857864376269049*z**2 - 0.585786437626905*z + 1),
    # Third order methods
    'RK3': lambda z: 1 + z + z**2/2 + z**3/6,
    'RK53': lambda z: 1 + z + z**2/2 + z**3/6 + z**4/26 + z**5/182,
    'SDIRK3': lambda z: (-0.237660690809725*z**2 - 0.307599564525379*z + 1) /
        (-0.0828057581196304*z**3 + 0.569938873715654*z**2
         - 1.30759956452538*z + 1),
    # Fourth order methods
    'RK4': lambda z: 1 + z + z**2/2 + z**3/6 + z**4/24,
    'SDIRK54': lambda z: (0.00258844870108142*z**8 + 0.0122346760314181*z**7
                          - 0.0195644048996919*z**6 - 0.202186867042821*z**5
                          - 0.0641999421296173*z**4 + 0.999095775462969*z**3
                          + 71/72*z**2 - 41/48*z - 1) /
        ((1 - z/4)**5*(0.283989800347222*z**4 + 1.01775896990741*z**3 +
                       337/576*z**2 - 53/48*z - 1)),
    # Fith order method
    'RK65': lambda z: 1 + z + z**2/2 + z**3/6 + z**4/24 + z**5/120 + z**6/1280,
    # Exact integration (infinite order)
    'EXACT': lambda z: np.exp(z)}


@setParams(
    rkScheme=MultipleChoices(*STABILITY_FUNCTIONS.keys()),
    nStepsPerPoint=PositiveNumber()
)
class RungeKutta(BlockScheme):
    """
    Generic class for Runge-Kutta schemes
    
    Parameters
    ----------
    rkScheme : str, optional
        Name of the Runge-Kutta scheme (BE, FE, TRAP, RK4, ...).
    nStepsPerPoint : int, optional
        Number of time-steps per block time point.
    """
    def __init__(self, nPoints, ptsType='EQUID', quadType='LOBATTO', form='Z2N',
                 rkScheme='BE', nStepsPerPoint=1):
        self.checkParams(locals())
