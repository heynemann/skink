#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
sqlalchemy_tool.py (donated to the public domain by Nando Florestan)
================== http://code.google.com/p/webpyte

SQLAlchemy integration for CherryPy,
such that you can access multiple databases,
but only one of these databases per request or thread.

The database to be accessed is chosen by a properly configured CherryPy tool,
which takes care of the transaction (commiting it at the end, or rolling back
if an exception is raised).

Usage:
from sqlalchemy_tool import metadata, session, mapper
# Use the above metadata, session, mapper when defining your models

In your application configuration:

[/]
tools.SATransaction.on = True
tools.SATransaction.dburi = 'sqlite:///database.sqlite'
tools.SATransaction.echo = False           # this is the default
tools.SATransaction.convert_unicode = True # this is the default

If you set *echo* to True, SQLAlchemy will print the SQL statements.

*convert_unicode* should always be True and you should always
use unicode strings with SQLAlchemy!

When you are at the interpreter you can do:

    from sqlalchemy_tool import configure_session_for_app
    configure_session_for_app(your_cherrypy_app)
'''


from sqlalchemy import MetaData, create_engine, __version__ as sa_version
from sqlalchemy.orm import scoped_session, sessionmaker

if sa_version.split(".") < ["0", "5", "0"]:
    raise ImportError("Version 0.5 or later of SQLAlchemy required.")

def new_session():
    return scoped_session(sessionmaker(autoflush=True, autocommit=False))

metadata = MetaData()
session = new_session()
mapper = session.mapper

# A dict in which keys are connection strings and values are SA engine objects
_engines = {}

def configure_session(dburi='sqlite:///database.sqlite',
                      echo=False, convert_unicode=True):
    """This function is called on each request.
    Tool configuration is automatically passed to it as arguments.
    It gets a *dburi*,
    creates a corresponding SQLAlchemy engine if it doesn't exist,
    chooses the corresponding SQLALchemy engine,
    and binds the session to it.
    
    Additional arguments or configuration are used if an engine is created:
    *echo*: whether to print SQL statements, default is False.
    *convert_unicode*: default is True, so you should use unicode strings
    """
    engine = _engines.get(dburi, None) # Look up the dict.
    if engine is None:              # If missing engine, create and store it.
        _engines[dburi] = engine = \
            create_engine(dburi, echo=echo, convert_unicode=convert_unicode)
    session.bind = engine # Set engine for this thread or request

def configure_session_for_app(app, echo=False, convert_unicode=True):
    '''Useful when you are at the interpreter, or whenever you are outside
    a request and need to bind the session in the current thread.
    Assuming app is configured with a SQLAlchemy connection string,
    binds the session to the corresponding engine.
    '''
    adict = app.config.get('/', {})
    dburi = adict.get('tools.SATransaction.dburi', '')
    if not dburi:
        raise RuntimeError('This app is not configured for SATransaction.')
    configure_session(dburi, echo=echo, convert_unicode=convert_unicode)


import cherrypy
from cherrypy import request
from sys import exc_info


class SATransaction(cherrypy.Tool):
    """A tool that encloses each request handler in a SQLAlchemy transaction.
    See this module's docstring for more details.
    """
    # A list of exceptions that do not cause rollback. Extendable by apps.
    passable_exceptions=[cherrypy.HTTPRedirect] # KeyboardInterrupt, SystemExit
    
    def __init__(self):
        self._name = 'SATransaction'
        self._point = 'on_start_resource'
        self.callable = configure_session
        self._priority = 50
        # If this priority is not appropriate for both hook points, know that
        # you can set a 'priority' attribute on the actual functions.
        # Tool.priority is just a shortcut for that.
    
    def _setup(self):
        '''This method is called on each request to attach this tool's hooks,
        unless tools.SATransaction.on = False.
        
        If in a static request (using tools.staticdir or tools.staticfile),
        the transaction is certainly not needed,
        and thus is disabled to (probably) save some CPU time.
        '''
        if request.config.get('tools.staticdir.on', False) or \
            request.config.get('tools.staticfile.on', False):
                return
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('on_end_resource', self.on_end_resource)
    
    def on_end_resource(self):
        """Method that is called after the CherryPy request handler.
        Tries to commit the transaction, then if an exception is raised,
        rolls back and raises the exception so the response body is changed.
        Ensures the session is reset and ready for next request.
        """
        typ, value, trace = exc_info()
        # Rollback if exception raised in request handler
        if value is not None and not typ in self.passable_exceptions:
            session.rollback()  # undoes what has been flushed
            session.expunge_all() # undoes what has not been flushed
            # deconfigure (unbind) session so it is ready for next request
            session.remove()
            return
        # Else try to commit (which can raise a new exception)
        try:
            session.flush()
            session.commit()
        except:
            session.rollback()    # undoes what has been flushed
            session.expunge_all() # undoes what has not been flushed
            raise                 # let this exception propagate
        finally:
            # deconfigure (unbind) session so it is ready for next request
            session.remove()


cherrypy.tools.SATransaction = SATransaction()

