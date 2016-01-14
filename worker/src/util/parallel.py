#!/usr/bin/env python
# coding=utf-8

"""
Utility functions for easy parallel processing, thanks go to:

    http://stackoverflow.com/a/5792404/1467943
"""

from multiprocessing import Process, Pipe
from itertools import izip

def spawn(f):
    def fun(ppipe, cpipe,x):
        ppipe.close()
        cpipe.send(f(x))
        cpipe.close()
    return fun

def parallel_map(f,X):
    pipe=[Pipe() for x in X]
    proc=[Process(target=spawn(f),args=(p,c,x)) for x,(p,c) in izip(X,pipe)]
    [p.start() for p in proc]
    ret = [p.recv() for (p,c) in pipe]
    [p.join() for p in proc]
    return ret

