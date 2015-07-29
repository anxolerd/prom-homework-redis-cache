from wsgiref.simple_server import make_server
from cgi import parse_qs
import time


def simple_app(environ, start_response):
    time.sleep(2)
    start_response('200 OK', [('Content-type', 'text/plain')])
    parameters = parse_qs(environ.get('QUERY_STRING', ''))
    retval = ["%s = %s\n" % (k, v) for (k, v) in parameters.iteritems()]
    if not len(retval):
        retval.append('empty')
    return retval

if __name__ == '__main__':
    make_server('', 8000, simple_app).serve_forever()
