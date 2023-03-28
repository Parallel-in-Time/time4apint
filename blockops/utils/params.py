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

# -----------------------------------------------------------------------------
# Base classes
# -----------------------------------------------------------------------------

class ParamError(Exception):
    """Exception class to be used with bad parameter values"""

    def __init__(self, name, value, reason):
        self.reason = reason
        msg = f"{name}={value} -> {reason}"
        super().__init__(msg)


class Parameter(object):
    """Base class to describe a parameter"""
    
    name = None
    docs = None
    default = None
    value = None

    def error(self, value, reason):
        reason+= f" ({self.pType})"
        raise ParamError(self.name, value, reason)

    @property
    def pType(self):
        """str: name of the Parameter object"""
        return self.__class__.__name__

    def check(self, value):
        """Default check method, accept all parameters"""
        return True
    
    def __repr__(self):
        return f"{self.pType}(default={self.default})"
        
        
class ParamClass(object):
    """
    Base class that list its parameters, default value and documentation.
    It allows to check and store the parameter values using the 
    `initialize` method on the first line of the constructor method.
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

    def initialize(self, localVars: dict):
        """Check parameters given in localVars dictionnary"""
        self.PARAMS = copy.deepcopy(self.PARAMS)
        for name, value in localVars.items():
            if name != 'self' and not name.startswith('__'):
                self.PARAMS[name].check(value)
                self.PARAMS[name].value = value
                
    @classmethod
    def extractParamDocs(cls, *names):
        """Extract documentation associated to a list of parameter names"""
        docs = cls.__doc__
        
        if docs is None:
            raise ValueError(f'undocumented class {cls}')
        
        for name in names:
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

            cls.PARAMS[name].docs = '\n'.join(descr)
                
            
# -----------------------------------------------------------------------------
# Main class decorator to be applied on ParamClass children
# -----------------------------------------------------------------------------

def setParams(**kwargs) -> Callable[[ParamClass], ParamClass]:
    """Class decorator to set the parameter types"""

    def wrapper(cls):
        
        # Copy original PARAMS dictionnary so it's not shared with other classes
        cls.PARAMS = copy.deepcopy(cls.PARAMS)
        
        # Get constructor signature
        sig = inspect.signature(cls.__init__)
        
        # Add parameter object to the class PARAMS dictionnary
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
        cls.extractParamDocs(*kwargs.keys())
        for name, par in sig.parameters.items():
            if name == 'self':
                continue
            default = par.default if par.default != inspect._empty else None
            cls.PARAMS[name].default = default

        return cls

    return wrapper


# -----------------------------------------------------------------------------
# Parameter implementations
# -----------------------------------------------------------------------------

class PositiveNumber(Parameter):
    """Parameter that accept (stricly) positive integer"""

    def check(self, value):
        try:
            assert int(value) == value
        except (ValueError, TypeError):
            self.error(value, "cannot be interpreted as integer")
        except AssertionError:
            self.error(value, "is not a rounded integer")
        if value < 1:
            self.error(value, "is not a strictly positive integer")
        return True


class MultipleChoices(Parameter):
    """Parameter that accepts different parameter values or parameter types"""

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
    """Parameter that accepts an ordered list of float values in [0, 1]"""

    def check(self, value):
        try:
            value = np.array(value, dtype=float)
            assert len(value.shape) == 1
        except (ValueError, AssertionError):
            self.error(value, "cannot be interpreted as a list of float")
        if not np.all(np.sort(value) == value):
            self.error(value, "points are not ordered increasingly")
        if value[0] < 0 or value[-1] > 1:
            self.error(value, "points are not included in [0, 1]")
        return True
    
    
class Boolean(Parameter):
    """Parameter that accepts boolean values"""
    
    def check(self, value):
        if not isinstance(value, bool):
            self.error(value, "not of boolean type")
        return True
