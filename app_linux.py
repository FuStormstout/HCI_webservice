# -*- coding: UTF-8 -*-
from flask import Flask, request, render_template, redirect, url_for, session
from wordcloud import WordCloud
import matplotlib.pylab as plt
import string
import random
from os import path
import os
import pymysql
import base64
import pyttsx3
import os.path
import time
from aip import AipSpeech

app = Flask(__name__)

app.config['SECRET_KEY'] = '123456'
# baidu audio->text api
APP_ID = '24101838'
API_KEY = '21YIezwElGu94qpVGFCWG8H0'
SECRET_KEY = 'oCVvvsdYZKfQECITVhMhlCaAGOtpkknX'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))



@app.route('/create_publish', methods=['GET', 'POST'])
def create_publish():
    if request.method == 'GET':
        return render_template('create_publish.html')
    if request.method == 'POST':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql_initialize = "update child_user set layer_partner='',current_job='',finish_task='',current_task_code='',current_status=0 where username<>'' "
        cursor.execute(sql_initialize)
        code = id_generator()

        os.mkdir('static/Task/' + code)
        os.mkdir('static/Task/' + code + '/record')



        os.mkdir('static/Task/' + code + '/description_picture')
        os.mkdir('static/Task/' + code + '/character_background')
        os.mkdir('static/Task/' + code + '/conversation_picture')
        introduction = request.form.get('introduction')
        visual_method = request.form.get('visual_method')
        print(visual_method + "is visual method")
        mix_layer = ''

        if visual_method == 'mix layer':
            mix_layer = 'on'
        elif visual_method == 'default individual':
            mix_layer = 'off'

        task_name = request.form.get("task_name")
        age_group = request.form.get("age_group")
        select_all = request.form.get("select_all")
        task_status = 'allocated'
        award_star = request.form.get("award_star")
        if award_star == '':
            award_star = 20

        time_limit = request.form.get("time_limit")
        #分组
        select_group=request.form.get("select_group")
        group_no=request.form.get("group_no")

        print(select_group)
        print(group_no)
        vote_system = ''
        ## initializing paramters

        layer1_demand = ''
        layer2_demand = ''
        mode = ''
        character_task_demand = ''
        scenario_task_demand = ''
        #record use loop structure to insure the progress

        if mix_layer == 'off':

            oral_section = request.form.get("oral_section")
            if oral_section!=None:
                img1 = request.files['description_picture']
                base_path = path.abspath(path.dirname(__file__))
                upload_path = path.join(base_path, 'static/Task/' + code + '/description_picture/')
                img1.save(upload_path + 'description_picture.png')

                img2 = request.files['character_background']
                base_path = path.abspath(path.dirname(__file__))
                upload_path = path.join(base_path, 'static/Task/' + code + '/character_background/')
                img2.save(upload_path + 'character_background.png')

                img3 = request.files['conversation_picture']
                base_path = path.abspath(path.dirname(__file__))
                upload_path = path.join(base_path, 'static/Task/' + code + '/conversation_picture/')
                img3.save(upload_path + 'conversation_picture.png')

                vote_system = request.form.get("vote_system")

                mode_agile = request.form.get("mode_agile")
                mode_linear = request.form.get("mode_linear")


                voice_text_list=request.form.getlist("voice_text")
                print(voice_text_list)
                for i in range(len(voice_text_list)):
                    engine = pyttsx3.init()
                    engine.save_to_file(voice_text_list[i], 'static/Task/' + code + '/record/record'+str(i+1)+'_robot.wav')
                    engine.runAndWait()



                keywords = request.form.getlist("keywords")
                print(keywords)



                f=open('static/Task/' + code + '/record/keywords.txt','a')
                for keyword in keywords:
                    f.write(keyword+'\n')
                f.close()

                f=open('static/Task/' + code + '/record/questions.txt','a')
                for question in voice_text_list:
                    f.write(question+'\n')
                f.close()

                print('questions and keywords have been recorded!')

                character_task_demand = request.form.get("character_design_demand")
                scenario_task_demand = request.form.get("scenario_design_demand")

                print(oral_section)

                if mode_linear == 'on':
                    mode = 'linear'
                elif mode_agile == 'on':
                    mode = 'agile'
                else:
                    mode = ''
                if oral_section == None:
                    mode = 'pure_visual'
            else:
                img1 = request.files['description_picture']
                base_path = path.abspath(path.dirname(__file__))
                upload_path = path.join(base_path, 'static/Task/' + code + '/description_picture/')
                img1.save(upload_path + 'description_picture.png')

                img2 = request.files['character_background']
                base_path = path.abspath(path.dirname(__file__))
                upload_path = path.join(base_path, 'static/Task/' + code + '/character_background/')
                img2.save(upload_path + 'character_background.png')

                img3 = request.files['conversation_picture']
                base_path = path.abspath(path.dirname(__file__))
                upload_path = path.join(base_path, 'static/Task/' + code + '/conversation_picture/')
                img3.save(upload_path + 'conversation_picture.png')

                vote_system = request.form.get("vote_system")

                character_task_demand = request.form.get("character_design_demand")
                scenario_task_demand = request.form.get("scenario_design_demand")


                mode = 'pure_visual'

        else:
            layer1_demand = request.form.get("layer1_demand")
            layer2_demand = request.form.get("layer2_demand")

        sql = "insert into task (code,task_name,introduction,time_limit,vote_system,mode,award_star,age_group,select_all,task_status,character_task_demand, scenario_task_demand, layer1_demand, layer2_demand, mix_layer,create_time) \
         values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',now())" % (
            code, task_name, introduction, time_limit, vote_system, mode, award_star, age_group, select_all,
            task_status, character_task_demand, scenario_task_demand, layer1_demand, layer2_demand, mix_layer)
        cursor.execute(sql)

        ###distribute to objects with different ages
            #use group number to allocate the mission

        if select_group=='on':
            print("select group"+str(group_no))
            sql="update child_user set current_task_code='%s' where group_no='%s'" %(code,group_no)
            cursor.execute(sql)


        if select_all == 'on':
            sql_change_code1 = "update child_user set current_task_code='%s' where username is not null" % (code)
            cursor.execute(sql_change_code1)
            # distribute to all members
        if age_group != '':
            age_min = int(age_group) - 2
            age_max = int(age_group) + 2
            sql="select count(*) from child_user where age>=%s and age<=%s and finish_task <> 'N'" %(age_min,age_max)
            cursor.execute(sql)
            amount=cursor.fetchall()
            if amount[0]['count(*)']>0:
                sql_change_code2 = "update child_user set current_task_code='%s' where age>=%s and age<=%s and finish_task<>'N'" % (
                    code, age_min, age_max)
                cursor.execute(sql_change_code2)
            else:
                age_group=""
                select_all='on'
                sql_change_code1 = "update child_user set current_task_code='%s' where username is not null" % (code)
                cursor.execute(sql_change_code1)


        ##distribute only to a bias in 4 (-2 & +2)

        print(mix_layer)
        if mix_layer == 'off':
            if mode=='pure_visual':
                sql="update child_user set current_job='pure_visual',finish_task='N' where current_task_code='%s'" %(code)
                cursor.execute(sql)
            elif mode == 'linear':
                sql_change_user_mode_linear = "update child_user set current_job='all', finish_task='N' where current_task_code='%s'" % (code)
                cursor.execute(sql_change_user_mode_linear)
            elif mode == 'agile':
                sql_current_user_list = "select username from child_user where current_task_code='%s'" % (code)
                cursor.execute(sql_current_user_list)
                us = []
                userlist = cursor.fetchall()
                for i in range(len(userlist)):
                    us.append(userlist[i]['username'])
                count = 0
                name_odd = []
                name_even = []
                for name in us:
                    if count % 2 == 0:
                        name_odd.append(name)
                    else:
                        name_even.append(name)
                    count = count + 1
                for name in name_odd:
                    sql_change_job_visual = "update child_user set current_job='visual', finish_task='N' where username='%s'" % (
                        name)
                    cursor.execute(sql_change_job_visual)
                for name in name_even:
                    sql_change_job_oral = "update child_user set current_job='oral', finish_task='N' where username='%s'" % (
                        name)
                    cursor.execute(sql_change_job_oral)
            # get sample size and add it to task table


        elif mix_layer == 'on':  ## if use mix layer design method
            sql_current_user_list = "select username from child_user where current_task_code='%s'" % (code)
            cursor.execute(sql_current_user_list)
            us = []
            userlist = cursor.fetchall()
            length = len(userlist)

            if length%2==0:

                for i in range(len(userlist)):
                    us.append(userlist[i]['username'])

                count = 0
                i = 0
                while i < len(us):
                    sql = "update child_user set layer_partner='%s' where username='%s'" % (us[i + 1], us[i])
                    cursor.execute(sql)
                    sql = "update child_user set layer_partner='%s' where username='%s'" % (us[i], us[i + 1])
                    i = i + 2
                    cursor.execute(sql)
                name_odd = []
                name_even = []
                for name in us:
                    if count % 2 == 0:
                        name_odd.append(name)
                    else:
                        name_even.append(name)
                    count = count + 1
                print(name_odd)
                print(name_even)
                for name1 in name_odd:
                    print(name1 + "set as layer1")
                    sql_change_job_layer1 = "update child_user set current_job='layer_1', finish_task='N' where username='%s'" % (
                        name1)
                    cursor.execute(sql_change_job_layer1)
                for name2 in name_even:
                    print(name2 + "set as layer2")
                    sql_change_job_layer2 = "update child_user set current_job='layer_2' , finish_task='N' where username='%s'" % (
                        name2)
                    cursor.execute(sql_change_job_layer2)
            else:
                for i in range(len(userlist)-1):
                    us.append(userlist[i]['username'])

                count = 0
                i = 0
                while i < len(us):
                    sql = "update child_user set layer_partner='%s' where username='%s'" % (us[i + 1], us[i])
                    cursor.execute(sql)
                    sql = "update child_user set layer_partner='%s' where username='%s'" % (us[i], us[i + 1])
                    i = i + 2
                    cursor.execute(sql)

                sql="update child_user set layer_partner='%s' where username='%s'" %(userlist[-1]['username'],userlist[-1]['username'])
                cursor.execute(sql)
                name_odd = []
                name_even = []
                for name in us:
                    if count % 2 == 0:
                        name_odd.append(name)
                    else:
                        name_even.append(name)
                    count = count + 1
                print(name_odd)
                print(name_even)
                for name1 in name_odd:
                    print(name1 + "set as layer1")
                    sql_change_job_layer1 = "update child_user set current_job='layer_1', finish_task='N' where username='%s'" % (
                        name1)
                    cursor.execute(sql_change_job_layer1)
                for name2 in name_even:
                    print(name2 + "set as layer2")
                    sql_change_job_layer2 = "update child_user set current_job='layer_2' , finish_task='N' where username='%s'" % (
                        name2)
                    cursor.execute(sql_change_job_layer2)

                sql="update child_user set current_job='layer1_2',finish_task='N' where username='%s'" %(userlist[-1]['username'])
                cursor.execute(sql)
        # initialize finish_task

        # record user info in local file
        sql_get_code_users = "select username,current_job,current_task_code,layer_partner from child_user where current_task_code='%s'" % (
            code)
        cursor.execute(sql_get_code_users)
        name_list_1 = cursor.fetchall()

        print(name_list_1)
        for i in range(len(name_list_1)):
            sql_update_records = "insert into records (username, code,job_type,layer_partner,finish_task,vote_star) values ('%s','%s','%s','%s','N',0) " % (
            name_list_1[i]['username'], name_list_1[i]['current_task_code'], name_list_1[i]['current_job'],name_list_1[i]['layer_partner'])
            cursor.execute(sql_update_records)


        sample_size=len(name_list_1)
        sql="update task set sample_size=%s where code='%s'" %(sample_size,code)
        cursor.execute(sql)
        sql="select username from records where code='%s'" %(code)
        cursor.execute(sql)
        users_in_code=cursor.fetchall()

        db.commit()
        db.close()


        #为用户创建文件夹
        for i in range(len(users_in_code)):
            user_code_folder = 'static/user/' + users_in_code[i]['username'] + '/' + code
            user_character_design_folder = 'static/user/' + users_in_code[i]['username'] + '/' + code + '/character_design'
            user_scenario_design_folder = 'static/user/' + users_in_code[i]['username'] + '/' + code + '/conversation_picture'
            user_record = 'static/user/' + users_in_code[i]['username'] + '/' + code + '/record'
            user_mix_layer1 = 'static/user/' + users_in_code[i]['username'] + '/' + code + '/mix_layer1'
            user_mix_layer2 = 'static/user/' + users_in_code[i]['username'] + '/' + code + '/mix_layer2'

            print(user_code_folder)
            print(os.path.exists(user_code_folder))
            if os.path.exists(user_code_folder) == False:
                os.mkdir(user_code_folder)
            if os.path.exists(user_character_design_folder) == False:
                os.mkdir(user_character_design_folder)
            if os.path.exists(user_scenario_design_folder) == False:
                os.mkdir(user_scenario_design_folder)
            if os.path.exists(user_record) == False:
                os.mkdir(user_record)
            if os.path.exists(user_mix_layer1) == False:
                os.mkdir(user_mix_layer1)
            if os.path.exists(user_mix_layer2) == False:
                os.mkdir(user_mix_layer2)
            print("finishing create folders for "+users_in_code[i]['username'])
        return redirect(url_for('designer_interface'))

@app.route('/login',methods=['GET'])
def login():
    if request.method=='GET':
        return render_template('login_select.html')


@app.route('/designer_login',methods=['GET','POST'])
def designer_login():
    if request.method=='GET':
        return render_template('designer_login.html')
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username=='designer' and password=='123456':
            return redirect(url_for('designer_interface'))
        else:
            return redirect(url_for('designer_login'))

@app.route('/child_register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        c_password = request.form.get("c_password")
        gender = request.form.get("gender")
        age = request.form.get("age")
        country=request.form.get("country")
        group_no=request.form.get("group_no")
        if gender=="Boy":
            gender="male"
        elif gender=="Girl":
            gender="female"
        else:
            gender=""

        if c_password == password:
            db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                                 port=25081,
                                 user='root',
                                 passwd='direnjieE2',
                                 db='ECCA',
                                 charset='utf8')
            cursor = db.cursor()
            sql = "insert into child_user (username,password,age,gender,current_status,finish_task,country,score,group_no) \
                     values ('%s','%s','%s','%s',0,'','%s',0,%s)" % (username, password, age, gender,country,group_no)
            cursor.execute(sql)
            db.commit()
            db.close()
            os.mkdir('static/user/' + username)
        return redirect(url_for('child_login'))


@app.route('/child_login', methods=['GET', 'POST'])
def child_login():
    if request.method == 'GET':
        return render_template('child_login.html')
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql_account="select count(*) from child_user where username='%s' and password='%s'" %(username,password)
        cursor.execute(sql_account)
        result=cursor.fetchall()
        if result[0]['count(*)']==1:
            sql_account = "select * from child_user where  username=('%s') and password=('%s')" % (username, password)
            cursor.execute(sql_account)
            tmp = cursor.fetchall()
            session['user'] = username
            sql_current_job = "select current_job from child_user where username='%s'" % (session['user'])
            cursor.execute(sql_current_job)
            current_job = cursor.fetchall()
            current_job = current_job[0]['current_job']
            session['current_job'] = current_job
            db.close()
            cc = tmp[0]['current_task_code']  # 貌似不能跨越函数
            session['code'] = cc
            return redirect(url_for("child_user_account"))
        else:
            return redirect(url_for("child_login"))



@app.route('/start_task', methods=['GET', 'POST'])
def start_task():
    if request.method == 'GET':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "select finish_task,current_task_code,current_job from child_user where username='%s'" % (session['user'])
        cursor.execute(sql)
        finish_task = cursor.fetchall()
        ft= finish_task[0]['finish_task']

        task_code=finish_task[0]['current_task_code']
        session['code']=task_code
        session['current_job']=finish_task[0]['current_job']
        db.commit()
        db.close()
        if ft == 'N':
            if session['current_job']=='pure_visual':
                return render_template('task_model_visual.html')
            elif session['current_job'] == 'all':
                return render_template('task_model.html', code=session['code'])
            elif session['current_job'] == 'visual':
                return render_template('task_model_visual.html', code=session['code'])
            elif session['current_job'] == 'oral':
                return render_template('task_model_oral.html', code=session['code'])
            elif session['current_job'] == 'layer_1':
                return redirect(url_for('mix_layer1'))
            elif session['current_job'] == 'layer_2':
                return redirect(url_for('mix_layer2'))
            elif session['current_job']=='layer1_2':
                return redirect(url_for('mix_layer1'))
            else:
                return render_template('ERROR.html')

        else:
            return redirect(url_for('wait_for_task'))


@app.route('/character_design', methods=['GET', 'POST'])
def character_design():
    if request.method == 'GET':
        session['start_time']=time.time()
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "select time_limit,character_task_demand from task where code='%s'" % (session['code'])
        cursor.execute(sql)
        info = cursor.fetchall()
        db.commit()
        db.close()
        print(info)
        return render_template('character_design.html', code=session['code'], minute=info[0]['time_limit'],
                               character_task_demand=info[0]['character_task_demand'])
    if request.method == 'POST':
        session['end_time']=time.time()
        time_use=int(float(session['end_time']-session['start_time']))
        session['start_time']=""
        session['end_time']==""
        print("time use is"+ str(time_use))
        character_name=request.form.get('character_name')
        img_base64 = str(request.form.get('image'))
        img_base64 = img_base64.replace('data:image/png;base64,', '')
        img_data = base64.b64decode(img_base64)
        file = open(
            'static/user/' + session['user'] + '/' + session['code'] + '/character_design/character_design.jpg',
            'wb')
        file.write(img_data)
        file.close()
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "update child_user set current_status=1 where username='%s'" % (session['user'])
        cursor.execute(sql)
        sql="update records set character_name='%s',time_use_character='%s' where code='%s' and username='%s'" %(character_name,time_use,session['code'],session['user'])
        cursor.execute(sql)
        db.commit()
        db.close()
        return redirect(url_for('scenario_design'))


@app.route('/scenario_design', methods=['GET', 'POST'])
def scenario_design():
    if request.method == 'GET':
        session['start_time']=time.time()
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)

        sql = "select time_limit,scenario_task_demand from task where code='%s'" % (session['code'])
        cursor.execute(sql)
        info = cursor.fetchall()
        return render_template('scenario_design.html', code=session['code'], minute=info[0]['time_limit'],
                               scenario_task_demand=info[0]['scenario_task_demand'])

    if request.method == 'POST':
        session['end_time']=time.time()
        time_use=int(float(session['end_time']-session['start_time']))
        img_base64 = str(request.form.get('image'))
        img_base64 = img_base64.replace('data:image/png;base64,', '')
        img_data = base64.b64decode(img_base64)
        file = open('static/user/' + session['user'] + '/' + session[
            'code'] + '/conversation_picture/conversation_picture.jpg', 'wb')
        file.write(img_data)
        file.close()
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor()

        sql = "update child_user set current_status=2 where username='%s'" % (session['user'])
        cursor.execute(sql)
        sql="update records set time_use_scenario='%s' where username='%s' and code='%s'" %(time_use,session['user'],session['code'])
        cursor.execute(sql)
        if session['current_job'] == 'all':
            db.commit()
            db.close()
            return redirect(url_for('collect_record_model',number=1))
        elif session['current_job'] == 'visual' or session['current_job']=='pure_visual':
            sql_change_finish_task = "update child_user set finish_task='Y' where username='%s'" % (session['user'])
            cursor.execute(sql_change_finish_task)
            sql="update records set finish_task='Y' where username='%s' and code='%s'" %(session['user'],session['code'])
            cursor.execute(sql)
            db.commit()
            db.close()

            return redirect(url_for('visual_star'))


@app.route('/mix_layer1', methods=['GET', 'POST'])
def mix_layer1():
    if request.method == 'GET':
        session['start_time']=time.time()
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "select time_limit,layer1_demand from task where code='%s'" % (session['code'])
        cursor.execute(sql)
        info = cursor.fetchall()
        db.commit()
        db.close()
        print(info)
        return render_template('mix_layer1.html', code=session['code'], minute=info[0]['time_limit'],
                               mix_layer1_demand=info[0]['layer1_demand'])
    if request.method == 'POST':
        session['end_time']=time.time()
        time_use=int(float(session['end_time']-session['start_time']))
        print("layer1用时："+str(time_use))
        img_base64 = str(request.form.get('image'))
        img_base64 = img_base64.replace('data:image/png;base64,', '')
        img_data = base64.b64decode(img_base64)
        file = open(
            'static/user/' + session['user'] + '/' + session['code'] + '/mix_layer1/layer1.png',
            'wb')
        file.write(img_data)
        file.close()

        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql="update records set time_use_layer1=%s where username='%s' and code='%s'" %(time_use,session['user'],session['code'])
        cursor.execute(sql)
        if session['current_job']=='layer_1':
            sql_change_finish_task = "update child_user set finish_task='Y' where username='%s'" % (session['user'])
            cursor.execute(sql_change_finish_task)
            sql="update records set finish_task='Y' where username='%s' and code='%s'" %(session['user'],session['code'])
            cursor.execute(sql)
            db.commit()
            db.close()
            return redirect(url_for('visual_star'))
        elif session['current_job']=='layer1_2':
            db.commit()
            db.close()
            return redirect(url_for('mix_layer2'))





@app.route('/mix_layer2', methods=['GET', 'POST'])
def mix_layer2():
    if request.method == 'GET':
        session['start_time']=time.time()
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)

        sql = "select layer_partner from child_user where username='%s'" % (session['user'])
        cursor.execute(sql)
        info2 = cursor.fetchall()
        partner_layer1 = info2[0]['layer_partner']
        sql="select finish_task from records where username='%s' and code='%s'" %(partner_layer1,session['code'])
        cursor.execute(sql)
        ft=cursor.fetchall()
        print(session['code'])
        print("完成任务状态是"+ft[0]['finish_task'])

        if ft[0]['finish_task']=='N' and session['current_job']=='layer_2':
            return render_template('mix_layer2_wait.html')
        elif ft[0]['finish_task']=='N' and session['current_job']=='layer1_2':
            sql = "select time_limit,layer2_demand from task where code='%s'" % (session['code'])
            cursor.execute(sql)
            info = cursor.fetchall()
            db.commit()
            db.close()
            return render_template('mix_layer2.html', code=session['code'], minute=info[0]['time_limit'],
                                   mix_layer2_demand=info[0]['layer2_demand'], partner_layer1=session['user'])
        else:

            sql = "select time_limit,layer2_demand from task where code='%s'" % (session['code'])
            cursor.execute(sql)
            info = cursor.fetchall()
            db.commit()
            db.close()
            return render_template('mix_layer2.html', code=session['code'], minute=info[0]['time_limit'],
                                   mix_layer2_demand=info[0]['layer2_demand'], partner_layer1=partner_layer1)
    if request.method == 'POST':
        session['end_time']=time.time()
        time_use=int(float(session['end_time']-session['start_time']))
        img_base64 = str(request.form.get('image'))
        img_base64 = img_base64.replace('data:image/png;base64,', '')
        img_data = base64.b64decode(img_base64)
        file = open(
            'static/user/' + session['user'] + '/' + session['code'] + '/mix_layer2/layer2.png',
            'wb')
        file.write(img_data)
        file.close()
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql_change_finish_task = "update child_user set finish_task='Y' where username='%s'" % (session['user'])
        cursor.execute(sql_change_finish_task)
        sql = "update records set finish_task='Y',time_use_layer2='%s' where username='%s' and code='%s'" % (time_use,session['user'],session['code'])
        cursor.execute(sql)
        db.commit()
        db.close()
        return redirect(url_for('visual_star'))


@app.route('/collect_record_model/<number>',methods=['GET','POST'])
def collect_record_model(number):
    if request.method=='GET':
        f = open('static/Task/' + session['code'] + '/record/questions.txt', 'r')
        question_list = f.readlines()
        f.close()
        index_length=len(question_list)
        print("共有"+str(index_length))
        number=int(number)
        if (number-1)<index_length:
            return render_template('talk_model.html', voice_text=question_list[number-1], code=session['code'], index=number, index_next=number+1)
        else:
            db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                                 port=25081,
                                 user='root',
                                 passwd='direnjieE2',
                                 db='ECCA',
                                 charset='utf8')
            cursor = db.cursor(pymysql.cursors.DictCursor)
            sql = "update records set finish_task='Y' where code='%s' and username='%s'" % (
            session['code'], session['user'])
            cursor.execute(sql)
            sql_change_finsih_task = "update child_user set finish_task='Y' where username='%s' and current_task_code='%s'" % (
                session['user'], session['code'])
            cursor.execute(sql_change_finsih_task)
            db.commit()
            db.close()
            return redirect(url_for('text_record_store'))
    if request.method=="POST":
        file_path = 'static/user/' + session['user'] + '/' + session['code'] + '/record/'
        input_record = request.files['audio_data']
        with open(file_path + 'record'+number+'.wav', 'wb') as audio:
            input_record.save(audio)
        os.system('sox static/user/' + session['user'] + '/' + session[
            'code'] + '/record/record'+number+'.wav -r 16000 ' + file_path + 'record'+number+'_new.wav')
        test = client.asr(get_file_content(file_path + 'record'+number+'_new.wav'), 'wav', 16000, {
            'dev_pid': 1737,
        })
        f = open('static/Task/' + session['code'] + '/record/keywords.txt', 'r')
        keyword_list = f.readlines()
        f.close()

        print('string is: ' + test['result'][0])
        print('keyword: ' + keyword_list[0])

        print('judging...')
        if (keyword_list[int(number)-1].strip() in test['result'][0]) == True:
            match = 'hit'
        else:
            match = 'miss'

        print(match)
        with open(file_path + 'record_text.txt', 'a') as t:
            t.write(test['result'][0] + '  --result: ' + match + '\n')
        f = open('static/Task/' + session['code'] + '/record/corpus_Q'+number+'.txt', 'a')
        f.write(test['result'][0] + '  --result: ' + match + '\n')
        f.close()
        return redirect(url_for('collect_record_model',number=str(int(number)+1)))




@app.route('/award_star', methods=['GET', 'POST'])
def visual_star():
    if request.method == 'GET':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "select award_star from task where code='%s'" % (session['code'])
        cursor.execute(sql)
        award_star = cursor.fetchall()
        db.commit()
        db.close()
        star_name = ''
        if award_star[0]['award_star'] == 1:
            star_name = 'one_star.png'
        elif award_star[0]['award_star'] == 2:
            star_name = 'two_star.png'
        elif award_star[0]['award_star'] == 3:
            star_name = 'three_star.png'
        elif award_star[0]['award_star'] == 4:
            star_name = 'four_star.png'
        elif award_star[0]['award_star'] == 5:
            star_name = 'five_star.png'
        return render_template('award_star.html', star_name=star_name)







@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'GET':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')

        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "select vote_system from task where code='%s'" % (session['code'])
        cursor.execute(sql)
        vote_sys=cursor.fetchall()

        if vote_sys[0]['vote_system']=='on':
            sql = "select current_status from child_user where current_task_code='%s'" % (session['code'])
            cursor.execute(sql)
            status_list = cursor.fetchall()
            status_amount = 0
            for number in status_list:
                status_amount = status_amount + int(number['current_status'])
            sql = "select count(*) from records where code='%s' and finish_task='N'" % (session['code'])
            cursor.execute(sql)
            nfinish_amount=cursor.fetchall()
            nfinish_amount=nfinish_amount[0]['count(*)']
            print("未完成人数有: "+str(nfinish_amount))
            if nfinish_amount==0:
                sql = "select username from records where code='%s' and job_type in ('visual','pure_visual','all')" % (
                    session['code'])
                cursor.execute(sql)
                name_list = cursor.fetchall()
                db.commit()
                db.close()
                return render_template('vote.html', name_list=name_list, task_code=session['code'])
            else:
                return render_template('vote_wait.html')
        else:
            return redirect(url_for('child_user_account'))
        # 如果有人没完成任务则投票会无法加载对应的图片

    if request.method == 'POST':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "select username from records where code='%s' and job_type in ('visual','pure_visual','all')" % (
        session['code'])
        cursor.execute(sql)
        name_list = cursor.fetchall()

        print(name_list)
        for name in name_list:
            character_score = request.form.get(name['username'] + '_character')
            print(name['username']+"获得"+character_score)
            scenario_score = request.form.get(name['username'] + '_scenario')
            print(name['username']+"获得"+scenario_score)


            sql="update records set vote_star=vote_star+%s+%s where code='%s' and username='%s' " %(character_score,scenario_score,session['code'],name['username'])
            cursor.execute(sql)
            sql="update child_user set score=score+%s+%s where username='%s'" %(character_score,scenario_score,name['username'])
            cursor.execute(sql)
            print('successfully update scores in both records and user account')
        db.commit()
        db.close()
        return redirect(url_for('vote_finish'))




@app.route('/vote_finish', methods=['GET'])
def vote_finish():
    if request.method == 'GET':
        return render_template('vote_finish.html')


@app.route('/child_interface', methods=['GET','POST'])
def child_user_account():
    if request.method == 'GET':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "select * from child_user where username='%s'" % (session['user'])
        cursor.execute(sql)
        tmp = cursor.fetchall()
        session['code']=tmp[0]['current_task_code']
        session['current_job']=tmp[0]['current_job']
        db.commit()
        db.close()
        if tmp[0]['finish_task'] == '' or tmp[0]['current_task_code']=='':
            current_task_code = 'There is no task now !        '
            task_status = 'wait for task'
        else:
            task_status='start task'
            current_task_code=tmp[0]['current_task_code']

        group=tmp[0]['group_no']
        if tmp[0]['group_no']==None or tmp[0]['group_no']=='':
            group='You are not in any gourps now!'

        return render_template('child_interface.html', username=session['user'], gender=tmp[0]['gender'],
                               age=tmp[0]['age'], current_task_code=current_task_code, task_status=task_status,country=tmp[0]['country'],score=tmp[0]['score'],group=group)

    if request.method=='POST':
        new_group=request.form.get("new_group")
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql="update child_user set group_no='%s' where username='%s'" %(new_group,session['user'])
        cursor.execute(sql)
        db.commit()
        db.close()
        return redirect(url_for('child_user_account'))

@app.route('/designer_interface', methods=['GET'])
def designer_interface():
    if request.method == 'GET':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)

        sql_task_info = "select * from task order by create_time desc"
        cursor.execute(sql_task_info)
        task_list = cursor.fetchall()

        ###这个地方是否需要增加曾经的code，只迭代一层 同时进度用平均progress来表达
        return render_template('designer_interface.html', task_list=task_list)


@app.route("/ini_task", methods=['GET'])
def ini_task():
    if request.method == 'GET':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "truncate table task"
        cursor.execute(sql)
        os.system('rm -rf static/Task/*')
        db.commit()
        db.close()
        return redirect(url_for("designer_interface"))




@app.route("/ini_user", methods=['GET'])
def ini_user():
    if request.method == 'GET':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql="update child_user set group_no=''"
        cursor.execute(sql)
        db.commit()
        db.close()
        return redirect(url_for("designer_interface"))



@app.route('/task_detail/<code>', methods=['GET','POST'])
def task_detail(code):
    if request.method == 'GET':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')

        cursor = db.cursor(pymysql.cursors.DictCursor)
        # get user information under this task

        sql = "select mix_layer,mode from task where code='%s'" % (code)
        cursor.execute(sql)
        task_information = cursor.fetchall()
        print(task_information)
        mix_layer_switch = task_information[0]['mix_layer']
        mode = task_information[0]['mode']



##1. 获取用户列表
        #if mix_layer=off
            #get all-user
     #       sql
            #get visual-user
        #elif mix_Layer=o
##2. 填充到网页中


        #check whether participants have finished the task
        sql="select count(*) from child_user where current_task_code='%s' and finish_task='N'" %(code)
        cursor.execute(sql)
        result=cursor.fetchall()
        sql = "select username,finish_task from records where code='%s'" % (code)
        cursor.execute(sql)
        user_info = cursor.fetchall()



        if result[0]['count(*)']>0: #如果有还没完成任务的人，则给出一个目前的进度
            if mix_layer_switch=='off':
                if mode=='linear':
                    db.commit()
                    db.close()
                    return render_template("Participant_Not_finish_mix_off.html", visual_not_finish_amount=result[0]['count(*)'], oral_not_finish_amount=result[0]['count(*)'],user_info=user_info)
                elif mode=='agile':
                    sql="select count(*) from records where code='%s' and finish_task='N' and job_type ='visual'" %(code)
                    cursor.execute(sql)
                    visual_us_nfinish=cursor.fetchall()
                    sql="select count(*) from records where code='%s' and finish_task='N' and job_type='oral'" %(code)
                    cursor.execute(sql)
                    oral_us_nfinish=cursor.fetchall()
                    db.commit()
                    db.close()
                    return render_template("Participant_Not_finish_mix_off.html",visual_not_finish_amount=visual_us_nfinish[0]['count(*)'],oral_not_finish_amount=oral_us_nfinish[0]['count(*)'],user_info=user_info)
                elif mode=='pure_visual':
                    sql="select count(*) from records where code='%s' and finish_task='N' and job_type='pure_visual' " %(code)
                    cursor.execute(sql)
                    pure_visual_us_nfinish=cursor.fetchall()
                    db.commit()
                    db.close()
                    return render_template("Participant_Not_finish_mix_off.html",visual_not_finish_amount=pure_visual_us_nfinish[0]['count(*)'],user_info=user_info,oral_not_finish_amount=0)
            else: #mix layer open
                sql="select count(*) from records where code='%s' and job_type in ('layer_1','layer1_2') and finish_task='N'" %(code)
                cursor.execute(sql)
                layer1_us_nfinish=cursor.fetchall()

                sql="select count(*) from records where code='%s' and job_type in ('layer_2','layer1_2') and finish_task='N'" %(code)
                cursor.execute(sql)
                layer2_us_nfinish=cursor.fetchall()

                sql="select username,finish_task,job_type from records where code='%s'" %(code)
                cursor.execute(sql)
                mix_us_list=cursor.fetchall()

                db.commit()
                db.close()
                return render_template("Participant_Not_finish_mix_on.html",layer1_not_finish_amount=layer1_us_nfinish[0]['count(*)'],layer2_not_finish_amount=layer2_us_nfinish[0]['count(*)'],mix_us_list=mix_us_list,code=code)
        else:# 如果已经完成了任务，则给出结果而非进度表

            if mix_layer_switch=='off':
                #如果没有使用mixlayer模式 则是agile或者linear的

                #如果使用的是线性模式，visual->oral
                if mode=='linear':
                    sql="select username,vote_star,character_name,time_use_character,time_use_scenario from records where code='%s' and job_type='all'" %(code)
                    cursor.execute(sql)
                    linear_user_list=cursor.fetchall()

                    sql = "select value_map from task where code='%s'" % (code)
                    cursor.execute(sql)
                    value_map = cursor.fetchall()
                    if value_map[0]['value_map'] == "" or value_map[0]['value_map'] == 0 or value_map[0][
                        'value_map'] == None:
                        sql = "select avg(time_use_character), avg(time_use_scenario),avg(vote_star),variance(time_use_character),variance(time_use_scenario),variance(vote_star) from records where code='%s'" % (
                            code)
                        cursor.execute(sql)
                        value_list = cursor.fetchall()
                        avg_time_cost_character = value_list[0]["avg(time_use_character)"]
                        avg_time_cost_scenario = value_list[0]["avg(time_use_scenario)"]
                        avg_score = value_list[0]["avg(vote_star)"]
                        var_time_cost_character = value_list[0]["variance(time_use_character)"]
                        var_time_cost_scenario = value_list[0]["variance(time_use_scenario)"]
                        var_score = value_list[0]["variance(vote_star)"]
                        avg_list = [avg_time_cost_scenario, avg_time_cost_character]
                        var_list = [var_time_cost_character, var_time_cost_scenario]
                        y1 = avg_list
                        y2 = var_list
                        # plt.plot(index,y1)
                        plt.plot(y2, label='var time cost 0:basic 1:vivid', marker='o', markersize=6,
                                 markeredgecolor='black', markerfacecolor='brown')
                        plt.plot(y1, label='avg time cost 0:basic 1:vivid', marker='o', markersize=6,
                                 markeredgecolor='black', markerfacecolor='brown')
                        plt.bar(2, avg_score, color='b', label='avg score')
                        plt.bar(3, var_score, color='g', label='var score')
                        plt.legend()
                        plt.savefig('static/Task/'+code+'/value_map.png')
                        plt.close()
                        sql = "update task set value_map=1 where code='%s'" % (code)
                        cursor.execute(sql)


                    #corpus 1-5的命中和
                    f = open('static/Task/'+code+'/record/keywords.txt', 'r')
                    keyword_list = f.readlines()
                    f.close()

                    f = open('static/Task/'+code+'/record/questions.txt', 'r')
                    question_list = f.readlines()
                    f.close()

                    list = []

                    for i in range(len(keyword_list)):
                        f = open('static/Task/'+code+'/record/corpus_Q' + str(i + 1) + '.txt', 'r')
                        tmp_list = f.readlines()
                        f.close()
                        print(tmp_list)
                        count_hit=0
                        for ele in tmp_list:
                            if 'hit' in ele:
                                count_hit=count_hit+1
                        count_pro=count_hit/len(tmp_list)
                        print('the count is '+str(count_hit))
                        print(str(count_pro)+"the probability is")
                        list.append(dict(keyword=keyword_list[i], question=question_list[i], corpus=tmp_list,index=i+1,count_pro=count_pro))

                    db.commit()
                    db.close()
                    return render_template("task_detail_mix_layer_off.html",user_list_visual=linear_user_list,user_list_oral=linear_user_list,code=code,corpus_result=list,avg_score=avg_score\
                                           ,avg_time_cost_character=avg_time_cost_character,avg_time_cost_scenario=avg_time_cost_scenario,var_score=var_score\
                                           ,var_time_cost_character=var_time_cost_character,var_time_cost_scenario=var_time_cost_scenario)

                if mode=='agile':

                    sql = "select value_map from task where code='%s'" % (code)
                    cursor.execute(sql)
                    value_map = cursor.fetchall()
                    if value_map[0]['value_map'] == "" or value_map[0]['value_map'] == 0 or value_map[0][
                        'value_map'] == None:
                        sql = "select avg(time_use_character), avg(time_use_scenario),variance(time_use_character),variance(time_use_scenario) from records where code='%s' and job_type='visual'" % (
                            code)
                        cursor.execute(sql)
                        value_list = cursor.fetchall()
                        avg_time_cost_character = value_list[0]["avg(time_use_character)"]
                        avg_time_cost_scenario = value_list[0]["avg(time_use_scenario)"]
                        var_time_cost_character = value_list[0]["variance(time_use_character)"]
                        var_time_cost_scenario = value_list[0]["variance(time_use_scenario)"]
                        avg_score = value_list[0]["avg(vote_star)"]
                        var_score = value_list[0]["variance(vote_star)"]

                        avg_list = [avg_time_cost_scenario, avg_time_cost_character]
                        var_list = [var_time_cost_character, var_time_cost_scenario]
                        y1 = avg_list
                        y2 = var_list
                        # plt.plot(index,y1)
                        plt.plot(y2, label='var time cost 0:basic 1:vivid', marker='o', markersize=6,
                                 markeredgecolor='black', markerfacecolor='brown')
                        plt.plot(y1, label='avg time cost 0:basic 1:vivid', marker='o', markersize=6,
                                 markeredgecolor='black', markerfacecolor='brown')
                        plt.bar(2, avg_score, color='b', label='avg score')
                        plt.bar(3, var_score, color='g', label='var score')
                        plt.legend()
                        plt.savefig('static/Task/' + code + '/value_map.png')
                        plt.close()
                        sql = "update task set value_map=1 where code='%s'" % (code)
                        cursor.execute(sql)



                    sql="select username,vote_star,character_name from records where code='%s' and job_type='visual'" %(code)
                    cursor.execute(sql)
                    agile_user_list_visual=cursor.fetchall()

                    sql="select username,character_name from records where code='%s' and job_type='oral'" %(code)
                    cursor.execute(sql)
                    agile_user_list_oral=cursor.fetchall()

                    f = open('static/Task/' + code + '/record/keywords.txt', 'r')
                    keyword_list = f.readlines()
                    f.close()

                    f = open('static/Task/' + code + '/record/questions.txt', 'r')
                    question_list = f.readlines()
                    f.close()

                    list = []

                    for i in range(len(keyword_list)):
                        f = open('static/Task/' + code + '/record/corpus_Q' + str(i + 1) + '.txt', 'r')
                        tmp_list = f.readlines()
                        f.close()
                        print(tmp_list)
                        count_hit = 0
                        for ele in tmp_list:
                            if 'hit' in ele:
                                count_hit = count_hit + 1
                        count_pro = count_hit / len(tmp_list)
                        print('the count is ' + str(count_hit))
                        print(str(count_pro) + "the probability is")
                        list.append(
                            dict(keyword=keyword_list[i], question=question_list[i], corpus=tmp_list, index=i + 1,
                                 count_pro=count_pro))
                    db.commit()
                    db.close()
                    return render_template("task_detail_mix_layer_off.html",user_list_visual=agile_user_list_visual,user_list_oral=agile_user_list_oral,code=code,corpus_result=list,avg_score=avg_score\
                                           ,avg_time_cost_character=avg_time_cost_character,avg_time_cost_scenario=avg_time_cost_scenario,var_score=var_score\
                                           ,var_time_cost_character=var_time_cost_character,var_time_cost_scenario=var_time_cost_scenario)
                if mode=='pure_visual':

                    sql = "select value_map from task where code='%s'" % (code)
                    cursor.execute(sql)
                    value_map = cursor.fetchall()
                    if value_map[0]['value_map'] == "" or value_map[0]['value_map'] == 0 or value_map[0][
                        'value_map'] == None:
                        sql = "select avg(time_use_character), avg(time_use_scenario),avg(vote_star),variance(time_use_character),variance(time_use_scenario),variance(vote_star) from records where code='%s'" % (
                            code)
                        cursor.execute(sql)
                        value_list = cursor.fetchall()
                        avg_time_cost_character = value_list[0]["avg(time_use_character)"]
                        avg_time_cost_scenario = value_list[0]["avg(time_use_scenario)"]
                        avg_score = value_list[0]["avg(vote_star)"]
                        var_time_cost_character = value_list[0]["variance(time_use_character)"]
                        var_time_cost_scenario = value_list[0]["variance(time_use_scenario)"]
                        var_score = value_list[0]["variance(vote_star)"]
                        avg_list = [avg_time_cost_scenario, avg_time_cost_character]
                        var_list = [var_time_cost_character, var_time_cost_scenario]
                        y1 = avg_list
                        y2 = var_list
                        # plt.plot(index,y1)
                        plt.plot(y2, label='var time cost 0:basic 1:vivid', marker='o', markersize=6,
                                 markeredgecolor='black', markerfacecolor='brown')
                        plt.plot(y1, label='avg time cost 0:basic 1:vivid', marker='o', markersize=6,
                                 markeredgecolor='black', markerfacecolor='brown')
                        plt.bar(2, avg_score, color='b', label='avg score')
                        plt.bar(3, var_score, color='g', label='var score')
                        plt.legend()
                        plt.savefig('static/Task/' + code + '/value_map.png')
                        plt.close()
                        sql = "update task set value_map=1 where code='%s'" % (code)
                        cursor.execute(sql)


                    os.system('cp static/Icons/shut.png static/Task/'+code+'/record/wordcloud.png')
                    sql="select username,vote_star,character_name,time_use_character,time_use_scenario from records where code='%s' and job_type='pure_visual'" %(code)
                    cursor.execute(sql)
                    pure_visual_user_list=cursor.fetchall()
                    db.commit()
                    db.close()
                    return render_template("task_detail_mix_layer_off.html",user_list_visual=pure_visual_user_list,code=code,avg_score=avg_score\
                                           ,avg_time_cost_character=avg_time_cost_character,avg_time_cost_scenario=avg_time_cost_scenario,var_score=var_score\
                                           ,var_time_cost_character=var_time_cost_character,var_time_cost_scenario=var_time_cost_scenario)
            else:##mix layer mode

                sql="select value_map from task where code='%s'" %(code)
                cursor.execute(sql)
                value_map=cursor.fetchall()
                if value_map[0]['value_map']=="" or value_map[0]['value_map']==0 or value_map[0]['value_map']==None:

                    sql = "select avg(time_use_layer1),variance(time_use_layer1) from records where code='%s' and job_type in('layer_1','layer1_2')" % (
                        code)
                    cursor.execute(sql)
                    value_list1 = cursor.fetchall()
                    avg_time_layer1 = value_list1[0]["avg(time_use_layer1)"]
                    var_time_layer1 = value_list1[0]["variance(time_use_layer1)"]

                    sql = "select avg(time_use_layer2),variance(time_use_layer2) from records where code='%s' and job_type in('layer_2','layer1_2')" % (
                        code)
                    cursor.execute(sql)
                    value_list1 = cursor.fetchall()
                    avg_time_layer2 = value_list1[0]["avg(time_use_layer2)"]
                    var_time_layer2 = value_list1[0]["variance(time_use_layer2)"]

                    avg_list = [avg_time_layer1, avg_time_layer2]
                    var_list = [var_time_layer1, var_time_layer2]
                    y1 = avg_list
                    y2 = var_list
                    # plt.plot(index,y1)
                    plt.plot(y2, label='var time cost 0:layer1 1:layer2', marker='o', markersize=6,
                             markeredgecolor='black', markerfacecolor='brown')
                    plt.plot(y1, label='avg time cost 0:layer1 1:layer2', marker='o', markersize=6,
                             markeredgecolor='black', markerfacecolor='brown')

                    plt.legend()
                    plt.savefig('static/Task/' + code + '/value_map.png')
                    plt.close()
                    sql = "update task set value_map=1 where code='%s'" % (code)
                    cursor.execute(sql)

                sql="select username,time_use_layer1,layer_partner from records where code='%s' and job_type in ('layer_1','layer1_2')" %(code)
                cursor.execute(sql)
                layer1_user_list=cursor.fetchall()

                sql="select username,time_use_layer2,layer_partner from records where code='%s' and job_type in ('layer_2','layer1_2')" %(code)
                cursor.execute(sql)
                layer2_user_list=cursor.fetchall()



                db.commit()
                db.close()

                return render_template("task_detail_mix_layer_on.html",layer1_user_list= layer1_user_list,layer2_user_list=layer2_user_list,code=code,avg_time_layer1=avg_time_layer1\
                                       ,var_time_layer1=var_time_layer1,avg_time_layer2=avg_time_layer2,var_time_layer2=var_time_layer2)

    if request.method=='POST':

        return redirect(url_for('designer_interface'))




@app.route('/wait_for_task', methods=['GET'])
def wait_for_task():
    if request.method == 'GET':
        session['code']=''
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql = "select finish_task from child_user where username='%s'" % (session['user'])
        cursor.execute(sql)
        finish_task = cursor.fetchall()
        if finish_task[0]['finish_task'] == 'Y':
            return redirect(url_for("wait_for_task"))
        else:
            return redirect(url_for('child_user_account'))

@app.route('/text_record_restore',methods=['GET'])

#将个人的回答存储后转存到task路径下汇总
def text_record_store():
    if request.method=='GET':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)


        sql_vote_exist = "select vote_system from task where code='%s'" % (session['code'])
        cursor.execute(sql_vote_exist)
        vote_exist = cursor.fetchall()[0]['vote_system']

        #更改用户状态





        sql="select count(*) from records where finish_task='N' and code='%s'" %(session['code'])
        cursor.execute(sql)
        count_uf=cursor.fetchall()


        # 如果未完成的全部清零了，则说明可以进行分析了
        f=open('static/Task/'+session['code']+'/record/keywords.txt','r')
        keyword_list=f.readlines()
        f.close()
        total_corpus=''
        if count_uf[0]['count(*)']==0:
            for i in range(len(keyword_list)):
                f=open('static/Task/'+session['code']+'/record/corpus_Q'+str(i+1)+'.txt','r')
                total_corpus=total_corpus+f.read().replace('\n',' ')+' '
                f.close()

            wordcloud = WordCloud().generate(total_corpus)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.savefig('static/Task/'+session['code']+'/record/wordcloud.png')
            plt.close()


        db.commit()
        db.close()
        if vote_exist == 'on':
            return redirect(url_for('vote'))
        else:
            return redirect(url_for('visual_star'))

@app.route('/user_control',methods=['GET','POST'])
def user_control():
    if request.method=='GET':
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        sql="select * from child_user"
        cursor.execute(sql)
        child_info=cursor.fetchall()
        db.commit()
        db.close()
        return render_template("user_control.html",child_info=child_info)
    if request.method=='POST':
        userlist=request.form.getlist("username")
        new_group=request.form.getlist("change_group")
        db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                             port=25081,
                             user='root',
                             passwd='direnjieE2',
                             db='ECCA',
                             charset='utf8')
        cursor = db.cursor(pymysql.cursors.DictCursor)
        for i in range(len(userlist)):
            if new_group[i]=="":
                continue
            sql="update child_user set group_no='%s' where username='%s'" %(new_group[i],userlist[i])
            cursor.execute(sql)
        db.commit()
        db.close()
        return redirect(url_for('user_control'))




if __name__ == '__main__':

    app.run(host='0.0.0.0')

