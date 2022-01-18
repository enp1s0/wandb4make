import subprocess
import os
import argparse
import wandb
import pandas as pd
import math
import shutil
import time
from pydoc import locate

###################################################
# User definition
###################################################
# wandb.init(project=project_name)
project_name = 'hoge'
project_dir = './test_project'

args_table = {
        'hoge' : 'int',
        'foo' : 'str',
        }
source_files_list = [
        'src',
        'Makefile',
        ]
user_run_command = './test.out'

def user_preprocess(args, is_debug):
    yield

def user_build(is_debug):
    subprocess.call(["make", "clean"])
    return subprocess.call(["make", "-j"])
    yield

def user_output_parse(process, wdb, is_debug):
    for line in process.stdout:
        print(line)
        # wdb.log('bar', 10)

def user_clean(is_debug):
    yield

is_debug = True


###################################################
# System function
###################################################

def system_shutdown(base_dir, working_dir, is_debug):
    user_clean(is_debug)
    os.chdir(base_dir)
    shutil.rmtree(working_dir)

###################################################
# Main
###################################################

if __name__ == '__main__':
    base_dir = os.getcwd()
    if (is_debug == False):
        wandb.init(project=project_name)

    # Arguments parser
    parser = argparse.ArgumentParser()
    for n, t in args_table.items():
        parser.add_argument('--' + n, type=locate(t))

    args = parser.parse_args()

    target_name = project_name
    for n, _ in args_table.items():
        target_name += '-' + n + '_' + str(vars(args)[n])

    if (is_debug == True):
        print('Target name : ', target_name)

    # Copy source files to working directiory
    try:
        os.mkdir(project_name)
    except OSError as error:
        print("[INFO]" + error.strerror)

    working_dir = project_name + '/' + target_name + '/'
    try:
        os.mkdir(working_dir)
    except OSError as error:
        print('[INFO]' + error.strerror)
        print('[INFO] Remove ' + working_dir)
        shutil.rmtree(working_dir)
        os.mkdir(working_dir)

    for s in source_files_list:
        src = project_dir + '/' + s
        dst = working_dir + '/' + s
        print('[INFO] Copy ' + src + ' to ' + dst)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)

    os.chdir(working_dir)
    user_preprocess(vars(args), is_debug)

    # Build
    build_stat = user_build(is_debug)
    if build_stat != 0:
        if is_debug == False:
            wandb.log('status', 'build error')
        system_shutdown(base_dir, working_dir, is_debug)
        exit(0)

    # Run
    p = subprocess.Popen([user_run_command], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    run_stat = user_output_parse(p, wandb, is_debug)
    if build_stat != 0:
        if is_debug == False:
            wandb.log('status', 'build error')
        system_shutdown(base_dir, working_dir, is_debug)
        exit(0)

    # Shutdown
    system_shutdown(base_dir, working_dir, is_debug)
