from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.images import Image, JPEG

import re, urllib

ALLOWED_URL_WIDTHS = (
    (re.compile(
        r'http://www1\.sciencemuseum\.org\.uk/hommedia\.ashx\?id=\d+&size=\w+'
    ), (100, 250)),
)

class BaseResizeHandler(webapp.RequestHandler):
    def get(self, width):
        url = self.request.get('url')
        width = int(width)
        if not url or not url_and_width_is_allowed(url, width):
            return self.error('Invalid arguments')
        
        cached = self.get_cached(url, width)
        if cached is not None:
            self.response.headers['Content-Type'] = 'image/jpeg'
            self.response.out.write(cached)
            return
        
        img = self.load_image(url)
        self.process_image(img, width)
        resized = img.execute_transforms(output_encoding = JPEG)
        self.response.headers['Content-Type'] = 'image/jpeg'
        self.response.out.write(resized)
    
    def get_cached(self, url, width):
        return None
    
    def load_image(self, url):
        return Image(image_data = urllib.urlopen(url).read()) 
    
    def error(self, msg):
        self.response.out.write("""
            <html>
            <head><title>Error</title></head>
            <body><h1>%s</h1></body>
            </html>""" % msg
        )

class WidthHandler(BaseResizeHandler):
    def process_image(self, img, width):
        img.resize(
            width = min(width, img.width),
        )

class SquareHandler(BaseResizeHandler):
    def process_image(self, img, width):
        for op, kwargs in resize_crop_square(img.width, img.height, width):
            getattr(img, op)(**kwargs)

def resize_crop_square(width, height, dimension):
    if width == height:
        return [('resize', {'width': dimension, 'height': dimension})]
    
    if width > height:
        # Resize so smallest side is required dimension
        r_height = dimension
        r_width = int(float(width) / height * dimension)
        left = (r_width - dimension) / 2.0
        right = r_width - left
        ops = [
            ('resize', {'width': r_width, 'height': r_height}),
            ('crop', {
                'left_x': left / r_width,
                'right_x': right / r_width,
                'top_y': 0.0,
                'bottom_y': 1.0,
            })
        ]
        return ops
    else:
        r_width = dimension
        r_height = int(float(height) / width * dimension)
        top = (r_height - dimension) / 2.0
        bottom = r_height - top
        ops = [
            ('resize', {'width': r_width, 'height': r_height}),
            ('crop', {
                'left_x': 0.0,
                'right_x': 1.0,
                'top_y': top / r_height,
                'bottom_y': bottom / r_height,
            })
        ]
        return ops

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
