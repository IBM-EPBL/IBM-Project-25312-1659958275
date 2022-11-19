from flask import Flask, render_template, request, redirect, session 
import ibm_db
import re

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=lfx34122;PWD=jmQDS9wCaxqRIlQd",'','')
    
app = Flask(__name__)
app.secret_key = 'a'


#HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/")
def add():
    return render_template("home.html")

#SIGN--UP--OR--REGISTER


@app.route("/signup")
def signup():
    return render_template("signup.html")



@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        sql = "SELECT * FROM USERS WHERE USERNAME=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_assoc(stmt)
        if acc:
            msg = "Account already exists !!"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',email):
            msg = "Invalid Email address"
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg = "Name must contain only characters and numbers !!"
        else:
            sql = "INSERT INTO USERS VALUES (?,?,?)"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,username)
            ibm_db.bind_param(stmt,2,email)
            ibm_db.bind_param(stmt,3,password)
            ibm_db.execute(stmt)
            msg = "Successgully registered !!Login to continue"
            return render_template('login.html', msg = msg)
    elif request.method == 'POST':
        msg = "Please fill out the form !"
    return render_template('register.html', msg = msg)

 #LOGIN--PAGE
    
@app.route("/signin")
def signin():
    return render_template("login.html")
        
@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
   
  
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        
        sql = "SELECT * FROM USERS WHERE EMAIL=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_assoc(stmt)
        if acc:
            session['loggedin'] = True
            session['id'] = acc['USERNAME']
            userid = acc['USERNAME']
            session['username'] = acc['USERNAME']
            msg = acc['USERNAME']
            
            return render_template('homepage.html', msg = msg)
        else:
            msg = "Incorrect username/password!!"
    return render_template('login.html', msg = msg) 

#ADDING----DATA
@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    
    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']
    sql = "INSERT INTO EXPENSES VALUES (?,?,?,?,?,?)"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['id'])
    ibm_db.bind_param(stmt,2,date)
    ibm_db.bind_param(stmt,3,expensename)
    ibm_db.bind_param(stmt,4,amount)
    ibm_db.bind_param(stmt,5,paymode)
    ibm_db.bind_param(stmt,6,category)
    ibm_db.execute(stmt)
    
    return redirect("/display")
#DISPLAY---graph 
@app.route("/display")
def display():
    sql = "SELECT * FROM EXPENSES WHERE ID=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['id'])
    ibm_db.execute(stmt)
    
    acc = ibm_db.fetch_assoc(stmt)
    expense = []
    while acc != False:
       expense.append(acc)
       acc = ibm_db.fetch_assoc(stmt)
    return render_template('display.html' ,expense = expense)                       
          
 #limit
@app.route("/limit" )
def limit():
       return redirect('/limitn')

@app.route("/limitnum" , methods = ['POST' ])
def limitnum():
     if request.method == "POST":
         number= request.form['number']
         sql1 = "SELECT * FROM LIMITS WHERE ID=?"
         stmt = ibm_db.prepare(conn,sql1)
         ibm_db.bind_param(stmt,1,session['id'])
         ibm_db.execute(stmt)
         acc = ibm_db.fetch_assoc(stmt)
         if(acc):
             sql = "update limits set limit=? where ID=?"
             stmt = ibm_db.prepare(conn,sql)
             ibm_db.bind_param(stmt,1,number)
             ibm_db.bind_param(stmt,2,session['id'])
             ibm_db.execute(stmt)
         else:
             sql = "INSERT INTO LIMITS VALUES (?,?)"
             stmt = ibm_db.prepare(conn,sql)
             ibm_db.bind_param(stmt,1,session['id'])
             ibm_db.bind_param(stmt,2,number)
             ibm_db.execute(stmt)
         return redirect('/limitn')
     
         
@app.route("/limitn") 
def limitn():
    sql = "SELECT * FROM LIMITS WHERE ID=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['id'])
    ibm_db.execute(stmt)
    
    acc = ibm_db.fetch_assoc(stmt)
        
    return render_template("limit.html" , y= acc)

#REPORT

@app.route("/today")
def today():
      sql = "SELECT * FROM EXPENSES WHERE ID=? and DATE(date) = DATE(NOW())"
      stmt = ibm_db.prepare(conn,sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      
      acc = ibm_db.fetch_assoc(stmt)
      expense = []
      while acc != False:
         expense.append(acc)
         acc = ibm_db.fetch_assoc(stmt)
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
     
      for x in expense:
          total += x['AMOUNT']
          if x['CATEGORY'] == "food":
              t_food += x['AMOUNT']
            
          elif x['CATEGORY'] == "entertainment":
              t_entertainment  += x['AMOUNT']
        
          elif x['CATEGORY'] == "business":
              t_business  += x['AMOUNT']
          elif x['CATEGORY'] == "rent":
              t_rent  += x['AMOUNT']
           
          elif x['CATEGORY'] == "EMI":
              t_EMI  += x['AMOUNT']
         
          elif x['CATEGORY'] == "other":
              t_other  += x['AMOUNT']
      sql = "SELECT * FROM LIMITS WHERE ID=?"
      stmt = ibm_db.prepare(conn,sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      acc = ibm_db.fetch_assoc(stmt)
      s = ""
      if acc['LIMIT'] <= total:
          s = "YOU WERE EXCEEDED YOUR CURRENT EXPENSE LIMIT"
        
      return render_template("today.html", expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other , alert = s)
     
@app.route("/month")
def month():
      sql = "SELECT * FROM EXPENSES Where ID=? AND MONTH(DATE(date))= MONTH(now())"
      stmt = ibm_db.prepare(conn,sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      
      acc = ibm_db.fetch_assoc(stmt)
      expense = []
      while acc != False:
         expense.append(acc)
         acc = ibm_db.fetch_assoc(stmt)
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
     
      for x in expense:
          total += x['AMOUNT']
          if x['CATEGORY'] == "food":
              t_food += x['AMOUNT']
            
          elif x['CATEGORY'] == "entertainment":
              t_entertainment  += x['AMOUNT']
        
          elif x['CATEGORY'] == "business":
              t_business  += x['AMOUNT']
          elif x['CATEGORY'] == "rent":
              t_rent  += x['AMOUNT']
           
          elif x['CATEGORY'] == "EMI":
              t_EMI  += x['AMOUNT']
         
          elif x['CATEGORY'] == "other":
              t_other  += x['AMOUNT']
      return render_template("today.html", expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )     
@app.route("/year")
def year():
      sql = "SELECT * FROM EXPENSES Where ID=? AND YEAR(DATE(date))= YEAR(now())"
      stmt = ibm_db.prepare(conn,sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      
      acc = ibm_db.fetch_assoc(stmt)
      expense = []
      while acc != False:
         expense.append(acc)
         acc = ibm_db.fetch_assoc(stmt)
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
     
      for x in expense:
          total += x['AMOUNT']
          if x['CATEGORY'] == "food":
              t_food += x['AMOUNT']
            
          elif x['CATEGORY'] == "entertainment":
              t_entertainment  += x['AMOUNT']
        
          elif x['CATEGORY'] == "business":
              t_business  += x['AMOUNT']
          elif x['CATEGORY'] == "rent":
              t_rent  += x['AMOUNT']
           
          elif x['CATEGORY'] == "EMI":
              t_EMI  += x['AMOUNT']
         
          elif x['CATEGORY'] == "other":
              t_other  += x['AMOUNT']
      return render_template("today.html", expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

#log-out

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')

             

if __name__ == "__main__":
    app.run()