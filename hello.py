# -*- coding: utf-8 -*-：
#!/usr/bin/python


from flask import Flask, render_template, request
# from jw import Jw
import sys
import requests
import hashlib
import re
from datetime import *
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding( "utf-8" )
def md5(str):
    return hashlib.md5(str.encode('gb2312')).hexdigest()


class Jw:
    def __init__(self, jw_url, sc_code):
        #是出血p

        self.__jw_url = jw_url

        self.__sc_code = sc_code

        self.__login_url = 'http://202.198.0.54/jwweb/_data/login.aspx'

    def getCheckCode(self):
        self.__session = requests.session()
        self.__session.headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0'
        self.__session.headers['Referer'] = self.__jw_url
        self.__session.get(self.__login_url)
        self.__session.headers['Referer'] = self.__login_url
        response = self.__session.get(self.__login_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        self.__VIEWSTATE = soup.find('input', attrs={'name': '__VIEWSTATE'}).attrs['value']
        # print(self.__VIEWSTATE)
        # print('------------------------------------------')
        yzm_response = self.__session.get('http://202.198.0.54/jwweb/sys/ValidateCode.aspx')
        yzm_response.encoding = yzm_response.apparent_encoding
        return yzm_response.content

    def login(self, stuid, passwd, code):
        data = {
            '__VIEWSTATE': self.__VIEWSTATE,
            'pcInfo': 'Mozilla/5.0+(Windows+NT+6.1;+Win64;+x64;+rv:52.0)+Gecko/20100101+Firefox/52.0Windows+NT+6.1;+Win64;+x645.0+(Windows)+SN:NULL',
            'typeName': u'学生'.encode('gb2312'),
            'dsdsdsdsdxcxdfgfg': md5(stuid + md5(passwd)[0:30].upper() + self.__sc_code)[0:30].upper(),
            'fgfggfdgtyuuyyuuckjg': md5(md5(code.upper())[0:30].upper() + self.__sc_code)[0:30].upper(),
            'Sel_Type': 'STU',
            'txt_asmcdefsddsd': stuid,
            'txt_pewerwedsdfsdff': '',
            'txt_sdertfgsadscxcadsads': ''
        }
        login_response = self.__session.post(self.__login_url, data)
        login_response.encoding = login_response.apparent_encoding
        login_html = login_response.text
        # print login_html
        # print(login_html)
        # if 'MAINFRM.aspx' in login_html:
        #     return 'True'
        # return 'False'
        soup = BeautifulSoup(login_html, 'html.parser')
        log = soup.find_all(id='divLogNote')
        log1 = list(log[0].strings)[0].encode("utf-8")
        # print log1
        return log1

    def getScores(self, xn, xq, sj):
        scores = []
        self.__session.headers['Referer'] = 'http://202.198.0.54/jwweb/xscj/Stu_MyScore.aspx'
        data = {
            'sel_xn': xn,
            'sel_xq': xq,
            'SJ': sj,
            'btn_search': u'检索'.encode('gb2312'),
            'SelXNXQ': '2',
            'zfx_flag': '0',
            'zxf': '0'

        }
        scores_response = self.__session.post('http://202.198.0.54/jwweb/xscj/Stu_MyScore_rpt.aspx', data)
        scores_response.encoding = scores_response.apparent_encoding

        return scores_response.text

    def get(self, xn, xq, sj,xh):
        xq = str(xq)

        aa = jw.getScores(xn, xq, sj)
        soup = BeautifulSoup(aa, 'html.parser')
        imgs = soup.find_all('img')
        imgs = str(imgs)
        re1 = re.findall(r'<img src="(.*?)"', imgs)
        # request = requests.session()
        for index, img in enumerate(re1):
            imglist = img.split('amp;')
            img = 'http://202.198.0.54/jwweb/xscj/' + ''.join(imglist)
            #print(img)
            # self.request = requests.session()
            self.__session.headers[
                'User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0'
            self.__session.headers['Referer'] = 'http://202.198.0.54/jwweb/xscj/Stu_MyScore_rpt.aspx'
            # self.__session.headers['Cookie'] = r'ASP.NET_SessionId=iq304hr3iz1vp255nlurtw45'
            pic = self.__session.get(img).content
            with open('static/cj/{}{}{}{}.jpg'.format(xh,xn,xq,index), 'wb') as fd:
                fd.write(pic)
            print("success")

        tr = soup.find_all('tr')
        score = []
        for i in range(2, len(tr)):

            for td in tr[i].find_all('td'):
                score.append(td.get_text().strip())
        global mes
        mes = []
        flg = "1"
        if sj is flg:
            mes.append(score[4])
            mes.append(score[3])
            mes.append(score[1])
            mes.append(score[0])
            mes.append(score[2])
        else:
            mes.append(score[3])
            mes.append(score[2])
            mes.append(score[1])
            mes.append(score[0])
            mes.append('')


        return len(re1)
# jw = Jw('http://202.198.0.54/jwweb/default.aspx', '10193')
# with open('static/CheckCode.jpg', 'wb') as fd:
#     fd.write(jw.getCheckCode())

def picfor(xh,picnum,xn,xq):
    pic1 = []
    for picnum1 in range(picnum):
        filename = 'cj/'+xh+xn+xq+str(picnum1)+".jpg"
        pic1.append(filename)
        # print filename
    return pic1

app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=0.1)

@app.route('/')
def hello_world():
    global jw
    jw = Jw('http://202.198.0.54/jwweb/default.aspx', '10193')
    with open('static/CheckCode.jpg', 'wb') as fd:
        fd.write(jw.getCheckCode())

    return render_template("login.html")



#
@app.route('/tishi',methods=['GET','POST'])
def tishi():
    global xh
    xh = str(request.form['xh'])
    mm = str(request.form['mm'])
    yzm = str(request.form['yzm'])
    # xn = str(request.form['xn'])
    # xq = str(request.form['xq'])
    # sj = str(request.form['sj'])
    a = jw.login(xh, mm, yzm)
    flag1 = len(a)
    if flag1 !=27:
        return render_template("error.html",log=a)
    # print a
    else:
        return render_template("two.html", method=request.method)

@app.route('/chengjidan',methods=['GET','POST'])

def chengjidan():
    # xh = str(request.form['xh'])
    # mm = str(request.form['mm'])
    # yzm = str(request.form['yzm'])
    xn = str(request.form['xn'])
    xq = str(request.form['xq'])
    sj = str(request.form['sj'])
    # xn = '2017'###############
    # xq = '1'#####################
    # sj = '1'#################
    # a = jw.login(xh, mm, yzm)
    # print a
    # xh='12165108'##################################
    pic = jw.get(xn, xq, sj,xh)
    picnum = int(pic)
    filename = picfor(xh,picnum,xn,xq)
    # print filename


    return render_template("chengjidan.html",method=request.method,filename=filename,a1=mes[0],a2=mes[1],a3=mes[2],a4=mes[3],a5=mes[4])


#
# @app.route('/erro')
# def error():
#
#
#     return render_template("error.html")


if __name__ == '__main__':
    app.run()
