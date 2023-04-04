#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 16:16:27 2023

Contains utility classes and wrapper to list and check parameters.
"""
import inspect
from typing import Hashable, Callable
import copy
import numpy as np

from blockops.taskPool import TaskPool


# -----------------------------------------------------------------------------
# Base classes
# -----------------------------------------------------------------------------

class ParamError(Exception):
    """Exception class to be used with bad parameter values"""

    def __init__(self, name, value, reason):
        self.name = name
        self.value = value
        self.reason = reason
        self.msg = f"{name}={value} -> {reason}"
        super().__init__(self.msg)


class Parameter(object):
    """Base class to describe a parameter"""

    name = None
    docs = None
    default = None
    value = None

    def error(self, value, reason):
        reason += f" ({self.pType})"
        raise ParamError(self.name, value, reason)

    @property
    def pType(self):
        """str: name of the Parameter object"""
        return self.__class__.__name__

    def check(self, value):
        """Default check method, accept all parameters"""
        return True

    def __repr__(self):
        if self.value is None:
            return f"{self.pType}(default={self.default})"
        else:
            return f"{self.pType}(value={self.value})"


class ParamClass(object):
    """
    Base class that lists its parameters, default value and documentation in
    a `PARAMS` attribute.
    It allows to check and store the parameter values using the `initialize`
    method on the first line of the subclass constructor.
    """
    PARAMS = {}

    @classmethod
    def getParamsDocs(cls):
        return {name: param.docs for name, param in cls.PARAMS.items()}

    @classmethod
    def getParamsDefault(cls):
        return {name: param.default for name, param in cls.PARAMS.items()}

    def getParamsValue(self):
        return {name: param.value for name, param in self.PARAMS.items()}

    def initialize(self, params: dict):
        """Check given parameter values and store them in PARAMS elements"""
        self._copyParams()
        for name, value in params.items():
            if name in self.PARAMS:
                self.PARAMS[name].check(value)
                self.PARAMS[name].value = value

    def _copyParams(self):
        """Copy PARAMS to an attribute specific for the instance"""
        self.PARAMS = copy.deepcopy(self.PARAMS)

    @classmethod
    def extractParamDocs(cls, *names):
        """Extract documentation associated to a list of parameter names"""
        docs = cls.__doc__

        if docs is None:
            raise ValueError(f'undocumented class {cls}')

        for name in names:
            iStart = docs.find(f'\n    {name} :')
            if iStart == -1:
                iStart = docs.find(f'\n    **{name} :')
                if iStart == -1:
                    raise ValueError(f'{name} parameter not in {cls} docs')
            docLines = docs[iStart:].splitlines()[2:]
            descr = []
            for line in docLines:
                if line.startswith(8 * ' '):
                    descr.append(line.strip())
                elif line.strip() == '':
                    continue
                else:
                    break
            if len(descr) == 0:
                raise ValueError(f'empty documentation for {name} in {cls} docs')

            cls.PARAMS[name].docs = '\n'.join(descr)


# -----------------------------------------------------------------------------
# Main class decorator to be applied on ParamClass subclasses
# -----------------------------------------------------------------------------

def setParams(**kwargs) -> Callable[[ParamClass], ParamClass]:
    """Class decorator to set the parameter types"""

    def wrapper(cls):

        # Copy original PARAMS dictionnary so it's not shared with other classes
        cls.PARAMS = copy.deepcopy(cls.PARAMS)

        # Get constructor signature
        sig = inspect.signature(cls.__init__)

        # Ignore **kwargs type arguments
        sigParams = {name: par for name, par in sig.parameters.items()
                     if par.kind != par.VAR_KEYWORD}

        # Add parameter object to the class PARAMS dictionnary
        for name, pType in kwargs.items():
            pType.name = name
            cls.PARAMS[name] = pType

        # Check if signature of the constructor corresponds to given parameters
        clsParams = set(sigParams.keys())
        clsParams.remove('self')

        objParams = set(cls.PARAMS.keys())

        if objParams != clsParams:
            raise ValueError(
                f"object parameters set in setParams ({objParams}) are not"
                f" the same as __init__ parameters for the class ({clsParams})")

        # Add docs and default value for each parameters
        cls.extractParamDocs(*kwargs.keys())
        for name, par in sigParams.items():
            if name == 'self':
                continue
            default = par.default if par.default != inspect._empty else None
            cls.PARAMS[name].default = default

        return cls

    return wrapper


# -----------------------------------------------------------------------------
# Parameter implementations
# -----------------------------------------------------------------------------

class PositiveInteger(Parameter):
    """Accepts one (default strictly) positive integer"""

    def __init__(self, strict=True):
        self.strict = strict

    def check(self, value):
        try:
            assert int(value) == value
        except (ValueError, TypeError):
            self.error(value, "cannot be interpreted as an integer")
        except AssertionError:
            self.error(value, "cannot be rounded to an integer")
        except Exception:
            self.error(value, "something went wrong with this value")
        if self.strict and value < 1:
            self.error(value, "is not a strictly positive integer")
        if value < 0:
            self.error(value, "is not a positive integer")
        return True


class ScalarNumber(Parameter):
    """Accepts one scalar number (eventually a strict positive float)"""

    def __init__(self, positive=False):
        self.positive = positive

    def check(self, value):
        dtype = float if self.positive else complex
        try:
            value = np.array(value, dtype=dtype).ravel()
            assert value.size == 1
        except ValueError:
            self.error(value, f"cannot be interpreted as a {dtype}")
        except AssertionError:
            self.error(value, "is more than one value")
        except Exception:
            self.error(value, "something went wrong with this value")
        if self.positive and value <= 0:
            self.error(value, "is not a strictly positive number")
        return True


class VectorNumbers(Parameter):
    """Accepts one or several (complex or float) numbers"""

    def check(self, value):
        try:
            value = np.array(value, dtype=complex)
            assert len(np.squeeze(value).shape) < 2
        except ValueError:
            self.error(value, 'cannot be interpreted as an array of complex')
        except AssertionError:
            self.error(value, "has more than one array dimension")
        except Exception:
            self.error(value, "something went wrong with this value")
        return True


class MultipleChoices(Parameter):
    """Accepts different parameter values or parameter types"""

    def __init__(self, *choices):
        self.pTypes = [c for c in choices if isinstance(c, Parameter)]
        self.choices = [c for c in choices if not isinstance(c, Parameter)]

    def check(self, value):
        choices = [c for c in self.choices]
        for pType in self.pTypes:
            try:
                return pType.check(value)
            except ParamError as err:
                choices.append(err.reason)
        if not isinstance(value, Hashable):
            self.error(value, f"is not in {[c for c in choices]}")
        if value not in self.choices:
            self.error(value, f"is not in {[c for c in choices]}")
        return True


class CustomPoints(Parameter):
    """Accepts an ordered list of float values in [0, 1]"""

    def check(self, value):
        try:
            value = np.array(value, dtype=float)
            assert len(value.shape) == 1
        except (ValueError, AssertionError):
            self.error(value, "cannot be interpreted as a list of float")
        except Exception:
            self.error(value, "something went wrong with this value")
        if not np.all(np.sort(value) == value):
            self.error(value, "points are not ordered increasingly")
        if value[0] < 0 or value[-1] > 1:
            self.error(value, "points are not included in [0, 1]")
        return True


class Boolean(Parameter):
    """Accepts a boolean value"""

    def check(self, value):
        if not isinstance(value, bool):
            self.error(value, "not of boolean type")
        return True


class TaskPoolParam(Parameter):
    """Accepts a taskPool class"""

    def check(self, value):
        if not isinstance(value, TaskPool):
            self.error(value, "not of TaskPool type")
        return True
