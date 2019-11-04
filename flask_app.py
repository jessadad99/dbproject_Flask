from flask import Flask, render_template, redirect, url_for, request, make_response, flash, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta
from passlib.hash import sha256_crypt
from base64 import b64encode
import datetime
import secrets
import pymysql
import threading
import schedule
import time

class SQL():
    def __init__(self):
        self.connections = pymysql.connect(host='us-cdbr-iron-east-05.cleardb.net',
                                           user='b2010704c8097f',
                                           password='15c8326c',
                                           db='heroku_067ee230eac21e3',
                                           charset='utf8mb4',
                                           cursorclass=pymysql.cursors.DictCursor)
  
    def regUser(self, infoList):
        with self.connections.cursor() as cur:
            sqlQuery = 'CALL AddUser(%s,%s,%s,%s,%s,%s)'
            cur.execute(sqlQuery,(infoList[0],infoList[1],infoList[2],infoList[3],infoList[4],infoList[5],))
        self.connections.commit()
        print('added')

    def loginUser(self, email):
        password = {'password':'','isconfirm':0}

        with self.connections.cursor() as cur:
            sqlQuery = "SELECT password, isconfirm FROM accountdata WHERE email=%s"
            cur.execute(sqlQuery, (email,)) 
            password = cur.fetchone()
        self.connections.commit()

        return password

    def delUser(self, email):
        with self.connections.cursor() as cur:
            cur.execute('CALL DelUser("{0}")'.format(email))
        self.connections.commit()

    def checkregisted(self, email):
        with self.connections.cursor() as cur:
            cur.execute('SELECT COUNT(email) FROM accountdata WHERE email="{0}"'.format(email))
            count = cur.fetchone()
            return count['COUNT(email)']

    def verifyMail(self, email):
        with self.connections.cursor() as cur:
            cur.execute('CALL Confirmed("{0}")'.format(email))
        self.connections.commit()

    def addToy(self, Tinfo):
        with self.connections.cursor() as cur:
            sqlQuery = "CALL AddToy(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sqlQuery, (Tinfo[0],Tinfo[1],Tinfo[2],Tinfo[3],Tinfo[4],Tinfo[5],Tinfo[6],Tinfo[7],Tinfo[8],Tinfo[9],)) 
        self.connections.commit()

    def getToy(self, search):
        search = '%{0}%'.format(search)
        with self.connections.cursor() as cur:
            sqlQuery = "SELECT toydata.*, toyimage.image FROM toydata INNER JOIN toyimage WHERE toydata.tid LIKE %s or toydata.name LIKE %s or toydata.`from` LIKE %s"
            cur.execute(sqlQuery, (search, search, search,))
            toylist = cur.fetchall()
        self.connections.commit()
        return toylist

    def updateToy(self, Tinfo):
        with self.connections.cursor() as cur:
            sqlQuery = "CALL UpdateToy(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sqlQuery, (Tinfo[0],Tinfo[1],Tinfo[2],Tinfo[3],Tinfo[4],Tinfo[5],Tinfo[6],Tinfo[7],Tinfo[8],Tinfo[9],)) 
        self.connections.commit()

    def delToy(self, tid):
        with self.connections.cursor() as cur:
            sqlQuery = "CALL DelToy(%s)"
            cur.execute(sqlQuery, (tid,)) 
        self.connections.commit()

    def buyToy(self, email, tid, amount, price):
        with self.connections.cursor() as cur:
            sqlQuery = "CALL BuyToy(%s,%s,%s,%s)"
            cur.execute(sqlQuery, (email,tid,amount,price,)) 
        self.connections.commit()

    def getHistory(self, email):
        with self.connections.cursor() as cur:
            sqlQuery = "SELECT bh.bid, buydate, td.`name`, bh.amount, bh.price\
                        FROM accountdata, toydata AS td, buyhistory AS bh\
                        WHERE (SELECT uid FROM accountdata WHERE email = %s) = bh.uid"
            cur.execute(sqlQuery, (email,))
            historylist = cur.fetchall()
        self.connections.commit()
        return historylist

    def getUserDetail(self, email):
        with self.connections.cursor() as cur:
            sqlQuery = "SELECT ad.email, ud.`name`, ud.surname, ud.address, ud.tel\
                        FROM accountdata AS ad, userdata AS ud\
                        WHERE ad.email = %s"
            cur.execute(sqlQuery, (email,))
            UserDetail = cur.fetchone()
        self.connections.commit()
        return UserDetail

    def updateUser(self, Uinfo):
        with self.connections.cursor() as cur:
            sqlQuery = "CALL UpdateUser(%s,%s,%s,%s,%s)"
            cur.execute(sqlQuery, (Uinfo[0],Uinfo[1],Uinfo[2],Uinfo[3],Uinfo[4],)) 
        self.connections.commit()

    def reConnect(self):
        self.connections.close()
        self.connections = pymysql.connect(host='us-cdbr-iron-east-05.cleardb.net',
                                           user='b2010704c8097f',
                                           password='15c8326c',
                                           db='heroku_067ee230eac21e3',
                                           charset='utf8mb4',
                                           cursorclass=pymysql.cursors.DictCursor)

class Functions():
    def __init__(self):
        self.passSalt = 'this is pass salt'
        self.mySQL = SQL()

    def regUser(self, infoList):
        # mySQL = SQL()
        self.reConnect()
        pwnPasswd = sha256_crypt.hash(infoList[1]+self.passSalt)
        for i in range(len(infoList)):
            if infoList[i] == '':
                print('has space')
                return 0
        if self.mySQL.checkregisted(infoList[0]) == 0:
            infoList[1] = pwnPasswd
            self.mySQL.regUser(infoList)
            return 1
        print('other')
        return 0

    def loginUser(self, infoList):
        # mySQL = SQL()
        self.reConnect()
        for i in range(len(infoList)):
            if infoList[i] == '':
                return 2,0
        pwnPass = self.mySQL.loginUser(infoList[0])
        try:
            if sha256_crypt.verify(infoList[1]+self.passSalt, pwnPass['password']):
                return pwnPass['isconfirm'], pwnPass['password']
        except Exception:
            return 2, 0

    def verifyMail(self, email):
        # mySQL = SQL()
        self.reConnect()
        self.mySQL.verifyMail(email)
        return 1

    def addToy(self, Tinfo):
        # mySQL = SQL()
        self.reConnect()
        self.mySQL.addToy(Tinfo)
        return 1

    def getToy(self, search):
        if search != '':
            self.reConnect()
        # mySQL = SQL()
        rawList = self.mySQL.getToy(search)
        outList = {}
        for i in range(len(rawList)):
            rawList[i]['image'] = b64encode(rawList[i]['image']).decode('utf-8')
            outList[str(rawList[i]['tid'])] = rawList[i]
        return outList

    def updateToy(self, Tinfo):
        # mySQL = SQL()
        self.reConnect()
        self.mySQL.updateToy(Tinfo)
        return 1

    def delToy(self, tid):
        # mySQL = SQL()
        self.reConnect()
        self.mySQL.delToy(tid)
        return 1

    def buyToy(self,email,tid,amount, price):
        self.reConnect()
        self.mySQL.buyToy(email, tid, amount, price)
        return 1

    def getHistory(self, email):
        self.reConnect()
        rawList = self.mySQL.getHistory(email)
        outList = {}
        for i in range(len(rawList)):
            rawList[i]['buydate'] = rawList[i]['buydate'].strftime('%d/%m/%Y')
            outList[str(rawList[i]['bid'])] = rawList[i]
        return outList

    def getUserDetail(self, email):
        self.reConnect()
        rawList = self.mySQL.getUserDetail(email)
        return rawList

    def updateUser(self, Uinfo):
        self.reConnect()
        self.mySQL.updateUser(Uinfo)
        return 1

    def reConnect(self):
        self.mySQL.reConnect()

    def runSchedule(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

def startApp():
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg')
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
    mail = Mail(app)

    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    Func = Functions()
    schedule.every().minute.do(Func.reConnect)
    
    sch = threading.Thread(target=Func.runSchedule)
    sch.start()

    @app.route('/')
    def index():
        return redirect('/home')
    @app.route('/home')
    def home():
        if request.method == 'GET':
            try:
                message = session['message']
                whatshow = session['whatshow']
                session.clear()
            except Exception:
                message = '0'
                whatshow = '0'
            try:
                userdetail = session['userdetail']
            except Exception:
                userdetail = ['0',0]
            search = request.args.get('search', default='', type=str)
            toyList = Func.getToy(search)
            return render_template('index.html', title='Home', message = message, whatshow = whatshow, userdetail = userdetail, ToyList = toyList)

    @app.route('/register', methods = ['POST'])
    def register():
        if request.method == 'POST':
            session.clear()
            if (request.form['regpass1'] == request.form['regpass2']):
                infoList = []
                infoList.append(request.form['regemail'])
                infoList.append(request.form['regpass1'])
                infoList.append(request.form['regfname'])
                infoList.append(request.form['regsname'])
                infoList.append(request.form['regaddress'])
                infoList.append(request.form['regtel'])
                for i in range(len(infoList)):
                    if infoList[i] == '':
                        session['message'] = ['fail']
                        session['whatshow'] = 'reg'
                        return redirect('/home')
                if Func.regUser(infoList) == 0:
                    session['message'] = 'regfail'
                    session['whatshow'] = 'reg'
                    return redirect('/home')

                verifyMail(infoList[0])
                return redirect('/home')

    @app.route('/login', methods = ['POST'])
    def login():
        if request.method == 'POST':
            detail = []
            detail.append(request.form['logemail'])
            detail.append(request.form['logpass'])
            if detail[0] == 'ad@min.com' and detail[1] == 'admin':
                session['userdetail'] = [detail[0],1]
                return redirect('/stock')
            result = Func.loginUser(detail)
            if result[0] == 0:
                session['userdetail'] = [detail[0],0]
                return redirect('/verify')
            elif result[0] == 1:
                session['userdetail'] = [detail[0],1]
                return redirect('/home')
            else:
                session['message'] = 'logfail'
                session['whatshow'] = 'login'
                return redirect('/home')
        return 'FAILED'

    @app.route('/verify', methods = ['GET','POST'])
    def verifyPage():
        try:
            email = session['userdetail'][0]
        except Exception:
            return redirect('/home', code=302)
        if request.method == 'GET':
            return render_template('verify.html', verify = 'no', email = email, title = 'verify')

        verifyMail(email)

        return render_template('verify.html', verify='sent', title = 'verify')

    @app.route('/verify/<token>', methods = ['GET','POST'])
    def verifyToken(token):
        try:
            email = s.loads(token, salt='email-confirm', max_age=60)
        except Exception:
            return render_template('verify.html', verify='invalid', title = 'verify')
        
        Func.verifyMail(email)
        return render_template('verify.html', verify='yes', title = 'verify')

    @app.route('/logout', methods = ['GET'])
    def logout():
        if request.method == 'GET':
            session.clear()
            return redirect('/home')

    @app.route('/product/<tid>', methods= ['GET', 'POST'])
    def product(tid):
        toyList = Func.getToy(tid)
        try:
            userdetail = session['userdetail']
        except Exception:
            userdetail = ['0',0]
        if request.method == 'GET':
            try:
                isbuy = session['isbuy']
                Func.reConnect()
            except:
                isbuy = [False,0, 0]
            return render_template('product.html', isbuy=isbuy[0], amount=isbuy[1], price=isbuy[2], ToyList = toyList[tid], title = toyList[tid]['name'], userdetail = userdetail)

        # if request.method == 'POST':
        if userdetail[0] == '0' and userdetail[1] == 0:
            session['message'] = ''
            session['whatshow'] = 'login'
            return redirect('/home',code=302)
        else:
            amount = int(request.form['buyamount'])
            if toyList[tid]['amount'] < amount:
                return render_template('product.html', amounterror=True, ToyList = toyList[tid], title = toyList[tid]['name'], userdetail = userdetail)
            else:
                price = float(toyList[tid]['price'])*amount
                Func.buyToy(userdetail[0], tid, amount, price)
                session['isbuy'] = [True, amount, price]
                return redirect('/product/{0}'.format(tid),code=302)

        return redirect('/home')
            
    @app.route('/profile', methods = ['GET', 'POST'])
    def profile():
        try:
            userdetail = session['userdetail']
        except Exception:
            userdetail = ['0',0]
        if request.method == 'GET':
            if userdetail[0] != '0' and userdetail[1] != 0:
                buyhList = Func.getHistory(userdetail[0])
                userprofile = Func.getUserDetail(userdetail[0])
                print(userprofile)
                return render_template('profile.html', buylist = buyhList, title = '{0} {1}'.format(userprofile['name'], userprofile['surname']), userprofile = userprofile , userdetail = userdetail)
        if userdetail[0] != '0' and userdetail[1] != 0:
            datalist = []
            datalist.append(userdetail[0])
            datalist.append(request.form['editName'])
            datalist.append(request.form['editSurname'])
            datalist.append(request.form['editAddress'])
            datalist.append(request.form['editTel'])
            Func.updateUser(datalist)

            return redirect('/profile', code=302)

        return redirect('/')



    # ADMIN
    @app.route('/stock', methods = ['GET', 'POST'])
    def stock():
        try:
            if request.method == 'GET' and session['userdetail'][0] == 'ad@min.com':
                search = request.args.get('search', default='', type=str)
                toyList = Func.getToy(search)
                userdetail = ['ad@min.com',1]
                return render_template('stock.html', ToyList=toyList, title='admin', userdetail=userdetail)
        except Exception:
            return redirect('/home')

    @app.route('/stock/add', methods = ['POST'])
    def addstock():
        if session['userdetail'][0] == 'ad@min.com':
            Tinfo = []
            Tinfo.append(request.form['addName'])
            Tinfo.append(request.form['addSize'])
            Tinfo.append(request.form['addMaterial'])
            Tinfo.append(request.form['addBrand'])
            Tinfo.append(request.form['addSubject'])
            Tinfo.append(request.form['addCollection'])
            Tinfo.append(request.form['addPrice'])
            Tinfo.append(request.form['addAmount'])
            img = request.files['imgFile']
            imgread = img.read()
            Tinfo.append(imgread)
            Tinfo.append(request.form['addDetail'])
            Func.addToy(Tinfo)
            return redirect('/stock')
        return redirect('/')

    @app.route('/stock/update/<tid>', methods = ['POST'])
    def updatestock(tid):
        if session['userdetail'][0] == 'ad@min.com':
            Tinfo = []
            Tinfo.append(tid)
            Tinfo.append(request.form['editName'])
            Tinfo.append(request.form['editSize'])
            Tinfo.append(request.form['editMaterial'])
            Tinfo.append(request.form['editBrand'])
            Tinfo.append(request.form['editSubject'])
            Tinfo.append(request.form['editCollection'])
            Tinfo.append(request.form['editPrice'])
            Tinfo.append(request.form['editAmount'])
            Tinfo.append(request.form['editDetail'])
            Func.updateToy(Tinfo)
            return redirect('/stock')
        return redirect('/')

    @app.route('/stock/del/<tid>')
    def delstock(tid):
        if session['userdetail'][0] == 'ad@min.com':
            Func.delToy(tid)
            return redirect('/stock')
        return redirect('/')

    def verifyMail(email):
        token = s.dumps(email, salt='email-confirm')

        link = url_for('verifyToken', token=token, _external=True)

        sent = threading.Thread(target=sendVerify, args=(email, link,))
        sent.start()
        return 1

    def sendVerify(email, link):
        msg = Message('Confirm Email', sender=('Carstore Service', "service@dbproject_carstore.com"), recipients=[email])

        assert msg.sender == "Carstore Service <service@dbproject_carstore.com>"

        msg.body = 'Confirm Your Email'

        msg.html = '<form action="{0}"><input type="submit" value="Verify" formtarget="_blank"></form>'.format(link)

        with app.app_context():
            mail.send(msg)
            print("Sent")
        return True

    return app

app = startApp()

if __name__ == "__main__":
    app.run(debug=True)
