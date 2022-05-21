from flask import *  
from time import localtime
import subprocess
import numpy as np
import database
import docker_manage

app = Flask(__name__)

# 查詢
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

# 申請
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        # 獲取用戶名、時間段
        usr_name = request.form.get('usr_name')
        period = request.form.get('time_dialog')
        period = int(period[11]+period[12]) - 9
        usr_exist = database.check(usr_name)

        #  檢查用戶名稱是否存在
        if usr_exist is not None:
            machine_no = database.check_one_available(period) + 1
            port = database.get_port(usr_name, machine_no)
            docker_name = usr_name + '_' + str(machine_no)
            database.update_timetable(period, machine_no, docker_name)
  
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
    database.init_daily()

    t = localtime()

    log_name = str(t.tm_year) + '_' + str(t.tm_mon) + '_' + str(t.tm_mday) + '.log'

    with open("./log/" + log_name, "w") as f:
        f.write('LOG for ' + log_name + '\n')
    
    app.run(host='0.0.0.0', port=8183, debug=True)
