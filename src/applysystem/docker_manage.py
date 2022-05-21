from flask import *  
import time
import subprocess
import database
import time
import docker

# 機器數目
machine_num = 3

# 啟動Docker
def start_docker(usr_name):
    output = subprocess.check_output(["docker start " + str(usr_name)], shell=True)
    output = str(output)
    output = output.replace('b\'', "")
    output = output.replace('\\n\'', "")
    return output

# 停止Docker
def stop_docker(usr_name):
    output = subprocess.check_output(["docker stop " + str(usr_name)], shell=True)
    output = str(output)
    output = output.replace('b\'', "")
    output = output.replace('\\n\'', "")
    return output

# 新建Docker
def make_docker(usr_name):
    user_num = database.check_size() - 1
    outputs=[]

    for id in range(machine_num):
        # Port從20000開始，每個用戶新增三個Docker，分配三個Port
        port = 20000 + 3 * user_num + id
        docker_command ="docker run -itd" + \
                        " -w /root/" + usr_name + \
                        " -v /docker_usr/user/" + usr_name + ":/root/" + usr_name + \
                        " -v /docker_usr/info/" + usr_name + "/ssh_keys/" + ":/root/.ssh" + \
                        " -p " + str(port) + \
                        ":10008" + \
                        " --net testnet" + \
                        " --name " + usr_name + "_" + str(id + 1) + \
                        " --device=/dev/ttyUSB" + str(id * 2 + 1) + \
                        " ubuntu:u740 bash"
        subprocess.check_output([docker_command], shell=True)
        time.sleep(1)
        docker_command ="docker stop " + usr_name + "_" + str(id + 1)
        output = subprocess.check_output([docker_command], shell=True)
        output = str(output)
        output = output.replace('b\'', "")
        output = output.replace('\\n\'', "")
        outputs.append(output)
        
    return outputs