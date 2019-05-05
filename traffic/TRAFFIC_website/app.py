from flask import Flask,render_template, request, redirect, url_for, send_from_directory, jsonify
import os
from flask_bootstrap import Bootstrap
from flask_script import Manager
import pymysql
import csv
import numpy as np


app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)


UPLOAD_FOLDER = 'file'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 設定文件上傳的目標資料夾
basedir = os.path.abspath(os.path.dirname(__file__))  # 取得當前項目的絕對路徑
ALLOWED_EXTENSIONS = set(['csv'])  # 允許上傳的檔案類型

people_score_weight = [0.0,    0.021122816, 0.027863027, 0.017078982, 0.054269292, 0.064056023,# 手動輸入
                        0.025526217, 0.124973317, 0.018129, 0.027518233, 0.010182227, 
                        0.044095788, 0.011135441, 0.052132797, 0.040526932, 0.039586673, 0.10938803,# 歷史資料
                        0.056088288, 0.050060013, 0.009846618, 0.007971857,  # 主動資料
                        0.024069192, 0.138390236, 0.025989]
good_score_weight = []



# 判斷文件是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def setlevel(score):
    if score > 90 :
        return '優等'
    elif score > 80:
        return '甲等'
    elif score > 70:
        return '乙等'
    elif score > 60:
        return '丙等'
    elif score > 50:
        return '丁等'
    elif score > 40:
        return '戊等'
    elif score > 30:
        return '己等'
    elif score > 20:
        return '庚等'
    elif score > 10:
        return '辛等'
    elif score > 0:
        return '壬等'      


conn = pymysql.connect(host='localhost' , user='root',
                       passwd='rootroot', charset='UTF8', autocommit=True)
cur = conn.cursor()
cur.execute("USE traffic")
cur.execute("SET SQL_SAFE_UPDATES=0")


@app.route('/', methods = ['GET', 'POST'])
def index():

    if request.method == 'POST':
        get_choice = request.form['choice']

        if get_choice=="select_people":
            return render_template("people.html")
        if get_choice=="select_goods":
            return render_template("goods.html")

    return render_template("index.html")

@app.route('/people', methods = ['GET', 'POST'])
def people():

    if request.method == 'POST':

        all_people_scores = []
        total_score = 0 
        score_level = []               

        all_people_scores.append(float(request.form['regulation']))           
        all_people_scores.append(float(request.form['shift']))
        all_people_scores.append(float(request.form['physical']))
        all_people_scores.append(float(request.form['labor']))
        all_people_scores.append(float(request.form['training']))
        all_people_scores.append(float(request.form['resting']))
        all_people_scores.append(float(request.form['fitness']))
        all_people_scores.append(float(request.form['insurance']))
        all_people_scores.append(float(request.form['transportation']))
        all_people_scores.append(float(request.form['otherwise']))

        file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])  # 拼接合法文件夾路徑
        if not os.path.exists(file_dir):
           os.makedirs(file_dir)            # 若文件夾不存在就創建一個文件夾

        f = request.files['activetime']       # 取得主動收集上傳檔案
        if f and allowed_file(f.filename):  # 判斷是否是允許上傳的檔案類型
            active_file_name = f.filename
            f.save(os.path.join(file_dir, active_file_name))  #保存檔案到指定資料夾

        with open('C:/Users/chenhur/Desktop/TRAFFIC/file/' + active_file_name, newline='',) as csvfile:
            rows = list(csv.reader(csvfile))
            row_one = rows[1]  

            for i in range(1,9,1):
                if i==7:
                    all_people_scores[6] = all_people_scores[6] + float(row_one[i])
                    continue
                all_people_scores.append(float(row_one[i]))               

        f=request.files['Historical']  # 取得歷史資料CSV檔

        if f and allowed_file(f.filename):   # 判斷是否是允許上傳的檔案類型
            historical_file_name = f.filename
            f.save(os.path.join(file_dir, historical_file_name)) #保存檔案到指定資料夾

        with open('C:/Users/chenhur/Desktop/TRAFFIC/file/' + historical_file_name, newline='',) as csvfile:
            
            rows = list(csv.reader(csvfile))
            row_one = rows[1]   
            for i in range(1,7,1):               
                all_people_scores.append(float(row_one[i]))
                


        for i in range(0,len(all_people_scores),1):
            total_score += people_score_weight[i+1] * all_people_scores[i]
     
        score_level.append(total_score)
        score_level.append(setlevel(total_score))

        all_people_scores.append(total_score)
        all_people_scores.append(str(setlevel(total_score)))
        
        sql_attribute_name = ["regulations", "shift", "physical", "labor", "training", "resting", "fitness", "insurance", "transportation", "otherwise", "behavior", "speeding", "belt", "daily", "periodical", "retention", "breath", "Phones" , "Drugs", "Others", "Crashes", "alcohol", "Penalties", "totalscore", "level"]
        
        sql_insert_prefix = "INSERT INTO people ("
        sql_insert_value = "VALUES("
        # 串接SQL指令的for迴圈
        for i in range(0, len(sql_attribute_name), 1) :
            # sql_insert = "INSERT INTO people (" + sql_attribute_name[i] +") VALUES( '%f'  )" % (all_people_scores[i])
            if i == 0:
                # 第一筆資料處理
                sql_insert_prefix = sql_insert_prefix + "`" + sql_attribute_name[i] + "`"
                sql_insert_value = sql_insert_value + "'%f'"
            elif i == (len(sql_attribute_name)- 1):
                # 最後一筆資料處理
                sql_insert_prefix = sql_insert_prefix + ", " + "`" + sql_attribute_name[i] + "`)"
                sql_insert_value = sql_insert_value + ", '%s')"
            else:
                # 第二筆資料開始的處理 (差異: 中間是否有逗號隔開)
                sql_insert_prefix = sql_insert_prefix + ", " + "`" + sql_attribute_name[i] + "`"
                sql_insert_value = sql_insert_value + ", '%f'"

        complete_sql = sql_insert_prefix + " " + sql_insert_value
        
        print(complete_sql, '/n')
        print(tuple(all_people_scores))
        
        try:
            cur.execute(complete_sql % (tuple(all_people_scores)))
        except Exception as e:
            print("test wrong", e)

        conn.commit()

        return render_template("result.html", names = score_level)
    return render_template("people.html")


@app.route('/result', methods = ['GET', 'POST'])
def result():
    if request.method == 'GET':
        return render_template('/')
    return render_template('result.html')


@app.route('/goods', methods = ['GET', 'POST'])
def goods():

    if request.method == 'POST':
        total_score = 0
        score_level = []
        all_goods_scores = []

        all_goods_scores.append(float(request.form['regulation']))            
        all_goods_scores.append(float(request.form['shift']))
        all_goods_scores.append(float(request.form['physical']))
        all_goods_scores.append(float(request.form['labor']))
        all_goods_scores.append(float(request.form['training']))
        all_goods_scores.append(float(request.form['resting']))
        all_goods_scores.append(float(request.form['fitness']))
        all_goods_scores.append(float(request.form['insurance']))
        all_goods_scores.append(float(request.form['transportation']))
        all_goods_scores.append(float(request.form['otherwise']))
        all_goods_scores.append(float(request.form['mark']))
        all_goods_scores.append(float(request.form['pack']))
        all_goods_scores.append(float(request.form['doc']))
        all_goods_scores.append(float(request.form['insurprotectionance']))
        all_goods_scores.append(float(request.form['fixed']))
        all_goods_scores.append(float(request.form['accident']))


        file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])  # 拼接合法文件夾路徑
        if not os.path.exists(file_dir):
           os.makedirs(file_dir)            # 若文件夾不存在就創建一個文件夾

        f=request.files['activetime']       # 取得主動收集上傳檔案
        if f and allowed_file(f.filename):  # 判斷是否是允許上傳的檔案類型
            active_file_name = f.filename
            f.save(os.path.join(file_dir, active_file_name))  #保存檔案到指定資料夾

        with open('C:/Users/chenhur/Desktop/TRAFFIC/file/' + active_file_name, newline='',) as csvfile:
            row_one = np.genfromtxt(csvfile, delimiter=',',skip_header=1) 
            row_one.tolist()    

            for i in range(1,9,1):
                if i==7:
                    all_goods_scores[6] = all_goods_scores[6] + float(row_one[1][i])
                    continue
                all_goods_scores.append(float(row_one[1][i]))               

        f=request.files['Historical']  # 取得歷史資料CSV檔

        if f and allowed_file(f.filename):   # 判斷是否是允許上傳的檔案類型
            historical_file_name = f.filename
            f.save(os.path.join(file_dir, historical_file_name)) #保存檔案到指定資料夾

        with open('C:/Users/chenhur/Desktop/TRAFFIC/file/' + historical_file_name, newline='',) as csvfile:
            
            row_one = np.genfromtxt(csvfile, delimiter=',',skip_header=1)    
            row_one = row_one.tolist() 
                   
            for i in range(1,7,1):               
                all_goods_scores.append(float(row_one[1][i]))
                print(type(row_one[1][2]))

        
        for i in range(0,len(all_goods_scores),1):
            total_score += good_score_weight[i+1] * all_goods_scores[i]
     
        
        score_level.append(total_score)
        score_level.append(setlevel(total_score)) 

        all_goods_scores.append(total_score)
        all_goods_scores.append(str(setlevel(total_score)))
        
        sql_attribute_name = ["regulations", "shift", "physical", "labor", "training", "resting", "fitness", "insurance", "transportation", "otherwise", 'mark', 'pack', 'doc', 'insurprotectionance', 'fixed', 'accident', "behavior", "speeding", "belt", "daily", "periodical", "retention", "breath", "Phones" , "Drugs", "Others", "Crashes", "alcohol", "Penalties", "totalscore", "level"]

        sql_insert_prefix = "INSERT INTO goods ("
        sql_insert_value = "VALUES("
        # 串接SQL指令的for迴圈
        for i in range(0, len(sql_attribute_name), 1) :
            # sql_insert = "INSERT INTO goods (" + sql_attribute_name[i] +") VALUES( '%f'  )" % (all_goods_scores[i])
            if i == 0:
                # 第一筆資料處理
                sql_insert_prefix = sql_insert_prefix + "`" + sql_attribute_name[i] + "`"
                sql_insert_value = sql_insert_value + "'%f'"
            elif i == (len(sql_attribute_name)- 1):
                # 最後一筆資料處理
                sql_insert_prefix = sql_insert_prefix + ", " + "`" + sql_attribute_name[i] + "`)"
                sql_insert_value = sql_insert_value + ", '%s')"
            else:
                # 第二筆資料開始的處理 (差異: 中間是否有逗號隔開)
                sql_insert_prefix = sql_insert_prefix + ", " + "`" + sql_attribute_name[i] + "`"
                sql_insert_value = sql_insert_value + ", '%f'"

        
        complete_sql = sql_insert_prefix + " " + sql_insert_value
        print(complete_sql)
        print(tuple(all_goods_scores))

        try:
            cur.execute(complete_sql % (tuple(all_goods_scores)))
        except Exception as e:
            print("test wrong", e)

        conn.commit()


        return render_template("result.html", names = score_level)

    return render_template("goods.html")



if __name__ == "__main__":
    manager.run()