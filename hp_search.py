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

# When this flag is True, all wandb methods are not called
is_debug = True

# wandb.init(project=project_name)
project_name = 'hoge'
project_path = './test_project'

args_table = {
        'hoge' : 'int',
        'foo' : 'str',
        }

# These files are copied to a working directory
source_files_list = [
        'src',
        'Makefile',
        ]

# This command is executed inside working directiory
user_run_command = './test.out'

# This funstion is executed before source files copy
def user_check_arguments(args, is_debug):
    # When the arguments are invalid, return other than 0
    # This returnig value is shown in `status` on the wandb sweep table
    return 0

# This funstion is executed inside working directiory
def user_preprocess(args, is_debug):
    # Write arguments to some header files or replace some strings to the arguments
    # When the preprocess fails, return other than 0
    # This value code is shown in `status` on the wandb sweep table
    return 0

# This funstion is executed inside working directiory
def user_build(is_debug):
    #subprocess.call(["make", "clean"])
    #return subprocess.call(["make", "-j"])
    # When the build fails, return other than 0
    # This value code is shown in `status` on the wandb sweep table
    return 0

def user_output_parse(process, wdb, is_debug):
    for line in process.stdout:
        line = str(line.decode('utf-8')).replace('\n', '')

        result = {
                #'acc' : float(line)
                }
        if is_debug == False:
            wdb.log(result)
        else:
            print(result)
    return 0

# This funstion is executed inside working directiory
def user_clean(is_debug):
    yield


###################################################
# System function
###################################################

def system_shutdown(base_dir, working_path, is_debug):
    user_clean(is_debug)
    os.chdir(base_dir)
    shutil.rmtree(working_path)

###################################################
# Main
###################################################

if __name__ == '__main__':
    if is_debug:
        print("#################################################")
        print("# The debug mode is enabled.                    #")
        print("# All results are not sent to the wandb server. #")
        print("# To disable debug mode, set is_debug False.    #")
        print("#################################################")
    base_dir = os.getcwd()
    if (is_debug == False):
        wandb.init(project=project_name)

    # Arguments parser
    parser = argparse.ArgumentParser()
    for n, t in args_table.items():
        parser.add_argument('--' + n, type=locate(t))

    args = parser.parse_args()

    check_arguments_stat = user_check_arguments(vars(args), is_debug)
    if check_arguments_stat != 0:
        print('[INFO] Arguments checking failed (' + str(check_arguments_stat) + ')')
        if is_debug == False:
            wandb.log({'status' : 'invalid arguments (' + str(check_arguments_stat) + ')'})
        exit(0)
    print('[INFO] Arguments checking was successfully completed')

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

    working_path = project_name + '/' + target_name + '/'
    try:
        os.mkdir(working_path)
    except OSError as error:
        print('[INFO]' + error.strerror)
        print('[INFO] Remove ' + working_path)
        shutil.rmtree(working_path)
        os.mkdir(working_path)

    for s in source_files_list:
        src = project_path + '/' + s
        dst = working_path + '/' + s
        print('[INFO] Copy ' + src + ' to ' + dst)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)
    print('[INFO] Source files were successfully copied')

    os.chdir(working_path)
    preprocess_stat = user_preprocess(vars(args), is_debug)
    if preprocess_stat != 0:
        print('[INFO] Preprocess failed (' + str(preprocess_stat) + ')')
        if is_debug == False:
            wandb.log({'status' : 'preprocess error (' + str(preprocess_stat) + ')'})
        system_shutdown(base_dir, working_path, is_debug)
        exit(0)
    print('[INFO] Preprocessing was successfully completed')

    # Build
    build_stat = user_build(is_debug)
    if build_stat != 0:
        print('[INFO] Build failed (' + str(build_stat) + ')')
        if is_debug == False:
            wandb.log({'status' : 'build error (' + str(build_stat) + ')'})
        system_shutdown(base_dir, working_path, is_debug)
        exit(0)
    print('[INFO] Build was successfully completed')

    # Run
    p = subprocess.Popen([user_run_command], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    run_stat = user_output_parse(p, wandb, is_debug)
    if run_stat != 0:
        print('[INFO] Execution failed (' + str(run_stat) + ')')
        if is_debug == False:
            wandb.log({'status' : 'runtime error (' + str(run_stat) + ')'})
        system_shutdown(base_dir, working_path, is_debug)
        exit(0)
    print('[INFO] Execution was successfully completed')
    if is_debug == False:
        wandb.log({'status' : 'complete'})

    # Shutdown
    print('[INFO] See you...')
    system_shutdown(base_dir, working_path, is_debug)
