#!/usr/bin/env python
# coding: utf-8

# In[2]:


#사전에 만든 posneg 단어 리스트 가져오기

with open("./pos_word.txt", encoding = 'utf-8') as pos:
    positive = pos.readlines()
    positive = [pos.replace("\n", "") for pos in positive]

with open("./neg_word.txt", encoding = 'utf-8') as neg:
    negative = neg.readlines()
    negative = [neg.replace("\n", "") for neg in negative]

positive


# In[2]:


#기존 데이터로 라벨링
import re
import pandas as pd

labels = []
datas = []
j = 0

with open("./samsung_twit_list.txt", encoding = 'utf-8') as samsung:
    while True:
        data = samsung.readline()
        if not data: 
            break
        clean_data = re.sub('[-=+,#/\?:^$.@*\"~&%!※]', '', data)
        #my_data_dic["line"].append(data)
        negflag = False

        label = 0
        for i in range(len(negative)):
            if negative[i] in clean_data:
                label = 1
                negflag = True
                print("negative 비교단어: ", negative[i], "clean_data: ", clean_data)
                break
        if negflag == False:
            for i in range(len(positive)):
                if positive[i] in clean_data:
                    label = 0
                    print("positive 비교단어: ", positive[i], "clean_data: ", clean_data)
                    break
        datas.append(clean_data)
        labels.append(label)


my_data_df = pd.DataFrame({"data":datas, "label":labels})


# In[3]:


#기사 크롤링 하면서 라벨링
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

labels = []
clean_titles = []
name = ['삼성전자', 'LG에너지솔루션' '현대차', 'SK하이닉스', '삼성SDI', 'POSCO홀딩스', '삼성바이오로직스', '삼성전자우', '카카오',
        '기아', '신한지주', '삼성물산', '셀트리온', '카카오뱅크', '현대모비스', 'LG화학', 'SK', 'SK이노베이션', 'NAVER', 'KB금융', '삼성물산', '신한지주', 
       '셀트리온', 'SK이노베이션', '카카오뱅크', '현대모비스', 'SK', 'LG전자' '한국전력', 'HMM', '하나금융지주', '삼성생명', 'SK텔레콤', '두산에너빌리티',
       'S-Oil', 'LG', '삼성전기', '크래프톤', '카카오페이', 'KT&G', '우리금융지주', '삼성에스디에스', '현대중공업', '고려아연', 'LG생활건강', '대한항공' ,'포스코케미칼',
       '삼성화재', '엔씨소프트', 'KT', 'SK바이오사이언스', '아모레퍼시픽', '하이브', '기업은행', '현대글로비스', '롯데케미칼', '한국조선해양', '넷마블', 'SK바이오팜', 'SK스퀘어',
       'LG디스플레이', 'CJ제일제당', '한화솔루션', '한온시스템', '강원랜드', 'LG유플러스', '맥쿼리인프라', '현대제철', 'SKC', 'F&F', 'KODEX200', '코웨이', '삼성엔지니어링', '삼성중공업',
       '에스디바이오센서', '미래에셋증권', '현대건설' ,'HD현대', '메리츠화재', '한국항공우주', '금호석유', '한국타이어앤테크놀로지', '팬오션', 'GS', 'DB손해보험', '유한양행',
       '메리츠금융지주', '한국가스공사', '일진머티리얼즈', '두산밥캣', '메리츠증권', '삼성카드', '한국금융지주', '한진칼', '한미약품', '쌍용C&E', '아모레G', '오리온', '롯데지주', '이마트',
       '현대오토에버', '현대차2우B', '삼성증권', 'GS건설', 'NH투자증권']

j = 0

for n in range(len(name)):
    for k in range(1, 400, 10):
        num = k
        url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + name[n] + "&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=55&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all,a:all&start=" + str(num)

        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')
        titles = soup.select("ul.list_news > li")
        for title in titles:
            title_data = title.select_one("a.news_tit").text
            clean_title = re.sub('[-=+,#/\?:^$.@*\"~&%!※]', '', title_data)
            negative_flag = False

            label = 0
            for i in range(len(negative)):
                if negative[i] in clean_title:
                    label = 1
                    negative_flag = True
                    print("negative 비교단어: ", negative[i], "clean_title: ", clean_title)
                    clean_titles.append(clean_title)
                    labels.append(label)
                    break
            if negative_flag == False:
                for j in range(len(positive)):
                    if positive[j] in clean_title:
                        label = 0
                        print("positive 비교단어: ", positive[j], "clean_title: ", clean_title)
                        clean_titles.append(clean_title)
                        labels.append(label)
                        break

            
my_title_df = pd.DataFrame({"title":clean_titles, "label":labels})


# In[ ]:


my_data_df


# In[4]:


my_title_df


# In[5]:


my_title_df['label'].value_counts()


# In[5]:


my_title_df.to_csv('./Sen_data.csv')


# In[6]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings('ignore')


# In[7]:


import re
from konlpy.tag import Okt
from collections import Counter

from sklearn.feature_extraction.text import CountVectorizer

def text_cleaning(text):
    hangul = re.compile('[^ ㄱ-ㅣ 가-힣]')  # 정규 표현식 처리
    result = hangul.sub('', text)
    okt = Okt()  # 형태소 추출
    nouns = okt.nouns(result)
    nouns = [x for x in nouns if len(x) > 1]  # 한글자 키워드 제거
    return nouns

vect = CountVectorizer(tokenizer = lambda x: text_cleaning(x))
bow_vect = vect.fit_transform(my_title_df['title'].tolist()) #기사 크롤링 했을 때
#bow_vect = vect.fit_transform(my_data_df['data'].tolist()) # 트위터 크롤링 데이터
word_list = vect.get_feature_names()
count_list = bow_vect.toarray().sum(axis=0)


# In[8]:


from sklearn.feature_extraction.text import TfidfTransformer

tfidf_vectorizer = TfidfTransformer()
tf_idf_vect = tfidf_vectorizer.fit_transform(bow_vect)

#벡터-단어 mapping

vect.vocabulary_


# In[9]:


from sklearn.model_selection import train_test_split

#random_idx = positive_random_idx + negative_random_idx
x = tf_idf_vect
y = my_title_df['label'] #기사 크롤링
#y = my_data_df['label'] #트위터 크롤링
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=1)


# In[10]:


from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

lr = LogisticRegression(random_state = 0)
lr.fit(x_train, y_train)
y_pred = lr.predict(x_test)


# In[13]:


print('accuracy: %.2f' % accuracy_score(y_test, y_pred))
print('precision: %.2f' % precision_score(y_test, y_pred))
print('recall: %.2f' % recall_score(y_test, y_pred))
print('F1: %.2f' % f1_score(y_test, y_pred))


# In[14]:


from sklearn.metrics import confusion_matrix

confu = confusion_matrix(y_true = y_test, y_pred = y_pred) #col -> pred

plt.figure(figsize=(4, 3))
sns.heatmap(confu, annot=True, annot_kws={'size':15}, cmap='OrRd', fmt='.10g')
plt.title('Confusion Matrix')
plt.show()


# In[35]:


#크롤링으로 타이틀, 링크, 메인 이미지 가져오기 
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

my_title = []
link = []
image = []
name = '하이브'
j = 0

url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + name + "&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=55&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all,a:all&start=1"
bogi = "https://postfiles.pstatic.net/MjAyMTAzMjNfMTQ3/MDAxNjE2NDc3MTgxODkz.Q0De_R90sw1LVaTlhCSPqIq5rmT5wPjBFeV0gUakQ3Ig.QXjotxDdqPaL4kZO8skx6X1PrZrdG5FO2ADUYCOzq5Mg.JPEG.gyqls1225/IMG_3227.JPG?type=w773"


req = requests.get(url)
soup = BeautifulSoup(req.text, 'html.parser')

titles = soup.select(".news_tit")
images = soup.select("ul.list_news > li")

for title in titles:     
    href = title.attrs["href"]
    data = title.text
    my_title.append(data)
    link.append(href)
    
for img in images:
    img_data = img.select_one("a > img")
    
    if(img_data is None):
        image.append(bogi)
        continue
    image.append(img_data.get('src'))
    
data = {"title":my_title, "link":link, "image":image}


# In[34]:


data


# In[36]:


image


# In[ ]:




