sc-benchmark
============

Scientific Computing benchmarks (HPC, storage, genomics)

Setup
-------
```
$ sudo apt-get install python-pip
$ pip install -r requirements.txt
```

scratch-dna.py
--------------

```
$ ~/py/scratch-dna.py
scratch-dna
    A storage benchmarking tool that creates a random DNA string,
    concatenates this string a random number of times and writes
    the result multiple files with varying length.

    Backend support: localfile system / swift cluster(throught swift APIs)

Usage:
    scratch-dna.py -o OBJS -s SIZE -m SIZE_MULTI [-d DIR]
    scratch-dna.py -o OBJS -s SIZE -m SIZE_MULTI -d DIR -i API_SERVER -u USER -k KEY [-c CONCURRENCY]
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
```

Example
--------------

* To local file system
```
 $ ./scratch-dna.py -m 3 -s 2000 -o 1000 -d /tmp/sc
CharzMac.local: ... building random DNA sequence of 1.953 KB...
CharzMac.local: ... writing 1000 files with filesizes between 1.953 KB and 5.859 KB ...
CharzMac.local: 3.977718 MB written in 0.143 seconds (27.796 MB/s, 6987 files/s)
```
here we are writing 1000 files into the current directory to evaluate throughput performance. The files contain a dna snippet that is 2000 bytes long and each snippet is contatenated with the running file counter and the current hostname and then duplicated n times (n is a random number between 1 and 3).

```
$ ./scratch-dna.py -o 10000 -s 4 -m 1 -d /tmp/sc
CharzMac.local: ... building random DNA sequence of 0.004 KB...
CharzMac.local: ... writing 10000 files with filesizes between 0.004 KB and 0.004 KB ...
CharzMac.local: 0.208750 MB written in 1.320 seconds (0.158 MB/s, 7576 files/s)
```

here we are writing 10000 small files (max 12 bytes) into the current directory to evaluate metadata performance. The dna snippet is 4 bytes long and is not duplicated.

In general dna snippet would be much more random if it could be regenerated for each file, however this would increase compute times. If we run this scratch-dna.py on a compute cluster each node would generate unique data.

* To Swift Cluster (through Swift APIs)
```
$ ./scratch-dna.py -i 192.168.200.101 -u swiftstack -k swiftstack -m 1 -s 1024 -o 50 -d /tmpxx
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

