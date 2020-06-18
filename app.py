from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import random, string, datetime
import MySQLdb
import os

app = Flask(__name__)
mail=Mail(app)

static = os.path.join(app.root_path, 'static')
os.makedirs(static, exist_ok=True)

app.secret_key = 'secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sabari@1'
app.config['MYSQL_DB'] = 'dbmslab'

mysql = MySQL(app)



################################################################################

###########################  USER ##############################################

################################################################################






@app.route('/',methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM accounts WHERE username = %s AND password = %s',(username,password))
        account = cur.fetchone()

        if account:

            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['email'] = account['email']
            session['password'] = account['password']
            
            return redirect(url_for('user_home'))
        
        else:
            flash('Incorrect username/password!')

    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)',(username, password, email,))
        mysql.connection.commit()
        flash('You have successfully registered!')
        
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/user_logout')
def user_logout():

    if session['loggedin']:

        flash('Logged Out Successfully!')

        session['loggedin'] = None
        session.pop('id', None)
        session.pop('username', None)
        session.pop('email',None)
        session.pop('password',None)

    else:
        flash('Login required!')

    return redirect(url_for('login'))

@app.route('/user_home', methods=['GET','POST'])
def user_home():

    if session['loggedin']:

        quotes = [ "'If people do not believe that mathematics is simple, it is only because they do not realize how complicated life is.' -- John Louis von Neumann ",
        "'Computer science is no more about computers than astronomy is about telescopes' --  Edsger Dijkstra ",
        "'To understand recursion you must first understand recursion..' -- Unknown",
        "'You look at things that are and ask, why? I dream of things that never were and ask, why not?' -- Unknown",
        "'Mathematics is the key and door to the sciences.' -- Galileo Galilei",
        "'Not everyone will understand your journey. Thats fine. Its not their journey to make sense of. Its yours.' -- Unknown",
        "'Be yourself; everyone else is already taken.' ― Oscar Wilde","“Two things are infinite: the universe and human stupidity; and I'm not sure about the universe.” ― Albert Einstein",
        "“Be who you are and say what you feel, because those who mind don't matter, and those who matter don't mind.” ― Bernard M. Baruch",
        "“You've gotta dance like there's nobody watching, Love like you'll never be hurt, Sing like there's nobody listening, And live like it's heaven on earth.” ― William W. Purkey" ]
        
        randomNumber = random.randint(0,len(quotes)-1)
        quote = quotes[randomNumber]

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            sort = request.form['sort_by']
            if sort == 'costlh':
                cur.execute('SELECT * FROM restaurants ORDER BY rest_cost')
            elif sort == 'costhl':
                cur.execute('SELECT * FROM restaurants ORDER BY rest_cost DESC')
            elif sort == 'veg':
                cur.execute('SELECT * FROM restaurants where rest_veg="Veg" order by rest_name')
            elif sort == 'non-veg':
                cur.execute('SELECT * FROM restaurants where rest_veg="Non-veg" order by rest_name')
            elif sort == 'vegan':
                cur.execute('SELECT * FROM restaurants where rest_veg="Vegan" order by rest_name')
            elif sort == 'drinks':
                cur.execute('SELECT * FROM restaurants where rest_drinks="Yes" order by rest_name')
            elif sort == 'no-drinks':
                cur.execute('SELECT * FROM restaurants where rest_drinks="No" order by rest_name')
            elif sort == 'weekends':
                cur.execute('SELECT * FROM restaurants where rest_days!="weekdays" and rest_days!="sunclosed" order by rest_name')
            elif sort == 'weekdays':
                cur.execute('SELECT * FROM restaurants where rest_days!="weekends" and rest_days!="monclosed" and rest_days!="thursclosed" order by rest_name')
        else:
            cur.execute('SELECT * FROM restaurants ORDER BY rest_id DESC')

        restaurants = cur.fetchall()

        return render_template('user_home.html', username=session['username'], quote=quote, restaurants=restaurants)

    return redirect(url_for('login'))


@app.route('/wishlist', methods=['GET','POST'])
def wishlist():

    if request.method == 'POST':
        rest_id = request.form['rest_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM restaurants WHERE rest_id = %s',rest_id)
        restaurant = cur.fetchone()

        try:
            review = request.form['review']
            cur.execute('INSERT INTO reviews values (NULL, %s, %s, %s, %s)',(session['username'], restaurant['rest_code'], review, datetime.datetime.now()))
            mysql.connection.commit()
        finally:
            cur.execute('SELECT * FROM reviews WHERE rest_code = %s ORDER BY id DESC',[restaurant['rest_code']])
            rev = cur.fetchall()

            return render_template('wishlist.html', restaurant=restaurant, rev=rev)

    return render_template('wishlist.html')


@app.route('/update_review', methods=['GET','POST'])
def update_review():

    if request.method == 'POST':
        rest_id = request.form['rest_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM restaurants WHERE rest_id = %s',rest_id)
        restaurant = cur.fetchone()

        rev_id = request.form['rev_id']
        cur.execute('SELECT * FROM reviews WHERE id = %s',[rev_id])
        review = cur.fetchone()
        old_rev = review['review']
        cur.execute('DELETE FROM reviews WHERE id=%s', [rev_id])
        mysql.connection.commit()

        cur.execute('SELECT * FROM reviews WHERE rest_code = %s ORDER BY id DESC',[restaurant['rest_code']])
        rev = cur.fetchall()

        return render_template('update_review.html', restaurant=restaurant, old_rev=old_rev, rev=rev)

    return 'Method Not Allowed.'

@app.route('/delete_review',methods=['GET','POST'])
def delete_review():
    if request.method == 'POST':
        rest_id = request.form['rest_id']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM restaurants WHERE rest_id = %s',rest_id)
        restaurant = cur.fetchone()

        rev_id = request.form['rev_id']
        cur.execute('DELETE FROM reviews WHERE id=%s', [rev_id])
        mysql.connection.commit()

        cur.execute('SELECT * FROM reviews WHERE rest_code = %s ORDER BY id DESC',[restaurant['rest_code']])
        rev = cur.fetchall()

        return render_template('update_review.html', restaurant=restaurant, rev=rev)

    return 'Method Not Allowed.'

@app.route('/profile')
def profile():

    if session['loggedin']:

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cur.fetchone()
        s = ''
        m = len(account['password'])
        for i in range(m):
            s += '*'

        return render_template('profile.html', account=account, s=s)

    return redirect(url_for('login'))

@app.route('/editprofile', methods=['GET','POST'])
def editprofile():

    if request.method == 'POST':
        
        id_data = session['id']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        session['username'] = username
        session['email'] = email
        session['password'] = password

        cur = mysql.connection.cursor()
        cur.execute('UPDATE accounts SET username=%s,email=%s,password=%s WHERE id=%s',(username,email,password,id_data))

        flash('Data Updated Successfully!')
        mysql.connection.commit()
        
        return redirect(url_for('profile'))

    return render_template('editprofile.html')

@app.route('/forgotpw', methods=['GET','POST'])
def forgotpw():

    if request.method == 'POST' and 'id' in session:

        username = request.form['username']
        email = request.form['email']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM accounts WHERE username = %s AND email = %s',(username,email))
        account = cur.fetchone()

        if account:

            letters = string.ascii_lowercase
            u=str(random.randint(10000000,99999999))
            letters += u
            new_pw = ''.join(random.choice(letters) for i in range(12))

            app.config['MAIL_SERVER']='smtp.gmail.com'
            app.config['MAIL_PORT'] = 465
            app.config['MAIL_USERNAME'] = 'devanshi1500@gmail.com'
            app.config['MAIL_PASSWORD'] = 'mercury9480'
            app.config['MAIL_USE_TLS'] = False
            app.config['MAIL_USE_SSL'] = True
            mail = Mail(app)

            msg = Message('New Password', sender = 'devanshi1500@gmail.com', recipients = [account['email']])
            msg.body = 'You new password: ' + new_pw + '. Please refrain from sharing this password with other people. Keeping it to yourself is in your benefit and best for your account data security.'
            mail.send(msg)

            cur.execute('UPDATE accounts SET password=%s WHERE id = %s',(new_pw, account['id']))
            mysql.connection.commit()
            cur.close()

            flash('Your new password has been sent to you on your email account.')

            return redirect(url_for('login'))
        
        else:
            flash('Incorrect username or email! Try again!')

    return render_template('forgotpw.html')

@app.route('/forgotopw', methods=['GET','POST'])
def forgotopw():

    if request.method == 'POST':

        ownername = request.form['ownername']
        owneremail = request.form['owneremail']
        rest_id = request.form['rest_id']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM owners WHERE ownername = %s AND owneremail = %s AND rest_id = %s',(ownername, owneremail, rest_id))
        account = cur.fetchone()

        if account:

            letters = string.ascii_lowercase
            u=str(random.randint(10000000,99999999))
            letters += u
            new_pw = ''.join(random.choice(letters) for i in range(12))

            app.config['MAIL_SERVER']='smtp.gmail.com'
            app.config['MAIL_PORT'] = 465
            app.config['MAIL_USERNAME'] = 'devanshi1500@gmail.com'
            app.config['MAIL_PASSWORD'] = 'mercury9480'
            app.config['MAIL_USE_TLS'] = False
            app.config['MAIL_USE_SSL'] = True
            mail = Mail(app)

            msg = Message('New Password', sender = 'devanshi1500@gmail.com', recipients = [account['owneremail']])
            msg.body = 'You new password: ' + new_pw + '\n Please refrain from sharing this password with other people. Keeping it to yourself is in your benefit and best for your account data security.'
            mail.send(msg)

            cur.execute('UPDATE owners SET passcode=%s WHERE rest_id = %s',(new_pw, account['rest_id']))
            mysql.connection.commit()
            cur.close()

            flash('Your new password has been sent to you on your email account.')

            return redirect(url_for('login'))
        
        else:
            flash('Incorrect username or email! Try again!')

    return render_template('forgotopw.html')





################################################################################

########################### OWNER ##############################################

################################################################################







@app.route('/owner_login',methods=['GET','POST'])
def owner_login():

    if request.method == 'POST':

        ownername = request.form['ownername']
        rest_id = request.form['rest_id']
        passcode = request.form['passcode']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM owners WHERE ownername = %s AND passcode = %s AND rest_id = %s',(ownername,passcode,rest_id))
        owner = cur.fetchone()

        if owner:

            session['loggedin'] = True
            session['ownerid'] = owner['ownerid']
            session['ownername'] = owner['ownername']
            session['owneremail'] = owner['owneremail']
            session['passcode'] = owner['passcode']
            session['rest_id'] = owner['rest_id']
            session['phone'] = owner['phone']
            
            return redirect(url_for('home'))
        
        else:
            flash('Incorrect Owner, Passcode or Restaurant ID!')

    return render_template('owner_login.html')

@app.route('/register_owner', methods=['GET','POST'])
def register_owner():

    if request.method == 'POST':

        ownername = request.form['ownername']
        passcode = request.form['passcode']
        owneremail = request.form['owneremail']
        phone = request.form['phone']
        rest_id = request.form['rest_id']

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO owners VALUES (NULL, %s, %s, %s, %s,%s)',(ownername, owneremail, phone, rest_id, passcode))
        cur.execute('INSERT INTO restinfo VALUES (NULL, %s, %s, "No")',(ownername, rest_id))
        mysql.connection.commit()
        flash('You have successfully registered!')
        
        return redirect(url_for('owner_login'))

    return render_template('register_owner.html')

@app.route('/logout')
def logout():

    if session['loggedin']:

        flash('Logged Out Successfully!')

        session['loggedin'] = None
        session.pop('ownerid', None)
        session.pop('ownername', None)
        session.pop('owneremail',None)
        session.pop('rest_id',None)
        session.pop('passcode',None)

    else:
        flash('Login required!')

    return redirect(url_for('owner_login'))

@app.route('/restinfo')
def restinfo():

    if session['loggedin']:

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if 'rest_id' in session:
            cur.execute('SELECT * FROM restaurants WHERE rest_code=%s',[session['rest_id']])
            restaurant = cur.fetchone() 

            if restaurant:
                return render_template('restinfo.html', restaurant=restaurant)
            else:
                return 'Nothing great to show!'
        else:
            return 'Nothing great to show'

    else:
        return 'No restaurant info'


@app.route('/home',methods=['GET','POST'])
def home():

    if 'rest_id' in session:

        if session['loggedin']:

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if request.method == 'POST':
                sort = request.form['sort_by']
                if sort == 'costlh':
                    cur.execute('SELECT * FROM restaurants ORDER BY rest_cost')
                elif sort == 'costhl':
                    cur.execute('SELECT * FROM restaurants ORDER BY rest_cost DESC')
                elif sort == 'veg':
                    cur.execute('SELECT * FROM restaurants where rest_veg="Veg" order by rest_name')
                elif sort == 'non-veg':
                    cur.execute('SELECT * FROM restaurants where rest_veg="Non-veg" order by rest_name')
                elif sort == 'vegan':
                    cur.execute('SELECT * FROM restaurants where rest_veg="Vegan" order by rest_name')
                elif sort == 'drinks':
                    cur.execute('SELECT * FROM restaurants where rest_drinks="Yes" order by rest_name')
                elif sort == 'no-drinks':
                    cur.execute('SELECT * FROM restaurants where rest_drinks="No" order by rest_name')
                elif sort == 'weekends':
                    cur.execute('SELECT * FROM restaurants where rest_days!="weekdays" and rest_days!="sunclosed" order by rest_name')
                elif sort == 'weekdays':
                    cur.execute('SELECT * FROM restaurants where rest_days!="weekends" and rest_days!="monclosed" and rest_days!="thursclosed" order by rest_name')
            else:
                cur.execute('SELECT * FROM restaurants ORDER BY rest_id DESC')
            restaurants = cur.fetchall()
            cur.execute('SELECT * FROM restaurants WHERE rest_code=%s',[session['rest_id']])
            rest_info = cur.fetchone()
            if rest_info:
                return render_template('home.html', restaurants=restaurants,rest_info=rest_info)
            else:
                return render_template('home.html', restaurants=restaurants)
    
    return redirect(url_for('owner_login'))


@app.route('/create', methods=['GET','POST'])
def create():

    if request.method == 'POST' and request.form.get('rest_name',False):

        rest_code = request.form['rest_id']
        rest_name = request.form.get('rest_name',False)
        rest_locality = request.form.get('rest_locality',False)
        rest_veg = request.form['rest_veg']
        rest_drinks = request.form['rest_drinks']
        rest_cost = request.form['rest_cost']
        rest_desc = request.form['rest_desc']
        rest_days = request.form['rest_days']
        rest_best = request.form['rest_best']
        f = request.files['file']

        fname = rest_code + '.' + f.filename.split('.')[-1]
        f.save(os.path.join(static, fname))

        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO restaurants VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',(rest_name, rest_locality, rest_veg, rest_drinks, rest_cost, rest_desc, rest_days, rest_best, rest_code, fname))
        mysql.connection.commit()
        flash('You have successfully entered your restaurant details!')
        
        return redirect(url_for('home'))        

    return render_template('create.html')


@app.route('/owner_profile')
def owner_profile():

    if session['loggedin']:

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM owners WHERE ownerid = %s', [session['ownerid']])
        owner = cur.fetchone()
        s = ''
        m = len(owner['passcode'])
        for i in range(m):
            s += '*'

        return render_template('owner_profile.html', owner=owner, s=s)

    return redirect(url_for('owner_login'))

@app.route('/editownerprofile', methods=['GET','POST'])
def editownerprofile():

    if request.method == 'POST':
        
        id_data = session['ownerid']
        ownername = request.form['ownername']
        owneremail = request.form['owneremail']
        passcode = request.form['passcode']
        phone = request.form['phone']
        session['ownername'] = ownername
        session['owneremail'] = owneremail
        session['passcode'] = passcode
        session['phone'] = phone

        cur = mysql.connection.cursor()
        cur.execute('UPDATE owners SET ownername=%s,owneremail=%s,passcode=%s,phone=%s WHERE ownerid=%s',(ownername,owneremail,passcode,phone,id_data))

        flash('Data Updated Successfully!')
        mysql.connection.commit()
        
        return redirect(url_for('owner_profile'))

    return render_template('editownerprofile.html')



if __name__ == '__main__':
    app.run(debug=True)



######################showpassword#in#profile#################################
# edit restaurant info
# advanced search
# wifi, outdoor seating, wheelchair access, discount
# Establishment Type
# Quick Bites10755
# Casual Dining5179
# Bakeries2461
# Dessert Parlor2415
# Cafés879
# Beverage Shops637
# Sweet Shops607
# Bars587
# Food Courts334
######################put#photos##############################################
###########################edit#owner#profile#################################
# mail on profile update and register
################forgotpw for owners###########################################
# fix the class active in both layout files
# chat application between users and owners
###############################edit#and#delete#reviews########################
# rating
# menu card photo in wishlist
# display all the info for a special admin account maybe
############################fix#login#registration#for#both###################
# put this and parwiz project on github with readme .sql files etc
# update resume
    