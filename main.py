# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
import time
import pandas as pd
import os
from lxml import etree
from tabulate import tabulate


def df_plt(temp_df):
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    
    mpl.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  #設置中文字體
    mpl.rcParams['axes.unicode_minus'] = False
    
    
    # DataFrame=>png
    plt.figure('DF')            # 視窗名稱
    ax = plt.axes(frame_on=False)# 不要額外框線
    ax.xaxis.set_visible(False)  # 隱藏X軸刻度線
    ax.yaxis.set_visible(False)  # 隱藏Y軸刻度線
    pd.plotting.table(ax, temp_df, loc='center') #將df投射到ax上，且放置於ax的中間
    plt.show()
    # plt.savefig('table.jpg',dpi=200)     # 存檔



    
    
    
    
    
    

focus_area = {'板橋區','三重區','永和區','新莊區','土城區','蘆洲區','樹林區'
              ,'三峽區','中和區','汐止區','新店區','五股區','泰山區','鶯歌區'
              ,'林口區','淡水區','八里區'}
nonfocus_area = {'三芝區','石門區','萬里區','金山區','瑞芳區','貢寮區','深坑區'
                  ,'烏來區','雙溪區','平溪區','石碇區','坪林區'}

high_area = {'五股區','鶯歌區','林口區','三芝區','深坑區','烏來區','平溪區','石碇區',
             '坪林區'}
low_area = {'板橋區','三重區','永和區','新莊區','土城區','蘆洲區','樹林區','三峽區',
            '中和區','汐止區','新店區','泰山區','淡水區','八里區','石門區','萬里區',
            '金山區','瑞芳區','貢寮區','雙溪區'}

waters_safe_area = {'烏來區','坪林區','三峽區','新店區'}

# =============================================================================
# 使用get提取網頁資料(需要有cookies) URL0、1為QPESUMS URL1為氣象局10分鐘雨量
# 接著轉為DF
# =============================================================================
# os.system("cls");
# print("下載氣象局QPESUMS最新雨量資訊...") 
# print('　：EOC輪值人員進駐\n　：EOC強化三級開設\n　：行政區強化三級開設\n　：雨情巡查')
# print('')
url = 'http://117.56.4.156/taiwan-html/ChartDirector/gaugemax.php?column=8&sort=1&filter=0&hour_s=hour_1&sh_in=&county_in=0'
# url0 = 'http://117.56.4.156/taiwan-html/ChartDirector/gaugemax.php?column=8&sort=1&filter=0.5&hour_s=hour_1&sh_in=&county_in=0'
# url1 = 'https://www.cwb.gov.tw/V8/C/P/Rainfall/MOD_10M/65.html'

my_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}
my_cookies = {'__utma' : '173357155.195835215.1593327131.1593327131.1593327131.1',
              '__utmb' : '173357155.152.10.1593327131',
              '__utmc' : '173357155',
              '__utmt' : '1',
              '__utmz' : '173357155.1593327131.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
              'onalert' : 'taiwan!mosaic!none!1!RCKT!taiwan!mosaic!125!100!nidsB!0!1!0!0!1!0!0!0!0!0!0!0!0!0!0!0!0!0!0!0!0!0!1!0!0!0!0!0!0!0!0!0!0!0!0!0!0!0!1!0!0!!!!!!!!!'}
r = requests.get(url, headers = my_headers, cookies = my_cookies, timeout = 3)
# r0 = requests.post(url0, data = my_data, cookies = my_cookies, timeout = 3)
# r1 = requests.get(url1, headers = my_headers, cookies = {'TS01c55bd7' : '0107dddfefd1ffe42fda2d207216ead0ded47bdf246819085c0aa15dac2d5e8b641eb632d2'}, timeout = 3)

df = pd.read_html(r.text, encoding='utf-8')[0]


# 更改欄位名稱
df.rename(columns={0 : "縣市",1 : "鄉鎮",2 : "雨量站",3 : "測站高度",4 : "10分鐘",5 : "1小時",6 : "3小時"
                   ,7 : "6小時",8 : "12小時",9 : "24小時"},inplace=True)
# 將空白列刪除
df = df.drop(0).reset_index(drop=True)
# 篩選出需要的縣市
df = df[df['縣市'].str.contains('新北市', na=False)]
df['縣市'] = '新北市'
# 將測站高度欄位裡，非數字的部分去除
df['測站高度'] = df['測站高度'].map(lambda x: str(x)[:-1])
# 將-修改為0
df.replace('-', '0', inplace=True)
df.replace('×', '-1', inplace=True)
# 將數字欄位更改為浮點數(未完成)
# df = df.infer_objects()
df[['測站高度','10分鐘','1小時','3小時','6小時','12小時','24小時']] = df[['測站高度','10分鐘','1小時','3小時','6小時','12小時','24小時']].apply(pd.to_numeric, errors='coerce')
# 將Nan更改為-1
df.fillna(-1, inplace=True)
# 排序後重設INDEX
df.sort_values("1小時",ascending=False, inplace=True)
df.sort_values("10分鐘",ascending=False, inplace=True)
df.reset_index(drop=True, inplace=True)


# =============================================================================
# 時間
# =============================================================================
html = etree.HTML(r.text)
current_time = html.xpath('//html/body/div[11]/form/select/option[1]/text()')[0]
current_time = str(current_time)

# =============================================================================
# 將過高測站刪除另存DF(雨情、強三使用)
# =============================================================================
def filter_isin_Column(df_temp, Column, *Values):
    return df_temp[df_temp[Column].isin(*Values)]

def filter_under_Column(df_temp, Column, Values):
    return df_temp.loc[(df_temp[Column] < Values)]

df_high_dist = filter_under_Column(filter_isin_Column(df, '鄉鎮', high_area), '測站高度', 300)
df_low_dist = filter_under_Column(filter_isin_Column(df, '鄉鎮', low_area), '測站高度', 60)

df_dist = pd.merge(df_high_dist,df_low_dist,how='outer')

# =============================================================================
# 判斷DF使用的函式
# =============================================================================
# 某列高於某值
def df_column_over_value(df_temp,Column,Value):
    return (df_temp[df_temp[Column] >= Value])

# 某列包含某值
def df_column_isin_value(df_temp,Column,Values):
    return (df_temp[df_temp[Column].isin(Values)])

# 某列包含某集合
def df_column_isin_values(df_temp,Column,*Values):
    return (df_temp[df_temp[Column].isin(*Values)])

# 超過10分鐘10min雨量的DF
def df_10min_df(df_temp,mm):
    return (df_column_over_value(df_temp,"10分鐘",mm))


# =============================================================================
# 判斷雨量是否達標使用的函式
# =============================================================================
# 10分鐘雨量是否達mm
def df_10min_bool(df_temp,mm):
    return (df_column_over_value(df_temp,"10分鐘",mm)['10分鐘'].any())

# (重點區)1小時雨量是否達mm
def df_1hr_focus_bool(df_temp,mm):
    return (df_column_over_value(df_column_isin_values(df_temp,"鄉鎮",focus_area),"1小時",mm)['1小時'].any())

# (非重點區)1小時雨量是否達mm
def df_1hr_nonfocus_bool(df_temp,mm):
    return (df_column_over_value(df_column_isin_values(df_temp,"鄉鎮",focus_area),"1小時",mm)['1小時'].any())

# (重點區)1小時雨量達mm的數量
def df_1hr_focus_count(df_temp,mm,count):
    return (df_column_over_value(df_column_isin_values(df_temp,"鄉鎮",focus_area),"1小時",mm)['1小時'].count()>= count)

# (非重點區)1小時雨量達mm的數量
def df_1hr_nonfocus_count(df_temp,mm,count):
    return (df_column_over_value(df_column_isin_values(df_temp,"鄉鎮",nonfocus_area),"1小時",mm)['1小時'].count()>= count)

# =============================================================================
# 應變機制判斷用的函式
# =============================================================================
# 是否進駐EOC
def into_EOC():
    if  df_10min_bool(df,10) or df_1hr_focus_bool(df,30) or df_1hr_nonfocus_bool(df,50):
        return(True)
    else:
        return(False)

# 是否EOC強化三級開設
def EOC_flood_force_3():
    if df_10min_bool(df_dist,10) and( df_1hr_focus_count(df_dist,40,3) or df_1hr_focus_count(df_dist,50,2) or df_1hr_focus_count(df_dist,60,1)):
        return(True)
    else:
        if df_10min_bool(df_dist,10) and( df_1hr_nonfocus_count(df_dist,80,2) or df_1hr_nonfocus_count(df_dist,90,1)):
            return(True)
        else:
            return(False)

# 是否區級強化三級開設
def Dist_force_3():
    if df_1hr_focus_bool(df_dist,40) or df_1hr_nonfocus_bool(df_dist,60):
        return(True)
    else:
        return(False)
    
# 是否雨情巡查
def rain_patrol():
    if df_1hr_focus_bool(df_dist,40) or df_1hr_nonfocus_bool(df_dist,60):
        return(True)
    else:
        return(False)
    
# def waters_safe():

 

# =============================================================================
# 各式文字訊息
# =============================================================================

def SMS_10min(temp_df):
    SMS = '新北市EOC:'+current_time[6:]
    for dist,site,mm in zip(temp_df['鄉鎮'],temp_df['雨量站'],temp_df['10分鐘']):
        SMS = SMS + dist + '(' + site + ')' + str(mm) + 'mm/10分鐘、'
    SMS = SMS[:-1]+'。'
    return(SMS)

# =============================================================================
#     
# =============================================================================
os.system("cls");
print("本程式由新北市政府消防局技佐郭峻廷提供 版本:0.9")
print("下載氣象局QPESUMS最新雨量資訊...") 
    
print('\r\r\r\r')
# print(df.head(10).sort_values('10分鐘', ascending=False))
print(str(current_time) +'，前10名雨量站(依10分鐘雨量及1小時雨量排序):')
print(tabulate(df.head(10).sort_values('1小時', ascending=False).sort_values('10分鐘', ascending=False), headers='keys', tablefmt= 'fancy_grid', numalign="right"))
print('')

print('開設及進駐警示；')
    # 顯示是否進駐EOC
if into_EOC():
    print("○：EOC輪值人員進駐")
else:
    print("Ｘ：EOC輪值人員進駐")
    
# 顯示是否強化三級開設
if EOC_flood_force_3():
    print("○：EOC強化三級開設")
else:
    print("Ｘ：EOC強化三級開設")

# 顯示是否區級強化三級開設
if EOC_flood_force_3():
    print("○：行政區強化三級開設")
else:
    print("Ｘ：行政區強化三級開設")

# 顯示是否雨情巡查
if rain_patrol():
    print("○：雨情巡查")
else:
    print("Ｘ：雨情巡查")


print('')
# 顯示10分鐘雨量達標簡訊
if into_EOC():
    print('10分鐘雨量簡訊:')
    print(SMS_10min(df_10min_df(df,10)))
else:
    print('10分鐘雨量未達標無簡訊')
    
print("\n準備重新下載雨量資料", end = '\r')
print("5...", end = '\r')
time.sleep(1)    
print("4...", end = '\r')
time.sleep(1)
print("3...", end = '\r')
time.sleep(1)
print("2...", end = '\r')
time.sleep(1)
print("1...", end = '\r')
time.sleep(1)
print("重新執行中           ", end = '\r')
time.sleep(5)



def main():
    print("本程式由新北市政府消防局技佐郭峻廷提供 版本:0.9")
    while(True):

     try:
          scheduler = BlockingScheduler()
          scheduler.add_job(myfunc, trigger=CronTrigger(minute="0,10,20,30,40,50"))
          scheduler.start()
     except Exception as e:
          log_msg = "main err : "+str(e)+".\n"
          write_log(log_msg)
          pass

if __name__ == '__main__':
     main()