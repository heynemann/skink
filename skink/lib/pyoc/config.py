import common
import os
import errors
import reflection 
import sys
import inspect

class BaseConfig(object):
    allowed_lifestyle_types = ("transient", "singleton",)
    
    def __init__(self, lifestyle_type = "singleton"):
        """Creates empty context.
        """
        self.components = {}
        self.assert_valid_lifestyle_type(lifestyle_type)
        self.default_lifestyle_type = lifestyle_type
        
    def set_default_lifestyle_type(self, lifestyle_type):
        self.assert_valid_lifestyle_type(lifestyle_type)
        self.default_lifestyle_type = lifestyle_type
        
    def assert_valid_lifestyle_type(self, lifestyle_type):
        if lifestyle_type not in BaseConfig.allowed_lifestyle_types:
            raise errors.InvalidLifestyleTypeError("The specified lifestyle type (%s) is not valid. Allowed lifestyle types: %s" %
                                            (lifestyle_type, ",".join(BaseConfig.allowed_lifestyle_types)))
        
    def assert_not_cyclical_dependency(self, property, component):
        component_args, var_args, var_kwargs = reflection.get_arguments_for_method(component)
        for component_arg in component_args.keys():
            if component_arg in self.components:
                parent_component_type, parent_lifestyle_type, parent_component, parent_args, parent_kwargs = self.components[component_arg]
                if parent_component_type == "instance": return
                parent_args, var_args, var_kwargs = reflection.get_arguments_for_method(parent_component)
                if property in parent_args:
                    raise errors.CyclicalDependencyError("There is a cyclical dependency between %s and %s. Cyclical dependencies are not supported yet!"
                                                  % (component.__name__, parent_component.__name__))
                
    def register(self, property, component, lifestyle_type = "UNKNOWN", *args, **kwargs):
        if (lifestyle_type == "UNKNOWN"): lifestyle_type = self.default_lifestyle_type
        self.assert_valid_lifestyle_type(lifestyle_type)
        
        if (args or kwargs) and not callable(component):
            raise ValueError(
                    "Only callable component supports extra args: %s, %s(%s, %s)"
                    % (property, component, args, kwargs))

        if callable(component): self.assert_not_cyclical_dependency(property, component)
        component_definition = ("direct", lifestyle_type, component, args, kwargs,)
        self.components[property] = component_definition
        if callable(component): self.components[component] = component_definition
        
    def register_instance(self, property, instance, lifestyle_type = "UNKNOWN"):
        if (lifestyle_type == "UNKNOWN"): lifestyle_type = self.default_lifestyle_type
        self.assert_valid_lifestyle_type(lifestyle_type)
        
        component_definition = ("instance", lifestyle_type, instance, None, None,)
        self.components[property] = component_definition

    def register_files(self, property, root_path, pattern, lifestyle_type = "UNKNOWN"):
        if (lifestyle_type == "UNKNOWN"): lifestyle_type = self.default_lifestyle_type
        self.assert_valid_lifestyle_type(lifestyle_type)        
        
        all_classes = []
        for module_path in common.locate(pattern, root=root_path):
            module = reflection.get_module_from_path(module_path)
            
            class_name = common.camel_case(module.__name__)
            cls = reflection.get_class_for_module(module, class_name)
            
            if cls == None:
                raise AttributeError("The class %s could not be found in file %s. Please make sure that the class has the same name as the file, but Camel Cased."
                                     % (class_name, module_name))
            
            all_classes.append(cls)
        
        component_definition = "indirect", lifestyle_type, all_classes, None, None
        self.components[property] = component_definition
    
    def register_inheritors(self, property, root_path, base_type, lifestyle_type = "UNKNOWN", include_base = False):
        if (lifestyle_type == "UNKNOWN"): lifestyle_type = self.default_lifestyle_type
        self.assert_valid_lifestyle_type(lifestyle_type)        
        
        all_classes = []
        
        for module_path in common.locate("*.py", root=root_path, recursive=False):
            module = reflection.get_module_from_path(module_path)            classes = reflection.get_classes_for_module(module)
            
            for cls in classes:
                should_include = include_base and cls.__name__ == base_type.__name__
                should_include = should_include or (cls.__bases__ is (list, tuple) and base_type.__name__ in [klass.__name__ for klass in cls.__bases__])
                if should_include:
                    all_classes.append(cls)
        
        component_definition = "indirect", lifestyle_type, all_classes, None, None
        self.components[property] = component_definition

class InPlaceConfig(BaseConfig):
    '''
    Creates a blank configuration for code configuration.
    Pretty useful for unit testing the container and dependencies.
    '''
    def __init__(self):
        super(InPlaceConfig, self).__init__()
    
class FileConfig(BaseConfig):
    '''
    Creates a container using the definitions in the specified file.
    The file MUST be a python module and MUST declara a "def config(container):" function.
    This is the function that will configure the container.
    
    Default file is pyoc_config.py.
    '''
    def __init__(self, filename = "pyoc_config.py", root_path=os.path.abspath(os.curdir)):
        super(FileConfig, self).__init__()
        self.execute_config_file(root_path, filename)
    
    def execute_config_file(self, root_path, filename):
        module = reflection.get_module_from_path(os.path.join(root_path, filename))
        func = getattr(module, "config")
        config_helper = FileConfig.ContainerConfigHelper(self)
        func(config_helper)
    
    class ContainerConfigHelper(object):
        def __init__(self, file_config):
            self.file_config = file_config
            
        def register(self, property, component, *args, **kwargs):
            self.file_config.register(property, component, *args, **kwargs)
            
        def register_files(self, property, root_path, pattern):
            self.file_config.register_files(property, root_path, pattern)
