import sqlite3 as sql
from werkzeug.security import generate_password_hash as gph
from werkzeug.security import check_password_hash as cph
import datetime

dbname="test.db"
conn=sql.connect(dbname)
cur=conn.cursor()
#com="DROP TABLE data"
#cur.execute(com)
#com="CREATE TABLE users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, user_name VARCHAR(32) NOT NULL, pass VAARCHAR(32) NOT NULL, date VARCHAR(32) NOT NULL)"
#com="CREATE TABLE data (data_id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INT, data_name VARCHAR(32), serv VAARCHAR(32) NOT NULL, date VARCHAR(32) NOT NULL)"
#cur.execute(com)
#com="INSERT INTO data (data_id,user_id,serv,date) VALUES (1,1,'telling','"+str(datetime.datetime.today())[0:19]+"')"
#print(str(datetime.datetime.today())[0:19])

#com="INSERT INTO users (user_name,pass,date) values ('MAHU','"+gph("aaaaaaaa")+"','"+str(datetime.datetime.today())[0:18]+"')"
#print(gph("aaaaaaaa"))
#com="DELETE FROM users where user_id==2"
#cur.execute(com)
com="SELECT * FROM users"# WHERE user_name='decarch19'"
#print(request.form["name"])
#cur.execute(com)
cur.execute("SELECT * FROM data")
res=[]
for row in cur:
    res.append(row[0])
    print(row)
print(res[0])
print(len(res))
#print(cph(row[1],"aaaaaaaa"))
conn.commit()
#conn.close()  
"""
com="select * from data"
cur.execute(com)
for row in cur:
    print(row)

conn.close()
"""
#com="CREATE TABLE users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, user_name VARCHAR(32) NOT NULL, pass VAARCHAR(32) NOT NULL, date DATE NOT NULL)"
