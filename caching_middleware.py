from wsgiref.simple_server import make_server
from example_server import simple_app
from cgi import parse_qs
import redis
import pickle

TIMEOUT = 30
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
REDIS = redis.Redis(connection_pool=POOL)


def cache(app, _cache=dict()):

    def wrapped_app(environ, start_response):
        parameters = parse_qs(environ.get('QUERY_STRING', ''))
        need_new = parameters.pop('cached', [])
        need_new = map(lambda x: x.lower(), need_new)
        key_base = environ['PATH_INFO'] + '?' + pickle.dumps(parameters)
        key_data = "DATA:%s" % key_base
        key_headers = "HEADERS:%s" % key_base
        key_status = "STATUS:%s" % key_base
        data, headers, status = (
            REDIS.get(key_data),
            REDIS.get(key_headers),
            REDIS.get(key_status),
        )

        # Need better naming
        need_new = 'false' in need_new
        if (not (data or headers or status) or need_new):
            data = app(environ, start_response)
            headers = start_response.im_self.headers._headers
            status = start_response.im_self.status

            REDIS.set(key_data, pickle.dumps(data))
            REDIS.set(key_headers, pickle.dumps(headers))
            REDIS.set(key_status, pickle.dumps(status))
            REDIS.expire(key_data, TIMEOUT)
            REDIS.expire(key_headers, TIMEOUT)
            REDIS.expire(key_status, TIMEOUT)
        else:
            data = pickle.loads(data)
            headers = pickle.loads(headers)
            status = pickle.loads(status)
            start_response(status, headers)
        return data

    return wrapped_app

if __name__ == '__main__':
    make_server('', 8000, cache(simple_app)).serve_forever()
