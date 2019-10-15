#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import programmatic_server as ps
import json
import sys

def dir_check(prefix,port):
    while True:
        with open('files.json') as f:
            files = json.load(f)
        files_current = ps.programmatic_server().get_modules(set_attribs=False)[1]
        if files_current != files:
            print('Files added or removed')
            subprocess.run('sudo kill -9 `sudo lsof -t -i:'+port+'`',shell=True)
            time.sleep(3) 
            subprocess.run('nohup python programmatic_server.py '+prefix+' '+port+' > programmatic_server.log &',shell=True)
            print('Done fixing')
        else:
            print ('Fine')
        time.sleep(10)

if __name__ == '__main__':
    # args
    prefix = sys.argv[1]
    port = sys.argv[2]
    # kicking off process at the beginning
    subprocess.run('nohup python programmatic_server.py '+prefix+' '+port+' > programmatic_server.log &', shell=True)
    # running while loop
    dir_check(prefix,port)

