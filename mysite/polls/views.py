from flask import Flask, render_template, request
import os, sys, ctypes
import win32com.client
import threading
import pandas as pd
from datetime import datetime
from slacker import Slacker
import time, calendar
import requests 
import pythoncom
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from pywinauto import application
from datetime import time
import time
from enum import Enum
from matplotlib import pyplot as plt
import json
from django.shortcuts import render
from django.http import HttpResponse
from .models import Stockname
import subprocess
import pymysql
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image



conn = pymysql.connect(
  host='127.0.0.1',
  user='root',
  password='227899',
  db='stock')

curs = conn.cursor()

pythoncom.CoInitialize()
# 크레온 플러스 공통 OBJECT
cpCodeMgr = win32com.client.Dispatch('CpUtil.CpStockCode')
cpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
cpTradeUtil = win32com.client.Dispatch('CpTrade.CpTdUtil')
cpStock = win32com.client.Dispatch('DsCbo1.StockMst')
cpOhlc = win32com.client.Dispatch('CpSysDib.StockChart')
cpBalance = win32com.client.Dispatch('CpTrade.CpTd6033')
cpCash = win32com.client.Dispatch('CpTrade.CpTdNew5331A')
cpOrder = win32com.client.Dispatch('CpTrade.CpTd0311')

g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
g_objCpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')
g_objFutureMgr = win32com.client.Dispatch("CpUtil.CpFutureCode")
g_objKsdFMgr = win32com.client.Dispatch("CpUtil.CpKFutureCode")
g_objElwMgr = win32com.client.Dispatch("CpUtil.CpElwCode")
g_objOptionMgr = win32com.client.Dispatch("CpUtil.CpOptionCode")
g_objUsMgr = win32com.client.Dispatch("CpUtil.CpUsCode")


# 통신 제한 회피를 위한 대기 함수
# type 0 - 주문 관련 제한 1 - 시세 관련 제한
class Rqtype(Enum):
    ORDER = 0
    SISE = 1

def waitRqLimit(rqtype):
    
    remainCount = g_objCpStatus.GetLimitRemainCount(rqtype.value)

    if remainCount > 0:
        print('남은 횟수: ',remainCount)
        return True

    remainTime = g_objCpStatus.LimitRequestRemainTime
    print('조회 제한 회피 time wait %.2f초 ' % (remainTime / 1000.0))
    time.sleep(remainTime / 1000)
    return True

def charttest(request):
    data = [{ 'Date': 1646222400000, 'Open': 388.93, 'High': 389.22, 'Low': 375.21, 'Close': 380.03, 'Volume': 5356800 }]
    return render(request,'polls/test.html',{'data':data})
def query(request):
    return render(request,'polls/test.html')
def query2(request):
    return render(request,'polls/3.html')
# 일/주/월 차트 조회 - 개수로 조회
def chart_simple1(request):
    stockcode2 = request.POST.get('stockcode2')



    my_title = []
    link = []
    image = []

    name = stockcode2 #크롤링할 종목이름
    j = 0

    url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + name + "&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=55&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all,a:all&start=1"
    bogi = "https://postfiles.pstatic.net/MjAyMTAzMjNfMTQ3/MDAxNjE2NDc3MTgxODkz.Q0De_R90sw1LVaTlhCSPqIq5rmT5wPjBFeV0gUakQ3Ig.QXjotxDdqPaL4kZO8skx6X1PrZrdG5FO2ADUYCOzq5Mg.JPEG.gyqls1225/IMG_3227.JPG?type=w773"

    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    images = soup.select(".news_wrap.api_ani_send")
    #sp_nws1 > div.news_wrap.api_ani_send > a > img

    titles = soup.select(".news_tit")
    for title in titles:     
        href = title.attrs["href"]
        data = title.text
        my_title.append(data)
        link.append(href)
    
        
    for img in images:
        img_data = img.select_one("a > img")
        #img_data = img.select_one("a > img")['src']
        if(img_data is None):
            image.append(bogi)
            continue
        image.append(img_data.get('src'))


    

    
    print(image[0])


    curs.execute("SELECT code FROM stock.stockname where name =%s",stockcode2)
    
    rs = curs.fetchall()
    for row in rs:
        for code in row:
            print(code,end='') 
    
    
    code = "A"+code
    stockvalue = request.POST.get('stockvalue')
    stockvalue2 = request.POST.get('stockvalue2')
    print(type(stockcode2))
    print(type(stockvalue))
    print(type(stockvalue2))
    objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
    objStockChart.SetInputValue(0, code)  # 종목 코드 - 삼성전자
    objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
    objStockChart.SetInputValue(4, 100)
    objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
    objStockChart.SetInputValue(6, ord('D'))  # '차트 주기
    objStockChart.SetInputValue(8, ord('0'))  # 갭보정여부(char)
    objStockChart.SetInputValue(9, ord('1'))  # 수정주가(char) - '0': 무수정 '1': 수정주가
    objStockChart.SetInputValue(10, ord('1'))  # 거래량구분(char) - '1' 시간외거래량모두포함[Default]

    cData = []

    while (1):
        # 시세 연속 제한 체크 
        waitRqLimit(Rqtype.SISE)
        # 차트 통신
        objStockChart.BlockRequest()
        rqStatus = objStockChart.GetDibStatus()
        rqRet = objStockChart.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return

        clen = objStockChart.GetHeaderValue(3)


        for i in range(0, clen):
            item = {}
            dateFormat = '%Y%m%d'
            date = objStockChart.GetDataValue(0, i)
            Y = int(date / 10000)
            m = int((date - (Y * 10000)) / 100)
            d = date - Y*10000 - m*100
            dt = datetime(Y, m, d)
            a = time.mktime(dt.timetuple())
            # a = objStockChart.GetDataValue(0, i)
            item['Date'] = int(a) * 1000
            item['Open'] = objStockChart.GetDataValue(1, i)
            item['High'] = objStockChart.GetDataValue(2, i)
            item['Low'] = objStockChart.GetDataValue(3, i)
            item['Close'] = objStockChart.GetDataValue(3, i)
            item['Volume'] = objStockChart.GetDataValue(5, i)
            
            cData.append(item)
            
        if (objStockChart.Continue == False):
            # print('연속플래그 없음')
            break

    request.session['test'] = cData
    request.session['name'] = stockcode2
    request.session['title'] = my_title
    request.session['link'] = link
    request.session['news'] = image
    
    return render(request, 'polls/main.html', {"cData": cData,"stockcode3":stockcode2,
    'my_title0':my_title[0],'link0':link[0],'my_title1':my_title[1],'link1':link[1],'my_title2':my_title[2],'link2':link[2],
    'my_title3':my_title[3],'link3':link[3],'my_title4':my_title[4],'link4':link[4],'my_title5':my_title[5],'link5':link[5],
    'my_title6':my_title[6],'link6':link[6],'my_title7':my_title[7],'link7':link[7],'my_title8':my_title[8],'link8':link[8],
    'my_title9':my_title[9],'link9':link[9],'image0':image[0],'image1':image[1],'image2':image[2],'image3':image[3],'image4':image[4],'image5':image[5],'image6':image[6],'image7':image[7],'image8':image[8],'image9':image[9]})

   
def dl(request):
    return render(request,"polls/dl.html")

def get_current_cash():
    """증거금 100% 주문 가능 금액을 반환한다."""
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0]  # 계좌번호
    accFlag = cpTradeUtil.GoodsList(acc, 1)  # -1:전체, 1:주식, 2:선물/옵션
    cpCash.SetInputValue(0, acc)  # 계좌번호
    cpCash.SetInputValue(1, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
    cpCash.BlockRequest()
    return cpCash.GetHeaderValue(9)  # 증거금 100% 주문 가능 금액


    
def index(request):
    return render(request,'polls/hello.html')
    #return HttpResponse("Hello, world. You're at the polls index.")

def hello(request):
    
    if request.method == "POST":
        list=request.POST.get("num")
        hi=request.POST.get("name")
        passwd = request.POST.get("pass")
        print(list)
        print(hi)
        print(passwd)
        os.system('taskkill /IM coStarter* /F /T')
        os.system('taskkill /IM CpStart* /F /T')
        os.system('taskkill /IM DibServer* /F /T')
        os.system('wmic process where "name like \'%coStarter%\'" call terminate')
        os.system('wmic process where "name like \'%CpStart%\'" call terminate')
        os.system('wmic process where "name like \'%DibServer%\'" call terminate')
               
    
        app = application.Application()
        app.start('C:\CREON\STARTER\coStarter.exe /prj:cp /id:{list} /pwd:{hi} /pwdcert:{passwd} /autostart'.format(list=list, hi=hi, passwd=passwd))
        time.sleep(20)

    stockcode3= '삼성전자'
       
    image = []
    my_title = []
    link = []
    name = stockcode3 #크롤링할 종목이름
    j = 0

    url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + name + "&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=55&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all,a:all&start=1"
    bogi = "https://postfiles.pstatic.net/MjAyMTAzMjNfMTQ3/MDAxNjE2NDc3MTgxODkz.Q0De_R90sw1LVaTlhCSPqIq5rmT5wPjBFeV0gUakQ3Ig.QXjotxDdqPaL4kZO8skx6X1PrZrdG5FO2ADUYCOzq5Mg.JPEG.gyqls1225/IMG_3227.JPG?type=w773"

    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    images = soup.select(".news_wrap.api_ani_send")
    titles = soup.select(".news_tit")
    for title in titles:     
        href = title.attrs["href"]
        data = title.text
        my_title.append(data)
        link.append(href)

    for img in images:
        img_data = img.select_one("a > img")
        #img_data = img.select_one("a > img")['src']
        if(img_data is None):
            image.append(bogi)
            continue
        image.append(img_data.get('src'))



    code = 'A005930'
    objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
    objStockChart.SetInputValue(0, code)  # 종목 코드 - 삼성전자
    objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
    objStockChart.SetInputValue(4, 100)
    objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
    objStockChart.SetInputValue(6, ord('D'))  # '차트 주기
    objStockChart.SetInputValue(8, ord('0'))  # 갭보정여부(char)
    objStockChart.SetInputValue(9, ord('1'))  # 수정주가(char) - '0': 무수정 '1': 수정주가
    objStockChart.SetInputValue(10, ord('1'))  # 거래량구분(char) - '1' 시간외거래량모두포함[Default]

    cData = []

    while (1):
        # 시세 연속 제한 체크 
        waitRqLimit(Rqtype.SISE)
        # 차트 통신
        objStockChart.BlockRequest()
        rqStatus = objStockChart.GetDibStatus()
        rqRet = objStockChart.GetDibMsg1()
        # print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return

        clen = objStockChart.GetHeaderValue(3)


        for i in range(0, clen):
            item = {}
            dateFormat = '%Y%m%d'
            date = objStockChart.GetDataValue(0, i)
            Y = int(date / 10000)
            m = int((date - (Y * 10000)) / 100)
            d = date - Y*10000 - m*100
            dt = datetime(Y, m, d)
            a = time.mktime(dt.timetuple())
            # a = objStockChart.GetDataValue(0, i)
            item['Date'] = int(a) * 1000
            item['Open'] = objStockChart.GetDataValue(1, i)
            item['High'] = objStockChart.GetDataValue(2, i)
            item['Low'] = objStockChart.GetDataValue(3, i)
            item['Close'] = objStockChart.GetDataValue(3, i)
            item['Volume'] = objStockChart.GetDataValue(5, i)
            
            cData.append(item)

        if (objStockChart.Continue == False):
            # print('연속플래그 없음')
            break
    return render(request,'polls/main.html',{'cData':cData,'my_title0':my_title[0],'link0':link[0],'my_title1':my_title[1],'link1':link[1],'my_title2':my_title[2],'link2':link[2],
    'my_title3':my_title[3],'link3':link[3],'my_title4':my_title[4],'link4':link[4],'my_title5':my_title[5],'link5':link[5],
    'my_title6':my_title[6],'link6':link[6],'my_title7':my_title[7],'link7':link[7],'my_title8':my_title[8],'link8':link[8],
    'my_title9':my_title[9],'link9':link[9],'stockcode3':stockcode3,'image0':image[0],'image1':image[1],'image2':image[2],'image3':image[3],
    'image4':image[4],'image5':image[5],'image6':image[6],'image7':image[7],'image8':image[8],'image9':image[9]})




def dbgout(message):
    """인자로 받은 문자열을 파이썬 셸과 슬랙으로 동시에 출력한다."""
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message)
    strbuf = datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    #post_message(myToken,"#stock",strbuf)

def printlog(message, *args):
    """인자로 받은 문자열을 파이썬 셸에 출력한다."""
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message, *args)


def check_creon_system():
    """크레온 플러스 시스템 연결 상태를 점검한다."""
    # 관리자 권한으로 프로세스 실행 여부
    if not ctypes.windll.shell32.IsUserAnAdmin():
        printlog('check_creon_system() : admin user -> FAILED')
        return False

    # 연결 여부 체크
    if (cpStatus.IsConnect == 0):
        printlog('check_creon_system() : connect to server -> FAILED')
        return False

    # 주문 관련 초기화 - 계좌 관련 코드가 있을 때만 사용
    if (cpTradeUtil.TradeInit(0) != 0):
        printlog('check_creon_system() : init trade -> FAILED')
        return False
    return True


def get_current_price(code):
    """인자로 받은 종목의 현재가, 매도호가, 매수호가를 반환한다."""
    cpStock.SetInputValue(0, code)  # 종목코드에 대한 가격 정보
    cpStock.BlockRequest()
    item = {}
    item['cur_price'] = cpStock.GetHeaderValue(11)  # 현재가
    item['ask'] = cpStock.GetHeaderValue(16)  # 매도호가
    item['bid'] = cpStock.GetHeaderValue(17)  # 매수호가
    return item['cur_price'], item['ask'], item['bid']


def get_ohlc(code, qty):
    """인자로 받은 종목의 OHLC 가격 정보를 qty 개수만큼 반환한다."""
    cpOhlc.SetInputValue(0, code)  # 종목코드
    cpOhlc.SetInputValue(1, ord('2'))  # 1:기간, 2:개수
    cpOhlc.SetInputValue(4, qty)  # 요청개수
    cpOhlc.SetInputValue(5, [0, 2, 3, 4, 5])  # 0:날짜, 2~5:OHLC
    cpOhlc.SetInputValue(6, ord('D'))  # D:일단위
    cpOhlc.SetInputValue(9, ord('1'))  # 0:무수정주가, 1:수정주가
    cpOhlc.BlockRequest()
    count = cpOhlc.GetHeaderValue(3)  # 3:수신개수
    columns = ['open', 'high', 'low', 'close']
    index = []
    rows = []
    for i in range(count):
        index.append(cpOhlc.GetDataValue(0, i))
        rows.append([cpOhlc.GetDataValue(1, i), cpOhlc.GetDataValue(2, i),
                     cpOhlc.GetDataValue(3, i), cpOhlc.GetDataValue(4, i)])
    df = pd.DataFrame(rows, columns=columns, index=index)
    return df


def get_stock_balance(code):
    """인자로 받은 종목의 종목명과 수량을 반환한다."""
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0]  # 계좌번호
    accFlag = cpTradeUtil.GoodsList(acc, 1)  # -1:전체, 1:주식, 2:선물/옵션
    cpBalance.SetInputValue(0, acc)  # 계좌번호
    cpBalance.SetInputValue(1, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
    cpBalance.SetInputValue(2, 50)  # 요청 건수(최대 50)
    cpBalance.BlockRequest()
    if code == 'ALL':
        dbgout('계좌명: ' + str(cpBalance.GetHeaderValue(0)))
        dbgout('결제잔고수량 : ' + str(cpBalance.GetHeaderValue(1)))
        dbgout('평가금액: ' + str(cpBalance.GetHeaderValue(3)))
        dbgout('평가손익: ' + str(cpBalance.GetHeaderValue(4)))
        dbgout('종목수: ' + str(cpBalance.GetHeaderValue(7)))
    stocks = []
    for i in range(cpBalance.GetHeaderValue(7)):
        stock_code = cpBalance.GetDataValue(12, i)  # 종목코드
        stock_name = cpBalance.GetDataValue(0, i)  # 종목명
        stock_qty = cpBalance.GetDataValue(15, i)  # 수량
        if code == 'ALL':
            dbgout(str(i + 1) + ' ' + stock_code + '(' + stock_name + ')'
                   + ':' + str(stock_qty))
            stocks.append({'code': stock_code, 'name': stock_name,
                           'qty': stock_qty})
        if stock_code == code:
            return stock_name, stock_qty
    if code == 'ALL':
        return stocks
    else:
        stock_name = cpCodeMgr.CodeToName(code)
        return stock_name, 0





def get_target_price(code):
    """매수 목표가를 반환한다."""
    try:
        time_now = datetime.now()
        str_today = time_now.strftime('%Y%m%d')
        ohlc = get_ohlc(code, 10)
        if str_today == str(ohlc.iloc[0].name):
            today_open = ohlc.iloc[0].open
            lastday = ohlc.iloc[1]
        else:
            lastday = ohlc.iloc[0]
            today_open = lastday[3]
        lastday_high = lastday[1]
        lastday_low = lastday[2]
        target_price = today_open + (lastday_high - lastday_low) * 0.5
        return target_price
    except Exception as ex:
        dbgout("`get_target_price() -> exception! " + str(ex) + "`")
        return None


def get_movingaverage(code, window):
    """인자로 받은 종목에 대한 이동평균가격을 반환한다."""
    try:
        time_now = datetime.now()
        str_today = time_now.strftime('%Y%m%d')
        ohlc = get_ohlc(code, 20)
        if str_today == str(ohlc.iloc[0].name):
            lastday = ohlc.iloc[1].name
        else:
            lastday = ohlc.iloc[0].name
        closes = ohlc['close'].sort_index()
        ma = closes.rolling(window=window).mean()
        return ma.loc[lastday]
    except Exception as ex:
        dbgout('get_movingavrg(' + str(window) + ') -> exception! ' + str(ex))
        return None


def buy_etf(code):
    buy_percent = 1 #퍼센트도 변수로 넣어야된다.
    total_cash = int(get_current_cash())  # 100% 증거금 주문 가능 금액 조회
    buy_amount = total_cash * buy_percent  # 종목별 주문 금액 계산
    """인자로 받은 종목을 최유리 지정가 FOK 조건으로 매수한다."""
    try:
        global bought_list  # 함수 내에서 값 변경을 하기 위해 global로 지정
        if code in bought_list:  # 매수 완료 종목이면 더 이상 안 사도록 함수 종료
            # printlog('code:', code, 'in', bought_list)
            return False
        time_now = datetime.now()
        current_price, ask_price, bid_price = get_current_price(code)
        target_price = get_target_price(code)  # 매수 목표가
        ma5_price = get_movingaverage(code, 5)  # 5일 이동평균가
        ma10_price = get_movingaverage(code, 10)  # 10일 이동평균가
        buy_qty = 0  # 매수할 수량 초기화
        if ask_price > 0:  # 매도호가가 존재하면
            buy_qty = buy_amount // ask_price
        stock_name, stock_qty = get_stock_balance(code)  # 종목명과 보유수량 조회
        # printlog('bought_list:', bought_list, 'len(bought_list):',
        #    len(bought_list), 'target_buy_count:', target_buy_count)
        if current_price > target_price and current_price > ma5_price \
                and current_price > ma10_price:
            printlog(stock_name + '(' + str(code) + ') ' + str(buy_qty) +
                     'EA : ' + str(current_price) + ' meets the buy condition!`')
            cpTradeUtil.TradeInit()
            acc = cpTradeUtil.AccountNumber[0]  # 계좌번호
            accFlag = cpTradeUtil.GoodsList(acc, 1)  # -1:전체,1:주식,2:선물/옵션
            # 최유리 FOK 매수 주문 설정
            cpOrder.SetInputValue(0, "2")  # 2: 매수
            cpOrder.SetInputValue(1, acc)  # 계좌번호
            cpOrder.SetInputValue(2, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
            cpOrder.SetInputValue(3, code)  # 종목코드
            cpOrder.SetInputValue(4, buy_qty)  # 매수할 수량
            cpOrder.SetInputValue(7, "2")  # 주문조건 0:기본, 1:IOC, 2:FOK
            cpOrder.SetInputValue(8, "12")  # 주문호가 1:보통, 3:시장가
            # 5:조건부, 12:최유리, 13:최우선
            # 매수 주문 요청
            ret = cpOrder.BlockRequest()
            printlog('최유리 FoK 매수 ->', stock_name, code, buy_qty, '->', ret)
            if ret == 4:
                remain_time = cpStatus.LimitRequestRemainTime
                printlog('주의: 연속 주문 제한에 걸림. 대기 시간:', remain_time / 1000)
                time.sleep(remain_time / 1000)
                return False
            time.sleep(2)
            printlog('현금주문 가능금액 :', buy_amount)
            stock_name, bought_qty = get_stock_balance(code)
            printlog('get_stock_balance :', stock_name, stock_qty)
            if bought_qty > 0:
                bought_list.append(code)
                dbgout("`buy_etf(" + str(stock_name) + ' : ' + str(code) +
                       ") -> " + str(bought_qty) + "EA bought!" + "`")
    except Exception as ex:
        dbgout("`buy_etf(" + str(code) + ") -> exception! " + str(ex) + "`")


def sell_all():
    """보유한 모든 종목을 최유리 지정가 IOC 조건으로 매도한다."""
    try:
        cpTradeUtil.TradeInit()
        acc = cpTradeUtil.AccountNumber[0]  # 계좌번호
        accFlag = cpTradeUtil.GoodsList(acc, 1)  # -1:전체, 1:주식, 2:선물/옵션
        while True:
            stocks = get_stock_balance('ALL')
            total_qty = 0
            for s in stocks:
                total_qty += s['qty']
            if total_qty == 0:
                return True
            for s in stocks:
                if s['qty'] != 0:
                    cpOrder.SetInputValue(0, "1")  # 1:매도, 2:매수
                    cpOrder.SetInputValue(1, acc)  # 계좌번호
                    cpOrder.SetInputValue(2, accFlag[0])  # 주식상품 중 첫번째
                    cpOrder.SetInputValue(3, s['code'])  # 종목코드
                    cpOrder.SetInputValue(4, s['qty'])  # 매도수량
                    cpOrder.SetInputValue(7, "1")  # 조건 0:기본, 1:IOC, 2:FOK
                    cpOrder.SetInputValue(8, "12")  # 호가 12:최유리, 13:최우선
                    # 최유리 IOC 매도 주문 요청
                    ret = cpOrder.BlockRequest()
                    printlog('최유리 IOC 매도', s['code'], s['name'], s['qty'],
                             '-> cpOrder.BlockRequest() -> returned', ret)
                    if ret == 4:
                        remain_time = cpStatus.LimitRequestRemainTime
                        printlog('주의: 연속 주문 제한, 대기시간:', remain_time / 1000)
                time.sleep(1)
            time.sleep(30)
    except Exception as ex:
        dbgout("sell_all() -> exception! " + str(ex))

def test(request):

        try:
            symbol_list = ['A005930'] # 사용자가 이용하게끔 변수로 바꿔야함,삼전
            bought_list = []  # 매수 완료된 종목 리스트
            target_buy_count = 0  # 매수할 종목 수
            buy_percent = 1 #퍼센트도 변수로 넣어야된다.
            printlog('check_creon_system() :', check_creon_system())  # 크레온 접속 점검
            stocks = get_stock_balance('ALL')  # 보유한 모든 종목 조회
            total_cash = int(get_current_cash())  # 100% 증거금 주문 가능 금액 조회
            buy_amount = total_cash * buy_percent  # 종목별 주문 금액 계산
            printlog('100% 증거금 주문 가능 금액 :', total_cash)
            printlog('종목별 주문 비율 :', buy_percent)
            printlog('종목별 주문 금액 :', buy_amount)
            printlog('시작 시간 :', datetime.now().strftime('%m/%d %H:%M:%S'))
            soldout = False

            while True:
                t_now = datetime.now()
                t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
                t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
                t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
                t_exit = t_now.replace(hour=15, minute=20, second=0, microsecond=0)
                today = datetime.today().weekday()
                if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
                    printlog('Today is', 'Saturday.' if today == 5 else 'Sunday.')
                    sys.exit(0)
                if t_9 < t_now < t_start and soldout == False:
                    soldout = True
                    sell_all()
                if t_start < t_now < t_sell:  # AM 09:05 ~ PM 03:15 : 매수
                    for sym in symbol_list:
                        if len(bought_list) < target_buy_count:
                            buy_etf(sym)
                            time.sleep(1)
                    if t_now.minute == 30 and 0 <= t_now.second <= 5:
                        get_stock_balance('ALL')
                        time.sleep(5)
                if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
                    if sell_all() == True:
                        dbgout('`sell_all() returned True -> self-destructed!`')
                        sys.exit(0)
                if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
                    dbgout('`self-destructed!`')
                    sys.exit(0)
                time.sleep(3)
        except Exception as ex:
            dbgout('`main -> exception! ' + str(ex) + '`')
        return render(request,{'symbol_list':symbol_list},'polls/main.html')

    

def login(request):
    return render(request,'polls/login.html')



def logout(request):
    cpStatus.PlusDisconnect()
    os.system('taskkill /IM coStarter* /F /T')
    os.system('taskkill /IM CpStart* /F /T')
    os.system('taskkill /IM DibServer* /F /T')
    os.system('wmic process where "name like \'%coStarter%\'" call terminate')
    os.system('wmic process where "name like \'%CpStart%\'" call terminate')
    os.system('wmic process where "name like \'%DibServer%\'" call terminate')
    return render(request,'polls/login.html')

def test2(request):
    var1 = 10
    var2 = "hello"
    #os.system("python polls/stock.py {0} {1}".format(var1, var2))
    #testvalue = 2
    #os.system("python polls/stock.py")
    return render(request,'polls/main.html')

def auto(request):
    
    stockcode2 = request.POST.get('stockcode2')
    curs.execute("SELECT code FROM stock.stockname where name =%s",stockcode2)
    
    rs = curs.fetchall()
    for row in rs:
        for stockcode2 in row:
            print(stockcode2,end='') 
    
    stockcode2 = "A"+stockcode2
    stockvalue = request.POST.get('stockpercent')
    global sp
    
    #os.system("python polls/stock.py {0} {1}".format(stockcode2, stockvalue))
    sp = subprocess.Popen(["python","polls/stock.py",stockcode2,stockvalue])
    
    
    
    # sp.terminate()
    testchart = request.session['test']
    my_title = request.session['title']
    link = request.session['link']
    chartname = request.session['name']
    image =  request.session['news'] 
    return render(request,'polls/main.html',{'testchart':testchart,'my_title0':my_title[0],'link0':link[0],'my_title1':my_title[1],'link1':link[1],'my_title2':my_title[2],'link2':link[2],
    'my_title3':my_title[3],'link3':link[3],'my_title4':my_title[4],'link4':link[4],'my_title5':my_title[5],'link5':link[5],
    'my_title6':my_title[6],'link6':link[6],'my_title7':my_title[7],'link7':link[7],'my_title8':my_title[8],'link8':link[8],
    'my_title9':my_title[9],'link9':link[9],'chartname':chartname,'image0':image[0],'image1':image[1],'image2':image[2],'image3':image[3],
    'image4':image[4],'image5':image[5],'image6':image[6],'image7':image[7],'image8':image[8],'image9':image[9]})

def set(request):
    return render(request,'polls/main.html')

def current(request):
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0]  # 계좌번호
    accFlag = cpTradeUtil.GoodsList(acc, 1)  # -1:전체, 1:주식, 2:선물/옵션
    cpBalance.SetInputValue(0, acc)  # 계좌번호
    cpBalance.SetInputValue(1, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
    cpBalance.SetInputValue(2, 50)  # 요청 건수(최대 50)
    cpBalance.BlockRequest()
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0] #계좌번호
    print(acc)
    name = '계좌번호 :'
    hi = '계좌명 :'
    #account = '결제잔고수량:'
    money = '평가금액 :'
    profit = '평가손익 :'
    event = '종목수 :'
    hi1 = str(cpBalance.GetHeaderValue(0))
    #account1 = str(cpBalance.GetHeaderValue(1))
    money1 = str(cpBalance.GetHeaderValue(3))
    profit1 = str(cpBalance.GetHeaderValue(4))
    event1 = str(cpBalance.GetHeaderValue(7))
    
    testchart = request.session['test']
    my_title = request.session['title']
    link = request.session['link']
    chartname = request.session['name']
    image = request.session['news']
    
    return render(request,'polls/main.html',{'hi':hi,'money':money,'profit':profit,'event':event,'hi1':hi1,'money1':money1,'profit1':profit1,'event1':event1,'acc':acc,'name':name,'testchart':testchart,'my_title0':my_title[0],'link0':link[0],'my_title1':my_title[1],'link1':link[1],'my_title2':my_title[2],'link2':link[2],
    'my_title3':my_title[3],'link3':link[3],'my_title4':my_title[4],'link4':link[4],'my_title5':my_title[5],'link5':link[5],
    'my_title6':my_title[6],'link6':link[6],'my_title7':my_title[7],'link7':link[7],'my_title8':my_title[8],'link8':link[8],
    'my_title9':my_title[9],'link9':link[9],'chartname':chartname,'image0':image[0],'image1':image[1],'image2':image[2],'image3':image[3],
    'image4':image[4],'image5':image[5],'image6':image[6],'image7':image[7],'image8':image[8],'image9':image[9]})

def mainbuy(request):
    stockcode2 = request.POST.get('stockcode2')
    
    stockvalue = request.POST.get('stockvalue')
    stockvalue2 = request.POST.get('stockvalue2')
    curs.execute("SELECT code FROM stock.stockname where name =%s",stockcode2)
    rs = curs.fetchall()
    for row in rs:
        for stockcode2 in row:
            print(stockcode2,end='') 
    
    stockcode2 = "A"+stockcode2
    stockvalue = float(stockvalue)
    stockvalue = int(stockvalue)
    print(type(stockcode2))
    print(type(stockvalue))
    print(type(stockvalue2))
    
    # 연결 여부 체크
    objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    bConnect = objCpCybos.IsConnect
    if (bConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        exit()
 
# 주문 초기화
    objTrade =  win32com.client.Dispatch("CpTrade.CpTdUtil")
    initCheck = objTrade.TradeInit(0)
    if (initCheck != 0):
        print("주문 초기화 실패")
        exit()
 
 
# 주식 매수 주문
    acc = objTrade.AccountNumber[0] #계좌번호
    accFlag = objTrade.GoodsList(acc, 1)  # 주식상품 구분
    print(acc, accFlag[0])
    objStockOrder = win32com.client.Dispatch("CpTrade.CpTd0311")
    objStockOrder.SetInputValue(0, "2")   # 2: 매수
    objStockOrder.SetInputValue(1, acc )   #  계좌번호
    objStockOrder.SetInputValue(2, accFlag[0])   # 상품구분 - 주식 상품 중 첫번째
    objStockOrder.SetInputValue(3, stockcode2)   # 종목코드 - A017040 - 광명전기
    objStockOrder.SetInputValue(4, stockvalue)   # 매수수량 
    objStockOrder.SetInputValue(5, stockvalue2)   # 주문단가  - 14,100원
    objStockOrder.SetInputValue(7, "0")   # 주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK
    objStockOrder.SetInputValue(8, "01")   # 주문호가 구분코드 - 01: 보통
 
# 매수 주문 요청
    objStockOrder.BlockRequest()
 
    rqStatus = objStockOrder.GetDibStatus()
    rqRet = objStockOrder.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        exit()
    testchart = request.session['test']
    my_title = request.session['title']
    link = request.session['link']
    chartname = request.session['name']
    image = request.session['news']
    return render(request,'polls/main.html',{'testchart':testchart,'my_title0':my_title[0],'link0':link[0],'my_title1':my_title[1],'link1':link[1],'my_title2':my_title[2],'link2':link[2],
    'my_title3':my_title[3],'link3':link[3],'my_title4':my_title[4],'link4':link[4],'my_title5':my_title[5],'link5':link[5],
    'my_title6':my_title[6],'link6':link[6],'my_title7':my_title[7],'link7':link[7],'my_title8':my_title[8],'link8':link[8],
    'my_title9':my_title[9],'link9':link[9],'chartname':chartname,'image0':image[0],'image1':image[1],'image2':image[2],'image3':image[3],
    'image4':image[4],'image5':image[5],'image6':image[6],'image7':image[7],'image8':image[8],'image9':image[9]})

def mainsell(request): #매도
    stockcode2 = request.POST.get('stockcode2')
    curs.execute("SELECT code FROM stock.stockname where name =%s",stockcode2)
    rs = curs.fetchall()
    for row in rs:
        for stockcode2 in row:
            print(stockcode2,end='') 
    
    stockcode2 = "A"+stockcode2
    stockvalue = request.POST.get('stockvalue')
    stockvalue2 = request.POST.get('stockvalue2')
    print(type(stockcode2))
    print(type(stockvalue))
    print(type(stockvalue2))
    # 연결 여부 체크
    objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    bConnect = objCpCybos.IsConnect
    if (bConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        exit()
 
    # 주문 초기화
    objTrade =  win32com.client.Dispatch("CpTrade.CpTdUtil")
    initCheck = objTrade.TradeInit(0)
    if (initCheck != 0):
        print("주문 초기화 실패")
        exit()
 
 
    # 주식 매도 주문
    acc = objTrade.AccountNumber[0] #계좌번호
    accFlag = objTrade.GoodsList(acc, 1)  # 주식상품 구분
    print(acc, accFlag[0])
    objStockOrder = win32com.client.Dispatch("CpTrade.CpTd0311")
    objStockOrder.SetInputValue(0, "1")   #  1: 매도
    objStockOrder.SetInputValue(1, acc )   #  계좌번호
    objStockOrder.SetInputValue(2, accFlag[0])   #  상품구분 - 주식 상품 중 첫번째
    objStockOrder.SetInputValue(3, stockcode2)   #  종목코드 - A003540 - 대신증권 종목
    objStockOrder.SetInputValue(4, stockvalue)   #  매도수량 10주   
    objStockOrder.SetInputValue(5, stockvalue2)   #  주문단가  - 14,100원
    objStockOrder.SetInputValue(7, "0")   #  주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK
    objStockOrder.SetInputValue(8, "01")   # 주문호가 구분코드 - 01: 보통
 
    # 매도 주문 요청
    objStockOrder.BlockRequest()
 
    rqStatus = objStockOrder.GetDibStatus()
    rqRet = objStockOrder.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        exit()
    testchart = request.session['test']
    my_title = request.session['title']
    link = request.session['link']
    chartname = request.session['name']
    image = request.session['news']
    return render(request,'polls/main.html',{'testchart':testchart,'my_title0':my_title[0],'link0':link[0],'my_title1':my_title[1],'link1':link[1],'my_title2':my_title[2],'link2':link[2],
    'my_title3':my_title[3],'link3':link[3],'my_title4':my_title[4],'link4':link[4],'my_title5':my_title[5],'link5':link[5],
    'my_title6':my_title[6],'link6':link[6],'my_title7':my_title[7],'link7':link[7],'my_title8':my_title[8],'link8':link[8],
    'my_title9':my_title[9],'link9':link[9],'chartname':chartname,'image0':image[0],'image1':image[1],'image2':image[2],'image3':image[3],
    'image4':image[4],'image5':image[5],'image6':image[6],'image7':image[7],'image8':image[8],'image9':image[9]})

def fix(request):
    
    sp.kill()
    testchart = request.session['test']
    my_title = request.session['title']
    link = request.session['link']
    chartname = request.session['name']
    image = request.session['news']
    return render(request,'polls/main.html',{'testchart':testchart,'my_title0':my_title[0],'link0':link[0],'my_title1':my_title[1],'link1':link[1],'my_title2':my_title[2],'link2':link[2],
    'my_title3':my_title[3],'link3':link[3],'my_title4':my_title[4],'link4':link[4],'my_title5':my_title[5],'link5':link[5],
    'my_title6':my_title[6],'link6':link[6],'my_title7':my_title[7],'link7':link[7],'my_title8':my_title[8],'link8':link[8],
    'my_title9':my_title[9],'link9':link[9],'chartname':chartname,'image0':image[0],'image1':image[1],'image2':image[2],'image3':image[3],
    'image4':image[4],'image5':image[5],'image6':image[6],'image7':image[7],'image8':image[8],'image9':image[9]})

def cancel(request):
    os.system("python cancel.py")
    testchart = request.session['test']
    my_title = request.session['title']
    link = request.session['link']
    chartname = request.session['name']
    image = request.session['news']
    return render(request,'polls/main.html',{'testchart':testchart,'my_title0':my_title[0],'link0':link[0],'my_title1':my_title[1],'link1':link[1],'my_title2':my_title[2],'link2':link[2],
    'my_title3':my_title[3],'link3':link[3],'my_title4':my_title[4],'link4':link[4],'my_title5':my_title[5],'link5':link[5],
    'my_title6':my_title[6],'link6':link[6],'my_title7':my_title[7],'link7':link[7],'my_title8':my_title[8],'link8':link[8],
    'my_title9':my_title[9],'link9':link[9],'chartname':chartname,'image0':image[0],'image1':image[1],'image2':image[2],'image3':image[3],
    'image4':image[4],'image5':image[5],'image6':image[6],'image7':image[7],'image8':image[8],'image9':image[9]})

def mysql(request):
    stocks = Stockname.objects.all()
    return render(request, 'polls/test2.html',{'stocks':stocks})




pythoncom.CoUninitialize()