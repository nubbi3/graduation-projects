from flask import *  
import database
import docker_manage
from pathlib import Path

app = Flask(__name__)
    
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
            existed = database.check(usr_name)

            # 不存在則報錯
            if existed is not None:
                return render_template('register.html', existed=existed)
            else:
                path = "/docker_usr/info/" + usr_name + "/log"
                Path(path).mkdir(parents=True, exist_ok=True)
                
                path = "/docker_usr/info/" + usr_name + "/ssh_keys"
                Path(path).mkdir(parents=True, exist_ok=True)

                filename = "/authorized_keys"

                with open(path + filename, "w") as f:
                    f.write(ssh_key + '\n')

                # 數據庫中添加用戶
                result = database.add(id, usr_name)

                if result == 1:
                    outputs = docker_manage.make_docker(usr_name)

                    # 添加三個Docker
                    name1 = usr_name + '_1'
                    name2 = usr_name + '_2'
                    name3 = usr_name + '_3'

                    # 檢查三個Docker名稱是否為Dockername_1, Dockername_2, Dockername_3
                    if outputs[0] == name1 and outputs[1] == name2 and outputs[2] == name3:
                        return render_template('register.html', success=usr_name)
                    else:
                        return render_template('register.html', fail='fail')  
                else:
                    return render_template('register.html', fail='fail')
        else:
            return render_template('register.html', wrong_info='wrong')
            
    return render_template('register.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8184, debug=True)
    
