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




def InitPlusCheck(isOrder):
    # 프로세스가 관리자 권한으로 실행 여부
    if ctypes.windll.shell32.IsUserAnAdmin():
        print('정상: 관리자권한으로 실행된 프로세스입니다.')
    else:
        print('오류: 일반권한으로 실행됨. 관리자 권한으로 실행해 주세요')
        return False

    # 연결 여부 체크
    if (g_objCpStatus.IsConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        return False

    # 주문 관련 초기화
    if isOrder == True:
        if (g_objCpTrade.TradeInit(0) != 0):
            print("주문 초기화 실패")
        return False

    return True

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



# in_NumOrMoney '1' 순매수량 '2' 추정금액(백만)
def rq_7254(code, termFlag, in_NumOrMoney, rqCnt):
    objRq = win32com.client.Dispatch('CpSysDib.CpSvr7254')
    objRq.SetInputValue(0, code)
    objRq.SetInputValue(1, termFlag)  # 일자별
    objRq.SetInputValue(4, ord('0'))  # '0' 순매수 '1' 매매비중
    objRq.SetInputValue(5, 0)  # '전체
    objRq.SetInputValue(6, in_NumOrMoney)  # '1' 순매수량 '2' 추정금액(백만)
    sumcnt = 0

    ret7254 = []

    while True:
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()
        # 현재가 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        if rqStatus != 0:
            return (False, ret7254)

        cnt = objRq.GetHeaderValue(1)
        sumcnt += cnt

        for i in range(cnt):
            item = {}
            fixed = objRq.GetDataValue(18, i)
            # 잠정치는 일단 버린다
            if (fixed == ord('0')):
                continue

            item['일자'] = objRq.GetDataValue(0, i)
            item['종가'] = objRq.GetDataValue(14, i)
            item['개인'] = objRq.GetDataValue(1, i)
            item['외국인'] = objRq.GetDataValue(2, i)
            item['기관'] = objRq.GetDataValue(3, i)
            item['거래량'] = objRq.GetDataValue(17, i)
            item['대비율'] = objRq.GetDataValue(16, i)
            #print(item)
            ret7254.append(item)
        if (sumcnt >= rqCnt):
            break
        if (objRq.Continue == False):
            break


    return (True, ret7254)




#####################################################################

def getCode_AllCode():
    codeList = g_objCodeMgr.GetStockListByMarket(1)  # 거래소
    print('\n거래소 종목리스트')
    for code in codeList:
        print(code, g_objCodeMgr.CodeToName(code))

    codeList2 = g_objCodeMgr.GetStockListByMarket(2)  # 코스닥
    print('\n코스닥 종목리스트')
    for code in codeList2:
        print(code, g_objCodeMgr.CodeToName(code))

def getCode_Inducstry():
    print('\n증권산업 업종코드')
    codeList = g_objCodeMgr.GetIndustryList()  # 증권 산업 업종 리스트
    for code in codeList:
        print(code, g_objCodeMgr.CodeToName(code))

    print('\n코스닥산업별코드리스트')
    codeList2 = g_objCodeMgr.GetKosdaqIndustry1List()  # 코스닥산업별코드리스트를반환한다.
    for code in codeList2:
        print(code, g_objCodeMgr.CodeToName(code))

def getCode_ETF():
    codeList = g_objCodeMgr.GetStockListByMarket(1)  # 거래소
    codeList2 = g_objCodeMgr.GetStockListByMarket(2)  # 코스닥
    allCode = codeList + codeList2


    ETFList = []
    for code in allCode:
        stockKind = g_objCodeMgr.GetStockSectionKind(code)
        if  stockKind == 10 or stockKind == 12 :
            ETFList.append(code)

    print('\nETF종목리스트')
    for code in ETFList:
        print(code, g_objCodeMgr.CodeToName(code))

def getCode_ETN():
    codeList = g_objCodeMgr.GetStockListByMarket(1)  # 거래소
    codeList2 = g_objCodeMgr.GetStockListByMarket(2)  # 코스닥
    allCode = codeList + codeList2


    ETNList = []
    for code in allCode:
        stockKind = g_objCodeMgr.GetStockSectionKind(code)
        if (code[0] == 'Q'):
            ETNList.append(code)

    print('\nETN종목리스트')
    for code in ETNList:
        print(code, g_objCodeMgr.CodeToName(code))

def getCode_K200():
    codeList = []
    codeList= g_objCodeMgr.GetGroupCodeList(180)
    print("\n코스피200 종목", len(codeList))
    for code in codeList:
        print(code, g_objCodeMgr.CodeToName(code))

def getCode_Future():
    codeList = []
    for i in range(g_objFutureMgr.GetCount()) :
        codeList.append(g_objFutureMgr.GetData(0,i))
    print("\n선물 종목 코드", len(codeList))
    for code in codeList:
        name = g_objFutureMgr.CodeToName(code)
        print(code, name)

    codeList = []
    for i in range(g_objKsdFMgr.GetCount()) :
        codeList.append(g_objKsdFMgr.GetData(0,i))
    print("\n코스닥선물 종목 코드", len(codeList))
    for code in codeList:
        name = g_objKsdFMgr.CodeToName(code)
        print(code, name)    

def getCode_Option():
    codeList = []
    for i in range(g_objOptionMgr.GetCount()):
        codeList.append(g_objOptionMgr.GetData(0, i))
    print("\n옵션종목 코드", len(codeList))
    for code in codeList:
        name = g_objCodeMgr.CodeToName(code)
        print(code, name)          


# 일/주/월 차트 조회 - 개수로 조회
def chart_simple1(dwm, code, cnt) :
    objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
    objStockChart.SetInputValue(0, code)  # 종목 코드 - 삼성전자
    objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
    objStockChart.SetInputValue(4, cnt)
    objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
    objStockChart.SetInputValue(6, dwm)  # '차트 주기
    objStockChart.SetInputValue(8, ord('0')) # 갭보정여부(char)
    objStockChart.SetInputValue(9, ord('1'))  # 수정주가(char) - '0': 무수정 '1': 수정주가
    objStockChart.SetInputValue(10, ord('1')) # 거래량구분(char) - '1' 시간외거래량모두포함[Default]


    totlen = 0
    list1= []
    list2 = []
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
        totlen += clen
        print(totlen)

        print("날짜", "시가", "고가", "저가", "종가", "거래량")

        for i in range(0, clen) :
            item = {}
            item['Date'] = objStockChart.GetDataValue(0, i)
            item['Open'] = objStockChart.GetDataValue(1, i)
            item['High'] = objStockChart.GetDataValue(2, i)
            item['Low'] = objStockChart.GetDataValue(3, i)
            item['Close'] = objStockChart.GetDataValue(3, i)
            item['Volume'] = objStockChart.GetDataValue(5, i)
            
            
            
            print(item)

        if (objStockChart.Continue == False):
            print('연속플래그 없음')
            break
    

    plt.plot(list1,list2,'ro')
    plt.show()

    return True


# 일/주/월 차트 조회 - 기간으로 조회
def chart_simple2(dwm, code, fromday, today) :
    objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
    objStockChart.SetInputValue(0, code)  # 종목 코드 - 삼성전자
    objStockChart.SetInputValue(1, ord('1'))  # 기간
    objStockChart.SetInputValue(2, today)
    objStockChart.SetInputValue(3, fromday)
    objStockChart.SetInputValue(5, [0, 2, 3, 4, 5, 8])  # 날짜,시가,고가,저가,종가,거래량
    objStockChart.SetInputValue(6, dwm)  # '차트 주기
    objStockChart.SetInputValue(8, ord('0')) # 갭보정여부(char)
    objStockChart.SetInputValue(9, ord('1'))  # 수정주가(char) - '0': 무수정 '1': 수정주가
    objStockChart.SetInputValue(10, ord('1')) # 거래량구분(char) - '1' 시간외거래량모두포함[Default]


    totlen = 0
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
        totlen += clen
        print(totlen)

        print("날짜", "시가", "고가", "저가", "종가", "거래량")

        for i in range(0, clen) :
            item = {}
            item['날짜'] = objStockChart.GetDataValue(0, i)
            item['시가'] = objStockChart.GetDataValue(1, i)
            item['고가'] = objStockChart.GetDataValue(2, i)
            item['저가'] = objStockChart.GetDataValue(3, i)
            item['종가'] = objStockChart.GetDataValue(4, i)
            item['거래량'] = objStockChart.GetDataValue(5, i)

            print(item)

        if (objStockChart.Continue == False):
            print('연속플래그 없음')
            break

    return True        

# 분/틱 차트 조회 - 개수로 조회
def chart_simple3(dwm, code, cnt) :
    objStockChart = win32com.client.Dispatch("CpSysDib.StockChart")
    objStockChart.SetInputValue(0, code)  # 종목 코드 - 삼성전자
    objStockChart.SetInputValue(1, ord('2'))  # 개수로 조회
    objStockChart.SetInputValue(4, cnt)
    objStockChart.SetInputValue(5, [0, 1, 2, 3, 4, 5, 8])  # 날짜,시간, 시가,고가,저가,종가,거래량
    objStockChart.SetInputValue(6, dwm)  # '차트 주기
    objStockChart.SetInputValue(8, ord('0')) # 갭보정여부(char)
    objStockChart.SetInputValue(9, ord('1'))  # 수정주가(char) - '0': 무수정 '1': 수정주가
    objStockChart.SetInputValue(10, ord('1')) # 거래량구분(char) - '1' 시간외거래량모두포함[Default]


    totlen = 0
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
        totlen += clen
        print(totlen)

        print("날짜", "시간", "시가", "고가", "저가", "종가", "거래량")

        for i in range(0, clen) :
            item = {}
            item['날짜'] = objStockChart.GetDataValue(0, i)
            item['시간'] = objStockChart.GetDataValue(1, i)
            item['시가'] = objStockChart.GetDataValue(2, i)
            item['고가'] = objStockChart.GetDataValue(3, i)
            item['저가'] = objStockChart.GetDataValue(4, i)
            item['종가'] = objStockChart.GetDataValue(5, i)
            item['거래량'] = objStockChart.GetDataValue(6, i)

            print(item)

        if (objStockChart.Continue == False):
            print('연속플래그 없음')
            break
        if totlen >= cnt :
            break

    return True        

def chart_rq1() :
    chart_simple1(ord('D'), 'A005930', 100)
def chart_rq2() :
    chart_simple1(ord('D'), 'A005930', 5000)
def chart_rq3() :
    chart_simple2(ord('D'), 'A005930', 20200102, 20200417)
def chart_rq4() :
    chart_simple2(ord('D'), 'A005930', 19800104, 20200417)
def chart_rq5() :
    chart_simple1(ord('W'), 'A005930', 100)
def chart_rq6() :
    chart_simple1(ord('M'), 'A005930', 100)
def chart_rq7() :
    chart_simple3(ord('m'), 'A005930', 100)
def chart_rq8() :
    chart_simple3(ord('m'), 'A005930', 5000)


def info_7221(): 
    print('[투자자별 매매종합] CpSysDib.CpSvrNew7221')
    objRq = win32com.client.Dispatch('CpSysDib.CpSvrNew7221')
    objRq.SetInputValue(0, ord('1')) # 옵션금액 선물 계약
    objRq.BlockRequest()
    rqStatus = objRq.GetDibStatus()
    if rqStatus != 0:
        print("통신상태", rqStatus, objRq.GetDibMsg1())
        return False


    time = objRq.GetHeaderValue(0) # 시간
    cnt = objRq.GetHeaderValue(1)  # 시장구분수
    print(time, cnt)

    index = 0 # 거래소 주식
    name = '거래소주식'
    print(name)
    item = {}
    item['개인순매수'] = objRq.GetDataValue(2, index) 
    item['외국인순매수'] = objRq.GetDataValue(5, index) 
    item['기관순매수'] = objRq.GetDataValue(8, index)  
    print(item)

    index = 1 # 거래소 주식
    name = '코스닥주식'
    print(name)
    item = {}
    item['개인순매수'] = objRq.GetDataValue(2, index) 
    item['외국인순매수'] = objRq.GetDataValue(5, index) 
    item['기관순매수'] = objRq.GetDataValue(8, index)  
    print(item)



    index = 2 # 선물
    name = '선물'
    print(name)
    item = {}
    item['개인순매수'] = objRq.GetDataValue(2, index) 
    item['외국인순매수'] = objRq.GetDataValue(5, index) 
    item['기관순매수'] = objRq.GetDataValue(8, index) 
    print(item)

    index = 3 #
    name = '옵션콜'
    print(name)
    item = {}
    item['개인순매수'] = objRq.GetDataValue(2, index) 
    item['외국인순매수'] = objRq.GetDataValue(5, index) 
    item['기관순매수'] = objRq.GetDataValue(8, index) 
    print(item)

    index = 4 #
    name = '옵션풋'
    print(name)
    item = {}
    item['개인순매수'] = objRq.GetDataValue(2, index) 
    item['외국인순매수'] = objRq.GetDataValue(5, index) 
    item['기관순매수'] = objRq.GetDataValue(8, index) 
    print(item)


def info_7254_6() : 
    ret, datas = rq_7254('A005930', 6, ord('1'), 100)
    if ret == False :
        return
    
    for data in datas : 
        print(data)


def info_7254_3() : 
    ret, datas = rq_7254('A005930', 3, ord('1'), 100)
    if ret == False :
        return
    
    for data in datas : 
        print(data)

def info_7035() : 
    objRq = win32com.client.Dispatch("DsCbo1.StockIndexIR")
    objRq.SetInputValue(0, 'U001')      # 업종코드 - U + 업종코드

    while True:
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()

        # 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        if rqStatus != 0:
            print("통신상태", rqStatus, objRq.GetDibMsg1())
            return False

        cnt = objRq.GetHeaderValue(1)
        for i in range(cnt):
            item = {}
            item['시간'] = objRq.GetDataValue(0, i)  # 시간
            item['지수'] = objRq.GetDataValue(1, i)  # 지수
            item['전일대비'] = objRq.GetDataValue(2, i)  # 전일대비
            item['거래량'] = objRq.GetDataValue(3, i)  # 거래량
            item['거래대금'] = objRq.GetDataValue(4, i)  # 거래대금
            print(item)

        if objRq.Continue == False:
            break    

def info_7021() : 
    objRq = win32com.client.Dispatch("Dscbo1.StockMst")
    objRq.SetInputValue(0, 'A005930')
    objRq.BlockRequest()

    # 통신 및 통신 에러 처리
    rqStatus = objRq.GetDibStatus()
    rqRet = objRq.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        return False

    # 각 번호별 의미는 도움말 참고 
    for i in range(85):
        item = {}
        item[str(i)] = objRq.GetHeaderValue(i)
        print(item)


def info_8091() : 
    objRq = win32com.client.Dispatch('Dscbo1.CpSvr8091')
    objRq.SetInputValue(0, ord('5')) # 단일종목+외국계전체
    objRq.SetInputValue(2, 'A005930')

    totcnt = 0
    while True:
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()
        # 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        cnt = objRq.GetHeaderValue(0)
        totcnt  = totcnt + cnt
        for i in range(cnt):
            item = {}
            item['시간'] = objRq.GetDataValue(0, i)
            item['회원사명'] = objRq.GetDataValue(1, i)
            item['종목코드'] = objRq.GetDataValue(2, i)
            item['종목명'] = objRq.GetDataValue(3, i)
            item['매도/매수'] = objRq.GetDataValue(4, i)
            item['매수/매도량'] = objRq.GetDataValue(5, i)
            item['순매수'] = objRq.GetDataValue(6, i)
            item['순매수부호'] = objRq.GetDataValue(7, i)
            item['상태구분'] = objRq.GetDataValue(8, i)
            item['현재가등락율'] = objRq.GetDataValue(9, i)
            item['외국계전체누적순매수'] = objRq.GetDataValue(10, i)
            print(item)

        if objRq.Continue == False:
            break    
        if totcnt > 500:
            break

def info_7024():
    objRq = win32com.client.Dispatch("Dscbo1.StockBid")
    objRq.SetInputValue(0, 'A005930')
    objRq.SetInputValue(2, 80) # 요청개수
    objRq.SetInputValue(2, ord('C'))  # 'C': 체결가 비교방식, 'H' 호가 비교 방식

    totcnt = 0
    while True:
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()

        # 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        cnt = objRq.GetHeaderValue(2)
        totcnt += cnt
        for i in range(cnt):
            item = {}
            item['시각']= objRq.GetDataValue(9, i)  # 시각
            item['현재가']= objRq.GetDataValue(3, i)
            item['대비']= objRq.GetDataValue(1, i)
            item['현재가']= objRq.GetDataValue(3, i)
            item['순간체결량']= objRq.GetDataValue(6, i)
            item['거래량']= objRq.GetDataValue(5, i)
            flag = objRq.GetDataValue(7, i)
            if (flag == ord('1')) :
                item['매수매도'] = '매수'
            else:
                item['매수매도'] = '매도'
            exflag = objRq.GetDataValue(10, i)
            if (exflag == ord('1')) :
                item['장구분'] = '예상'
            else:
                item['장구분'] = '장중'
            print(item)

        if objRq.Continue == False:
            break
        if totcnt > 1000:
            break


def info_7026():
    objRq = win32com.client.Dispatch('Dscbo1.StockWeek')
    objRq.SetInputValue(0, 'A005930')
    sumcnt = 0

    while True:
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()
        # 현재가 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        if rqStatus != 0:
            return False

        cnt = objRq.GetHeaderValue(1)
        sumcnt += cnt
        print(cnt, sumcnt)

        for i in range(cnt):
            item = {}

            item['일자'] = objRq.GetDataValue(0, i)
            item['시가'] = objRq.GetDataValue(1, i)
            item['고가'] = objRq.GetDataValue(2, i)
            item['저가'] = objRq.GetDataValue(3, i)
            item['종가'] = objRq.GetDataValue(4, i)
            item['전일대비'] = objRq.GetDataValue(5, i)
            item['누적거래량'] = objRq.GetDataValue(6, i)
            item['외인보유'] = objRq.GetDataValue(7, i)
            item['외인보유전일대비'] = objRq.GetDataValue(8, i)
            item['등락률'] = objRq.GetDataValue(10, i)
            diffflag = objRq.GetDataValue(11, i)
            if diffflag == ord('4') or diffflag == ord('5') or diffflag == ord('8') or diffflag == ord('9') : 
                item['전일대비'] = item['전일대비'] * -1
                item['등락률'] = item['등락률'] * -1

            item['거래대금'] = objRq.GetDataValue(20, i)
            item['외국인순매수수량'] = objRq.GetDataValue(21, i)
            print(item)

        if (objRq.Continue == False):
            break
    
        if sumcnt > 100 : 
            break

def info_8114():
    objRq = win32com.client.Dispatch("CpSysDib.CpSvr8114")
    objRq.SetInputValue(0, ord('1'))  # 거래소
    objRq.SetInputValue(1, ord('2'))  # 시가총액상위순
    #        objRq.SetInputValue(4, ord('1'))  # 계약/금액 구분/옵션일 때만 유효

    objRq.BlockRequest()

    # 통신 및 통신 에러 처리
    rqStatus = objRq.GetDibStatus()
    rqRet = objRq.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        return False

    cnt = objRq.GetHeaderValue(0)
    for i in range(cnt):
        item = {}
        item['종목코드'] = objRq.GetDataValue(0, i)
        item['종목명'] = objRq.GetDataValue(1, i)
        item['시가총액'] = objRq.GetDataValue(2, i)
        item['매도잔량'] = objRq.GetDataValue(3, i)
        item['매수잔량'] = objRq.GetDataValue(5, i)
        item['순매수'] = objRq.GetDataValue(7, i)
        print(item)

def info_7223_1():
    objRq = win32com.client.Dispatch("DsCbo1.CpSvr7223")
    objRq.SetInputValue(0, ord('4'))  # 일자별 업종 투자자 매매 현황
    objRq.SetInputValue(1, '001')     # 업종코드

    totCnt = 0
    while True:
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()

        # 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        cnt = objRq.GetHeaderValue(1)
        totCnt = totCnt + cnt
        print(cnt)
        for i in range(cnt):
            item = {}
            item['일자'] =objRq.GetDataValue(0, i)  
            item['개인'] =objRq.GetDataValue(1, i)  
            item['외국인'] =objRq.GetDataValue(2, i)
            item['기관'] =objRq.GetDataValue(3, i)  
            item['금융투자'] =objRq.GetDataValue(4, i)  
            item['보험'] =objRq.GetDataValue(6, i)  
            item['투신'] =objRq.GetDataValue(6, i)  
            item['연기금'] =objRq.GetDataValue(9, i)  
            print(item)

        if objRq.Continue == False:
            break
        if totCnt > 500 :
            break


def info_7223_2():
    objRq = win32com.client.Dispatch("DsCbo1.CpSvr7223")
    objRq.SetInputValue(0, ord('1'))  # 장내

    totCnt = 0
    while True:
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()

        # 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        cnt = objRq.GetHeaderValue(1)
        totCnt = totCnt + cnt
        print(cnt)
        for i in range(cnt):
            item = {}
            item['업종명'] =objRq.GetDataValue(0, i)  
            item['개인'] =objRq.GetDataValue(1, i)  
            item['외국인'] =objRq.GetDataValue(2, i)
            item['기관'] =objRq.GetDataValue(3, i)  
            item['금융투자'] =objRq.GetDataValue(4, i)  
            item['보험'] =objRq.GetDataValue(6, i)  
            item['투신'] =objRq.GetDataValue(6, i)  
            item['연기금'] =objRq.GetDataValue(9, i)  
            print(item)

        if objRq.Continue == False:
            break
        if totCnt > 500 :
            break


def info_7222_1():
    objRq = win32com.client.Dispatch("CpSysDib.CpSvrNew7222")
    objRq.SetInputValue(0, ord('A')) # 'A' : 시장전체
    objRq.SetInputValue(1, 2)      #  투자자, 0 전체 1 개인 2 외국인, 3 기관계
    objRq.SetInputValue(2, ord('1'))  # 1: 누적, 2: 증감
    objRq.SetInputValue(4, ord('1'))  # 계약/금액 구분/옵션일 때만 유효
    totCnt = 0

    while (1) : 
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()

        # 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        cnt = objRq.GetHeaderValue(0)
        totCnt = totCnt + cnt
        for i in range(cnt):
            item = {}
            item['시간'] = objRq.GetDataValue(0, i)
            item['거래소'] = objRq.GetDataValue(1, i)
            item['코스닥']= objRq.GetDataValue(2, i) 
            item['선물'] = objRq.GetDataValue(3, i)  
            item['콜옵션계약'] = objRq.GetDataValue(4, i) 
            item['콜옵션금액'] = objRq.GetDataValue(5, i) 
            item['풋옵션계약'] = objRq.GetDataValue(6, i) 
            item['풋옵션금액'] = objRq.GetDataValue(7, i) 
            print(item)

        if objRq.Continue == False:
            break
        if totCnt > 100 :
            break


def info_7222_2():
    objRq = win32com.client.Dispatch("CpSysDib.CpSvrNew7222")
    objRq.SetInputValue(0, ord('B')) # 'B' : 거래소
    objRq.SetInputValue(1, 0)      #  투자자, 0 전체 1 개인 2 외국인, 3 기관계
    objRq.SetInputValue(2, ord('1'))  # 1: 누적, 2: 증감
    objRq.SetInputValue(4, ord('1'))  # 계약/금액 구분/옵션일 때만 유효
    totCnt = 0

    while (1) : 
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()

        # 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        cnt = objRq.GetHeaderValue(0)
        totCnt = totCnt + cnt
        for i in range(cnt):
            item = {}
            item['시간'] = objRq.GetDataValue(0, i)
            item['개인'] = objRq.GetDataValue(1, i)
            item['외국인']= objRq.GetDataValue(2, i) 
            item['기관계'] = objRq.GetDataValue(3, i)  
            item['금융투자'] = objRq.GetDataValue(4, i) 
            item['보험'] = objRq.GetDataValue(5, i) 
            item['투신'] = objRq.GetDataValue(6, i) 
            item['은행'] = objRq.GetDataValue(7, i) 
            item['연기금'] = objRq.GetDataValue(9, i) 
            print(item)

        if objRq.Continue == False:
            break
        if totCnt > 100 :
            break

def info_8412():
    objRq=win32com.client.Dispatch("Dscbo1.CpSvr8412")
    objRq.SetInputValue(0, 'A005930')
    objRq.SetInputValue(1, 888) # 회원사 코드 888: 외국계전체

    objRq.BlockRequest()
    rqStatus = objRq.GetDibStatus()
    rqRet = objRq.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        exit()

    cnt = objRq.GetHeaderValue(0)
    print(cnt)

    for i in range(cnt):
        item = {}
        item['일자'] =  objRq.GetDataValue(0, i)
        item['매수수량'] =  objRq.GetDataValue(1, i)
        item['매도수량'] =  objRq.GetDataValue(2, i)
        item['순매수'] =  objRq.GetDataValue(3, i)
        item['종가'] =  objRq.GetDataValue(4, i)
        item['전일대비'] =  objRq.GetDataValue(5, i)
        item['거래량'] =  objRq.GetDataValue(6, i)
        print(item)

def info_mst2():
    objRq=win32com.client.Dispatch("Dscbo1.StockMst2")
    # 요청할 종목 리스트 대신증권, 하이닉스, 거래소업종, 코스닥업종
    codeList = 'A003540,A000660,U001,U201'
    objRq.SetInputValue(0, codeList)
    objRq.BlockRequest()
    cnt = objRq.GetHeaderValue(0)

    for i in range(cnt) :
        item = {}
        item['코드'] = objRq.GetDataValue(0, i)
        item['종목명'] = objRq.GetDataValue(1, i)
        item['현재가'] = objRq.GetDataValue(3, i)  # 업종은 나누기 100 해야 함.
        item['상장주식수'] = objRq.GetDataValue(17,i)
        item['거래대금'] = objRq.GetDataValue(12,i)
        item['1차매도잔량'] = objRq.GetDataValue(15,i)
        item['1차매수잔량'] = objRq.GetDataValue(16,i)
        print(item)

def info_marketeye():
    # 관심종목 객체 구하기
    objRq = win32com.client.Dispatch("CpSysDib.MarketEye")
    # 요청 필드 세팅 - 종목코드, 종목명, 시간, 대비부호, 대비, 현재가, 거래량
    codes = ["A003540", "A000660", "A005930", "A035420", "A069500", "Q530031", 'A060250', 'A950180']

    # 요청 필드 배열 - 종목코드, 대비부호, 대비, 현재가, 시가, 고가, 저가, 거래량, 거래대금
    rqField = [0, 2, 3, 4, 5, 6, 7, 10, 11]  # 요청 필드

    objRq.SetInputValue(0, rqField)  # 요청 필드
    objRq.SetInputValue(1, codes)  # 종목코드 or 종목코드 리스트
    objRq.BlockRequest()

    # 현재가 통신 및 통신 에러 처리
    rqStatus = objRq.GetDibStatus()
    rqRet = objRq.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        return False

    cnt = objRq.GetHeaderValue(2)

    for i in range(cnt):
        item = {}
        item['코드'] = objRq.GetDataValue(0, i)
        item['종목명'] = g_objCodeMgr.CodeToName(item['코드'])
        item['대비'] = objRq.GetDataValue(2, i)
        item['현재가'] = objRq.GetDataValue(3, i)
        item['시가'] = objRq.GetDataValue(4, i)
        item['고가'] = objRq.GetDataValue(5, i)
        item['저가'] = objRq.GetDataValue(6, i)
        item['거래량'] = objRq.GetDataValue(7, i)
        item['거래대금'] = objRq.GetDataValue(8, i)
        print(item)
    return True

def info_8119():
    objRq = win32com.client.Dispatch("DsCbo1.CpSvrNew8119Day")
    # 조회 구분 0 - (char)  조회구분  ('0':최근5일,'1:한달, '2':3개월, '3':6개월)
    objRq.SetInputValue(0, ord("3"))
    objRq.SetInputValue(1, 'A005930')
    objRq.BlockRequest()

    while True :
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()
        cnt = objRq.GetHeaderValue(0)
        print(cnt)

        item = {}
        for i in range(cnt):
            item['일자'] = objRq.GetDataValue(0, i)  # 일자
            item['현재가'] = objRq.GetDataValue(1, i)  
            item['전일대비'] = objRq.GetDataValue(2, i)  
            item['거래량'] = objRq.GetDataValue(4, i)  
            item['순매수증감수량'] = objRq.GetDataValue(7, i)  
            item['순매수누적수량'] = objRq.GetDataValue(8, i)  
            print(item)

        if objRq.Continue == False:
            break

def info_7043_1() :
    objRq = win32com.client.Dispatch("CpSysDib.CpSvrNew7043")
    objRq.SetInputValue(0, ord('0')) # 거래소 + 코스닥
    objRq.SetInputValue(1, ord('1')) # 선택기준: 1 상한
    objRq.SetInputValue(2, ord('1')) # 기준일자구분: 당일 : 1, 전일 : 2
    objRq.SetInputValue(3, 31) # 순서구분: 연속일수 상위순 
    objRq.SetInputValue(4, ord('2')) # 관리구분: 1 관리 종목 제외 2 관리 포함
    objRq.SetInputValue(5, ord('0')) # 거래량구분: 0: 거래량 전체


    while True:
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()

        cnt = objRq.GetHeaderValue(0)
        cntTotal = objRq.GetHeaderValue(1)
        print("종목수 및 총 종목수", cnt, cntTotal)


        for i in range(cnt):
            items = {}
            items['코드'] = objRq.GetDataValue(0, i)
            items['종목명'] = objRq.GetDataValue(1, i) 
            items['현재가'] = objRq.GetDataValue(2, i) 
            items['대비플래그'] = objRq.GetDataValue(3, i) 
            items['대비'] = objRq.GetDataValue(4, i) 
            items['대비율'] = objRq.GetDataValue(5, i) 
            items['거래량'] = objRq.GetDataValue(6, i) 
            items['매수호가'] = objRq.GetDataValue(8, i) 
            items['연속일수'] = objRq.GetDataValue(10, i) 
            print(items)

        if objRq.Continue == False:
            break    

def info_7043_2() :
    objRq = win32com.client.Dispatch("CpSysDib.CpSvrNew7043")
    objRq.SetInputValue(0, ord('0')) # 거래소 + 코스닥
    objRq.SetInputValue(1, ord('2')) # 선택기준: 2: 상승
    objRq.SetInputValue(2, ord('1')) # 기준일자구분: 1: 당일
    objRq.SetInputValue(3, 21) # 순서구분: 전일대비율 상위순
    objRq.SetInputValue(4, ord('2')) # 관리구분: 1 관리 종목 제외 2 관리 포함
    objRq.SetInputValue(5, ord('0')) # 거래량구분: 0: 거래량 전체
    objRq.SetInputValue(6, ord('0')) # 표시항목: 시가대비
    objRq.SetInputValue(7, 20) # 등락율 시작
    objRq.SetInputValue(8, 30) # 등락율 끝

    totCnt = 0

    while True:
        waitRqLimit(Rqtype.SISE)
        objRq.BlockRequest()

        cnt = objRq.GetHeaderValue(0)
        totCnt = totCnt + cnt
        cntTotal = objRq.GetHeaderValue(1)
        print("종목수 및 총 종목수", cnt, cntTotal)


        for i in range(cnt):
            items = {}
            items['코드'] = objRq.GetDataValue(0, i)
            items['종목명'] = objRq.GetDataValue(1, i) 
            items['현재가'] = objRq.GetDataValue(2, i) 
            items['대비플래그'] = objRq.GetDataValue(3, i) 
            items['대비'] = objRq.GetDataValue(4, i) 
            items['대비율'] = objRq.GetDataValue(5, i) 
            items['거래량'] = objRq.GetDataValue(6, i) 
            items['시가'] = objRq.GetDataValue(7, i) 
            items['시가대비'] = objRq.GetDataValue(8, i) 
            items['연속일수'] = objRq.GetDataValue(10, i) 
            print(items)

        if objRq.Continue == False:
            break    

        if totCnt > 500: 
            break


def exit_prog():
    exit(1)

if __name__ == "__main__":

    InitPlusCheck(True)

    # 함수 호출 테이블 
    plusAPI = {100: getCode_AllCode,
            101: getCode_Inducstry,
            102: getCode_ETF,
            103: getCode_K200,
            104: getCode_Future,
            105: getCode_Option,
            106: getCode_ETN,
            200: chart_rq1,
            201: chart_rq2,
            202: chart_rq3,
            203: chart_rq4,
            204: chart_rq5,
            205: chart_rq6,
            206: chart_rq7,
            207: chart_rq8,
            300: info_7221, 
            301: info_7254_6,
            302: info_7254_3,
            303: info_7035,
            304: info_7021,
            305: info_8091,
            306: info_7024,
            307: info_7026,
            308: info_8114,
            309: info_7223_1,
            310: info_7223_2,
            311: info_7222_1,
            312: info_7222_2,
            313: info_8412,
            314: info_mst2,
            315: info_marketeye,
            316: info_8119,
            317: info_7043_1,
            318: info_7043_2,

            999: exit_prog}

    sAsk = '원하는 숫자를 입력하세요\n'
    sAsk += '------------------------------------------\n'
    sAsk += '100: 거래소/코스닥 구하기 \n'
    sAsk += '101: 업종 구하기 \n'
    sAsk += '102: ETF 구하기 \n'
    sAsk += '103: 코스피200 종목 구하기 \n'
    sAsk += '104: 선물종목 구하기 \n'
    sAsk += '105: 옵션종목 구하기 \n'
    sAsk += '106: ETN 종목 구하기 \n'
    # sAsk += '106: ETF 구하기 \n'
    sAsk += '------------------------------------------\n'
    sAsk += '200: 일간차트 -  100일 \n'
    sAsk += '201: 일간차트 - 5000일\n'
    sAsk += '202: 일간차트/기간 2020.1.2~2020.4.17 \n'
    sAsk += '203: 일간차트/기간 1980.01.04~2020.4.17 \n'
    sAsk += '204: 주간차트 -  100주 \n'
    sAsk += '205: 월간차트 -  100개월 \n'
    sAsk += '206: 1분차트 -  100개 \n'
    sAsk += '207: 1분차트 -  5000개 \n'

    sAsk += '------------------------------------------\n'
    sAsk += '300: 투자자별 매매종합 7221  \n'
    sAsk += '301: 투자주체별 매매현황 7254 - 기간별 조회  \n'
    sAsk += '302: 투자주체별 매매현황 7254 - 3개월 누적조회 \n'
    sAsk += '303: 업종지수 - 1분\n'
    sAsk += '304: 주식 현재가 기본 통신\n'
    sAsk += '305: 회원사 매매 현황\n'
    sAsk += '306: 주식종목 시간대별 체결\n'
    sAsk += '307: 주식종목 일자별 체결\n'
    sAsk += '308: 프로그램매매 호가잔량\n'
    sAsk += '309: 업종별 투자자 매매현황 - 업종 일자별\n'
    sAsk += '310: 업종별 투자자 매매현황 - 거래소/당일\n'
    sAsk += '311: 시간대별 투자자매매추이 - 시장: 전체, 투자자: 외국인\n'
    sAsk += '312: 시간대별 투자자매매추이 - 시장: 거래소, 투자자: 전체 \n'
    sAsk += '313: 회원별 매매동향 - 종목 일자별 \n'
    sAsk += '314: 주식복수 종목 조회(StockMst2) \n'
    sAsk += '315: 주식복수 종목 조회(MarketEye) \n'
    sAsk += '316: 종목별 프로그램매매 추이(일자별) \n'
    sAsk += '317: 주식 등락현황 (상승/하락/상한/하한조회) - 상한조회 \n'
    sAsk += '318: 주식 등락현황 (상승/하락/상한/하한조회) - 상승조회 20%~30% \n'


    sAsk += '------------------------------------------\n'
    sAsk += '------------------------------------------\n'
    sAsk += '------------------------------------------\n'
    sAsk += '999: 끝내기 \n'

    while (1):
        number = input(sAsk)
        try:
            plusAPI[int(number)]()
        except KeyError:
            exit(1)
