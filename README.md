<br>


# [HANSUNG STOCK] 딥러닝을 이용한 주가 예측 및 주식 매매 자동화 웹 서비스

<br>

<h2>목차</h2>

 - [소개](#소개) 
 - [팀원](#팀원) 
 - [개발 환경](#개발-환경)
 - [사용 기술](#사용-기술)
 - [시스템 아키텍처](#시스템-아키텍처) 
 - [화면 구성](#화면-구성)
 - [핵심 기능](#핵심-기능)
   - [Web](#web)
   - [Deep Learning](#deep-learning)
   - [Text Mining](#text-mining)
 - [Trouble Shooting](#trouble-shooting)


## 소개

**HANSUNG STOCK**는 각 분기 별 재무 데이터를 전처리, 특징을 추출하여 Keras를 이용해 딥러닝하고, 동시에 트위터 API tweepy로 수집한 SNS 데이터와 뉴스 기사 웹 크롤링으로 최근 동향을 Logistic Regression 감성 분석하여 예측된 결과를 기반으로 특정 종목을 추천하고, 변동성 돌파 전략을 이용한 자동 매매 시스템 및 기본적인 매매 인터페이스를 웹 서비스로 제공합니다. <br>

## 팀원

<table>
   <tr>
    <td align="center"><b><a href="https://github.com/IDeal7">정병현</a></b></td>
    <td align="center"><b><a href="https://github.com/yerim1004">김예림</a></b></td>
    <td align="center"><b><a href="https://github.com/jeeyoun-kang">강지윤</a></b></td>
    <td align="center"><b><a href="https://github.com/kyung412820">이경훈</a></b></td>
  <tr>
     <td align="center"><a href="https://github.com/IDeal7"><img src="https://avatars.githubusercontent.com/u/65962500?v=4" width="100px" /></a></td>
    <td align="center"><a href="https://github.com/yerim1004"><img src="https://avatars.githubusercontent.com/u/57720521?v=4" width="100px" /></a></td>
     <td align="center"><a href="https://github.com/jeeyoun-kang"><img src="https://avatars.githubusercontent.com/u/59076085?v=4" width="100px" /></a></td>
    <td align="center"><a href="https://github.com/kyung412820"><img src="https://avatars.githubusercontent.com/u/71320521?v=4" width="100px" /></a></td>
  </tr>
  <tr>
    <td align="center"><b>프로젝트 총괄</b></td>
    <td align="center"><b>Text Mining</b></td>
    <td align="center"><b>Web Developer</b></td>
    <td align="center"><b>Deep Learning</b></td>
</table>


## 개발 환경

 - Windows
 - Visual Code
 - GitHub



## 사용 기술 

- Library & Framework : Django, Sklearn, Keras, BeautifulSoup, Tweepy API, Creon API, KonlPy
- DB :Mysql
- Language : Python, Javascript, SQL, HTML



## 시스템 아키텍처

![hansung](https://user-images.githubusercontent.com/59076085/227718602-9125dfb4-519b-4e2c-90f9-a3248f7e6fb9.JPG)



## 💻 프로젝트 시연영상

[![Video Label](https://user-images.githubusercontent.com/59076085/227719172-a1ca931c-e28f-45d4-86c0-b89df5e0f5e1.png)](https://www.youtube.com/watch?v=34SGj0jQv7M)

## 핵심 기능

### Web

- 대신증권 CYBOS Plus api를 이용해 로그인을 하고 원하는 데이터를 파싱해 계좌정보를 출력했습니다.
- CYBOS Plus api에서 제공하는 함수로 원하는 데이터들을 append한 뒤 JSON.parse()를 이용해 데이터를 가공한 후 chart.js 라이브러리를 이용해 구현하였습니다.
  - [차트 구현](https://github.com/jeeyoun-kang/HASUNG-STOCK/blob/50af70f98312f416d3c2118277768fa550ce5d7c/mysite/polls/templates/polls/main.html#L1070)

- BeautifulSoup를 이용해 종목이름으로 원하는 top5 뉴스를 크롤링해 뉴스 롤링배너를 구현하였습니다.
  - [뉴스 롤링 배너 구현](https://github.com/jeeyoun-kang/HASUNG-STOCK/blob/50af70f98312f416d3c2118277768fa550ce5d7c/mysite/polls/views.py#L96)

- request.POST.get() 메소드를 이용해 원하는 종목이름을 입력하면 해당하는 종목코드로 종목에 대한 정보를 검색한 결과를 출력하게 구현하였습니다.
- 정해진 시간대에 설정한 자동매매 로직에 따라 매수를 하게 만든 후 장 종료 5분전부터 일괄 매도하게 만들어 자동매매를 구현하였습니다.
  - [자동매매 로직](https://github.com/jeeyoun-kang/HASUNG-STOCK/blob/master/mysite/polls/stock.py)


### Deep Learning

- Data Guide를 이용해 추출한 데이터들을 활성화 함수(Sigmoid,Relu)함수, 모델을 Sequential로 사용해서 AI를 제작해 DL TOP20과 Volumn Rising을 구현하였습니다.
  - [DL TOP20 & Volumn Rising](https://github.com/jeeyoun-kang/HASUNG-STOCK/blob/master/Deep%20Learning/final.ipynb)

### Text Mining

- Twitter에서 제공하는 Tweepy Api, BeautifulSoup으로 수집 대상인 회사와 관련된 트윗 및 기사를 수집했습니다.
  - [BeautifulSoup을 이용한 기사 크롤링](https://github.com/jeeyoun-kang/HASUNG-STOCK/blob/50af70f98312f416d3c2118277768fa550ce5d7c/Text%20Mining/pos_neg.py#L92)
  - [TwitterApi를 이용한 SNS 데이터 크롤링](https://github.com/jeeyoun-kang/HASUNG-STOCK/blob/6c9c7b493b154e3c03195516b50689d7266f42ef/Text%20Mining/TwitCrawling.ipynb?short_path=035a699#L197)

- KonlPy를 이용해 수집된 데이터 모델을 구축하고, LogisticRegression 함수를 이용해 모델 학습을 진행했습니다.
  - [데이터를 분석해 벡터화](https://github.com/jeeyoun-kang/HASUNG-STOCK/blob/50af70f98312f416d3c2118277768fa550ce5d7c/Text%20Mining/pos_neg.py#L171)

- 분류된 데이터를 바탕으로 탐욕-공포 그래프를 구현했습니다.


## Trouble Shooting

- 데이터를 전처리하는 과정, 실제 사용가능한 데이터로 만드는 과정에서 데이터의 정확도 문제가 발생하였습니다.
  - Keras에서 제공하는 Sequential모델을 이용해 비교적 가장 높은 확률의 원하는 결과를 얻을 수 있었습니다.

- 자동매매를 구현하는 과정에서 설정한 로직으로 인해 장이 종료될때까지 방해받지 않고 프로세스가 돌아가야되는 문제가 발생하였습니다.
  - [subprocess의 Popen() 메소드](https://github.com/jeeyoun-kang/HASUNG-STOCK/blob/50af70f98312f416d3c2118277768fa550ce5d7c/mysite/polls/views.py#L654)를 이용해 서브 프로세스가 돌아가게끔 구현을 해 문제를 해결하였습니다.

- SNS 데이터를 불러오기 위해 사용하는 함수는 100개 이상의 데이터를 한 번에 가져올 수가 없었습니다.
  - 함수를 변형, 반복하여 과거 데이터까지 수집할 수 있었습니다.

- 홈페이지에 관련 기사를 연결하는 과정에서 이미지가 없는 기사를 구현할 때 오류가 발생하는 문제가 있었습니다.
  - 이미지가 존재하지 않는 경우 설정한 defalut 이미지로 대체했습니다.

