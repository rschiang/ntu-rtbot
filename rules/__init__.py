import os
import importlib
import inspect

for f in os.listdir(os.path.dirname(__file__)):
    name, ext = os.path.splitext(f)
    if ext == '.py' and name != '__init__':
        module = importlib.import_module('.' + name, __name__)
        globals().update(inspect.getmembers(module, inspect.isclass))
