from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db

app = Flask(__name__)
app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb; HOSTNAME=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud; PORT=30426; SECURITY=SSL; SSLServerCertificate=DigiCertGlobalRootCA.crt; UID=rmy90481;PWD=qrJOWspW6naGUoOF",'','')

if(conn):
    print("CONNECTED SUCCESSFULLY")
    print("Connection : "+str(conn))

    sql="SELECT * FROM USER WHERE rollno=2019115110"
    #email="sudhirkumarsaminathan13@gmail.com"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)
    acc = ibm_db.fetch_assoc(stmt)
    if acc:
        print(acc)

if __name__ =='__':
    app.run()