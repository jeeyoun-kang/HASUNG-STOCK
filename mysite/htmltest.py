import sys
from datetime import time
import time
import ctypes
from enum import Enum
import win32com.client
from matplotlib import pyplot as plt




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
        #print('남은 횟수: ',remainCount)
        return True

    remainTime = g_objCpStatus.LimitRequestRemainTime
    print('조회 제한 회피 time wait %.2f초 ' % (remainTime / 1000.0))
    time.sleep(remainTime / 1000)
    return True



def chart_rq1() :
    chart_simple1(ord('D'), 'A005930', 100)
    

# 일/주/월 차트 조회 - 개수로 조회
def chart_simple1() :
    objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
    objStockChart.SetInputValue(0, 'A005930')  # 종목 코드 - 삼성전자
    objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
    objStockChart.SetInputValue(4, 100)
    objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
    objStockChart.SetInputValue(6, ord('D'))  # '차트 주기
    objStockChart.SetInputValue(8, ord('0')) # 갭보정여부(char)
    objStockChart.SetInputValue(9, ord('1'))  # 수정주가(char) - '0': 무수정 '1': 수정주가
    objStockChart.SetInputValue(10, ord('1')) # 거래량구분(char) - '1' 시간외거래량모두포함[Default]
    hi = []

    totlen = 0
    
    while (1):
        # 시세 연속 제한 체크 
        waitRqLimit(Rqtype.SISE)
        # 차트 통신
        objStockChart.BlockRequest()
        rqStatus = objStockChart.GetDibStatus()
        rqRet = objStockChart.GetDibMsg1()
        #print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return

        clen = objStockChart.GetHeaderValue(3)
        totlen += clen
        #print(totlen)

        #print("날짜", "시가", "고가", "저가", "종가", "거래량")

        for i in range(0, clen) :
            item = {}
            
            item['Date'] = objStockChart.GetDataValue(0, i)
            item['Open'] = objStockChart.GetDataValue(1, i)
            item['High'] = objStockChart.GetDataValue(2, i)
            item['Low'] = objStockChart.GetDataValue(3, i)
            item['Close'] = objStockChart.GetDataValue(4, i)
            item['Volume'] = objStockChart.GetDataValue(5, i)
            for j in range(0,clen):
                hi.append(item)
                
            #list1.append(item['날짜'])
            #list2.append(item['시가'])
            #print(item)
        
                        

        if (objStockChart.Continue == False):
            #print('연속플래그 없음')
            break
    print(hi)
       
    #return render(request,'polls/test2.html',{'hi':hi})
    

    #plt.plot(list1,list2,'ro')
    #plt.show()
    #print(hi)
    
    
chart_simple1()