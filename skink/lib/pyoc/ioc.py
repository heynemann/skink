import errors
import common
import reflection as ref

class IoC (object):
    '''IoC container that automatically resolves instances or 
    lists of instances.'''
    __instance = None
    
    def __init__(self):
        self.is_configured = False
        self.instances = {}
    
    @staticmethod
    def instance():
        '''Returns the current instance of the container. If no instance is found, a new one is created.'''
        if IoC.__instance == None:
            IoC.__instance = IoC()
        return IoC.__instance
    
    @staticmethod
    def reset():
        '''Resets the container.'''
        IoC.__instance = None
        
    @staticmethod
    def configure(config):
        '''Assigns the specified configuration to the container.'''
        container = IoC.instance()
        container.config = config
        container.is_configured = True
        
    @staticmethod
    def resolve(cls, **custom_kw):
        """Resolves an instance of the specified class.
        If arguments are specified they are used to instantiate the given class.
        If keyword arguments are specified they are used to instantiate any class in the dependency tree that uses them (by name).
        
        Examples:
        IoC.resolve(A) #A depends on B, that depends on C. All of them will get built in runtime.
        IoC.resolve(A, title="Some Title") #A depends on B, that depends on title. 
                                           #This way B gets built using the overriden title instead 
                                           #of the one configured in the IoC container. This is useful to create custom instances.
                                           #Notice that if your instance has already been loaded before with a different value you need to call IoC.reset()
        """
        container = IoC.instance()
        if not container.is_configured: raise errors.ContainerNotConfiguredError()
        
        registered_args = None
        registered_kwargs = None
        
        if container.config.components.has_key(cls):
            component_type, lifestyle_type, value, registered_args, registered_kwargs = container.config.components[cls]
            if component_type == "instance":
                return value
            if (cls in container.instances and lifestyle_type == "singleton"):
                return container.instances[cls]
        
        instance = container._instantiate("", cls, registered_args, registered_kwargs, custom_kw)
            
        container.instances[cls] = instance
        return instance

    @staticmethod
    def resolve_all(property, *args, **kwargs):
        container = IoC.instance()
        return container._instantiate_all(property, args, None, kwargs)
    
    def _instantiate(self, name, factory, factory_args, factory_kw, custom_kw = None):
        #static values
        if not callable(factory): return factory

        #resolves all the dependencies for the component being resolved
        factory_kwargs = self._resolve_dependencies(factory, custom_kw)
        
        argument_list, var_args, var_kwargs = ref.get_arguments_for_method(factory)
        kwargs = dict([(key, factory_kwargs[key]) for key in factory_kwargs.keys() if key in argument_list.keys()])
        if factory_args == None: factory_args = ()
        if kwargs == None: kwargs = {}

        instance = factory(*factory_args, **kwargs)
        return instance
        
    def _instantiate_all(self, property, factory_args, factory_kw, custom_kw):
        all_instances = []
        if property not in self.config.components:
            raise KeyError("No indirect component for: %s", property)
        if self.config.components[property][0]!="indirect":
            raise KeyError("No indirect component for: %s", property)

        component_type, lifestyle_type, all_classes, args, kwargs = self.config.components[property]

        if (property in self.instances and lifestyle_type == "singleton"):
            return self.instances[property]
            
        for cls in all_classes:
            instance = self._instantiate("", cls, factory_args, factory_kw, custom_kw)
            all_instances.append(instance)
        
        if lifestyle_type == "singleton": 
            self.instances[property] = all_instances
                
        return all_instances

    def _resolve_dependencies(self, factory, custom_kw):
        arguments_with_defaults, var_args, var_kwargs = ref.get_arguments_for_method(factory)

        dependencies = {}

        for arg, default in arguments_with_defaults.iteritems():
            if custom_kw and arg in custom_kw:
                dependencies[arg] = custom_kw[arg]
            elif arg in self.config.components:
                dependencies[arg] = self._get(arg, factory, custom_kw)
            elif default == None:
                raise KeyError("Argument %s in class %s's constructor was not found! Did you forget to register it in the container, or to pass it as a named argument?" 
                               % (arg, factory.__name__))

        return dependencies
        
    def _get(self, property, factory, custom_kw):
        if property not in self.config.components:
            raise KeyError("No factory for: %s", property)

        component_type, lifestyle_type, component, args, kwargs = self.config.components[property]

        if component_type == "instance": return component
        
        if (property in self.instances and lifestyle_type == "singleton"):
            return self.instances[property]

        if component_type != "indirect" and isinstance(component, (tuple, list, dict, set)):
            return component
        
        if (component_type != "indirect" and component in self.instances and lifestyle_type == "singleton"):
            return self.instances[component]

        if component_type == "indirect": 
            if args == None: args = []
            if kwargs == None: kwargs = {}
            
            indirect_property = self._instantiate_all(property, args, kwargs, custom_kw)
            return indirect_property
        
        instance = self._instantiate(property, component, args, kwargs, custom_kw)
        self.instances[property] = instance
        self.instances[component] = instance
        return instance
