"""
materials submodule.
"""
import inspect

class Path:
    def materials():
        return(inspect.getfile(Path).split("__init__")[0])