import sqlite3
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash
from contextlib import closing
import os
 
DATABASE = os.path.abspath(os.path.dirname(__file__))
#DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'admin'

app = Flask(__name__)
app.config.from_envvar('FLASKR_SETTING',silent=True)
app.config['DATABASE'] = DATABASE + r'\flasker.db'
app.config['USERNAME'] = USERNAME
app.config['PASSWORD'] = PASSWORD
app.config['SECRET_KEY'] = SECRET_KEY
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql',mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g,'db',None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    print('redirect')
    cur = g.db.execute('select title,text from entries order by id desc')
    entries = [dict(title=row[0],text=row[1]) for row in cur.fetchall()]
#    print(entries,type(entries))
    return render_template('show_entries.html',entries=entries)

@app.route('/add',methods=['POST'])
def add_entry():
    print('add_entry')
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title,text) values (?,?)',
                [request.form['title'],request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login',methods=['POST','GET'])
def login():
    error = None
#    session['e'] = 'e'
#    print(session['e'])
    print('entry login')
    if request.method == 'POST':
        print('username=%s,password=%s'%(request.form['username'],request.form['password']))
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            print('matched')
            session['logged_in'] = True
            print('session')
            flash('You were logged in')
            print('flash')
            return redirect(url_for('show_entries'))
    print(error)
    return render_template('login.html',error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()
#    print(session.logged_in)    
#    init_db()
