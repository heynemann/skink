import tornado.ioloop
import tornado.httpserver

from lettuce import before, after, world
from selenium.firefox.webdriver import WebDriver
from selenium.firefox.firefox_profile import FirefoxProfile
from threading import Thread
from skink.app import application

# FirefoxProfile hack for offline mode on Linux
prefs = FirefoxProfile._get_webdriver_prefs()
prefs['network.manage-offline-status'] = 'false'

@staticmethod
def prefs_func():
    return prefs

FirefoxProfile._get_webdriver_prefs = prefs_func

class Server(Thread):

    def __init__(self, http):
        self.http = http
        Thread.__init__(self)

    def run(self):
        self.http.listen(8888)
        tornado.ioloop.IOLoop.instance().start()

@before.all
def setup_browser():
    world.browser = WebDriver()

@before.all
def run_server():
    world._server_main = tornado.httpserver.HTTPServer(application)
    server = Server(world._server_main)
    server.start()

@after.all
def teardown_browser(total):
    world.browser.quit()

@after.all
def stop_server(total):
    world._server_main.stop()
    tornado.ioloop.IOLoop.instance().stop()
