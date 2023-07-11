from selenium import webdriver
import time
import requests
from time import sleep
from lxml import etree
import pandas as pd
import numpy as np
import csv


def save_datas():
    pass


def save_csv(df):
    df.to_csv(csv_path + csv_datas, index=None)


def switch_window(wd):
    windows = wd.window_handles
    wd.switch_to.window(windows[-1])


from selenium.webdriver import Chrome, ChromeOptions


# wd=webdriver.Chrome('C:/Users\lenovo\AppData\Local\Microsoft\WindowsApps\chromedriver.exe')
def get_urls():
    wd = webdriver.Chrome(
        executable_path=r'C:\Users\ASUS\.wdm\drivers\chromedriver\win32\105.0.5195.52\.wdm\drivers\chromedriver\win32\107.0.5304.62\chromedriver.exe')
    wd.get("https://www.themoviedb.org/movie/top-rated")
    wd.implicitly_wait(3)
    # #排序
    # 筛选点击
    # wd.find_element_by_xpath('//*[@id="media_v4"]/div/div/div[2]/div[1]/div[2]/div[1]').click()
    # wd.find_element_by_xpath('//*[@id="media_v4"]/div/div/div[2]/div[1]/div[1]/div[1]/span').click()
    # wd.find_element_by_xpath('//*[@id="media_v4"]/div/div/div[2]/div[1]/div[1]/div[2]/span/span/span[2]/span').click()
    # wd.find_element_by_xpath('//*[@id="media_v4"]/div/div/div[2]/div[1]/div[2]/div[1]/span').click()
    # wd.find_element_by_xpath('//*[@id="with_genres"]/li[1]/a').click()
    # wd.find_element_by_xpath('//*[@id="media_v4"]/div/div/div[2]/div[3]/p/a').click()
    switch_window(wd)
    there = input("请手动输入筛选条件，输入完毕后 输入<yes>即可开始:")
    switch_window(wd)
    # 先获取要详细获取的所有urls
    urls = []
    flag = 1
    is_ture = 1
    while is_ture == 1:
        # 从1开始
        now_urls = wd.find_elements_by_xpath('//section[@id="media_results"]/div[1]/div[{}]/div'.format(flag))
        print("正在获取", flag)
        if len(now_urls) == 0:
            try:
                wd.execute_script("window.scrollBy(0,999999)")
                time.sleep(3)
                wd.find_element_by_xpath('//*[@id="pagination_page_1"]/p/a').click()  # 第一次获取 #点击更多
            except:
                wd.execute_script("window.scrollBy(0,999999)")
                time.sleep(3)
                now_urls2 = wd.find_elements_by_xpath('//section[@id="media_results"]/div[1]/div[{}]/div'.format(flag))
                if len(now_urls2) == 0:
                    is_ture = 2
        else:
            for url in now_urls:
                try:

                    urls.append(url.find_element_by_xpath("./div[1]/div[1]/a").get_attribute("href"))
                except:
                    pass
            flag += 1
        print(urls)
    wd.close()
    df_urls = pd.DataFrame(urls)  # 保存爬取到的urls
    df_urls.to_csv(csv_path + csv_url_name, index=None)


def get_details():
    opt = ChromeOptions()
    opt.headless = True
    opt.add_argument('headless')
    wd = webdriver.Chrome(options=opt,
                          executable_path=r'C:\Users\ASUS\.wdm\drivers\chromedriver\win32\105.0.5195.52\.wdm\drivers\chromedriver\win32\107.0.5304.62\chromedriver.exe')
    wd.get("https://www.themoviedb.org/movie/top-rated")

    df_urls = pd.read_csv(csv_path + csv_url_name)
    urls = df_urls['0'].values.tolist()
    df = pd.DataFrame(
        columns=['名称', '类型', '导演', '主演', '评分', '上映时间', '时长', '简介', '参评人数', '票房', '预算', '关键词', '是否为系列电影', '相关系列电影名'])
    for url in urls:
        try:
            # url= 'https://www.themoviedb.org/movie/373001-el-cementerio-de-los-elefantes'
            # url=urls[13]
            wd.get(url)
            switch_window(wd)
            page_text = wd.page_source
            tree = etree.HTML(page_text)
            t1 = tree.xpath('//*[@id="original_header"]/div[2]/section/div[1]/h2/a/text()')[0]
            print("正在获取：", t1)
            wd.find_element_by_xpath('//*[@id="original_header"]/div[2]/section/ul/li[1]/div[1]/div/div/canvas').click()
            time.sleep(1)
            switch_window(wd)
            t2 = wd.find_element_by_xpath("//div[@class='user_score_chart']").get_attribute("data-percent")
            t3 = wd.find_element_by_xpath('//*[@id="rating_details_window"]/div/div[1]/div/div[2]/h3').get_attribute(
                "textContent")
            t4 = t3.split("个")[0]
            # 类型
            try:
                types = wd.find_element_by_xpath('//span[@class="genres"]').text
            except:
                types = np.NAN
            # duration时长
            try:
                duration = wd.find_element_by_xpath('//span[@class="runtime"]').text
            except:
                duration = np.NAN
            director = wd.find_elements_by_xpath('//ol[@class="people no_image"]/li')
            # 获取导演信息
            try:
                for itsdirector in director:
                    itsname = itsdirector.text.split("\n")[1]
                    if itsname.find(",") != -1:
                        itsnames = itsname.split(",")
                        for k in itsnames:
                            if k == 'Director':
                                director3 = itsdirector.text.split("\n")[0]
                    if itsname == 'Director':
                        director3 = itsdirector.text.split("\n")[0]
            except:
                director3 = np.NAN
            # 上映时间file_show
            file_show = wd.find_element_by_xpath('//span[@class="release"]').text
            # 简介brief
            try:
                brief = wd.find_element_by_xpath('//div[@class="overview"]').text
            except:
                brief = np.NAN
            # 预算 budget
            # 重写先获取这个再一一匹配
            row_list = wd.find_elements_by_xpath('//div[@class="column no_bottom_pad"]/section[1]/p')
            for row in row_list:
                row_name = row.text.split("\n")[0]
                if row_name == '票房':
                    box_office = row.text.split("\n")[1]
                if row_name == '预算':
                    budget = row.text.split("\n")[1]
            # budget = wd.find_element_by_xpath('//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div/section[1]/p[4]').text
            # budget = budget.split("\n")[1]
            # 票房 box_office
            # box_office = wd.find_element_by_xpath('//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div/section[1]/p[5]').text.split("\n")[1]
            # 是否为系列电影is_series 需要先滚动到最底
            wd.execute_script("window.scrollBy(0,1600)")  # 向下滚动1600px
            time.sleep(1)
            try:
                is_series = wd.find_element_by_xpath('//*[@id="collection_waypoint"]/div/div/h2').text
                # 相关系列电影名related_movies
                related_movies = wd.find_element_by_xpath('//*[@id="collection_waypoint"]/div/div/p').text.split(" ")[
                                 1:]
                related_movies = "".join(related_movies)
            except:
                # 没有
                is_series = '0'
                related_movies = np.NAN
            # 关键词key_word
            try:
                key_word = wd.find_element_by_xpath(
                    '//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div/section[2]/ul').text.replace("\n", ",")
            except:
                key_word = np.NAN
            try:
                acts = wd.find_elements_by_xpath('//*[@id="cast_scroller"]/ol/li')[:-1]  # 最后一个查看更多不要
                actsdata = []
                for act in acts:
                    actsdata.append(act.find_element_by_xpath('./p[1]/a[1]').text)
            except:
                actsdata = np.NAN
            itslen = len(df)
            # 存数据
            df.loc[itslen, '名称'] = t1
            df.loc[itslen, '评分'] = t2
            df.loc[itslen, '类型'] = types
            df.loc[itslen, '导演'] = director3
            df.loc[itslen, '主演'] = ",".join(actsdata)  # 转化为字符串
            df.loc[itslen, '上映时间'] = file_show
            df.loc[itslen, '时长'] = duration
            df.loc[itslen, '简介'] = brief
            df.loc[itslen, '预算'] = budget
            df.loc[itslen, '票房'] = box_office
            df.loc[itslen, '是否为系列电影'] = is_series
            df.loc[itslen, '相关系列电影名'] = related_movies
            df.loc[itslen, '关键词'] = key_word
            df.loc[itslen, '参评人数'] = t4
            print("获取成功")
            if len(df) % 10 == 0:  # 每10个保存一次
                save_csv(df)
                print("--------------------------保存成功--------------------------")
        except:
            print("获取失败")
            pass
    # wd.close()
    save_csv(df)
    print("--------------------------保存成功--------------------------")


def begin_csv():
    global csv_path
    csv_path = r'E:\ALL subjects\大三课程\综合实训\datas.csv'
    df = pd.DataFrame(
        columns=['名称', '类型', '导演', '主演', '评分', '上映时间', '时长', '简介', '参评人数', '票房', '预算', '关键词', '是否为系列电影', '相关系列电影名'])
    # df_author = pd.DataFrame(columns='')
    df.to_csv(csv_path, index=None)
    # df = pd.read_csv(csv_path,) #读取空列表时会报错


if __name__ == "__main__":
    # 存放的路径 主要后面有个/
    csv_path = r'E:\ALL subjects\大三课程\综合实训/'
    csv_url_name = 'urls.csv'  # 保存的url文件名
    csv_datas = 'datas.csv'  # 保存的数据文件名
    # 第一次运行需要运行这个代码 get_urls()
    get_urls()  # 第二次运行如果存在urls这个文件请注释掉
    print("执行获得详细信息中")
    get_details()
