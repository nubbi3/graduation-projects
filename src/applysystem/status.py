from time import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from time import localtime
import database
import docker_manage
from pathlib import Path
import check

# 服務器啟動時間
server_start_time = 9

# 服務器定期更新

# 每整點更新一次，用於Docker的更新
server_update_time_week = '0-6' # 0-6 代表 週一到週日工作
server_update_time_hour = '10-21' # 10-21 代表 10點開始第一次更新，21點最後一次更新
server_update_time_min = '0' # 代表 XX:00:XX 更新
server_update_time_sec = '1' # 代表 XX:XX:01 更新

# 每整點的55分檢查一次，用於提前5分鐘斷線的提示
server_check_time_week = '0-6'
server_check_time_hour = '10-21'
server_check_time_min = '55' # 代表 XX:55:XX 更新
server_check_time_sec = '1'

t = localtime()

log_name = str(t.tm_year) + '_' + str(t.tm_mon) + '_' + str(t.tm_mday) + '.log'

# 到時前五分鐘提示
def expired_remind():
    now_docker_names = database.get_status()[0]
    now_docker_names = [x for x in now_docker_names if x is not None]

    if now_docker_names:
        for now_docker_name in now_docker_names:
            check.expired_remind(now_docker_name)

# 更新Docker
def update_machine():
    t = localtime()
    period = t.tm_hour - 9

    # 第一個時間段不用特殊判斷
    if period == 1:
        docker_names = database.get_timetable(period)[0]
        machine_no = 1
        docker_names = [x for x in docker_names if x is not None]

        # 如果預約時間表不為空，即有人預約
        if docker_names:
            for docker_name in docker_names:
                if docker_name is not None:
                    output = docker_manage.start_docker(docker_name)

                    t = localtime()

                    # 記錄Docker啟動時間
                    with open("./log/" + log_name, "a") as f:
                        f.write('Start docker ' + output + ' at ' + str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec) + '\n')

                    # 更新當前機器使用狀態
                    database.update_status(period, machine_no, docker_name)
                    machine_no += 1

    # 之後的時間段，需要判斷 下個時間段有否預約，是否為同一人預約，是否使用同一機器
    else:
        # 獲取下個時間段使用信息
        next_docker_names = database.get_timetable(period)[0]
        machine_no = 1

        # 判斷下個時間段是否有人使用，即時間表中是否為 'NULL'
        next_docker_names = [x for x in next_docker_names if x is not None]
        
        # 下個時間段有人預約
        if next_docker_names:
            now_docker_names = database.get_status()[0]
            now_docker_names = [x for x in now_docker_names if x is not None]

            # 如果目前有機器有分配用戶
            # 則檢查下個時間段該用戶是否使用同一機器
            # 若為同一機器則不中斷SSH連線，若不為同一機器則中斷SSH連線(停止 Docker)
            if now_docker_names:
                for now_docker_name in now_docker_names:
                    # 不為同一機器
                    if now_docker_name not in next_docker_names:
                        user_name = now_docker_name[0:len(now_docker_name)-2]
                        
                        path = 'log/' + user_name
                        Path(path).mkdir(parents=True, exist_ok=True)

                        t = localtime()

                        # 停止Docker
                        output = docker_manage.stop_docker(now_docker_name)
                        
                        # 記錄Docker停止時間
                        with open("./log/" + log_name, "a") as f:
                            f.write('Stop  docker ' + output + ' at ' + str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec) + '\n')

                        # 保存用戶操作記錄
                        check.save_user_log(now_docker_name)
            
            # 根據預約時間表啟動下個時間段的Docker
            for next_docker_name in next_docker_names:
                if next_docker_name is not None:
                    output = docker_manage.start_docker(next_docker_name)

                    t = localtime()
                    with open("./log/" + log_name, "a") as f:
                        f.write('Start docker ' + output + ' at ' + str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec) + '\n')

                    # 更新當前機器使用狀態
                    database.update_status(period, machine_no, next_docker_name)
                    machine_no += 1

        # 下個時間段沒有預約
        else:
            now_docker_names = database.get_status()[0]
            now_docker_names = [x for x in now_docker_names if x is not None]
            
            # 檢查當前分配的用戶是否正在使用 <-- 檢查SSH連線情況，如果SSH用戶為0，則Docker沒人使用
            if now_docker_names:
                for now_docker_name in now_docker_names:
                    ssh_usr = check.check_alive(now_docker_name)

                    if ssh_usr == '0':
                        user_name = now_docker_name[0:len(now_docker_name)-2]
                        
                        path = 'log/' + user_name
                        Path(path).mkdir(parents=True, exist_ok=True)
                        
                        t = localtime()
                        
                        # 停止Docker
                        output = docker_manage.stop_docker(now_docker_name)

                        with open("./log/" + log_name, "a") as f:
                            f.write('Stop  docker ' + output + ' at ' + str(t.tm_hour) + ':' + str(t.tm_min) + ':' + str(t.tm_sec) + '\n')

                        # 保存用戶操作記錄
                        check.save_user_log(now_docker_name)

                        # 更新當前機器使用狀態
                        database.update_status(period, machine_no, 'NULL')
                    
                    machine_no += 1

if __name__ == '__main__':

    # 設定時間
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")

    while True:
        t = localtime()

        # 當時間在服務器工作時間時啟動服務
        if t.tm_hour >= server_start_time:

            # 添加更新時間表排程服務
            scheduler.add_job(update_machine, 'cron', 
                                            day_of_week=server_update_time_week, 
                                            hour=server_update_time_hour, 
                                            minute=server_update_time_min,
                                            second=server_update_time_sec
                                            )

            # 添加提示結束排程服務    
            scheduler.add_job(expired_remind, 'cron', 
                                            day_of_week=server_check_time_week, 
                                            hour=server_check_time_hour, 
                                            minute=server_check_time_min,
                                            second=server_check_time_sec
                                            )
            
            # 開啟排程服務
            scheduler.start()