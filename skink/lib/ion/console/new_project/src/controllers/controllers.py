from datetime import datetime

from ion.controllers import Controller, route

class DefaultController(Controller):

    @route('/')
    def index(self):
        return self.render_template("index.html", date=datetime.now())
