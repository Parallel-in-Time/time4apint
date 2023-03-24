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
        msg = f"{name}={value} -> {reason}"
        super().__init__(msg)


class ParamType(object):

    def error(self, name, value, reason):
        reason+= f" ({self.name})"
        raise ParamError(name, value, reason)

    @property
    def name(self):
        """str: name of the ParamChecker"""
        return self.__class__.__name__

    def __call__(self, name, value):
        raise NotImplementedError('cannot use abstract classe')

    def __repr__(self):
        return self.name


class PositiveNumber(ParamType):

    def __call__(self, name, value):
        try:
            assert int(value) == value
        except (ValueError, TypeError):
            self.error(name, value,
                       "cannot be interpreted as integer")
        except AssertionError:
            self.error(name, value,
                       "is not a rounded integer")
        if value < 1:
            self.error(name, value,
                       "is not a strictly positive integer")
        return True


class MultipleChoices(ParamType):

    def __init__(self, *choices):
        self.pType = None
        self.choices = set()
        for c in choices:
            if isinstance(c, ParamType):
                if self.pType is None:
                    self.pType = c
                else:
                    raise ValueError('MultipleChoices does not support more '
                                     'than one ParamType in its choices')
            else:
                self.choices.add(c)

    @property
    def accepted(self):
        accepted = {c for c in self.choices}
        if self.pType is not None:
            accepted.add(self.pType)
        return accepted

    def __repr__(self):
        return self.name+str(self.accepted)

    def __call__(self, name, value):
        if self.pType is not None:
            try:
                return self.pType(name, value)
            except ParamError:
                pass
        if not isinstance(value, typing.Hashable):
            self.error(name, value,
                       f"is not in {[c for c in self.accepted]}")
        if value not in self.choices:
            self.error(name, value,
                       f"is not in {[c for c in self.accepted]}")
        return True

class CustomPoints(ParamType):

    def __call__(self, name, value):
        try:
            value = np.array(value, dtype=float)
            assert len(value.shape) == 1
        except (ValueError, AssertionError):
            self.error(name, value,
                       "cannot be interpreted as a list of float")
        if not np.all(np.sort(value) == value):
            self.error(name, value,
                       "points are not ordered increasingly")
        if value[0] < 0 or value[-1] > 1:
            self.error(name, value,
                       "points are not included in [0, 1]")
        return True


def setParamTypes(**kwargs):

    def wrapper(cls):
        sig = inspect.signature(cls.__init__)
        clsParams = set(sig.parameters.keys())
        clsParams.remove('self')
        params = set(kwargs.keys())
        if params != clsParams:
            raise ValueError(
                f"parameters set in setParamTypes ({params}) are not the same"
                f" as class __init__ parameters ({clsParams})")

        cls.PARAMS.update(kwargs)
        return cls

    return wrapper


class ParamClass(object):

    PARAMS = {}

    def checkParams(self, localVars: dict):
        for name, value in localVars.items():
            if name != 'self':
                print(name)
                self.PARAMS[name](name, value)


@setParamTypes(
    M=PositiveNumber(),
    points=MultipleChoices('EQUID', 'LEGENDRE', CustomPoints()),
    quadType=MultipleChoices('GAUSS', 'LOBATTO', 'RADAU-RIGHT', 'RADAU-LEFT'),
    form=MultipleChoices('Z2N', 'N2N')
)
class BlockScheme(ParamClass):
    """Base class for a block scheme (define block points)"""

    def __init__(self, M, points, quadType='LOBATTO', form='Z2N'):
        self.checkParams(locals())
        # Generate nodes ...


    def generateBlockOperators(self):
        raise NotImplementedError()


class RKScheme(BlockScheme):

    STABILITY_FUNCTION = {
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

    def __init__(self, M):
        pass
