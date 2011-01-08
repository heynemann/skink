import tornado.web

class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("Hello world!")

application = tornado.web.Application([
    (r"/", MainHandler),
])
