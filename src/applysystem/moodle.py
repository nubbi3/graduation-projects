from flask import *  
from time import localtime
import subprocess
import numpy as np
import database
from time import timezone
from flask_apscheduler import APScheduler
from datetime import datetime
from my_docker import docker_manage
from pathlib import Path
import check
import socket

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# 服務器定期更新

# 每整點更新一次，用於Docker的更新
server_update_time_week = '0-6' # * 代表 週一到週日工作
server_update_time_hour = '10-21' # 10-21 代表 10點開始第一次更新，21點最後一次更新
server_update_time_min = '00' # 代表 XX:00:XX 更新
server_update_time_sec = '01' # 代表 XX:XX:01 更新

# 每整點的55分檢查一次，用於提前5分鐘斷線的提示
server_check_time_week = '0-6'
server_check_time_hour = '10-21'
server_check_time_min = '55' # 代表 XX:55:XX 更新
server_check_time_sec = '01'

app = Flask(__name__)

class Config(object):
    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()

# 到時前五分鐘提示
@scheduler.task('cron', id='expired_remind', day_of_week=server_check_time_week, 
                                             hour=server_check_time_hour, 
                                             minute=server_check_time_min,
                                             second=server_check_time_sec)
def expired_remind():
    now_user_names = database.get_status()[0]
    now_user_names = [x for x in now_user_names if x is not None]
    
    if now_user_names:
        for now_user_name in now_user_names:
            check.expired_remind(now_user_name)


# 更新時間表  
@scheduler.task('cron', id='update_timetable',day_of_week=server_update_time_week, 
                                              hour=server_update_time_hour, 
                                              minute=server_update_time_min,
                                              second=server_update_time_sec)
def update_machine():
    t = localtime()
    period = t.tm_hour - 9

    
    # 獲取下個時間段使用信息
    next_user_names = database.get_timetable(period)[0]
    # 判斷下個時間段是否有人使用，即時間表中是否為 'NULL'
    next_user_exist = [x for x in next_user_names if x is not None]

    # 第一個時間段不用特殊判斷
    if period == 1:
        
        #user_names = [x for x in user_names if x is not None]

        # 如果預約時間表不為空，即有人預約
        if next_user_names:
            for next_user_name in next_user_names:
                if next_user_name is not None:
                    port = database.get_port(next_user_name)

                    machine_no = next_user_names.index(next_user_name) + 1

                    output = docker_manage.start_docker(next_user_name, port, machine_no)
                    
                    t = localtime()

                    # 記錄Docker啟動時間
                    with open("/home/ubuntu/applysystem/log/" + log_name, "a") as f:
                        f.write('Start docker ' + output + ' at ' + str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec) + '\n')

                    # 更新當前機器使用狀態
                    database.update_status(period, machine_no, next_user_name)

    # 之後的時間段，需要判斷 下個時間段有否預約，是否為同一人預約，是否使用同一機器
    else:
        now_user_names = database.get_status()[0]
        now_user_exist = [x for x in now_user_names if x is not None]

        # 下個時間段有人預約
        if next_user_exist:
            # 如果目前機器有分配用戶
            # 則檢查下個時間段該用戶是否使用同一機器
            # 若為同一機器則不中斷SSH連線，若不為同一機器則中斷SSH連線(停止Docker)
            if now_user_exist:
                for now_user_name in now_user_names:
                    if now_user_name is not None:
                        # 不為同一人
                        if now_user_name not in next_user_names:
                            
                            t = localtime()

                            machine_no = now_user_names.index(now_user_name) + 1

                            # 停止Docker
                            output = docker_manage.stop_docker(now_user_name, machine_no)
                            
                            # 記錄Docker停止時間
                            with open("/home/ubuntu/applysystem/log/" + log_name, "a") as f:
                                f.write('Stop  docker ' + output + ' at ' + str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec) + '\n')
                        else:
                            now_machine_no = now_user_names.index(now_user_name) + 1
                            next_machine_no = next_user_names.index(now_user_name) + 1

                            if now_machine_no != next_machine_no:
                                output = docker_manage.stop_docker(now_user_name, now_machine_no)

                                with open("/home/ubuntu/applysystem/log/" + log_name, "a") as f:
                                    f.write('Stop  docker ' + output + ' at ' + str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec) + '\n')

            
            # 根據預約時間表啟動下個時間段的Docker
            for next_user_name in next_user_names:
                if next_user_name is not None and next_user_name not in now_user_names:
                    
                    port = database.get_port(next_user_name)
                    t = localtime()

                    machine_no = next_user_names.index(next_user_name) + 1

                    output = docker_manage.start_docker(next_user_name, port, machine_no)

                    with open("/home/ubuntu/applysystem/log/" + log_name, "a") as f:
                        f.write('Start docker ' + output + ' at ' + str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec) + '\n')

                    # 更新當前機器使用狀態
                    database.update_status(period, machine_no, next_user_name)

        # 下個時間段沒有預約
        else:
            # 檢查當前分配的用戶是否正在使用 <-- 檢查SSH連線情況，如果SSH用戶為0，則Docker沒人使用
            if now_user_exist:
                for now_user_name in now_user_names:
                    if now_user_name is not None:
                        ssh_usr = check.check_alive(now_user_name)

                        if ssh_usr == '0':
                            
                            t = localtime()
                            
                            machine_no = now_user_names.index(now_user_name) + 1

                            # 停止Docker
                            output = docker_manage.stop_docker(now_user_name, machine_no)

                            with open("/home/ubuntu/applysystem/log/" + log_name, "a") as f:
                                f.write('Stop  docker ' + output + ' at ' + str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec) + '\n')

                            # 保存用戶操作記錄
                            # check.save_user_log(now_user_name, machine_no)

                            # 更新當前機器使用狀態
                            database.update_status(period, machine_no, 'NULL')

# 申請帳號
@app.route('/register', methods=['GET', 'POST'])
def register():
    id = None
    usr_name = None
    
    if request.method == 'POST':
        id = request.args.get('id')
        usr_name = request.form.get('usr_name')
        ssh_key = request.form.get('ssh_key')

        # 判斷用戶名以及SSH KEY是否為空
        if usr_name != '' and usr_name != ' ' and usr_name is not None and ssh_key != '':
            
            # 檢查用戶是否已在數據庫中
            existed = database.check_id(id)

            # 不存在則報錯
            if existed is not None:
                return render_template('register.html', existed=existed)
            else:
                path = "/docker_usr/info/" + usr_name + "/log"
                Path(path).mkdir(parents=True, exist_ok=True)
                
                path = "./my_docker/ssh_keys/" + usr_name
                Path(path).mkdir(parents=True, exist_ok=True)

                filename = "/authorized_keys"

                with open(path + filename, "w") as f:
                    f.write(ssh_key + '\n')

                # 數據庫中添加用戶
                result = database.add(id, usr_name)

                if result == 1:
                    outputs = docker_manage.make_docker(usr_name) 

                    return render_template('register.html', success=usr_name)
                    
                else:
                    return render_template('register.html', fail='fail')
        else:
            return render_template('register.html', wrong_info='wrong')
            
    return render_template('register.html')

# 查詢預約
@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        usr_name = request.form.get('usr_name')
        
        if usr_name != "":
            # 檢查用戶是否存在數據庫中
            usr_exist = database.check(usr_name)
            if usr_exist is not None:
                queries = database.get_status_port_queries(usr_name)
                # 如果查詢預約時間段不為空
                if queries:
                    return render_template('query.html', queries=queries, usr_name=usr_name)
                # 為空
                else:
                    return render_template('query.html', no_query='yes', usr_name=usr_name)
            # 用戶不存在
            else:
                return render_template('query.html', wrong_username=usr_name)
        # 查詢用戶名稱為空
        else:
            return render_template('query.html', no_username='no_username')
    else:
        return render_template('query.html')

# 預約時間
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        # 獲取用戶名、時間段
        usr_name = request.form.get('usr_name')
        period = request.form.get('time_dialog')
        period = int(period[11]+period[12]) - 9
        usr_exist = database.check(usr_name)
        usr_appointment = usr_name in database.get_timetable(period)[0]

        #  檢查用戶名稱是否存在
        if usr_exist is not None and usr_appointment is False:
            previous_usrs = []
            if period != 1:
                previous_usrs = database.get_timetable(period - 1)
                previous_usrs = previous_usrs[0]
            if usr_name in previous_usrs:
                prev_machine_no = previous_usrs.index(usr_name) + 1
                now_machine_no = database.check_available_index(period)
                reserved_usr = database.get_one_timetable(period, prev_machine_no)[0]
                if reserved_usr is not None:
                    # switch
                    database.update_timetable(period, prev_machine_no, usr_name)
                    database.update_timetable(period, now_machine_no, reserved_usr)
                    port = database.get_port(usr_name)

                else:
                    database.update_timetable(period, prev_machine_no, usr_name)
                    port = database.get_port(usr_name)

            else:
                machine_no = database.check_available_index(period)
                port = database.get_port(usr_name)
                database.update_timetable(period, machine_no, usr_name)

            return render_template('success.html', port=port)
        else:
            return render_template('fail.html')
    else:
        available = []

        # 獲取空閒機器數量
        available = database.check_all_available()
        
        t = localtime()
        
        for i in range(len(available)):
            # 如果大於或等於預約時間即不可用
            if i + 10 <= t.tm_hour:
                available[i] = None

        # available1~12代表12個時段空閒機器數量
        return render_template('apply.html', 
                                available1=available[0],
                                available2=available[1], 
                                available3=available[2], 
                                available4=available[3], 
                                available5=available[4], 
                                available6=available[5], 
                                available7=available[6], 
                                available8=available[7], 
                                available9=available[8], 
                                available10=available[9], 
                                available11=available[10],
                                available12=available[11], )

if __name__ == '__main__':

    ip = get_host_ip()
    
    database.update_url(ip)

    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()
    
    database.init_daily()

    t = localtime()

    log_name = str(t.tm_year) + '_' + str(t.tm_mon) + '_' + str(t.tm_mday) + '.log'

    with open("/home/ubuntu/applysystem/log/" + log_name, "w") as f:
        f.write('LOG for ' + log_name + '\n')
    
    app.run(host="0.0.0.0", port=8188, debug=False)
