# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from flask import *
import os
from mail import *
import mysql.connector
import os
from datetime import timedelta
from random  import *
import smtplib
#import pyrebase

app=Flask(__name__)
app.secret_key=os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)
global COOKIE_TIME_OUT
#COOKIE_TIME_OUT = 60*60*24*7 #7 days
COOKIE_TIME_OUT = 60*60 #60 minutes


firstname=None
lastname=None
email=None
password=None


app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'dailytv.com25@gmail.com'
app.config['MAIL_PASSWORD'] = 'test@7820'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# mail = mail(app)
otp = randint(0, 0)


conn=mysql.connector.connect(host="localhost",username="root",password="root",database="billbook")
cursor=conn.cursor()
user_email=None
pwd=None
muser=None





@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login_validation',methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')
    # print(email)
    cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email,password))
    user=cursor.fetchall()
    print (user)
    if len(user)>0:
        session['key']=user[0][0]
        global user_email
        global pwd
        global muser
        muser=user
        user_email = user[0][0]
        pwd = user[0][1]
        print(user[0][2])
        print(type(email))
        print(type(pwd))
        print(email)
        print(pwd)
        return redirect('/index')
    else:
        return redirect('/')

@app.route('/index')
def index():
    if 'key' in session:
        cursor.execute(""" SELECT * FROM `all_client` WHERE `user_email`='{}' """.format(user_email))
        allclient = cursor.fetchall()
        total_client=len(allclient)

        cursor.execute(""" SELECT * FROM `all_project` WHERE `user_email`='{}' """.format(user_email))
        allproject = cursor.fetchall()
        total_project=len(allproject)

        cursor.execute(""" SELECT * FROM `project` WHERE `user_email`='{}' """.format(user_email))
        project = cursor.fetchall()
        total_active_project=len(project)

        cursor.execute(""" SELECT `client_name` FROM `client` WHERE `user_email`='{}' """.format(user_email))
        active_client = cursor.fetchall()
        total_active_client=len(active_client)

        cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
        client_name = cursor.fetchall()

        
        cursor.execute("SELECT * FROM `project` WHERE `user_email`='{}'".format(user_email))
        project_name = cursor.fetchall()
        print(project_name)

        cursor.execute("SELECT SUM(`estimated_amount`) FROM `project` WHERE `user_email`='{}'".format(user_email))
        total_active_amount=cursor.fetchall()[0][0]

        # total_active_amount=0

        cursor.execute("SELECT SUM(`estimated_amount`) FROM `all_project` WHERE `user_email`='{}'".format(user_email))
        total_amount=cursor.fetchall()[0][0]
        # total_amount=0
        # for i in project_name[1]:
        #     total_amount=total_amount+int(i)
        total_completed_amount=total_amount-total_active_amount
        print(total_amount)
        return render_template('index.html',user=muser,total_client=total_client,total_project=total_project,total_active_project=total_active_project,total_active_client=total_active_client,client_name=client_name,project_name=project_name,total_active_amount=total_active_amount,total_amount=total_amount,total_completed_amount=total_completed_amount)
    else:
         return redirect('/')

@app.route('/register')
def register():

    global s
    s= smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("dailytv.com25@gmail.com", "uqimhpxxkicbbtzi")

    return render_template('register.html')  

@app.route('/varify',methods=['POST'])
def varify():

    global firstname
    global lastname
    global email
    global password
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    password = request.form.get('password')
    message = "dear {} {} your otp for email verification is  ' {} '".format(firstname,lastname,str(otp))
    s.sendmail("dailytv.com25@gmail.com", [email], message)
    s.quit()
    print(email)
    print(otp)
    print(message)
    print(firstname)
    print(lastname)

    return render_template('varify.html') 

#this is for validation of otp
@app.route('/validate', methods=["POST"])
def validate():
    user_otp = request.form['otp']

    if otp == int(user_otp):

        cursor.execute("""INSERT INTO `user` (`f_name`,`l_name`,`email`,`password`) VALUES ('{}','{}','{}','{}')""".format(firstname, lastname, email, password))
        conn.commit()
        return redirect('/')
    else:
        return redirect('/register')

@app.route('/profile')
def profile():
    return render_template('profile.html',user=muser)



@app.route('/invoice')
def invoice():
    cursor.execute(""" SELECT * FROM `user` WHERE `email`='{}' AND `password`='{}'""".format(user_email, pwd))
    user = cursor.fetchall()
    if len(user) > 0:
        cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
        client_name = cursor.fetchall()
        return render_template('invoice.html', client_name=client_name,user=muser)
    else:
        return "PLease check your email/Password"

@app.route('/invoicedataclient',methods=['POST'])
def invoicedataclient():
    client=request.form.get('client_name')
    cursor.execute("SELECT * FROM `project` WHERE `client_name`='{}' AND `user_email`='{}'".format(client,user_email))
    project=cursor.fetchall()
    return render_template('invoice.html',project=project,client=client,user=muser)
    
@app.route('/invoicedata',methods=['POST'])
def invoicedata():
    detail=request.form.getlist('detail')
    data=[]

    sum=0
    for i in range(0, len(detail)):
        cursor.execute("SELECT * FROM `project` WHERE `detail`='{}'".format(detail[i]))
        eastimate=cursor.fetchall()
        print(eastimate)
        data.append(eastimate)
        data[i].append(i+1)
        print(data)
        sum=sum+eastimate[0][3]
    fees=float(request.form.get('fees'))
    fees=round(fees,2)
    workdone=float(request.form.get('workdone'))
    workdone=round(workdone,2)
    paid=float(request.form.get('paid'))
    paid=round(paid,2)
    amount= sum* fees* workdone/10000
    amount=round(amount,2)
    print(amount)
    total=amount-paid
    cgst=(total*0.09)
    cgst=round(cgst,2)
    sgst=(total*0.09)
    sgst=round(sgst,2)
    grand_total=total+cgst+sgst
    grand_total=round(grand_total,2)
    return render_template('bill.html',user=muser,data=data,sum=sum,fees=fees,workdone=workdone,paid=paid,amount=amount,total=total,cgst=cgst,sgst=sgst,grand_total=grand_total)

@app.route('/invoiceforapproval')
def invoiceforapproval():
    cursor.execute(""" SELECT * FROM `user` WHERE `email`='{}' AND `password`='{}'""".format(user_email, pwd))
    user = cursor.fetchall()
    if len(user) > 0:
        cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
        client_name = cursor.fetchall()
        return render_template('invoiceforapproval.html', client_name=client_name,user=muser)
    else:
        return "PLease check your email/Password"
    # return render_template('invoiceforapproval.html')
    
@app.route('/addclient')
def addclient():
    print(user_email)
    print(pwd)
    cursor.execute(""" SELECT * FROM `user` WHERE `email`='{}' AND `password`='{}'""".format(user_email, pwd))
    user = cursor.fetchall()
    if len(user) > 0:
        return render_template('addclient.html',user=muser)
    else:
        return "Error"

@app.route('/addclientdata',methods=['POST'])
def addclientdata():
    name=request.form.get('client_name')
    email=request.form.get('client_email')
    subject=request.form.get('subject')
    address=request.form.get('address')
    print("in side add client data")
    print(user_email)
    cursor.execute("""INSERT INTO `client` (`client_id`,`client_name`,`client_email`,`subject`,`address`,`user_email`) VALUES 
    (NULL,'{}','{}','{}','{}','{}') """.format(name,email,subject,address,user_email))
    conn.commit()
    cursor.execute("""INSERT INTO `all_client` (`client_id`,`client_name`,`client_email`,`subject`,`address`,`user_email`) VALUES 
    (NULL,'{}','{}','{}','{}','{}') """.format(name,email,subject,address,user_email))
    conn.commit()
    return render_template('addclient.html',user=muser)

@app.route('/clientlist')
def clientlist():
    # cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
    # client_name = cursor.fetchall()

    cursor.execute(""" SELECT * FROM `user` WHERE `email`='{}' AND `password`='{}'""".format(user_email, pwd))
    user = cursor.fetchall()
    if len(user) > 0:
        cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
        client_name = cursor.fetchall()
        return render_template('clientlist.html', client_name=client_name,user=muser)
    else:
        return "PLease check your email/Password"
    # return render_template('clientlist.html',client_name=client_name)

@app.route('/clientlistsort',methods=['POST'])
def clientlistsort():
    sortby=request.form.get('sortby')
    print(sortby)
    print(type(sortby))
    cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
    client_name = cursor.fetchall()

    if(sortby=="Client Name A to Z"):
        client_name.sort(key = lambda x: x[1])

    elif(sortby=="Client Name Z to A"):
        client_name.sort(key = lambda x: x[1] , reverse=True)

    return render_template('clientlist.html',client_name=client_name,user=muser)


@app.route('/removeclient')
def removeclient():
    cursor.execute(""" SELECT * FROM `user` WHERE `email`='{}' AND `password`='{}'""".format(user_email, pwd))
    user = cursor.fetchall()
    if len(user) > 0:
        cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
        client_name = cursor.fetchall()
        return render_template('removeclient.html', client_name=client_name,user=muser)
    else:
        return "PLease check your email/Password"


@app.route('/removeclientdata',methods=['POST'])
def removeclientdata():
    client=request.form.get('client_name')
    
    cursor.execute("""DELETE FROM `client` WHERE `client_name`='{}' AND `user_email`='{}'""".format(client,user_email))
    conn.commit()
    cursor.execute("""DELETE FROM `project` WHERE `client_name`='{}' AND `user_email`='{}'""".format(client,user_email))
    conn.commit()

    cursor.execute(""" SELECT * FROM `user` WHERE `email`='{}' AND `password`='{}'""".format(user_email, pwd))
    user = cursor.fetchall()
    if len(user) > 0:
        cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
        client_name = cursor.fetchall()
        return render_template('removeclient.html', client_name=client_name,user=muser)


@app.route('/addproject')
def addproject():
    cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
    client_name = cursor.fetchall()
    return render_template('addproject.html', client_name=client_name,user=muser)

@app.route('/addprojectdata',methods=['POST'])
def addprojectdata():
    #print("hello ")
    client=request.form.get('client_name')
    
    estimate_amount=request.form.get('estimated_amount')
    detail=request.form.get('detail')
    cursor.execute("""INSERT INTO `project` (`project_id`,`client_name`,`estimated_amount`,`detail`,`user_email`) VALUES 
     (NULL,'{}','{}','{}','{}') """.format(client,estimate_amount,detail,user_email))
    conn.commit()
    cursor.execute("""INSERT INTO `all_project` (`project_id`,`client_name`,`estimated_amount`,`detail`,`user_email`) VALUES 
     (NULL,'{}','{}','{}','{}') """.format(client,estimate_amount,detail,user_email))
    conn.commit()
    cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
    client_name = cursor.fetchall()

    return render_template('addproject.html', client_name=client_name,user=muser)


@app.route('/projectlist')
def projectlist():
    # cursor.execute("SELECT * FROM `project` WHERE `user_email`='{}'".format(user_email))
    # project_name = cursor.fetchall()
    # print(project_name[0][3])

    cursor.execute(""" SELECT * FROM `user` WHERE `email`='{}' AND `password`='{}'""".format(user_email, pwd))
    user = cursor.fetchall()
    if len(user) > 0:
        cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
        client_name = cursor.fetchall()
        return render_template('projectlist.html', client_name=client_name,user=muser)
    else:
        return "PLease check your email/Password"
    # return render_template('projectlist.html',project_name=project_name)


@app.route('/projectlistsort',methods=['POST'])
def projectlistsort():
    sortby=request.form.get('sortby')
    print(sortby)
    print(type(sortby))
    cursor.execute("SELECT * FROM `project` WHERE `user_email`='{}'".format(user_email))
    project_name = cursor.fetchall()

    if(sortby=="Estimated Amount High to Low"):
        project_name.sort(key = lambda x: x[3] , reverse=True)

    
    elif(sortby=="Estimated Amount Low to High"):
        project_name.sort(key = lambda x: x[3])

    elif(sortby=="Client Name"):
        project_name.sort(key = lambda x: x[1])
    return render_template('projectlist.html',project_name=project_name,user=muser)
  
@app.route('/removeproject')
def removeproject():
    cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
    client_name = cursor.fetchall()
    cursor.execute("SELECT * FROM `project`")
    project_name=cursor.fetchall()
    return render_template('removeproject.html', client_name=client_name, project_name=project_name,user=muser)

   
@app.route('/removeprojectdataclient',methods=['POST'])
def removeprojectdataclient():
    client = request.form.get('client_name')
    cursor.execute("SELECT * FROM `project` WHERE `client_name`='{}' AND `user_email`='{}'".format(client,user_email))
    client_project=cursor.fetchall()

    return render_template('removeproject.html',client_project=client_project,client=client,user=muser)


@app.route('/removeprojectdata',methods=['POST'])
def removeprojectdata():

    project=request.form.get('project_name')
    cursor.execute("""DELETE FROM `project` WHERE `detail`='{}' AND `user_email`='{}'""".format(project,user_email))
    conn.commit()
    cursor.execute("SELECT * FROM `client` WHERE `user_email`='{}'".format(user_email))
    client_name = cursor.fetchall()
    cursor.execute("SELECT * FROM `project`  ")
    project_name = cursor.fetchall()
    return render_template('removeproject.html', client_name=client_name, project_name=project_name,user=muser)


@app.route('/login')
def login():
    return render_template('login.html')    





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
