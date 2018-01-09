#coding:utf-8
import sys

import http.cookiejar
import http.cookies
import urllib.request
import urllib.parse
import pytesseract
from bs4 import BeautifulSoup
from PIL import Image

class swpuSpider:
    #构造函数
    def __init__(self,username,password):
        self.username=username #账号
        self.password=password #密码
        self.cookieName="F:\Cookie.txt" #cookie路径
        self.imageName="F:\\validate.jpg" #验证码路径
        self.htmlName="F:\Result.html"  #爬下来的路径
        self.pictureUrl="http://jwxt.swpu.edu.cn/validateCodeAction.do" #获取验证码
        self.postUrl="http://jwxt.swpu.edu.cn/loginAction.do" #登录
        self.searchUrl="http://jwxt.swpu.edu.cn/gradeLnAllAction.do?type=ln&oper=qbinfo&lnxndm=2014-2015%D1%A7%C4%EA%B4%BA(%C1%BD%D1%A7%C6%DA)"  #成绩查询
        self.cookie=self.GetCookie() #获取cookie值

    #main
    def Main(self,code):
        while self.IsLoginSuccess(self.PostLogin(code)):
            self.GetCookie()
            code=self.OCRpic()
            print(code)
        response=self.Search()
        self.OutputHtml(response)

        
    #获取cookie 验证码获取
    def GetCookie(self):
        #不然cookie丢失造成登录失败
        cookie=http.cookiejar.MozillaCookieJar(self.cookieName)  #cookie值存入文件
        handler=urllib.request.HTTPCookieProcessor(cookie)
        opener=urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)
        opener.addheaders=[('User-Agent', "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"),
                   ('Cache-Control', "max-age=0")]
        #事先请求一次验证码
        validateCode=opener.open(self.pictureUrl).read()
        #保存cookie
        cookie.save(ignore_discard=True,ignore_expires=True)
        self.SaveValidatePic(validateCode)
        return cookie

    #验证码图片 保存到本地
    def SaveValidatePic(self,validateCode):
        image=open(self.imageName,'wb')
        image.write(validateCode)
        image.close()

    #识别验证码 返回值
    def OCRpic(self):
        imagecode=Image.open(self.imageName)
        code=pytesseract.image_to_string(imagecode)
        return code

    #提交登录
    def PostLogin(self,validateCode):
        #使用文件读取cookie 不然cookie丢失造成登录失败
       cookie=http.cookiejar.MozillaCookieJar(self.cookieName)
       cookie.load(self.cookieName,ignore_discard=True,ignore_expires=True)
       opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
       opener=self.GetCookieFormFile()
       values = {"zjh":self.username,"mm":self.password,"v_yzm":validateCode}
       data=urllib.parse.urlencode(values).encode(encoding="UTF8") #url编码
       openerPost=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
       openerPost.addheaders=[('User-Agent', "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"),
                   ('Cache-Control', "max-age=0")]
       resquestPost=urllib.request.Request(self.postUrl,data) #POST请求
       response=openerPost.open(resquestPost).read().decode("GBK") #Response
       return response

    #查询成绩
    def Search(self):
         #使用文件读取cookie 不然cookie丢失造成登录失败
        opener=self.GetCookieFormFile()
        opener.addheaders=[('User-Agent', "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"),
                   ('Cache-Control', "max-age=0"),
                   ("Referer","http://jwxt.swpu.edu.cn/gradeLnAllAction.do?type=ln&oper=qb")]
        resquest = urllib.request.Request(self.searchUrl)
        response = opener.open(resquest).read().decode("GB2312")
        return response

    #输出结果
    def OutputHtml(self,response):
        htmlOut = open(self.htmlName,"w")
        htmlOut.write("<html>")
        htmlOut.write("<head>")
        htmlOut.write("<title>")
        htmlOut.write("您的成绩")
        htmlOut.write("</title>")
        htmlOut.write("</head>")
        htmlOut.write(response)
        htmlOut.write("</html>")

    #判断登录是否成功
    def IsLoginSuccess(self,response):
        soup=BeautifulSoup(response,"html.parser")
        note=soup.find(src="/img/icon/alert.gif")
        if  note!=None:
            return True
        return False

    #从文件中获取cookie
    def GetCookieFormFile(self):
        cookie=http.cookiejar.MozillaCookieJar(self.cookieName)
        cookie.load(self.cookieName,ignore_discard=True,ignore_expires=True)
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
        return opener



# spider=swpuSpider("1105020137","隐藏密码")
# spider.Main(spider.OCRpic())
def SearchStart(username,password):
    spider=swpuSpider(username,password)
    spider.Main(spider.OCRpic())

SearchStart(input("请输入学号："),input("请输入密码："))