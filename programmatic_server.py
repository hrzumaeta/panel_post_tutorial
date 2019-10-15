#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from functools import partial
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader 

import os
import json
import sys

class programmatic_server():
    
    def get_modules(self,set_attribs=False):

        path = os.path.dirname(os.path.abspath(__file__))
        
        subdir = []
        for i in os.scandir(path):
            if i.is_dir():
                subdir.append(i.path)
        
        subdir = list(filter(lambda k: 'ipynb' not in k and 'spy' not in k, subdir)) # removing notebooks and spyder project files
        
        filedir = []
        for i in subdir:
            for x  in os.scandir(i):
                if x.is_file() and x.path.endswith('.py')==True and x.path.endswith('main.py')==False:
                    filedir.append(x.path)
                
        filedir_name = [x.rsplit('/',1)[1] for x in filedir] # everything after last slash
        filedir_name = [x.rsplit('.py',1)[0] for x in filedir_name] # everything before .py
        modules = []
        for i in range(0,len(filedir)):    
            spec = spec_from_loader(name=filedir_name[i],
                                    loader=SourceFileLoader(fullname=filedir_name[i],
                                                            path=filedir[i])) 
            mod = module_from_spec(spec) 
            spec.loader.exec_module(mod) 
            modules.append(mod) # adding module to list
        
        objects = []
        for i in range(0,len(modules)):
            x = modules[i].panel_class(name=str.replace(filedir_name[i],'_',' ').title()) # setting name for top of widget to capitalized file name
            objects.append(x)

        if set_attribs==True:            
            self.applications = objects
            self.filedir_name = filedir_name
        else:
            return objects,filedir_name
        
    def modify_doc(self,panel,doc):
        panel_obj = panel.panel()
        title=panel.title
        return panel_obj.server_doc(title=title,doc=doc)

    def start_server(self,prefix_param='',port_param=5006):
        objects = self.applications
        filedir_name = self.filedir_name
        base_command = '{'
        for i in range(0,len(objects)):
            if i < len(objects)-1:
                adds = "'/"+str(filedir_name[i])+"': Application(FunctionHandler(partial(self.modify_doc,objects["+str(i)+"]))),"
                base_command = base_command+adds
            elif i==len(objects)-1:
                adds = "'/"+str(filedir_name[i])+"': Application(FunctionHandler(partial(self.modify_doc,objects["+str(i)+"])))}"
                base_command = base_command+adds
    
        server = Server(applications=eval(base_command),
                        port=port_param,
                        prefix='/'+prefix_param+'/', 
                        allow_websocket_origin=['localhost:'+str(port_param)], 
                        num_procs=8) 
        server.run_until_shutdown()

if __name__ == "__main__":
    # command line arguments
    prefix = sys.argv[1]
    port = sys.argv[2]
    port = int(port)
    # calling modules
    serv_obj = programmatic_server()
    serv_obj.get_modules(set_attribs=True) # setting objects, filedir_name attributes
    files,file_names = serv_obj.get_modules(set_attribs=False) # getting file names to write to json
    with open('files.json', 'w') as outfile: # writing filenames to json
        json.dump(file_names, outfile)
    serv_obj.start_server(prefix_param=prefix,port_param=port)
