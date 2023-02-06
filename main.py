# -*- coding:utf-8 -*-

from flask import Flask, render_template, flash, request,  redirect, url_for
from sqlalchemy import create_engine


app = Flask(__name__)




@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/loginaction/', methods=['GET', 'POST'])
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
        if username == "啾星" and password == "zhuikeai":
            return render_template('datanone.html')
        else:
            error_msg = "关闭客服大门（o´・ェ・｀o）"
    else:
        error_msg = '关闭客服大门（o´・ェ・｀o）'

    return render_template('index.html', error_msg=error_msg)

@app.route('/search/', methods=['GET', 'POST'])
def search():
    error_msg = ''
    list = ''

    if request.method == 'GET':
        peopleid = request.args.get('peopleid')
    else:
        peopleid = request.form.get('peopleid')

    print('peopleid:%s' % (peopleid))

    if peopleid is not None:
        list = getdata(peopleid)
        if len(list) < 1:
            error_msg = '暂未收录~(￣▽￣)~*'
        else:
            error_msg = '查询成功( •̀ ω •́ )y'
            return render_template('data.html', error_msg = error_msg, list = list, peopleid = peopleid)
    else:
        error_msg = '关闭客服大门（o´・ェ・｀o）'
    return render_template('datanone.html', error_msg = error_msg,  peopleid = peopleid)

def getdata(peopleid):

    sql = '''select 
        DISTINCT
         dt.CONTENT,
         dt.NAME,
         dt.LINK,
         dg.NAME,
         dp.LINK peoplelink,
         '主楼' remark
        from DB_TOPIC dt 
        left join DB_GROUP dg on dt.GROUPID = dg.ID
        left join DB_PEOPLE dp on dt.PEOPLEID = dp.ID
        where dp.ID = \"'''+peopleid+'''\"
        union all
        select
        DISTINCT
         dr.content,
         dt.NAME,
         dt.LINK,
         dg.NAME,
         dp.LINK peoplelink,
         '跟帖' remark
        from DB_REPLY dr 
        left join DB_TOPIC dt on dr.TOPICID = dt.ID
        left join DB_GROUP dg on dt.GROUPID = dg.ID
        left join DB_PEOPLE dp on dr.PEOPLEID = dp.ID
        where dp.ID = \"'''+peopleid+'''\"'''
    engine = create_engine(
#        'mysql+pymysql://jiuxing:c929@192.168.2.129:3306/jiuxing?charset=utf8mb4')
        'mysql+pymysql://jiuxing:c929@82.156.17.16:3306/jiuxing?charset=utf8mb4')
    cur = engine.execute(sql)
    data = cur.fetchall()

    return data



if __name__ == '__main__':
    flag = '1'
    app.run(port='5000', debug=True)