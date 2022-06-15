import docker

# 返回Docker SSH連線數
def check_alive(docker_name):

    client = docker.from_env()
    
    container = client.containers.get(docker_name)
    output = container.exec_run(cmd='w | grep pts')
    output = str(output[1]).split(',')

    num = output[1].replace(' ', "")

    return num[0]

# 預約到時提醒
def expired_remind(docker_name):

    client = docker.from_env()
    
    container = client.containers.get(docker_name)
    output = container.exec_run(cmd="wall /etc/remind")