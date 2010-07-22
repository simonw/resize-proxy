resize-proxy
============

A drop-dead simple image resizing proxy for Google App Engine. Configure it 
with a list of ALLOWED_URL_WIDTHS regular expressions and sizes (at the top
of main.py) and then construct URLs to images that look like this:

http://resize-proxy.appspot.com/s/100/?url=http://www1.sciencemuseum.org.uk/hommedia.ashx?id=11777%26size=Small

Where http://www1.sciencemuseum.org.uk/hommedia.ashx?id=11777%26size=Small is 
the URL to the original image, and /s/100/ means "crop to a square of width 
and height 100px". /w/100/ would resize without cropping to make the width 
100px.

Both fetched images and the resized/cropped versions are cached in memcached 
for between 25 and 35 days (a random cache length is used to avoid everything 
in the cache expiring at once).
