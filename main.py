from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.images import Image, JPEG

import re, urllib

ALLOWED_URL_WIDTHS = (
    (re.compile(
        r'http://www1\.sciencemuseum\.org\.uk/hommedia\.ashx\?id=\d+&size=\w+'
    ), (100, 250)),
)

class WidthHandler(webapp.RequestHandler):
    def get(self, width):
        url = self.request.get('url')
        width = int(width)
        if not url or not url_and_width_is_allowed(url, width):
            return self.error('Invalid arguments')
        img = self.load_image(url)
        img.resize(
            width = min(width, img.width),
        )
        resized = img.execute_transforms(output_encoding = JPEG)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(resized)
    
    def load_image(self, url):
        return Image(image_data = urllib.urlopen(url).read()) 
    
    def error(self, msg):
        self.response.out.write("""
            <html>
            <head><title>Error</title></head>
            <body><h1>%s</h1></body>
            </html>""" % msg
        )

class SquareHandler(webapp.RequestHandler):
    def get(self, width):
        self.response.out.write('not yet implemented')

def url_and_width_is_allowed(url, width):
    for r, widths in ALLOWED_URL_WIDTHS:
        if r.match(url) and width in widths:
            return True
    return False

if __name__ == '__main__':
    run_wsgi_app(webapp.WSGIApplication([
        (r'/w/(\d+)/', WidthHandler),
        (r'/s/(\d+)/', SquareHandler),
    ], debug=True))
