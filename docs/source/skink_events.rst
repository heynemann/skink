Ion Event Bus
===============

Ion features an event bus that allows advanced users to plug into the CI server lifecycle.

Usually that's required in plug-ins or for custom initialization of Ion.

------------
Ion events
------------

on_before_server_start
----------------------

This event is fired right before Ion's server infrastructure kicks in. This is a good oportunity to mess with settings, plugins and anything else you need to change before the server goes up.

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

This event is fired right after Ion's server is started.

To subscribe::
    def on_after_server_start_handler(data):
        #here you can do anything you need to do with the server or context.
        #data is a dictionary that comes with two keys:
        #*server - It's the current server instance
        #*context - The current context.
        #In order to access them just use data['server'] or data['context']

    server.subscribe('on_after_server_start', on_after_server_start_handler)

on_before_server_stop
---------------------

This event is fired right before Ion's server stops.

To subscribe::
    def on_before_server_stop_handler(data):
        #here you can do anything you need to do with the server or context.
        #data is a dictionary that comes with two keys:
        #*server - It's the current server instance
        #*context - The current context.
        #In order to access them just use data['server'] or data['context']

    server.subscribe('on_before_server_stop', on_before_server_stop_handler)

on_after_server_stop
--------------------

This event is fired right after Ion's server is stopped.

To subscribe::
    def on_after_server_stop_handler(data):
        #here you can do anything you need to do with the server or context.
        #data is a dictionary that comes with two keys:
        #*server - It's the current server instance
        #*context - The current context.
        #In order to access them just use data['server'] or data['context']

    server.subscribe('on_after_server_stop', on_after_server_stop_handler)

on_before_user_authentication
-----------------------------

This event is fired right before an user gets authenticated for an action that demands authentication.

To subscribe::
    def on_before_user_authentication_handler(data):
        #here you can do anything you need to do with the server or context.
        #data is a dictionary that comes with two keys:
        #*server - It's the current server instance
        #*context - The current context.
        #In order to access them just use data['server'] or data['context']

    server.subscribe('on_before_user_authentication', on_before_user_authentication_handler)

on_user_authentication_successful
---------------------------------

This event is fired when an user is already authenticated. This does not mean that the user is authenticating now, only that Ion could find the Controller.user property with some value other than *None*.

To subscribe::
    def on_user_authentication_successful_handler(data):
        #here you can do anything you need to do with the server or context.
        #data is a dictionary that comes with two keys:
        #*server - It's the current server instance
        #*context - The current context.
        #In order to access them just use data['server'] or data['context']

    server.subscribe('on_user_authentication_successful', on_user_authentication_successful_handler)


on_user_authentication_failed
-----------------------------

This event is fired when an user is not authenticated and the current action demands that he/she identifies him/herself. This is the best place to redirect the user to a login page.

To subscribe::
    def on_user_authentication_failed_handler(data):
        #here you can do anything you need to do with the server or context.
        #data is a dictionary that comes with two keys:
        #*server - It's the current server instance
        #*context - The current context.
        #In order to access them just use data['server'] or data['context']

    server.subscribe('on_user_authentication_failed', on_user_authentication_failed_handler)

