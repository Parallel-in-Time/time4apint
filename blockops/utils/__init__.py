import pkgutil

__all__ = [name for name in locals().keys() if not name.startswith('__')]
for loader, moduleName, _ in pkgutil.walk_packages(__path__):
     __all__.append(moduleName)
     __import__(__name__+'.'+moduleName)