import pymysql
from aip import AipSpeech
import matplotlib.pylab as plt
import os
from wordcloud import WordCloud
import sys

#speech_recognition 0 未解析 1解析中 2解析结束

code=str(sys.argv[1])

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()
# baidu audio->text api


APP_ID = '24101838'
API_KEY = '21YIezwElGu94qpVGFCWG8H0'
SECRET_KEY = 'oCVvvsdYZKfQECITVhMhlCaAGOtpkknX'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


def sr(code):

    db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                                     port=25081,
                                     user='root',
                                     passwd='direnjieE2',
                                     db='ECCA',
                                     charset='utf8')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    sql = "select speech_recognition from task where code='%s'" % (code)
    cursor.execute(sql)
    sr = cursor.fetchall()
    print(sr)

    db.commit()
    db.close()

    f = open('static/Task/' + code + '/record/keywords.txt', 'r')
    keyword_list = f.readlines()
    f.close()
    total_corpus = ''

    db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                         port=25081,
                         user='root',
                         passwd='direnjieE2',
                         db='ECCA',
                         charset='utf8')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    sql = "select username from records where code='%s' and job_type in ('all','oral')" % (code)
    cursor.execute(sql)
    current_user_list = cursor.fetchall()
    user_list=[]
    db.commit()
    db.close()


    for order in range(len(current_user_list)):
        user_list.append(current_user_list[order]['username'])

    print(user_list)
    current_user_list=user_list
    ##    file_path = 'static/user/' + session['user'] + '/' + code + '/record/'

    for j in range(len(current_user_list)):
        for i in range(len(keyword_list)):


            number = str(i + 1)
            print("现在是", current_user_list[j], "的第", number, "个音频")
            if os.path.exists('static/user/' + current_user_list[j] + '/' + code + '/record/record' + number + '_new.wav') == False:
                f = open('static/Task/' + code + '/record/corpus_Q' + number + '.txt', 'a')
                f.write("###context missing###" + '\n')
                f.close()
                db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                                     port=25081,
                                     user='root',
                                     passwd='direnjieE2',
                                     db='ECCA',
                                     charset='utf8')
                cursor = db.cursor(pymysql.cursors.DictCursor)
                sql = "update task set process_count=process_count+1 where code='%s'" % (code)
                cursor.execute(sql)
                sql="update task set net_error=net_error+1 where code='%s'" %(code)
                cursor.execute(sql)
                db.commit()
                db.close()
                continue


            try:
                test = client.asr(
                    get_file_content('static/user/' + current_user_list[j]+ '/' +code+ '/record/record' + number + '_new.wav'), 'wav', 16000, {
                        'dev_pid': 1737,
                    })
                f = open('static/Task/' + code + '/record/keywords.txt', 'r')
                keyword_list = f.readlines()
                f.close()

                print('string is: ' + test['result'][0])
                print('keyword: ' + keyword_list[i])

                print('judging...')
                if (keyword_list[int(number) - 1].strip() in test['result'][0]) == True:
                    match = 'hit'
                else:
                    match = 'miss'

                print(match)
                with open('static/user/' + current_user_list[j] + '/' + code + '/record/record_text.txt',
                          'a') as t:
                    t.write(test['result'][0] + '  --result: ' + match + '\n')
                f = open('static/Task/' + code + '/record/corpus_Q' + number + '.txt', 'a')
                f.write(test['result'][0] + '  --result: ' + match + '\n')
                f.close()
            except:
                f = open('static/Task/' + code + '/record/corpus_Q' + number + '.txt', 'a')
                f.write("###context error, server not recognise, please check the record file###" + '\n')
                f.close()

                db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                                     port=25081,
                                     user='root',
                                     passwd='direnjieE2',
                                     db='ECCA',
                                     charset='utf8')
                cursor = db.cursor(pymysql.cursors.DictCursor)
                sql="update task set nlp_error=nlp_error+1 where code='%s'" %(code)
                cursor.execute(sql)
                db.commit()
                db.close()

            db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                                 port=25081,
                                 user='root',
                                 passwd='direnjieE2',
                                 db='ECCA',
                                 charset='utf8')
            cursor = db.cursor(pymysql.cursors.DictCursor)
            sql="update task set process_count=process_count+1 where code='%s'" %(code)
            cursor.execute(sql)
            sql="select process_count from task where code='%s'" %(code)
            cursor.execute(sql)
            db.commit()
            db.close()
            print(cursor.fetchall(),'\n')

        for i in range(len(keyword_list)):
            f = open('static/Task/' + code + '/record/corpus_Q' + str(i + 1) + '.txt', 'r')
            total_corpus = total_corpus + f.read().replace('\n', ' ') + ' '
            f.close()

        total_corpus=total_corpus.replace("###context error, server not recognise, please check the record file###"," ")
        total_corpus=total_corpus.replace("###context missing###"," ")
        total_corpus=total_corpus.replace("--result: hit"," ")
        total_corpus=total_corpus.replace("--result: miss"," ")

        f = open('static/Task/' + code + '/record/total_corpus.txt', 'w')
        f.write(total_corpus)
        f.close()


        wordcloud = WordCloud().generate(total_corpus)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig('static/Task/' + code + '/record/wordcloud.png')
        plt.close()

    db = pymysql.connect(host='gz-cynosdbmysql-grp-df9ep7mf.sql.tencentcdb.com',
                         port=25081,
                         user='root',
                         passwd='direnjieE2',
                         db='ECCA',
                         charset='utf8')
    cursor = db.cursor(pymysql.cursors.DictCursor)
    sql="update task set speech_recognition=2 where code='%s'" %(code)
    cursor.execute(sql)
    print("Speech Translation Completed ######")
    db.commit()
    db.close()
    for name in current_user_list:
        os.system("zip -q -r static/user/"+name+"/"+code+"/"+name+"_"+code+"_record.zip static/user/"+name+"/"+code+"/record")

try:
    sr(code)
except ValueError:
    print("input code is not correct")
