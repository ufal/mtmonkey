#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path

from base64 import b64encode
from os import chdir, getcwd
from subprocess import Popen, PIPE
from shutil import rmtree
from tempfile import mkdtemp

def process_task(task):
    # Create temporary directory for computations
    temp_dir = mkdtemp()
    filename = 'a.c'
    
    # cd to temp directory
    cwd = getcwd()
    chdir(temp_dir)

    # Save sent source code
    f = open(filename, 'w')
    f.write(task['source_code'])
    f.close()

    # Execute task
    p = Popen(['gcc', filename], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()

    # Return computed data
    output_file = open('a.out')
    result = {
        'output_file': b64encode(output_file.read()),
        'stdout': stdout,
        'stderr': stderr,
    }
    
    # Remove temp dir
    chdir(cwd)
    rmtree(temp_dir)
    
    return result


