#! /usr/bin/env python

"""
scratch-dna
    A storage benchmarking tool that creates a random DNA string,
    concatenates this string a random number of times and writes
    the result multiple files with varying length.

    Backend support: localfile system / swift cluster(throught swift APIs)

Usage:
    scratch-dna.py -o OBJS -s SIZE -m SIZE_MULTI [-d DIR]
    scratch-dna.py -o OBJS -s SIZE -m SIZE_MULTI -d DIR -i API_SERVER \
-u USER -k KEY [-c CONCURRENCY]
    scratch-dna.py -h | --help

Options:
    -h --help       Show this screen.
    -d DIR          Writable directory(container) [default: /tmp]
    -o OBJS         File(object) number
    -s SIZE         File(object) size
    -m SIZE_MULTI   Random File(object) size multiplier

    -i API_SERVER   Swift API IP
    -u USER         Swift User
    -k KEY          Swift User's password
    -c CONCURRENCY  Concurrent processes [default: 10]
"""

import sys, os, time, random, socket
from client import swiftclient
from docopt import docopt

def main(numfiles, bytesize, maxmult, mydir,
         api_ip=None, user=None, key=None,
         concurrency=None):

    dnalist = list('ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT')

    kbytesize=float(bytesize)/1024
    hostname=socket.gethostname()

    print '%s: ... building random DNA sequence of %.3f KB...'% (hostname,
                                                                 kbytesize)

    dnastr = ''
    for i in range(bytesize):
        dnastr += random.choice(dnalist)


    print '%s: ... writing %s files with filesizes ' \
        'between %.3f KB and %.3f KB ...' % (hostname,
                                             numfiles,
                                             kbytesize,
                                             kbytesize*maxmult)
    def gen_fullstr(i):
        n = random.randint(1,maxmult)
        fullstr = (str(i)+dnastr+hostname) * n
        return fullstr

    if api_ip:
        container = mydir.replace('/','_')
        objname = 'scr-file'
        client = swiftclient(api_ip,
                            user,
                            key,
                            concurrency)
        client.get_token()
        client.put(container)

    start = time.time()
    wbytes = 0.0
    nfiles = 0

    if api_ip:
        client.concurrent( numfiles, client.put, container, objname, gen_fullstr, True)
        wbytes = client.content_size
        nfiles = numfiles
        print ''
    else:
        for i in range(numfiles):
            n = random.randint(1,maxmult)
            filename = "scr-%s-file-%s-%s" % (hostname,i,n)
            if not os.path.exists(os.path.join(mydir,hostname)):
                try:
                    os.mkdir(os.path.join(mydir,hostname))
                except:
                    pass
            #print "open %s ..." % filename)
            fullstr = (str(i)+dnastr+hostname) * n
            fh = open(os.path.join(mydir,hostname,filename), "w")
            fh.write(fullstr)
            fh.close()
            #print "closed %s ..." % filename)
            wbytes += len(fullstr)
            nfiles += 1

    elapsed = time.time() - start

    print '%s: %.6f MB written in %.3f seconds ' \
            '(%.3f MB/s, %d files/s)' % (hostname,
                                        wbytes/1048576.0,
                                        elapsed,
                                        wbytes/1048576.0/elapsed,
                                        nfiles/elapsed)

    if api_ip:
        client.report()

if __name__ == '__main__':
    argv = docopt(__doc__)
    objects = int(argv['-o'])
    size = int(argv['-s'])
    size_multi = int(argv['-m'])
    directory = argv['-d']

    api_ip = argv['-i']
    user = argv['-u']
    key = argv['-k']
    concurrency = int(argv['-c'])

    params = [objects, size, size_multi, directory]
    if api_ip:
        params.extend([api_ip, user, key, concurrency])

    main(*params)

