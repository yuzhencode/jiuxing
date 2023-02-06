# coding:utf-8

from flask import Flask, render_template, request, redirect
import fileutils

# 引入file_dict用户列表
fileutils.file_read()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/loginaction/', methods=["POST", "GET"])
def login():
    error_msg = ''

    if request.method == 'GET':
        username = request.args.get('username')
        password = request.args.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    print('username:%s,password:%s' % (username, password))

    if username and password:
        if username == "admin" and password == "admin":
            return redirect('/list')
        else:
            error_msg = "username or password is wrong"
    else:
        error_msg = 'need username and password'

    return render_template('login.html', error_msg=error_msg)


@app.route('/list/')
def userlist():
    userlist = fileutils.file_read().items()
    print('userlist:%s' % userlist)
    return render_template('list.html', userlist=userlist)


@app.route('/update/')
def update():
    username = request.args.get('username')
    password = fileutils.file_read().get(username)
    user = [username, password]
    print('update:%s' % user)
    return render_template('update.html', user=user)


@app.route('/updateaction/', methods=['POST'])
def updateaction():
    params = request.args if request.method == 'GET' else request.form

    username = params.get('username')
    password = params.get('password')
    fileutils.file_dict[username] = password
    fileutils.file_write()
    return redirect('/list/')


@app.route('/add/')
def add():
    return render_template('add.html')


@app.route('/addaction/', methods=['POST'])
def addaction():
    params = request.args if request.method == 'GET' else request.form
    username = params.get('username')
    password = params.get('password')

    if username in fileutils.file_dict:
        return redirect('/list/')
    else:
        fileutils.file_dict[username] = password
        fileutils.file_write()
        return redirect('/list/')


@app.route('/delete/')
def delete():
    username = request.args.get('username')
    fileutils.file_dict.pop(username)
    fileutils.file_write()
    return redirect('/list/')


if __name__ == "__main__":
    app.run(port='8000', debug=True)