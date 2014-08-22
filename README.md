# sc-benchmark


Scientific Computing benchmarks (HPC, storage, genomics)

## Setup

```
$ sudo apt-get install python-pip
$ pip install -r requirements.txt
```

## scratch-dna.py


```
$ ~/py/scratch-dna.py
scratch-dna
    A storage benchmarking tool that creates a random DNA string,
    concatenates this string a random number of times and writes
    the result multiple files with varying length.

    Backend support: localfile system / swift cluster(throught swift APIs)

Usage:
    scratch-dna.py -o OBJS -s SIZE -m SIZE_MULTI [-d DIR]
    scratch-dna.py -o OBJS -s SIZE -m SIZE_MULTI -d DIR -A AUTH -U USER -K KEY [-C CONCURRENCY]
    scratch-dna.py -h | --help

Options:
    -h --help       Show this screen.
    -d DIR          Writable directory(container) [default: /tmp]
    -o OBJS         File(object) number
    -s SIZE         File(object) size
    -m SIZE_MULTI   Random File(object) size multiplier

    -A AUTH         Swift URL for obtaining an auth token
    -U USER         Swift User for obtaining an auth token
    -K KEY          Swift Key for obtaining an auth token
    -C CONCURRENCY  Concurrent processes [default: 10]
```

## Example


### To local file system

```
 $ ./scratch-dna.py -m 3 -s 2000 -o 1000 -d /tmp/sc
CharzMac.local: ... building random DNA sequence of 1.953 KB...
CharzMac.local: ... writing 1000 files with filesizes between 1.953 KB and 5.859 KB ...
CharzMac.local: 3.977718 MB written in 0.143 seconds (27.796 MB/s, 6987 files/s)
```
here we are writing 1000 files into the current directory to evaluate throughput performance. The files contain a dna snippet that is 2000 bytes long and each snippet is contatenated with the running file counter and the current hostname and then duplicated n times (n is a random number between 1 and 3).

```
$ ./scratch-dna.py -o 10000 -s 4 -m 1 -d /tmp/sc

################################################################################
# Backend: Local file system (/tmp/sc) #
################################################################################

CharzMac.local: ... building random DNA sequence of 0.004 KB...
CharzMac.local: ... writing 10000 files with filesizes between 0.004 KB and 0.004 KB ...
CharzMac.local: 0.208750 MB written in 1.320 seconds (0.158 MB/s, 7576 files/s)
```

here we are writing 10000 small files (max 12 bytes) into the current directory to evaluate metadata performance. The dna snippet is 4 bytes long and is not duplicated.

In general dna snippet would be much more random if it could be regenerated for each file, however this would increase compute times. If we run this scratch-dna.py on a compute cluster each node would generate unique data.

### To Swift Cluster (through Swift APIs)

```
$ ./scratch-dna.py -A http://192.168.200.101/auth/v1.0 -U swiftstack -K swiftstack -m 1 -s 1024 -o 50 -d /tmpxx

################################################################################
# Backend: Swfit cluster (http://192.168.200.101/auth/v1.0) #
################################################################################

CharzMac.local: ... building random DNA sequence of 1.000 KB...
CharzMac.local: ... writing 50 files with filesizes between 1.000 KB and 1.000 KB ...
...................................................
CharzMac.local: 0.049582 MB written in 6.702 seconds (0.007 MB/s, 7 files/s)

object: 50  transfer data: 0.05 MB
elasped: 6.702s
concurrency: 10 
	 7.460 req/s
	 0.007 MB/s
	 0 error
```

Or you can export ST_AUTH, ST_USER and ST_KEY to environment variables.

```
$ export ST_AUTH=http://192.168.200.101/auth/v1.0
$ export ST_USER=swiftstack
$ export ST_KEY=swiftstack

$ env |grep ST
ST_AUTH=http://192.168.200.101/auth/v1.0
ST_USER=swiftstack
ST_KEY=swiftstack
```

Run command without -A, -U and -K.
 
```
$ ./scratch-dna.py -m 1 -s 1024 -o 50 -d /tmpxx

################################################################################
# Backend: Swfit cluster (http://192.168.200.101/auth/v1.0) #
################################################################################

CharzMac.local: ... building random DNA sequence of 1.000 KB...
CharzMac.local: ... writing 50 files with filesizes between 1.000 KB and 1.000 KB ...
...................................................
CharzMac.local: 0.049582 MB written in 5.827 seconds (0.009 MB/s, 8 files/s)

object: 50  transfer data: 0.05 MB
elasped: 5.827s
concurrency: 10 
	 8.581 req/s
	 0.009 MB/s
	 0 error

```





