#! /usr/bin/env python

import sys, os, time, random, socket

#print 'Argument List:', str(sys.argv)


def main(numfiles, bytesize, maxmult, mydir):
    dnalist = list('ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT')

    kbytesize=float(bytesize)/1024
    hostname=socket.gethostname()

    print '%s: ... building random DNA sequence of %.3f KB...'% (hostname,
                                                                 kbytesize)

    dnastr = ''
    for i in range(bytesize):
        dnastr += random.choice(dnalist)

    start = time.time()
    wbytes = 0.0
    nfiles = 0

    print '%s: ... writing %s files with filesizes ' \
        'between %.3f KB and %.3f KB ...' % (hostname,
                                             numfiles,
                                             kbytesize,
                                             kbytesize*maxmult)

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
                                        wbytes/1048576,
                                        elapsed,
                                        wbytes/1048576/elapsed,
                                        nfiles/elapsed)

def usage(program):
    print 'Error! 4 arguments required. ' \
          'Execute %s [number-of-files] [file-size-bytes] ' \
          '[random-file-size-multiplier] [writable-directory]' % program


if __name__ == '__main__':
    if len(sys.argv) == 5:
        if not os.path.isdir(sys.argv[4]):
            print 'folder %s does not exist' % sys.argv[4]
            sys.exit(1)
    else:
        usage(sys.argv[0])
        sys.exit(1)

    argv = map(int, sys.argv[1:4])
    argv.append(sys.argv[4])
    main(*argv)

