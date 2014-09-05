#!/usr/bin/python

import time
import json
import sys

import gevent.pool
from geventhttpclient import HTTPClient
from geventhttpclient.url import URL


class swiftclient(object):

    def __init__(self, auth_url, user, key,
                 concurrency=10, containers=1,
                 connect_timeout=30, network_timeout=60):
        self.auth_user = user
        self.auth_key = key
        self.token = ''
        self.auth_url = auth_url
        self.storage_url = ''

        self.containers = containers
        self.concurrency = concurrency
        self.connect_timeout = connect_timeout
        self.network_timeout = network_timeout

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

    def put_containers(self, container):
        for i in range(self.containers):
            new_container = '%s_%.6d'% (container, i)
            self.put(new_container)

    def put(self, container, name=None, content=None, concurrent=False):
        put_url = '%s/%s' % (self.storage_url, container)
        if name:
            put_url = '%s/%s' % (put_url, name)

        if content:
            headers = {'Content-Length': str(len(content)),
                       'x-auth-token': self.token,
                       'Content-Type': 'application/octet-stream'
                       }
        else:
            headers = {'Content-Length': '0',
                       'x-auth-token': self.token}

        url = URL(put_url)
        if self.http is None:
            self.http = HTTPClient.from_url(url,
                                            headers=headers,
                                            headers_type=dict,
                                            concurrency=self.concurrency,
                                            connection_timeout=self.connect_timeout,
                                            network_timeout=self.network_timeout
                                            )

        response = self.http.request('PUT',
                                     url.request_uri,
                                     body=content,
                                     headers=headers)
        if response.status_code not in [201, 202]:
            self.err_count += 1
            sys.stdout.write('E%s' % response.status_code)
            sys.stdout.flush()
            print response.headers
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
                       '%s_%.6d' % (args[0], (i % self.containers)),
                       '%s_%.6d' % (args[1], i),
                       content,
                       True)

        pool.join()
        self.elapsed = time.time() - self.start
        self.http.close()
        self.http = None

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

    client.put_containers(container)
    client.concurrent(objects, client.put, container, objname, content)
    client.report()

