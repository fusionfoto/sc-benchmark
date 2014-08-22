#!/usr/bin/python

import time
import json
import sys

import gevent.pool
from geventhttpclient import HTTPClient
from geventhttpclient.url import URL


class swiftclient(object):

    def __init__(self, auth_url, user, key,
                 concurrency=10, timeout=120):
        self.auth_user = user
        self.auth_key = key
        self.token = ''
        self.auth_url = auth_url
        self.storage_url = ''

        self.concurrency = concurrency
        self.timeout = timeout

        self.start = 0
        self.elapsed = 0
        self.objects = 0
        self.content_size = 0
        self.err_count = 0
        self.http = None

    def get_token(self):
        url = URL(self.auth_url)
        headers = {}
        headers['x-auth-user'] = self.auth_user
        headers['x-auth-key'] = self.auth_key

        self.http = HTTPClient.from_url(url, headers=headers)

        response = self.http.get(url.request_uri)
        assert response.status_code == 200

        self.token = response['x-auth-token']
        self.storage_url = response['x-storage-url']
        #print 'TOKEN: %s' % self.token
        #print 'URL: %s' % self.storage_url
        self.http.close()
        self.http = None

    def put(self, container, name=None, content=None, concurrent=False):
        put_url = '%s/%s' % (self.storage_url, container)
        if name:
            put_url = '%s/%s' % (put_url, name)

        url = URL(put_url)
        if self.http is None:
            self.http = HTTPClient.from_url(url,
                                            headers={'x-auth-token': self.token},
                                            concurrency=self.concurrency,
                                            connection_timeout=self.timeout,
                                            network_timeout=self.timeout
                                            )

        response = self.http.request('PUT',
                                     url.request_uri,
                                     body=content,
                                     headers={'x-auth-token': self.token})

        if response.status_code not in [201, 202]:
            self.err_count += 1
            sys.stdout.write('E%s' % response.status_code)
            sys.stdout.flush()
#            print response.headers
            return

        sys.stdout.write('.')
        sys.stdout.flush()

        if concurrent is False:
            self.http.close()
            self.http = None

    def concurrent(self, objects, func, *args):
        self.objects = objects

        self.start = time.time()
        pool = gevent.pool.Pool(self.concurrency)
        for i in range(self.objects):
            content = args[2](i)
            self.content_size += len(content)
            pool.spawn(func,
                       args[0],
                       '%s-%.6d' % (args[1], i),
                       content,
                       args[3])

        pool.join()
        self.http.close()
        self.http = None
        self.elapsed = time.time() - self.start

    def report(self):
        print ''
        print 'object: %d ' % self.objects,
        print 'transfer data: %.2f MB' % (self.content_size/(1024.0**2))
        print 'elasped: %.3fs' % self.elapsed
        print 'concurrency: %d ' % self.concurrency

        print '\t %.3f req/s' % (self.objects/self.elapsed)
        print '\t %.3f MB/s' % (self.content_size/(1024.0**2)/self.elapsed)
        print '\t %d error' % (self.err_count)


if __name__ == '__main__':
    container = '06bench'
    objname = 'obj'
    content = lambda i: '12xxwerwerwer' * i
    objects = 100
    auth_url = 'http://192.168.200.101/auth/v1.0'
    user = 'swiftstack'
    key = 'swiftstack'
    concurrency = 10

    client = swiftclient(auth_url,
                         user,
                         key,
                         concurrency)
    client.get_token()

    client.put(container)
    client.concurrent(objects, client.put, container, objname, content, True)
    client.report()
