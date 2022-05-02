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
        time.sleep(5)        
    
        app = application.Application()
        app.start('C:\CREON\STARTER\coStarter.exe /prj:cp /id:{list} /pwd:{hi} /pwdcert:{passwd} /autostart'.format(list=list, hi=hi, passwd=passwd))
        time.sleep(5)
    return render(request,'polls/main.html')

def test(request):
    # exec(open("test.py", 'r', encoding="utf-8").read())
    
    os.system("python hi.py")
    return render(request, 'polls/test.html')

def login(request):
    return render(request,'polls/login.html')

def account(request):
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0] #계좌번호
    print(acc)
   
    
    return render(request,'polls/account.html',{'acc':acc})

pythoncom.CoUninitialize()