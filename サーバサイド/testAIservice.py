#ライブラリのインポート
from flask import Flask,request,jsonify,render_template,session,redirect
from keras.applications.vgg16 import VGG16, decode_predictions
from sklearn.ensemble import GradientBoostingClassifier as GBC
from sklearn.ensemble import GradientBoostingRegressor as GBR
from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph
from datetime import timedelta
import sqlite3 as sql
import numpy as np
import pandas as pd
import cv2
import json
import pickle
import datetime
import os
import secrets
import html

#VGG16APIの読込
f=open("VGG16_class.json","r",encoding="shift-jis")
js=f.read()
f.close()
js=js.replace("'",'"')
dic=json.loads(js)

#VGG16の読込
model=VGG16()

#診断AI
loc="static/dataset/mode.sav"
model2=pickle.load(open(loc, 'rb'))

#データベース接続
dbname="test.db"
conn=sql.connect(dbname,check_same_thread=False)
cur=conn.cursor()

#サービススタート
app = Flask(__name__)

#セッション
#シークレットキー
app.secret_key='user'
#20分間セッションを維持
app.permanent_session_lifetime=timedelta(minutes=20)

#ログイン画面
@app.route("/login",methods=["GET","POST"])
def hello():
    #ログイン画面・セッションがあったら「/home」にリダイレクト
    if request.method=="GET":
        #セッションがある場合、「/home」にリダイレクト
        if "user_id" in session:
            return redirect("/home")
        
        #セッションがない場合、ログイン画面を表示
        else:
            page="<title>ログイン画面</title>\n"
            page=page+"<h1>メールアドレスとパスワードを入力してください</h1>\n"
            page=page+"<a href=create>ユーザー新規登録</a>\n"
            page=page+"<form method=POST action=login>\n"
            page=page+"<table border=1>\n"
            page=page+"<tr><td>メールアドレス</td><td><input type=text name=name></td></tr>\n"
            page=page+"<tr><td>パスワード</td><td><input type=password name=pass></td></tr>\n"
            page=page+"</table>\n"
            page=page+"<input type=submit value=送信>\n"
            page=page+"</form>"
            return page
        
    #ログイン成功ならリダイレクト・セッション作成、失敗なら入力しなおす
    elif request.method=="POST":
        #パスワードのロード
        #com="SELECT user_id,pass FROM users where user_name='"+request.form["name"]+"'"
        #cur.execute(com)
        cur.execute("SELECT user_id,pass FROM users where user_name=?",(str(request.form["name"]),))
        code=[]
        for row in cur:
            code.append(row[1])
        #パスワードの確認
        #パスワードが合っている場合リダイレクト・セッションの発行
        if cph(row[1],request.form["pass"]):
            session.permanent = True
            session["user_id"]=row[0]
            return redirect("/home")
        
        #パスワードが間違っている場合もう一回
        else:
            page="<title>ログイン画面</title>\n"
            page=page+"<h1>メールアドレスかパスワードが間違っています</h1>\n"
            page=page+"<a href=create>ユーザー新規登録</a>\n"
            page=page+"<form method=POST action=login>\n"
            page=page+"<table border=1>\n"
            page=page+"<tr><td>メールアドレス</td><td><input type=text name=name></td></tr>\n"
            page=page+"<tr><td>パスワード</td><td><input type=password name=pass></td></tr>\n"
            page=page+"</table>\n"
            page=page+"<input type=submit value=送信>\n"
            page=page+"</form>"
            return page

#JSON用ログイン機能
@app.route("/login-json",methods=["GET","POST"])
def loginjson():
    if request.method=="GET":
        tmp={}
        tmp["id"]="BAD REQUEST"
        tmp["name"]="正規の手法を使ってください"
        return jsonify(tmp)
    elif request.method=="POST":
        #com="SELECT user_id,pass FROM users where user_name='"+request.form["name"]+"'"
        #com="SELECT user_id,pass FROM users where user_name='"+request.args.get("name")+"'"
        #cur.execute(com)
        cur.execute("SELECT user_id,pass FROM users where user_name=?",(str(request.form["name"]),))
        code=[]
        for row in cur:
            code.append(row[1])
        tmp={}
        if cph(row[1],request.form["pass"]):
        #if cph(row[1],request.args.get("pass")):
            #tmp["name"]=request.args.get("name")
            tmp["name"]=request.form["name"]
            tmp["id"]=int(row[0])
        else:
            tmp["name"]="None"
            tmp["id"]=0   
        return jsonify(tmp)

#Web新規登録
@app.route("/create",methods=["GET","POST"])
def createuser():
    #アクセス時の入力フォーム
    if request.method=="GET":
        page="<title>ユーザ登録画面</title>\n"
        page=page+"<h1>登録に必要な下記の情報を入れてください</h1>\n"
        page=page+"<form action=create method=POST>\n"
        page=page+"<table border=1>\n"
        page=page+"<tr><td>メールアドレス</td><td><input type=text name=name></td></tr>"
        page=page+"<tr><td>パスワード</td><td><input type=password name=pass></td></tr>\n"
        page=page+"</table>"
        page=page+"<input type=submit value=送信>"
        page=page+"</form>"
        return page
    
    #入力後のページ
    elif request.method=="POST":
        #名前に重複が無いかチェック
        #com="SELECT user_id,user_name FROM users WHERE user_name='"+str(request.form["name"])+"'"
        #cur.execute(com)
        cur.execute("SELECT user_id,user_name FROM users WHERE user_name=?",(str(request.form["name"]),))
        res=[]
        for row in cur:
            res.append(row[0])
            res.append(row[1])
        
        #ユーザ名に重複がない
        if len(res)==0:
            t=(request.form["name"],gph(request.form["pass"]),str(datetime.datetime.today()))
            #登録できた場合
            try:
                cur.execute("INSERT INTO users (user_name,pass,date) VALUES (?,?,?)",t)
                conn.commit()
                #cur.execute("SELECT user_id FROM users WHERE user_name='"+request.form["name"]+"'")
                cur.execute("SELECT user_id FROM users WHERE user_name=?",(str(request.form["name"]),))
                user=[]
                for row in cur:
                    user.append(row[0])
                os.mkdir("static/media/"+str(user[0]))
                os.mkdir("static/stats_after/"+str(user[0]))
                os.mkdir("static/stats_before/"+str(user[0]))
                page="<title>登録成功</title>"
                page=page+"<h1>登録完了</h1>"
                page=page+"<a href=home>メニュー画面へ</a>"
            #登録出来なかった場合
            except:
                page="<title>登録失敗</title>"
                page=page+"<h1>登録に失敗しました。再度入力を</h1>"
                page=page+"<form action=create method=POST>\n"
                page=page+"<table border=1>\n"
                page=page+"<tr><td>メールアドレス</td><td><input type=text name=name></td></tr>"
                page=page+"<tr><td>パスワード</td><td><input type=password name=pass></td></tr>\n"
                page=page+"</table>"
                page=page+"<input type=submit value=送信>"
                page=page+"</form>"
        else:
            page="<title>登録失敗</title>"
            page=page+"<h1>そのアドレスはすでに登録されています</h1>"
            page=page+"<form action=create method=POST>\n"
            page=page+"<table border=1>\n"
            page=page+"<tr><td>メールアドレス</td><td><input type=text name=name></td></tr>"
            page=page+"<tr><td>パスワード</td><td><input type=password name=pass></td></tr>\n"
            page=page+"</table>"
            page=page+"<input type=submit value=送信>"
            page=page+"</form>"
    return page

#JSON新規登録
@app.route("/create-json",methods=["GET","POST"])
def createuserjson():
    #GETでアクセスされた場合
    if request.method=="GET":
        tmp={}
        tmp["result"]="アクセスが不正です"
        return jsonify(tmp)
    
    #POSTでアクセスされた場合
    elif request.method=="POST":
        #名前に重複が無いかチェック
        #com="SELECT user_id,user_name FROM users WHERE user_name='"+str(request.form["name"])+"'"
        #cur.execute(com)
        cur.execute("SELECT user_id,user_name FROM users WHERE user_name=?",(str(request.form["name"]),))
        res=[]
        tmp={}
        for row in cur:
            res.append(row[0])
            res.append(row[1])
        
        #ユーザ名に重複がない
        if len(res)==0:
            t=(request.form["name"],gph(request.form["pass"]),str(datetime.datetime.today()))
            #登録できた場合
            try:
                cur.execute("INSERT INTO users (user_name,pass,date) VALUES (?,?,?)",t)
                conn.commit()
                cur.execute("SELECT user_id FROM users WHERE user_name=?",(str(request.form["name"]),))
                user=[]
                for row in cur:
                    user.append(row[0])
                os.mkdir("static/media/"+str(user[0]))
                os.mkdir("static/stats_after/"+str(user[0]))
                os.mkdir("static/stats_before/"+str(user[0]))
                tmp["id"]=int(user[0])
                tmp["result"]="登録成功"
            #登録出来なかった場合
            except:
                tmp["id"]=0
                tmp["result"]="登録失敗(再度入力を)"
        else:
            tmp["id"]=0
            tmp["result"]="登録失敗(既にそのアドレスはあります)"
    return jsonify(tmp)

#メニュー
@app.route("/home")
def index():
    #セッションがあれば通常サービス
    if "user_id" in session:
        page="<title>ホーム</title>"
        page=page+"\n<a href=logout align=right>ログアウト</a>\n<h1>ホーム画面</h1><br>\n"
        page=page+"サービスを選んでください<br>\n"
        page=page+"・<a href=image>画像の予想</a><br>\n"
        page=page+"・<a href=telling>占い</a><br>\n"
        page=page+"・<a href=analysis>分析</a><br>\n"
        return page
    #セッションがない場合、「/login」にリダイレクト
    else:
        return redirect("/login")
    
#画像サービス
@app.route("/image")
def image():
    #セッションがあれば通常サービス
    if "user_id" in session:
        token=secrets.token_hex()
        session["image_key"]=token
        page="<title>画像予想</title>"
        page=page+"\n<a href=logout align=right>ログアウト</a>\n<h1>画像予想をします</h1><br>\n"
        page=page+"<form method=post action=image-result-html enctype=multipart/form-data><br>\n"
        page=page+"<input type=hidden name=user_id value="+str(session["user_id"])+">\n"
        page=page+"予測したい画像を入れてください<br>\nHTML<br>"
        page=page+"<input type=file name=img><br>\n"
        page=page+"<input type=hidden value="+token+" name=image_key>"
        page=page+"<input type=submit value=送信>\n"
        page=page+"</form>\n"
        page=page+"<form method=post action=image-result-json enctype=multipart/form-data><br>\n"
        page=page+"<input type=hidden name=user_id value="+str(session["user_id"])+">\n"
        page=page+"<br>\nJSON<br>"
        page=page+"<input type=file name=img><br>\n"
        page=page+"<input type=submit value=送信>\n"
        page=page+"</form>\n"
        return page
    #セッションがない場合、「/login」にリダイレクト
    else:
        return redirect("/login")

#JSON画像予測結果
@app.route("/image-result-json",methods=["GET","POST"])
def imgresultjsn():
    if request.method=="GET":
        return "不正なアクセスです"
    elif request.method=="POST":
        #画像の受信
        f=request.files["img"]
        name=f.filename
        f.save("static/media/"+str(request.form["user_id"])+"/"+name)#imgname
        #画像のサイズをVGG16に合わせる
        img=cv2.imread("static/media/"+str(request.form["user_id"])+"/"+name)
        img=cv2.resize(img,(224,224))
        #画像の画素値を0から1に変換
        x=[]
        x.append(img)
        x=np.array(x)
        x.astype("float32")
        x=x/255
        #VGG16による予測
        y_pred=model.predict(x)
        #上位10位の抽出
        result=decode_predictions(y_pred,top=10)
        res={}#出力用の連想配列
        #JSON内に連想配列を格納
        for i in range(len(result[0])):
            pred={}
            pred["proba"]=str(result[0][i][2]*100)
            pred["name"]=dic[result[0][i][0]]
            res[i+1]=pred
        #データベース書き込み
        t=(request.form["user_id"],name,"img-json",str(datetime.datetime.today()))
        cur.execute("INSERT INTO data (user_id,data_name,serv,date) VALUES (?,?,?,?)",t)
        conn.commit()
        #JSON出力
        return jsonify(res)
        

#HTML画像予測結果
@app.route("/image-result-html",methods=["GET","POST"])
def imgresulthtml():
    if request.method=="GET":
        return "不正なアクセスです"
    elif request.method=="POST":
        #セッションがあれば通常サービス
        if "user_id" in session:
            if str(session["image_key"])==str(request.form["image_key"]):
                #画像の受信
                f=request.files["img"]
                name=f.filename
                f.save("static/media/"+str(session["user_id"])+"/"+name)#imgname
                #画像の大きさ変更
                img=cv2.imread("static/media/"+str(session["user_id"])+"/"+name)
                img=cv2.resize(img,(224,224))
                #画像の賀措置を0から1に変換
                x=[]
                x.append(img)
                x=np.array(x)
                x.astype("float32")
                x=x/255
                #VGG16による予測
                y_pred=model.predict(x)
                #上位10位を出力
                result=decode_predictions(y_pred,top=10)
                page="<title>画像の予測結果</title>\n<a href=logout align=right>ログアウト</a>\n<br><a href=image>送信画面に戻る</a><br>\n<a href=home>メニューに戻る</a><br>\n"
                page=page+"<table>\n<tr><td>予測結果</td><td>確率(%)</td></tr>\n<tr>"
                for i in range(len(result[0])):
                    page=page+"<tr><td>"+dic[result[0][i][0]]+"</td><td>"+str(result[0][i][2]*100)+"</td></tr>\n"
                page=page+"</table>"
                #データベース書き込み
                t=(session["user_id"],name,"img-html",str(datetime.datetime.today()))
                cur.execute("INSERT INTO data (user_id,data_name,serv,date) VALUES (?,?,?,?)",t)
                conn.commit()
                size=""
                height,width=img.shape[0],img.shape[1]
                if height>=width:
                    size="height=224"
                else:
                    size="width=224"
                return render_template("sample.html", imgname="static/media/"+str(session["user_id"])+"/"+name+" "+size,page=page)
            else:
                return "正規のアクセスをしてください"
        #セッションがない場合、「/login」にリダイレクト
        else:
            return redirect("/login")

#占い入力フォーム
@app.route("/telling")
def fote():
    #セッションがあれば通常サービス
    if "user_id" in session:
        token=secrets.token_hex()
        session["telling_key"]=token
        page="<title>占い</title>\n<a href=logout align=right>ログアウト</a>\n"
        page=page+"<h1>占いをします：あなたがアメリカ人だったら何歳？</h1><br>\n"
        page=page+"<h2>以下の項目を入力してください</h2>\n"
        page=page+"<form action=telling-ans-html method=POST>\n"
        page=page+"<input type=hidden name=telling_key value="+token+">"
        page=page+"<input type=hidden name=user_id value="+str(session["user_id"])+">\n"
        page=page+"<h3>教育年数</h3>"
        page=page+"<input type=text name=education-num pattern=[0-9]+>"
        page=page+"<h3>年収</h3>"
        page=page+"<input type=radio name=Y value=0 checked>500万円未満<br>\n"
        page=page+"<input type=radio name=Y value=1>500万円以上<br>\n"
        page=page+"<h3>業務形態</h3>\n"
        page=page+"<input type=radio name=workclass value=workclass_? checked>不詳<br>\n"
        page=page+"<input type=radio name=workclass value=workclass_Federal-gov>国家公務員<br>\n"
        page=page+"<input type=radio name=workclass value=workclass_Local-gov>地方公務員(市区町村)<br>\n"
        page=page+"<input type=radio name=workclass value=workclass_Private>プライベート<br>\n"
        page=page+"<input type=radio name=workclass value=workclass_Self-emp-inc>自営業(法人)<br>\n"
        page=page+"<input type=radio name=workclass value=workclass_Self-emp-not-inc>自営業(法人ではない)<br>\n"
        page=page+"<input type=radio name=workclass value=workclass_State-gov>地方公務員(都道府県)<br>\n"
        page=page+"<h3>最終学歴</h3>\n"
        page=page+"<input type=radio name=education value=education_10th checked>10th<br>\n"
        page=page+"<input type=radio name=education value=education_11th>11th<br>\n"
        page=page+"<input type=radio name=education value=education_12th>12th<br>\n"
        page=page+"<input type=radio name=education value=education_1st-4th>１～４th<br>\n"
        page=page+"<input type=radio name=education value=education_5th-6th>5～6th<br>\n"
        page=page+"<input type=radio name=education value=education_7th-8th>7～8th<br>\n"
        page=page+"<input type=radio name=education value=education_9th>9th<br>\n"
        page=page+"<input type=radio name=education value=education_Assoc-acdm>Assoc-acdm<br>\n"
        page=page+"<input type=radio name=education value=education_Assoc-voc>Assoc-voc<br>\n"
        page=page+"<input type=radio name=education value=education_Bachelors>Bachelors<br>\n"
        page=page+"<input type=radio name=education value=education_HS-grad>HS-grad<br>\n"
        page=page+"<input type=radio name=education value=education_Masters>Masters<br>\n"
        page=page+"<input type=radio name=education value=education_Prof-school>Prof-school<br>\n"
        page=page+"<input type=radio name=education value=education_Some-college>Some-college<br>\n"
        page=page+"<h3>配偶者について</h3>\n"
        page=page+"<input type=radio name=marital-status value=marital-status_Married-civ-spouse checked>既婚・同居<br>\n"
        page=page+"<input type=radio name=marital-status value=marital-status_Never-married>未婚<br>\n"
        page=page+"<input type=radio name=marital-status value=marital-status_Separated>既婚・別居<br>\n"
        page=page+"<input type=radio name=marital-status value=marital-status_Widowed>未亡人<br>\n"
        page=page+"<h3>職業</h3>\n"
        page=page+"<input type=radio name=occupation value=occupation_? checked>不詳<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Adm-clerical>事務員<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Craft-repair>修理士・整備士<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Exec-managerial>幹部・経営<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Farming-fishing>農業・漁業<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Handlers-cleaners>警備員・清掃員<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Machine-op-inspct>機械作業員・検査員<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Prof-specialty>専門家・プロフェッサー<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Protective-serv>保安職<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Sales>セールスマン<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Tech-support>技術支援<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Transport-moving>配達員<br>\n"
        page=page+"<input type=radio name=occupation value=occupation_Transport-moving>配達員<br>\n"    
        page=page+"<input type=radio name=occupation value=occupation_Other-service>その他<br>\n"
        page=page+"<h3>家族関係</h3>\n"
        page=page+"<input type=radio name=relationship value=relationship_Husband checked>夫<br>\n"
        page=page+"<input type=radio name=relationship value=relationship_Not-in-family>家族ではない<br>\n"
        page=page+"<input type=radio name=relationship value=relationship_Own-child>子供<br>\n"
        page=page+"<input type=radio name=relationship value=relationship_Wife>妻<br>\n"
        page=page+"<input type=radio name=relationship value=relationship_Unmarried>未婚<br>\n"
        page=page+"<input type=radio name=relationship value=relationship_Other-relative>その他<br>\n"
        page=page+"<h3>人種</h3>\n"
        page=page+"<input type=radio name=race value=race_Asian-Pac-Islander checked>アジア人<br>\n"
        page=page+"<input type=radio name=race value=race_Black>黒人<br>\n"
        page=page+"<input type=radio name=race value=race_White>白人<br>\n"
        page=page+"<h3>性別</h3>\n"
        page=page+"<input type=radio name=sex value=sex_Female checked>女性<br>\n"
        page=page+"<input type=radio name=sex value=sex_Male>男性<br>\n"
        page=page+"<h3>母国</h3>\n"
        page=page+"<input type=radio name=native-country value=native-country_Mexico checked>メキシコ<br>\n"
        page=page+"<input type=radio name=native-country value=native-country_Philippines>フィリピン<br>\n"
        page=page+"<input type=radio name=native-country value=native-country_United-States>アメリカ合衆国<br>\n"
        page=page+"<input type=submit value=診断>\n</form>"
        return page
    #セッションがない場合、「/login」にリダイレクト
    else:
        return redirect("/login")

#HTML占い結果
@app.route("/telling-ans-html",methods=["GET","POST"])
def telanshtml():
    if request.method=="GET":
        return "不正なリクエストです"
    elif request.method=="POST":
        #セッションがあれば通常サービス
        if "user_id" in session:
            if session["telling_key"]==request.form["telling_key"]:
                try:
                    _=int(request.form["education-num"])
                except:
                    return redirect("telling")
                #国勢調査データの読込
                df=pd.read_csv("static/dataset/tohtml.csv",encoding="shift-jis")
                tmp=[]
                tab=[]
                page="<title>診断結果</title>\n<a href=logout align=right>ログアウト</a><br>\n<a href=telling>入力に戻る</a><br>\n<a href=home>メニューに戻る</a><br>\n"
                page=page+"<form method=POST action=telling-ans-json>\n"
                page=page+"<input type=hidden name=user_id value="+str(session["user_id"])+">\n"
                #データの読み込み
                #年収
                tmp.append("Y")
                tmp.append(int(request.form.get("Y")))
                page=page+"<input type=hidden name=Y value="+str(request.form.get("Y"))+">\n"
                tab.append(tmp)
                tmp=[]
                #教育年数
                tmp.append("education-num")
                tmp.append(int(request.form["education-num"]))
                page=page+"<input type=hidden name=education-num value="+str(request.form["education-num"])+">\n"
                tab.append(tmp)
                tmp=[]
                #業務形態
                tmp.append(request.form.get("workclass"))
                page=page+"<input type=hidden name=workclass value="+str(request.form.get("workclass"))+">\n"
                tmp.append(1)
                tab.append(tmp)
                tmp=[]
                #最終学歴
                tmp.append(request.form.get("education"))
                page=page+"<input type=hidden name=education value="+str(request.form.get("education"))+">\n"
                tmp.append(1)
                tab.append(tmp)
                tmp=[]
                #配偶者について
                tmp.append(request.form.get("marital-status"))
                page=page+"<input type=hidden name=marital-status value="+str(request.form.get("marital-status"))+">\n"
                tmp.append(1)
                tab.append(tmp)
                tmp=[]
                #職業
                tmp.append(request.form.get("occupation"))
                page=page+"<input type=hidden name=occupation value="+str(request.form.get("occupation"))+">\n"
                tmp.append(1)
                tab.append(tmp)
                tmp=[]
                #家族関係
                tmp.append(request.form.get("relationship"))
                page=page+"<input type=hidden name=relationship value="+str(request.form.get("relationship"))+">\n"
                tmp.append(1)
                tab.append(tmp)
                tmp=[]
                #人種
                tmp.append(request.form.get("race"))
                page=page+"<input type=hidden name=race value="+str(request.form.get("race"))+">\n"
                tmp.append(1)
                tab.append(tmp)
                tmp=[]
                #性別
                tmp.append(request.form.get("sex"))
                page=page+"<input type=hidden name=sex value="+str(request.form.get("sex"))+">\n"
                tmp.append(1)
                tab.append(tmp)
                tmp=[]
                #母国
                tmp.append(request.form.get("native-country"))
                page=page+"<input type=hidden name=native-country value="+str(request.form.get("native-country"))+">\n"
                tmp.append(1)
                tab.append(tmp)
                #表の作成
                tab=np.array(tab).T
                dfi=pd.DataFrame(tab)
                dfi.columns=tab[0]
                df=pd.concat([df,dfi])
                #欠損値を0にする
                x=[]
                x.append(df.values[len(df.values)-1])
                x=np.array(x).astype("float32")
                x=np.nan_to_num(x)
                #予測
                y_pred=model2.predict(x)
                page=page+str(int(y_pred[0]))+"歳とAIは予想しました\n<input type=submit value=JSON></form>"
                #データベース書き込み
                t=(session["user_id"],"telling-html",str(datetime.datetime.today()))
                cur.execute("INSERT INTO data (user_id,serv,date) VALUES (?,?,?)",t)
                conn.commit()
                return page
            else:
                return "正規のアクセスをしてください"
        #セッションがない場合、「/login」にリダイレクト
        else:
            return redirect("/login")

#JSON占い結果
@app.route("/telling-ans-json",methods=["GET","POST"])
def telansjson():
    if request.method=="GET":
        return "不正なリクエストです"
    elif request.method=="POST":
        #国勢調査データの読み込み
        df=pd.read_csv("static/dataset/tohtml.csv",encoding="shift-jis")
        tmp=[]
        tab=[]
        #各データの読込
        #年収
        tmp.append("Y")
        tmp.append(int(request.form["Y"]))
        tab.append(tmp)
        tmp=[]
        #教育年数
        tmp.append("education-num")
        tmp.append(int(request.form["education-num"]))
        tab.append(tmp)
        tmp=[]
        #業務形態
        tmp.append(request.form["workclass"])
        tmp.append(1)
        tab.append(tmp)
        tmp=[]
        #最終学歴
        tmp.append(request.form["education"])
        tmp.append(1)
        tab.append(tmp)
        tmp=[]
        #配偶者について
        tmp.append(request.form["marital-status"])
        tmp.append(1)
        tab.append(tmp)
        tmp=[]
        #職業
        tmp.append(request.form["occupation"])
        tmp.append(1)
        tab.append(tmp)
        tmp=[]
        #家族関係
        tmp.append(request.form["relationship"])
        tmp.append(1)
        tab.append(tmp)
        tmp=[]
        #人種
        tmp.append(request.form["race"])
        tmp.append(1)
        tab.append(tmp)
        tmp=[]
        #性別
        tmp.append(request.form["sex"])
        tmp.append(1)
        tab.append(tmp)
        tmp=[]
        #母国
        tmp.append(request.form["native-country"])
        tmp.append(1)
        tab.append(tmp)
        #表の作成
        tab=np.array(tab).T
        dfi=pd.DataFrame(tab)
        dfi.columns=tab[0]
        df=pd.concat([df,dfi])
        #欠損地を0に
        x=[]
        x.append(df.values[len(df.values)-1])
        x=np.array(x).astype("float32")
        x=np.nan_to_num(x)
        #予測
        y_pred=model2.predict(x)
        #連想配列の作成
        out={}
        #予測
        out["predict"]=str(int(y_pred[0]))
        #データベース書き込み
        t=(request.form["user_id"],"telling-json",str(datetime.datetime.today()))
        cur.execute("INSERT INTO data (user_id,serv,date) VALUES (?,?,?)",t)
        conn.commit()
        #JSON出力
        return jsonify(out)

#分析サービス
@app.route("/analysis")
def ans():
    #セッションがあれば通常サービス
    if "user_id" in session:
        page="<title>データ分析</title>\n"
        token=secrets.token_hex()
        session["analysis_key"]=token
        try:
            miss=request.args.get("miss")
            if int(miss)==1:
                page=page+"<h3>目的変数とカテゴリに一致があったため遷移しました</h3>"
        except:
            _=1
        page=page+"<a href=logout align=right>ログアウト</a>\n<h1>統計データを分析します</h1><br>\n"
        page=page+"予測したい統計データを入れてください<br>"
        page=page+"<form method=post action=stat-before-html enctype=multipart/form-data><br>\n"
        page=page+"<input type=hidden name=analysis_key value="+token+">"
        page=page+"<input type=hidden name=user_id value="+str(session["user_id"])+">\n"
        page=page+"HTML<br>"
        page=page+"<input type=file name=stat><br>"
        page=page+"<input type=submit value=送信>"
        page=page+"</form>"
        page=page+"<form method=post action=stat-before-json enctype=multipart/form-data><br>\n"
        page=page+"<input type=hidden name=user_id value="+str(session["user_id"])+">\n"
        page=page+"JSON<br>"
        page=page+"<input type=file name=stat><br>"
        page=page+"<input type=submit value=送信>"
        page=page+"</form>"
        return page
    #セッションがない場合、「/login」にリダイレクト
    else:
        return redirect("/login")

#HTMLでテーブルデータ表示
@app.route("/stat-before-html",methods=["GET","POST"])
def stbfrh():
    if request.method=="GET":
        return "不正なアクセスです"
    elif request.method=="POST":
        #セッションがあれば通常サービス
        if "user_id" in session:
            if session["analysis_key"]==request.form["analysis_key"]:
                token=secrets.token_hex()
                session["stat-before-html_key"]=token
                f=request.files["stat"]
                name=f.filename
                f.save("static/stats_before/"+str(session["user_id"])+"/"+name)
                df=pd.read_csv("static/stats_before/"+str(session["user_id"])+"/"+name,encoding="shift-jis")
                col=df.columns
                val=df.values
                page="<title>データ整形</title>\n<a href=logout align=right>ログアウト</a>\n<br><a href=analysis>送信画面に戻る</a><br>\n<a href=home>メニューに戻る</a><br>\n"
                page=page+"<form method=POST action=stat-html>目的変数の形式<br>\n数値<input type=radio name=yk value=reg checked><br>\n分類<input type=radio name=yk value=cla><br>\n<table border=1><tr>"
                page=page+"<input type=hidden name=stat-before-html_key value="+token+">"
                page=page+"<input type=hidden name=user_id value="+str(session["user_id"])+">\n"
                page=page+"<input type=hidden name=name value="+name+">"
                for i in range(len(col)):
                    if i==0:
                        page=page+"<td>"+html.escape(col[i])+"<br>目的変数<input type=radio name=y value="+html.escape(col[i])+" checked><br>カテゴリ<input type=checkbox name=cate value="+html.escape(col[i])+"></td>\n"
                    else:
                        page=page+"<td>"+html.escape(col[i])+"<br>目的変数<input type=radio name=y value="+html.escape(col[i])+"><br>カテゴリ<input type=checkbox name=cate value="+html.escape(col[i])+"></td>\n"
                page=page+"<input type=submit value=分析></tr>"
                for i in range(len(val)):
                    page=page+"<tr>"
                    for j in range(len(val[i])):
                        page=page+"<td>"+html.escape(str(val[i][j]))+"</td>"
                    page=page+"</tr>\n"
                page=page+"</table></form>"
                return page
            else:
                return "正規のアクセスをしてください"
        #セッションがない場合、「/login」にリダイレクト
        else:
            return redirect("/login")

#JSONでテーブルデータ表示    
@app.route("/stat-before-json",methods=["GET","POST"])
def stbfrj():
    if request.method=="GET":
        return "不正なアクセスです"
    elif request.method=="POST":
        f=request.files["stat"]
        name=f.filename
        f.save("static/stats_before/"+str(request.form["user_id"])+"/"+name)
        df=pd.read_csv("static/stats_before/"+str(request.form["user_id"])+"/"+name,encoding="shift-jis")
        col=df.columns
        val=df.values
        index=[]
        tmp={}
        tmp["name"]=name
        index.append(tmp)
        #index["col"]=str(col)
        for i in range(len(val)):
            tmp={}
            for j in range(len(val[i])):
                tmp[col[j]]=val[i][j]
            index.append(tmp)
        return jsonify(index)
        

#HTML版要因分析
@app.route("/stat-html",methods=["GET","POST"])
def statanshtml():
    if request.method=="GET":
        return "不正なアクセスです"
    elif request.method=="POST":
        #セッションがあれば通常サービス
        if "user_id" in session:
            if session["stat-before-html_key"]==request.form["stat-before-html_key"]:
                page="<title>分析結果</title><a href=logout align=right>ログアウト</a>\n<br><a href=analysis>送信画面に戻る</a><br>\n<a href=home>メニューに戻る</a><br>\n"
                name=request.form["name"]
                page=page+"<form method=POST action=stat-json>\n<input type=hidden name=name value="+name+">\n"
                page=page+"<input type=hidden name=user_id value="+str(session["user_id"])+">\n"
                df=pd.read_csv("static/stats_before/"+str(session["user_id"])+"/"+name,encoding="shift-jis")
                cate=request.form.getlist("cate")
                page=page+"<input type=hidden name=cate value="+str(cate).replace(" ", "")+">\n"
                if len(cate)!=0:#カテゴリ変数にダミー変数で数量化
                    try:
                        df=pd.get_dummies(df,columns=cate)
                        y_name=request.form.get("y")
                        page=page+"<input type=hidden name=y value="+html.escape(y_name)+">\n"
                        y=df[y_name].values
                        x_table=df.drop(y_name,axis=1)
                        x=x_table.values
                        x_name=x_table.columns
                        page=page+"<input type=hidden name=yk value="+request.form.get("yk")+">\n"
                        page=page+"JSON出力<br><input type=submit value=出力>\n"
                        #回帰
                        if request.form.get("yk")=="reg":
                            modelG=GBR(n_estimators=10)
                            modelG.fit(x,y)
                            imp=modelG.feature_importances_
                            out=[]
                            tmp=[]
                            page=page+"<table><tr><td>項目名</td><td>影響度(%)</td><td>相関係数</td></tr>"
                            for i in range(len(imp)):
                                tmp.append(x_name[i])
                                tmp.append(imp[i]*100)
                                tmp.append(np.corrcoef(x[:,i],y)[1][0])
                                out.append(tmp)
                                tmp=[]
                            dout=pd.DataFrame(out)
                            dout.columns=["項目名","影響度","相関係数"]
                            dout=dout.sort_values("影響度",ascending=False)
                            dout.to_csv("static/stats_after/"+str(session["user_id"])+"/"+name,encoding="shift-jis",index=False)
                            for i in range(len(dout.values)):
                                page=page+"<tr>"
                                for j in range(len(dout.values[i])):
                                    page=page+"<td>"+html.escape(str(dout.values[i][j]))+"</td>"
                                page=page+"</tr>\n"
                            page=page+"</table>"
                            t=(session["user_id"],name,"stat-reg-html",str(datetime.datetime.today()))
                            cur.execute("INSERT INTO data (user_id,data_name,serv,date) VALUES (?,?,?,?)",t)
                            conn.commit()
                            return page
                        #分類
                        elif request.form.get("yk")=="cla":            
                            modelG=GBC(n_estimators=10)
                            modelG.fit(x,y)
                            imp=modelG.feature_importances_
                            out=[]
                            tmp=[]
                            page=page+"<a href=logout align=right>ログアウト</a><table><tr><td>項目名</td><td>影響度(%)</td></tr>"
                            for i in range(len(imp)):
                                tmp.append(x_name[i])
                                tmp.append(imp[i]*100)
                                out.append(tmp)
                                tmp=[]
                            dout=pd.DataFrame(out)
                            dout.columns=["項目名","影響度"]
                            dout=dout.sort_values("影響度",ascending=False)
                            dout.to_csv("static/stats_after/"+str(session["user_id"])+"/"+name,encoding="shift-jis",index=False)
                            for i in range(len(dout.values)):
                                page=page+"<tr>"
                                for j in range(len(dout.values[i])):
                                    page=page+"<td>"+html.escape(str(dout.values[i][j]))+"</td>"
                                page=page+"</tr>\n"
                            page=page+"</table>"
                            t=(session["user_id"],name,"stat-cla-html",str(datetime.datetime.today()))
                            cur.execute("INSERT INTO data (user_id,data_name,serv,date) VALUES (?,?,?,?)",t)
                            conn.commit()
                            return page
                    except:
                        return redirect("/analysis?miss=1")
            else:
                return "正規のアクセスをしてください"
        #セッションがない場合、「/login」にリダイレクト
        else:
            return redirect("/login")

#JSON版要因分析
@app.route("/stat-json",methods=["GET","POST"])
def statansjson():
    if request.method=="GET":
        return "不正なアクセスです"
    elif request.method=="POST":
        name=request.form["name"]
        df=pd.read_csv("static/stats_before/"+str(request.form["user_id"])+"/"+name,encoding="shift-jis")
        cate=request.form["cate"]
        cate=cate[1:-1]
        cate=cate.replace("'","")
        cate=cate.split(",")
        if str(cate)!="['']":#カテゴリ変数にダミー変数で数量化
            df=pd.get_dummies(df,columns=cate)
        y_name=request.form["y"]
        y=df[y_name].values
        x_table=df.drop(y_name,axis=1)
        x=x_table.values
        x_name=x_table.columns
        #回帰
        if request.form.get("yk")=="reg":
            modelG=GBR(n_estimators=10)
            modelG.fit(x,y)
            imp=modelG.feature_importances_
            out=[]
            tmp=[]
            for i in range(len(imp)):
                tmp.append(x_name[i])
                tmp.append(imp[i]*100)
                tmp.append(np.corrcoef(x[:,i],y)[1][0])
                out.append(tmp)
                tmp=[]
            out=sorted(out,key=lambda x: x[1],reverse=True)
            temp={}
            js=[]
            for i in range(len(out)):
                temp["col"]=out[i][0]
                temp["imp"]=out[i][1]
                temp["cor"]=out[i][2]
                js.append(temp)
                temp={}
            t=(int(request.form["user_id"]),name,"stat-reg-json",str(datetime.datetime.today()))
            #print(int(request.form["user_id"]))
            #print(name)
            #print(str(datetime.datetime.today()))
            try:
                cur.execute("INSERT INTO data (user_id,data_name,serv,date) VALUES (?,?,?,?)",t)
                conn.commit()
                print("DB commited")
            except:
                _=1
            return jsonify(js)
        #分類
        elif request.form.get("yk")=="cla":
            modelG=GBC(n_estimators=10)
            modelG.fit(x,y)
            imp=modelG.feature_importances_
            out=[]
            tmp=[]
            for i in range(len(imp)):
                tmp.append(x_name[i])
                tmp.append(imp[i]*100)
                out.append(tmp)
                tmp=[]
            out=sorted(out,key=lambda x: x[1],reverse=True)
            temp={}
            js=[]
            for i in range(len(out)):
                temp["col"]=out[i][0]
                temp["imp"]=out[i][1]
                js.append(temp)
                temp={}
            t=(int(request.form["user_id"]),name,"stat-cla-json",str(datetime.datetime.today()))
            #print(int(request.form["user_id"]))
            #print(name)
            #print(str(datetime.datetime.today()))
            try:
                cur.execute("INSERT INTO data (user_id,data_name,serv,date) VALUES (?,?,?,?)",t)
                conn.commit()
                print("DB commited")
            except:
                _=1
            return jsonify(js)
        

#何もしていない場合ログイン画面に遷移
@app.route("/")
def start():
    return redirect("/login")

#ログアウト画面・セッションを無くす
@app.route("/logout")
def end():
    session.pop("user_id",None)
    return "ログアウトしました<br><br><a href=login>ログイン画面へ</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0")