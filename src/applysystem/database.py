import mysql.connector

# 連接數據庫
mydb = mysql.connector.connect(
  host="localhost",
  user="admin",
  passwd="admin",
  database="moodle"
)

mycursor = mydb.cursor()

# 初始新建時間表項
def init():
    sql = "INSERT INTO machine_timetable (machine_1, machine_2, machine_3) VALUES (%s, %s, %s)"
    val = (None, None, None)
    for i in range(12):
        mycursor.execute(sql, val)
    mydb.commit()

# 每天重置時間表
def init_daily():
    sql = "UPDATE machine_timetable SET machine_1=NULL, machine_2=NULL, machine_3=NULL"
    mycursor.execute(sql)
    mydb.commit()

    rec=mycursor.rowcount
    sql = "UPDATE machine_status SET machine_1=NULL, machine_2=NULL, machine_3=NULL, port_1=0, port_2=0, port_3=0"
    mycursor.execute(sql)
    mydb.commit()
    rec = rec + mycursor.rowcount

    print(rec, "record(s) affected")

# 返回用戶是否在數據庫中
def check(usr_name):
    sql = "SELECT * FROM docker_info WHERE usr_name ='" + usr_name + '\''
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if myresult:
        return myresult[0][1]
    else:  
        return None

def check_id(id):
    sql = "SELECT * FROM docker_info WHERE usr_id = " + str(id)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    if myresult:
        return myresult[0][1]
    else:  
        return None

# 返回用戶數量，用於分配Port
def check_size():
    sql = "SELECT * FROM docker_info"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return len(myresult)

# 新增用戶到數據庫
def add(id, usr_name):
    user_num = check_size()
    port = 20000 + user_num
    sql = "INSERT INTO docker_info (usr_id, usr_name, machine_port) VALUES (%s, %s, %s)"
    val = (id, usr_name, port)
    mycursor.execute(sql, val)
    mydb.commit()
    return mycursor.rowcount

# 返回預約時間表空閒機器數量
def check_all_available():
    sql = "SELECT machine_1, machine_2, machine_3 FROM machine_timetable"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    available = []
    for res in myresult:
        available.append(sum(x is None for x in res))
    return available

# 返回某一時間段的預約時間表空閒機器數量
def check_one_available(period):
    sql = "SELECT machine_1, machine_2, machine_3 FROM machine_timetable WHERE period=" + str(period)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    available = sum(x is not None for x in myresult[0])
    return available

# 返回某一時間段的預約時間表空閒機器數量
def check_available_index(period):
    sql = "SELECT machine_1, machine_2, machine_3 FROM machine_timetable WHERE period=" + str(period)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    available = [x is None for x in myresult[0]]
    machine_no = [i for i, x in enumerate(available) if x]

    #if machine_no:
    return int(machine_no[0]) + 1

# 更新預約時間表
def update_timetable(period, machine_no, docker_name):
    #machine_no = str(int(check_one_available(period)) + 1)
    sql = "UPDATE machine_timetable SET machine_" + str(machine_no) + '= \'' + str(docker_name) + '\' WHERE period = ' + str(period)
    mycursor.execute(sql)
    mydb.commit()
    return mycursor.rowcount

# 更新當前時間段機器使用狀態
def update_status(period, machine_no, docker_name):

    port = 0

    if docker_name != "NULL":
        usr_name=docker_name #[0:len(docker_name)-2]
        port = get_port(usr_name)
        sql = "UPDATE machine_status SET machine_" + str(machine_no) + "= \'" + str(docker_name) + "\'"
    else:
        sql = "UPDATE machine_status SET machine_" + str(machine_no) + "= NULL"

    mycursor.execute(sql)
    mydb.commit()

    sql = "UPDATE machine_status SET port_" + str(machine_no) + "= \'" + str(port) + "\'"
    mycursor.execute(sql)
    mydb.commit()
    
    sql = "UPDATE machine_status SET period=\'" + str(period) + "\'"
    mycursor.execute(sql)
    mydb.commit()

    return mycursor.rowcount

# 返回Port
def get_port(usr_name):
    sql = "SELECT machine_port FROM docker_info WHERE usr_name= '" + str(usr_name) +"\'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult[0][0]

# 返回當前機器使用狀態
def get_status():
    sql = "SELECT machine_1, machine_2, machine_3 FROM machine_status"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult

# 返回某個時間段的預約時間表
def get_timetable(period):
    sql = "SELECT machine_1, machine_2, machine_3 FROM machine_timetable WHERE period= '" + str(period) + '\''
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult

# 返回某個時間段的一個機器預約時間表
def get_one_timetable(period, machine_no):
    sql = "SELECT machine_" + str(machine_no) + " FROM machine_timetable WHERE period= '" + str(period) + '\''
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult[0]

# 返回當前機器使用Port
def get_status_port():
    sql = "SELECT port_1, port_2, port_3 FROM machine_status"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return myresult

# 返回用戶使用時間段以及Port
def get_status_port_queries(usr_name):
    result = []
    n_res = []
    queries = []

    for i in range(3):
        sql = "SELECT period, machine_" + str(i + 1) + " FROM machine_timetable WHERE machine_" + str(i + 1) + "=\'" + str(usr_name) + "\'"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for x in myresult:
          result.append(list(x))
       
    for res in result:
        period = str(int(res[0]) + 9) + ':00 -- ' + str(int(res[0]) + 10) + ':00'
        usr_name = res[1]
        port = get_port(usr_name)
        queries.append([period, port])
    
    return queries

def update_url(ip):

    sql = "UPDATE mdl_url SET externalurl='http://" + ip + ":8188/apply\' WHERE id=1"
    mycursor.execute(sql)
    mydb.commit()

    sql = "UPDATE mdl_url SET externalurl='http://" + ip + ":8188/register\' WHERE id=2"
    mycursor.execute(sql)
    mydb.commit()

    sql = "UPDATE mdl_url SET externalurl='http://" + ip + ":8188/query\' WHERE id=3"
    mycursor.execute(sql)
    mydb.commit()

    return mycursor.rowcount