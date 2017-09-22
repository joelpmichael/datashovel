#!/usr/bin/env python3
# -*- coding: utf_8 -*-

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# data shovel: multi-threaded data copying

# because, sometimes 100 people with shovels is faster than a backhoe...

import os
import argparse
import multiprocessing # for multiprocessing.cpu_count()
import time # for time.sleep()

import libshovel

# handle arguments
parser = argparse.ArgumentParser(description='shovel data between two locations')

parser.add_argument('-x', '--checksum',
                    action='store_const',
                    const=1,
                    default=0,
                    help='Checksum transferred data',
                   )

parser.add_argument('-p', '--parallel',
                    type=int,
                    default=multiprocessing.cpu_count(),
                    help='Number of parallel threads to use',
                   )

parser.add_argument('-b', '--buffer',
                    type=str,
                    default='1M',
                    help='Buffer size in bytes (optional K or M suffix)',
                   )

parser.add_argument('-c', '--chunk',
                    type=str,
                    default='256M',
                    help='Chunk size in Mbytes (optinoal M or G suffix)',
                   )

parser.add_argument('input',
                    type=str,
                    nargs='+',
                    help='1 or more input files or directories',
                   )

parser.add_argument('output',
                    type=str,
                    nargs=1,
                    help='Output file or directory',
                   )

args = parser.parse_args()

# parse and multiply buffer and chunk size

buffer_arg = args.buffer
buffer_last_char = buffer_arg[-1:]
if buffer_last_char.isdigit():
    buffer=int(buffer_arg)
else:
    if buffer_last_char=='K':
        buffer=int(buffer_arg[:-1])*1024
    elif buffer_last_char=='M':
        buffer=int(buffer_arg[:-1])*1024*1024
    else:
        raise ValueError('Buffer must be in bytes, or with a K or M suffix')

chunk_arg = args.chunk
chunk_last_char = chunk_arg[-1:]
if chunk_last_char.isdigit():
    chunk=int(chunk_arg)
else:
    if chunk_last_char=='K':
        chunk=int(chunk_arg[:-1])*1024
    elif chunk_last_char=='M':
        chunk=int(chunk_arg[:-1])*1024*1024
    elif chunk_last_char=='G':
        chunk=int(chunk_arg[:-1])*1024*1024*1024
    else:
        raise ValueError('Chunk must be in bytes, or with a K, M or G suffix')

if buffer > chunk:
    buffer = chunk

# sanity-check user-supplied source and destination paths
input_paths = args.input

output_path = args.output[0]

if output_path in input_paths:
    raise ValueError('Output must not be an input')

for input in input_paths:
    if not os.path.exists(input):
        raise ValueError('File does not exist', input)

shovel = libshovel.Shovel(args.parallel, buffer, chunk)
for input in input_paths:
    shovel.Copy(input,output_path)

while shovel.Running():
    print('Worker Status:')
    print(shovel.Status())
    print('Worker Queue:')
    print(shovel.Queue())
    time.sleep(5)

