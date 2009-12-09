skink Event Bus
===============

skink features an event bus that allows advanced users to plug into the CI server lifecycle.

Usually that's required in plug-ins or for custom initialization of skink.

------------
skink events
------------

on_before_server_start
----------------------

This event is fired right before skink's server infrastructure kicks in. This is a good oportunity to mess with settings, plugins and anything else you need to change before the server goes up.

To subscribe::
    def on_before_server_start_handler(data):
        #here you can do anything you need to do with the server or context.
        #data is a dictionary that comes with two keys:
        #*server - It's the current server instance
        #*context - The current context.
        #In order to access them just use data['server'] or data['context']
    
    server.subscribe('on_before_server_start', on_before_server_start_handler)

on_after_server_start
----------------------

This event is fired right after skink's server is started. This is a good oportunity do anything that needs to be done after the server is up.

To subscribe::
    def on_after_server_start_handler(data):
        #here you can do anything you need to do with the server or context.
        #data is a dictionary that comes with two keys:
        #*server - It's the current server instance
        #*context - The current context.
        #In order to access them just use data['server'] or data['context']
    
    server.subscribe('on_after_server_start', on_after_server_start_handler)
        
