# advance_blog
Advance blog is a very simple blog post application with user login, logout, dashboard for each individual user.


## Step 1:
Create a folder.

$ mkdir blog_login_system

Create a virtual enviroment. 

$pip install virtualenv

$ cd rblog_login_system

$ virtualenv env

$ source env/bin/activate

## Step 2:
Install requirements.txt

$pip install -r requirements.txt

## Step 3:
Create a MySQL database "AdvanceBlog", two tables "articles" & "users"

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `username` varchar(30) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `register_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

CREATE TABLE `articles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `author` varchar(100) DEFAULT NULL,
  `body` text,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;

## Step 4:
Edit app.py with your own database credentials.

app.config['MYSQL_HOST']='host'

app.config['MYSQL_USER']='username'

app.config['MYSQL_PASSWORD']='password'

app.config['MYSQL_DB']='database'

## Step 5:
Run project.

$ python app.py
