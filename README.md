# datashovel
multi-threaded data shovelling tool

Can provide a significant speed boost by copying data in parallel.

Will be faster: copying to and from RAID arrays, SAN LUNs and SSDs
Probably faster: copying directories with large numbers of files
Won't be faster: copying large files to or from a single HDD'

>5x speedup copying FreeBSD 11-STABLE source tree

root@keg:~# df -h /export/install/freebsd/11-STABLE/
Filesystem             Size   Used  Available Capacity  Mounted on
tank/export/install/freebsd/11-STABLE
14T   1.5G        11T     1%    /export/install/freebsd/11-STABLE
root@keg:~# find /export/install/freebsd/11-STABLE/ | wc -l
147557

root@keg:~# time cp -r /export/install/freebsd/11-STABLE /ssd/11-STABLE

real    27m25.768s
user    0m7.626s
sys     2m29.502s


root@keg:~# time datashovel.py /export/install/freebsd/11-STABLE /ssd/11-STABLE

real    4m43.245s
user    3m5.557s
sys     2m35.544s

>1.5x speedup copying photos

root@keg:~# time cp -r /export/photos/20170414\ easter/ /ssd/test

real    0m50.186s
user    0m0.029s
sys     0m40.542s

root@keg:~# time datashovel.py /export/photos/20170414\ easter/ /ssd/test

real    0m30.876s
user    0m4.646s
sys     0m14.843s

>2x speedup copying single huge file:

root@keg:~# time cp /export/net/shatter/bec-hd2.img /ssd/bec-hd2.img

real    38m51.206s
user    0m0.151s
sys     18m15.710s

root@keg:~# time datashovel.py /export/net/shatter/hd2.img /ssd/hd2.img

real    16m46.608s
user    1m47.935s
sys     6m31.219s

Test system details:
