from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL 
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app=Flask(__name__)

#==========================================================
#===============Config MySQL===============================
#======Fill up with your own database credentials==========

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='<username>'
app.config['MYSQL_PASSWORD']='<password>'
app.config['MYSQL_DB']='<database>'
app.config['MYSQL_CURSORCLASS']='DictCursor'

#==========================================================
#===============Init MYSQL=================================
#==========================================================
mysql=MySQL(app)


@app.route('/')
def index():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/articles')
def articles():
	
	#create cursor
	cur = mysql.connection.cursor()

	#get articles
	result = cur.execute("SELECT * FROM articles")

	articles = cur.fetchall()

	if result > 0:
		return render_template('/articles.html',articles=articles)

	else:
		msg= "No Articles Found"
		return render_template('/articles.html',msg=msg)

	#close connection
	cur.close()

@app.route('/article/<string:id>/')
def article(id):
	#create cursor
	cur = mysql.connection.cursor()

	#get articles
	result = cur.execute("SELECT * FROM articles WHERE id=%s",[id])

	article = cur.fetchone()
	return render_template('article.html',article=article)


#==========================================================
#===============Class to use WTForm========================
#==========================================================
class RegisterForm(Form):
	name = StringField('Name',[validators.Length(min=1, max=50)])
	username = StringField('Username',[validators.Length(min=4, max=25)])
	email = StringField('Email',[validators.Length(min=6, max=50)])
	password = PasswordField('Password',[validators.DataRequired(),validators.EqualTo('confirm',message='Password do not match')])
	confirm = PasswordField('confirm Password')


#===========================================================
#===============Register from route=========================
#===========================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():

		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		#Create Cursor
		cur = mysql.connection.cursor()

		#Execute query
		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",(name, email,username,password))

		#commit to DB
		mysql.connection.commit()
		cur.close()

		flash("You are now register and log in", 'success')
		
		return redirect(url_for('login'))

	return render_template('register.html',form=form)


#===========================================================
#===============User Login==================================
#===========================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		#Get form fields
		username = request.form['username']
		password_candidate = request.form['password']

		#Create cursor
		cur = mysql.connection.cursor()

		#get user name
		result = cur.execute('SELECT * FROM users WHERE username= %s',[username])

		if result>0:
			#get stored hash
			data = cur.fetchone()
			password = data['password']

			#compare password
			if sha256_crypt.verify(password_candidate, password):
				# app.logger.info('PASSWORD MATCHED')
				#if password passed than create a login session
				session['logged_in']=True
				session['username']=username
				flash('You are now logged in', 'success')
				return redirect(url_for('dashboard'))
			else:
				# app.logger.info('PASSWORD NOT MATCHED')
				error= 'Invalid login'
				return render_template('login.html',error=error)
			#close connection
			cur.close()	

		else:
			# app.logger.info('NO USER FOUND')
			error= 'Username not found'
			return render_template('login.html',error=error)


	return render_template('login.html')	


#===========================================================
#=======Decorator to check is the user is logged in:========
#===========================================================

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap

@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():

	#create cursor
	cur = mysql.connection.cursor()

	#get articles
	# use=cur.execute("SELECT * FROM users")
	# print use
	result = cur.execute("SELECT * FROM articles")

	articles = cur.fetchall()

	if result > 0:
		return render_template('/dashboard.html',articles=articles)

	else:
		msg = "No Articles Found"
		return render_template('/dashboard.html',msg=msg)

	#close connection
	cur.close()


#===========================================================
#===============Articles====================================
#===========================================================
class ArticleForm(Form):
	title = StringField('Title',[validators.Length(min=1, max=200)])
	body = TextAreaField('Body',[validators.Length(min=5)])
	
@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
	form = ArticleForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		#Create cursor
		cur = mysql.connection.cursor()

		#Execute
		cur.execute('INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)',(title,body,session['username']))

		#commit to DB
		mysql.connection.commit()

		#close connection
		cur.close()

		flash('Article created', 'success')

		return redirect(url_for('dashboard'))

	return render_template('add_article.html',form=form)

@app.route('/edit_article/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_article(id):
	#create cursor
	cur = mysql.connection.cursor()
	
	#GEt article by id
	result = cur.execute('SELECT * FROM articles WHERE id=%s',[id])

	article = cur.fetchone()

	#Get from
	form = ArticleForm(request.form)

	#Populate article from field
	form.title.data = article['title']
	form.body.data = article['body']

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']

		#Create cursor
		cur = mysql.connection.cursor()

		#Execute
		cur.execute('UPDATE articles SET title=%s, body=%s WHERE id=%s',(title ,body,id))

		#commit to DB
		mysql.connection.commit()

		#close connection
		cur.close()

		flash('Article Updated', 'success')

		return redirect(url_for('dashboard'))

	return render_template('edit_article.html',form=form)


#Delete article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
		#Create cursor
		cur = mysql.connection.cursor()

		#Execute
		cur.execute('DELETE FROM articles WHERE id=%s',[id])

		#commit to DB
		mysql.connection.commit()

		#close connection
		cur.close()

		flash('Article Deleted', 'success')

		return redirect(url_for('dashboard'))


if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)


















