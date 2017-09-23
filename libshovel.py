#!/usr/bin/env python3
# -*- coding: utf_8 -*-

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# libshovel: the heavy lifting for data shoveling

import threading
import queue
import os
import random

import time # for testing, to get sleep()

class Shovel():
    def __init__(self,threads,buffersize,chunksize):
        self.threads = threads
        self.buffersize = buffersize
        self.chunksize = chunksize

        self.queue = queue.Queue()
        self.thread = threading.Thread()

        self.worker_status_lock = threading.Lock()
        self.worker_status = {}

        self.worker_queue_lock = threading.Lock()
        self.worker_queue = {}

        for i in range(self.threads):
            t = threading.Thread(target=self._Worker)
            t.daemon = True
            t.start()

    def Copy(self,src,dst):
        if os.path.isfile(src):
            size=os.path.getsize(src)
            for i in range(0,size,self.chunksize):
                self._QueueFileChunk(src,dst,i)
        elif os.path.isdir(src):
            self._QueueDir(src,dst)
        else:
            # uh wtf?
            pass

    def Running(self):
        if not self.queue.empty():
            return 1
        threads_active=0
        with self.worker_status_lock:
            for key in self.worker_status.keys():
                if self.worker_status[key]:
                    threads_active=1
        return threads_active

    def Status(self):
        status = {}
        with self.worker_status_lock:
            status = self.worker_status
        return status

    def Queue(self):
        return len(self.worker_queue.keys())

    def _QueueFileChunk(self,src,dst,start):
        queue_key=self._CreateWorkerQueueKey()
        with self.worker_queue_lock:
            self.worker_queue[queue_key] = [self._CopyFileChunk,src,dst,start]
        self.queue.put(queue_key)

    def _QueueDir(self,src,dst):
        queue_key=self._CreateWorkerQueueKey()
        with self.worker_queue_lock:
            self.worker_queue[queue_key] = [self._CopyDir,src,dst]
        self.queue.put(queue_key)

    def _CopyFileChunk(self,src,dst,start):
        infile = open(src,'rb',self.buffersize)
        if os.path.exists(dst):
            outfile = open(dst,'r+b',self.buffersize)
        else:
            outfile = open(dst,'wb',self.buffersize)
        infile.seek(start,0)
        outfile.seek(start,0)
        eof=False
        total_bytesread=0
        while not eof:
            buffer = infile.read(self.buffersize)
            outfile.write(buffer)

            bytesread = len(buffer)
            total_bytesread += bytesread

            if bytesread < self.buffersize:
                eof=True

            if total_bytesread >= self.chunksize:
                eof=True

        infile.close()
        outfile.close()

    def _CopyDir(self,src,dst):
        os.mkdir(dst)
        for f in os.listdir(src):
            self.Copy(os.path.join(src,f), os.path.join(dst,f))

    def _CreateWorkerQueueKey(self):
        keychars = list('! #$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~')
        new_key = []
        for i in range(16):
            new_key.append(random.choice(keychars))
        key = ''.join(new_key)
        found_in_queue=0
        with self.worker_queue_lock:
            if key in self.worker_queue:
                found_in_queue=1
        if found_in_queue:
            return self._CreateWorkerQueueKey()
        else:
            return key

    def _Worker(self):
        self.thread = threading.current_thread()
        with self.worker_status_lock:
            self.worker_status[self.thread.ident] = None
        while True:
            # thread main loop
            # dequeue item
            item = self.queue.get()
            queue_item = []
            # update worker status with item
            with self.worker_status_lock:
                self.worker_status[self.thread.ident] = item
            # grab item from queue
            with self.worker_queue_lock:
                queue_item = self.worker_queue[item]

            # run item - item[0] is a bound method, item[1:] are its arguments
            queue_item[0](*queue_item[1:])

            # update worker status to idle
            with self.worker_status_lock:
                self.worker_status[self.thread.ident] = None
            # delete item from queue
            with self.worker_queue_lock:
                del self.worker_queue[item]
            self.queue.task_done()
