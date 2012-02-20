Introduction
------------

skink is a Continuous Integration server that's as simple as it gets. 

Specify a git repository, a shell command to execute 
to build your project and that's pretty much it.

Just ask skink to run your build and it will update your code, run a build
and keep track of your build history.

You can create a git hook to auto-execute the build upon push as well.

Installing
----------
It couldn't be easier. Run the three following commands in a shell::

    git clone git://github.com/heynemann/skink.git
    sudo pip install coverage # (if you do not want coverage or you don't need to run make all for skink, ignore this)
    make createdb
    make run

Congratulations! You are the happy owner of a build server!
Just reach http://localhost:8089 (or whatever port you configured in the config.ini file) and enjoy.

Create your project and start building!

Project Naming
--------------
The name for the project comes from the "Plestiodon skiltonianus" or Western Skink - http://www.wildherps.com/species/E.skiltonianus.html.

This very beautiful reptile keeps moving constantly, just like the skink server does.

Skinkize your project right now! Keep moving!

Project Website
---------------
You can check the project website at http://www.skinkci.org
