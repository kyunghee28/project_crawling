# 교육목적 크롤링입니다. 

import bs4,requests,re
import urllib.request
from bs4 import BeautifulSoup


# {'city_no':28,'city_id':'1014_paris','city_name':'파리','city_name_eng':'paris','city_no':28,'country_no':9,'pv_start_no':3800},
# {'city_no':29,'city_id':'1015_rome','city_name':'로마','city_name_eng':'rome','city_no':29,'country_no':9,'pv_start_no':4000},
# {'city_no':30,'city_id':'1016_london','city_name':'런던','city_name_eng':'london','city_no':30,'country_no':9,'pv_start_no':4200},
# {'city_no':31,'city_id':'1017_barcelona','city_name':'바르셀로나','city_name_eng':'barcelona','city_no':31,'country_no':9,'pv_start_no':4400},
# {'city_no':32,'city_id':'1018_croatia','city_name':'크로아티아','city_name_eng':'croatia','city_no':32,'country_no':9,'pv_start_no':4600},
# {'city_no':33,'city_id':'1019_istanbul','city_name':'이스탄불','city_name_eng':'istanbul','city_no':33,'country_no':9,'pv_start_no':4800}


city_id='1019_istanbul'
pv_no = 4800-1
country_no = 9
city_no = 33
city_name='이스탄불'

url = 'http://www.tourtips.com/dest/list/'+ city_id
data=requests.get(url)
obj = BeautifulSoup(data.content,'html.parser')
# print(obj)

# 해당도시 관광지의 마지막 페이지 까지

if(obj.find("span",{"class":"goLast"})!=None):
    data = obj.find("span",{"class":"goLast"})
    lastPage = data.find("a")["href"].split("=")[1]
    # print(lastPage) -> 15, print(type(lastPage)) -> str
    lastPage = int(lastPage)
else:
    data = obj.find("div",{"class":"paging"})
    lastPage=len(data.findAll("a"))

pvList = []

# 해당나라 관광지 전체페이지에서 링크 찾기.
for i in range(1,lastPage+1):
    page = str(i)
    # print(page)1~15까지 출력
    # http://www.tourtips.com/dest/list/1014_paris?&page=2
    url2 = "http://www.tourtips.com/dest/list/" + city_id + "?&page=" + page
    data2 = data = requests.get(url2)
    obj2 = bs4.BeautifulSoup(data2.content,'html.parser')
    # print(obj2)# 1~15페이지까지 html 출력

    point_list = obj2.find("div", {"class": "spot_list"})
    point_list = point_list.find("ul")
    point_lists = point_list.findAll("a")
    # print(point_lists)


    # 세부정보페이지에 들어갈 링크 뽑기.
    for link in point_lists:
        links = {}
        links['link'] = "http://www.tourtips.com/" + link.attrs['href']
        links['no'] = pv_no
        pvList.append(links)
        pv_no += 1

        r = requests.get(links['link'])
        point_obj = BeautifulSoup(r.content,"html.parser")
        # print(obj)


        #관광지명
        ponit_name = point_obj.find("div", {"class": "title_area"})
        ponit_name = ponit_name.find("h1").text
        ponit_name = ponit_name.replace("'", ' ')
        # print(ponit_name)

        # 관광지 top정보
        top_info = point_obj.find("div", {"class": "cnt_reason"})
        top_info = re.findall('<strong>(.+?)</strong>', str(top_info))
        # print(top_info) #['걷기 좋은 곳', '팔라펠 먹기', '귀족들의 장소']

        point_topinfo = u""
        if top_info != None:
            for p in top_info:
                p = p.replace("'", ' ')
                point_topinfo += str(p) + " "
            # print(point_topinfo) #:걷기 좋은 곳 팔라펠 먹기 귀족들의 장소

        # 관광지 상세정보(info)
        p_info = point_obj.find("div", {"class": "cnt_reason"})
        info = u""
        if '<div class="tip">' in str(p_info):
            p_info = re.findall('<div class="cnt_reason">(.+?)<div class="tip">', str(p_info), re.DOTALL)
            p_info = p_info[0]
        else:
            p_info = re.findall('<div class="cnt_reason">(.+?)</div>', str(p_info), re.DOTALL)[0]

        p_info = p_info.replace("<strong>", "")
        p_info = p_info.replace("</strong>", "")
        p_info = p_info.replace("<br/>", "")
        p_info = p_info.replace("\n", "")
        p_info = p_info.replace("'",' ')
        info = p_info.replace(",", ' ')
        # print(info)

        # 관광지 tip
        point_tip = point_obj.find("div", {"class": "tip"})
        if point_tip != None:
            point_tip = point_tip.text
            point_tip = point_tip.replace("  ", '')
            point_tip = point_tip.replace("'",' ')
            point_tip = point_tip.replace("\n", ' ')
            # print(point_tip)

        # 해쉬태그
        point_hash = point_obj.find("p", {"class": "category"}).text
        point_hash = point_hash.replace(" ", '')
        point_hash = "#" + point_hash + " #" + city_name

        # 이용시간
        point_hour = point_obj.find("li", {"class": "operating"})
        # print(point_time)
        point_time=''
        if point_hour != None:
            point_hour = point_hour.text
            point_hour = point_hour.replace("  ", '')
            point_hour = point_hour.replace("\n", " ")
            point_time = point_hour.replace(",", ' ')

        # print(point_time)

        # 관광지 주소
        addr = point_obj.find("li", {"class": "address"})
        point_addr = re.findall('<li class="address">(.+?)<a',str(addr))
        if len(point_addr) > 0:
            point_addr = point_addr[0]
            point_addr = point_addr.replace(",",'')
            point_addr = point_addr.replace("'",'')
        # print(point_addr)

        #관광지 위도 경도
        pointview_location_X = ""
        pointview_location_Y = ""

        howto = point_obj.find("li", {"class": "howto"})
        if howto != None:
            location = howto.find("a", {"class": "go_map"})

            if len(location) > 0:
                map = re.findall('destination=(.+?),(.+?)"', str(location), re.DOTALL)[0]
                pointview_location_X = map[0]
                pointview_location_Y = map[1]
            # print(pointview_location_X)

        # 관광지 요금
        p_pay = point_obj.find("li", {"class": "entrance"})
        point_pay=''
        if (p_pay != None):
            p_pay = p_pay.text
            p_pay = p_pay.replace("  ", "")
            p_pay = p_pay.replace("\n", "")
            point_pay = p_pay.replace(",", '.')

        # 관광지 이미지 : pv_osaka1_1.jpg ,pointview_image1_2.jpg,pointview_image1_3.jpg,pointview_image1_4.jpg
        point_img = point_obj.findAll("div", {"class": "thumb_img"})
        # print(point_img) : <img alt="" src="//cfd.tourtips.com/@cms_800/2016030331/gjf6fs/DSC01116.JPG"/>

        pointview_image1 = "no_img.jpg"
        pointview_image2 = "no_img.jpg"
        pointview_image3 = "no_img.jpg"
        pointview_image4 = "no_img.jpg"

        if len(point_img) > 0:
            img_cnt = len(point_img)
            # print(img_cnt)
            if img_cnt > 4:
                img_cnt = 4

            for i in range(img_cnt):
                link = re.findall('src="//(.+?)"/', str(point_img[i]))[0]
                # print(link)
                city_name_eng = 'paris'
                fname = "pv_" + city_name_eng + str(pv_no) + "_" + str(i + 1) + ".jpg"

                file = open("C:/projectpython/img/" + fname, "wb")

                imglink = requests.get("http://" + link)
                file.write(imglink.content)
                # print(file)
                file.close()

                if (i == 0):
                    pointview_image1 = "pv_" + city_name_eng + str(pv_no) + "_1.jpg"
                elif (i == 1):
                    pointview_image2 = "pv_" + city_name_eng + str(pv_no) + "_2.jpg"
                elif (i == 2):
                    pointview_image3 = "pv_" + city_name_eng + str(pv_no) + "_3.jpg"
                elif (i == 3):
                    pointview_image4 = "pv_" + city_name_eng + str(pv_no) + "_4.jpg"

        detail_dic = {}
        detail_dic['pointview_no'] = pv_no
        detail_dic['pointview_name_kor'] = ponit_name
        detail_dic['pointview_name_eng'] = ""
        detail_dic['pointview_topinfo'] = point_topinfo
        detail_dic['pointview_info'] = info
        detail_dic['pointview_hashtag'] = point_hash
        detail_dic['pointview_addr'] = point_addr
        detail_dic['pointview_hours'] = point_time
        detail_dic['pointview_pay'] = point_pay

        detail_dic['pointview_image1'] = pointview_image1
        detail_dic['pointview_image2'] = pointview_image2
        detail_dic['pointview_image3'] = pointview_image3
        detail_dic['pointview_image4'] = pointview_image4

        detail_dic['pointview_location_X'] = pointview_location_X
        detail_dic['pointview_location_Y'] = pointview_location_Y

        detail_dic['country_no'] = country_no
        detail_dic['city_no'] = city_no

        import cx_Oracle as oci
        import os

        os.environ["NLS_LANG"] = ".AL32UTF8"

        START_VALUE = u"Unicode \u3042 3".encode('utf-8')
        END_VALUE = u"Unicode \u3042 6".encode('utf-8')

        conn = oci.connect('madang/madang@203.236.209.99:1521/XE')
        cursor = conn.cursor()

        sql = "insert into pointview values("+str(detail_dic['pointview_no'])+",'"+str(detail_dic['pointview_name_kor'])+"','"\
               +str(detail_dic['pointview_topinfo'])+"','"+str(detail_dic['pointview_hashtag'])+"','"+str(detail_dic['pointview_addr'])+"','"\
               +str(detail_dic['pointview_hours'])+"','"+str(detail_dic['pointview_pay'])+"','"+str(detail_dic['pointview_image1'])+"','"\
               +str(detail_dic['pointview_image2'])+"','"+str(detail_dic['pointview_image3'])+"','"+str(detail_dic['pointview_image4'])+"','"\
               +str(detail_dic['pointview_location_X'])+"','"+str(detail_dic['pointview_location_Y'])+"','notFound',0,0,'notFound',"\
               +str(detail_dic['country_no'])+","+str(detail_dic['city_no'])+",'"+str(detail_dic['pointview_name_eng'])+"','"\
               +str(detail_dic['pointview_info'])+"')"

        print("insert into pointview values("+str(detail_dic['pointview_no'])+",'"+str(detail_dic['pointview_name_kor'])+"','"\
               +str(detail_dic['pointview_topinfo'])+"','"+str(detail_dic['pointview_hashtag'])+"','"+str(detail_dic['pointview_addr'])+"','"\
               +str(detail_dic['pointview_hours'])+"','"+str(detail_dic['pointview_pay'])+"','"+str(detail_dic['pointview_image1'])+"','"\
               +str(detail_dic['pointview_image2'])+"','"+str(detail_dic['pointview_image3'])+"','"+str(detail_dic['pointview_image4'])+"','"\
               +str(detail_dic['pointview_location_X'])+"','"+str(detail_dic['pointview_location_Y'])+"','notFound',0,0,'notFound',"\
               +str(detail_dic['country_no'])+","+str(detail_dic['city_no'])+",'"+str(detail_dic['pointview_name_eng'])+"','"\
               +str(detail_dic['pointview_info'])+"')")

        cursor.execute(sql)
        conn.commit()

cursor.close()
conn.close()
