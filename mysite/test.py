from flask import Flask, render_template, request
import os, sys, ctypes
import win32com.client
import threading
import pandas as pd
from datetime import datetime
import time, calendar
import requests
import pythoncom
#sys.coinit_flag = 0
import pywinauto
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

cpTradeUtil.TradeInit()
acc = cpTradeUtil.AccountNumber[0] #계좌번호
print(acc)

pythoncom.CoUninitialize()