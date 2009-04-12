import ihooks
import imp
import os
import sys
import inspect 

def get_module_from_path(path_for_module):
    """Import module from a named file"""
    if not os.path.exists(path_for_module):
        sys.stderr.write( "WARNING: Cannot import file. File %s was not found!" % path_for_module )
        
    loader = ihooks.BasicModuleLoader()
    path, file = os.path.split(path_for_module)
    name, ext = os.path.splitext(file)
    m = loader.find_module_in_dir(name, path)
    if not m:
        raise ImportError, name
    m = loader.load_module(name, m)
    return m

def get_class_for_module(module, class_name):
    cls = getattr(module, class_name, None)
    return cls

def get_classes_for_module(module):
    classes = [value for key, value in inspect.getmembers(module) if inspect.isclass(value)]
    return classes

def get_methods_for_class(klass):
    methods = [klass.__dict__[key] for key in klass.__dict__.keys() if inspect.ismethod(klass.__dict__[key]) or inspect.isfunction(klass.__dict__[key])]
    return methods
    
def get_arguments_for_method(method):
    arguments, var_args, var_kwargs, defaults = _getargspec(method)
    
    ret = {}
    
    arg_index = 0

    for argument in arguments:
        if defaults != None and arg_index >= len(arguments) - len(defaults):
            ret[argument] = defaults[arg_index - (len(arguments) - len(defaults))]
        else:
            ret[argument] = None
        arg_index += 1
    
    return (ret, var_args, var_kwargs)
    
#code obtained from http://kbyanc.blogspot.com/2007/07/python-more-generic-getargspec.html
def _getargspec(obj):
    """Get the names and default values of a callable's
       arguments

    A tuple of four things is returned: (args, varargs,
    varkw, defaults).
      - args is a list of the argument names (it may
        contain nested lists).
      - varargs and varkw are the names of the * and
        ** arguments or None.
      - defaults is a tuple of default argument values
        or None if there are no default arguments; if
        this tuple has n elements, they correspond to
        the last n elements listed in args.

    Unlike inspect.getargspec(), can return argument
    specification for functions, methods, callable
    objects, and classes.  Does not support builtin
    functions or methods.
    """
    if not callable(obj):
        raise TypeError, "%s is not callable" % type(obj)
    try:
        if inspect.isfunction(obj):
            return inspect.getargspec(obj)
        elif hasattr(obj, 'im_func'):
            # For methods or classmethods drop the first
            # argument from the returned list because
            # python supplies that automatically for us.
            # Note that this differs from what
            # inspect.getargspec() returns for methods.
            # NB: We use im_func so we work with
            #     instancemethod objects also.
            spec = list(inspect.getargspec(obj.im_func))
            spec[0] = spec[0][1:]
            return spec
        elif inspect.isclass(obj):
            return _getargspec(obj.__init__)
        elif isinstance(obj, object) and \
             not isinstance(obj, type(arglist.__get__)):
            # We already know the instance is callable,
            # so it must have a __call__ method defined.
            # Return the arguments it expects.
            return _getargspec(obj.__call__)
    except NotImplementedError:
        # If a nested call to our own getargspec()
        # raises NotImplementedError, re-raise the
        # exception with the real object type to make
        # the error message more meaningful (the caller
        # only knows what they passed us; they shouldn't
        # care what aspect(s) of that object we actually
        # examined).
        pass
    raise NotImplementedError, \
          "do not know how to get argument list for %s" % \
          type(obj)
