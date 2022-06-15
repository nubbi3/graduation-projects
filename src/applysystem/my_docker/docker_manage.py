from flask import *  
import time
import subprocess
import docker
import os
import database
import socket
import requests
import sys 
sys.path.append("..") 


# 保存用戶操作記錄到主機
def save_user_log(docker_name, machine_no):

    client = docker.from_env()
    usr_name = docker_name
    
    docker_command = 'docker cp ' + docker_name + ':/etc/session.log /docker_usr/info/' + usr_name + '/log/fresh.log'
    
    subprocess.check_output([docker_command], shell=True)

    path = '/docker_usr/info/' + usr_name + '/log/session_' + str(machine_no) + '.log'

    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("log\n")

    ms = open("/docker_usr/info/" + usr_name + "/log/fresh.log")  
    for line in ms.readlines():  
        with open(path, "a") as mon:  
            mon.write(line)

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# 啟動Docker
def start_docker(usr_name, port, machine_no):

    docker_command ="docker run -itd" + \
                        " -w /root/" + usr_name + \
                        " -v /docker_usr/user/" + usr_name + ":/root/" + usr_name + \
                        " -p " + str(port) + \
                        ":10008" + \
                        " --net testnet" + \
                        " --name " + usr_name + \
                        " --device=/dev/ttyUSB" + str(int(machine_no)*2 - 1) + \
                        " u740:" + usr_name + " bash"

    subprocess.check_output([docker_command], shell=True)

    return usr_name

# 停止Docker
def stop_docker(docker_name, machine_no):

    client = docker.from_env()
    
    container = client.containers.get(docker_name)

    container.stop()
    save_user_log(docker_name, machine_no)
    container.remove(force=True)

    ip = get_host_ip()
    url = "http://" + ip + ":8182/poweroff" + str(machine_no)
    response = requests.get(url)
    #print(response.text)

    return docker_name

# 新建Docker
def make_docker(usr_name):
    client = docker.from_env()
    
    buildargs = { "username" : usr_name }
    client.images.build(path="./my_docker", rm=True, tag="u740:" + usr_name, buildargs=buildargs)
    
    user_num = database.check_size() - 1