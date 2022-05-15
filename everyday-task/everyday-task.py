import json
import os
import pandas as pd
import bisect
from select import select
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
import time
import shutil
import datetime
from itertools import islice

#<<<<<<<< 要変更 >>>>>>>>>>#
common_path = "" #このリポジトリディレクトリへのフルパス
target_dir = common_path+'scraping/json-dir'  # TODO: file path change for cron

#時刻を取得
dt_now = datetime.datetime.now()
print(dt_now)
print("時刻取得 : OK")

#seleniumでHP上からデータを取得
coptions = webdriver.ChromeOptions()
coptions.add_argument('--headless')
coptions.add_experimental_option("prefs", {"download.default_directory": common_path+'everyday-task'})
driver = webdriver.Chrome(ChromeDriverManager().install(), options=coptions)
driver.implicitly_wait(3)
url = "https://www.seisen.maff.go.jp/seisen/bs04b040md001/BS04B040UC020SC001-Evt007.do"
driver.get(url)

dropdown_y = driver.find_element_by_name('s027.year')
select_y = Select(dropdown_y)
dropdown_m = driver.find_element_by_name('s027.month')
select_m = Select(dropdown_m)
dropdown_s = driver.find_element_by_name('s027.tendays')

select_s = Select(dropdown_s)
select_y.select_by_value(str(dt_now.year))

month_str = str(dt_now.month)
if (dt_now.month <= 9): month_str = "0"+str(dt_now.month)
select_m.select_by_value(month_str)

day_str = "1"
if (0 <= dt_now.day <= 10): day_str = "1"
elif (11 <= dt_now.day <= 20): day_str = "2"
else: day_str = "3"
select_s.select_by_value(day_str)

driver.find_element_by_name('CSV').click()
time.sleep(3)
driver.close()
driver.quit()
print("スクレイピング : OK")

#zip解凍
path = common_path+'everyday-task'  # TODO: file path change for cron
files_z = os.listdir(path)
files_file_z = [f for f in files_z if (os.path.isfile(os.path.join(path, f)))]
for f in files_file_z:
  zip_without_dot = os.path.splitext(f)[1][1:]
  if (zip_without_dot == 'zip'):
    shutil.unpack_archive(path+'/'+f, path)
    os.remove(path+'/'+f)
print("zip解凍 : OK")

#これまででできたjsonファイルの読み込み
json_open_d = open(target_dir+'/data_all.json', 'r')
data_all = json.load(json_open_d)
json_open_fcn = open(target_dir+'/food_code_to_name_dict.json', 'r')
food_code_to_name_dict = json.load(json_open_fcn)
json_open_fnc = open(target_dir+'/food_name_to_code_dict.json', 'r')
food_name_to_code_dict = json.load(json_open_fnc)
json_open_ccn = open(target_dir+'/city_code_to_name_dict.json', 'r')
city_code_to_name_dict = json.load(json_open_ccn)
json_open_cnc = open(target_dir+'/city_name_to_code_dict.json', 'r')
city_name_to_code_dict = json.load(json_open_cnc)
print("json読み込み : OK")

#前日に読み込んだファイルの記録
history = open(common_path+'everyday-task/history.json', 'r')  # TODO: file path change for cron
past_files = json.load(history)
history.close()
new_past_files = {}
print("json記録読み込み : OK")

#このファイルは記録から除外
rm_list = ['history.json', 'everyday-task.py', 'update.json']

#カレントディレクトリ上のファイルを全探索(driverが読んできたcsvファイル)
path = common_path+'everyday-task' # TODO: file path change for cron
files = os.listdir(path)
files_file = [f for f in files if (os.path.isfile(os.path.join(path, f)))]

remove_food_code_list = ["40000", "40001", "49500", "50000", "50900", "30000", "31550", "39000", "39100", "39200"] #果実総量, 国産果実総量, 他の国産果実, 輸入果実計, 他の輸入果実, 野菜総量, その他の菜類, その他の野菜, 輸入野菜計, 他の輸入野菜
remove_food_code_list.sort()

for f in files_file:
  print(f + " before")

  if (f in rm_list):
    continue

  if (f in past_files):
    new_past_files[f] = True #Trueは特に意味はない, jsonで扱うために仕方なく使っているだけ
    continue

  new_past_files[f] = True

  if (len(f) < 11 or f[10] == '.'): continue
  df = pd.read_csv(path+'/'+f, encoding="shift-jis")
  before_food_code = "00000"
  for food_code, city_code, food_name, city_name, price, y, m, d in zip(df['品目コード'], df['都市コード'], df['品目名'], df['都市名'], df['価格'], df['年'], df['月'], df['日']):
    #空白判定
    if ((not food_code) or (not city_code) or (not food_name) or (not city_name) or (not price) or (not y) or (not m) or (not d)): continue
    #'-', '...'判定
    if ((food_code == '－') or (city_code == '－') or (food_name == '－') or (city_name == '－') or (price == '－') or (y == '－') or (m == '－') or (d == '－')): continue
    if ((food_code == '…') or (city_code == '…') or (food_name == '…') or (city_name == '…') or (price == '…') or (y == '…') or (m == '…') or (d == '…')): continue

    food_code_str = str(food_code)
    city_code_str = str(city_code)
    if (city_code_str == "401"): city_code_str = "0401"
    if (before_food_code == food_code_str): continue
    if (food_name == "　　うち輸入"): continue
    if (food_code_str == remove_food_code_list[bisect.bisect_left(remove_food_code_list, food_code_str)]): continue
    before_food_code = food_code_str
    if (not food_code_str in food_code_to_name_dict):
      data_all[food_code_str] = {}
      food_code_to_name_dict[food_code_str] = food_name
      food_name_to_code_dict[food_name] = food_code_str
    if (not city_code_str in data_all[food_code_str]):
      data_all[food_code_str][city_code_str] = []
    if (not city_code_str in city_code_to_name_dict):
        data_all[food_code_str][city_code_str] = []
        city_code_to_name_dict[city_code_str] = city_name
        city_name_to_code_dict[city_name] = city_code_str
    date_str = str(y)
    if (0 <= m <= 9): date_str += "0"
    date_str += str(m)
    if (0 <= d <= 9): date_str += "0"
    date_str += str(d)
    #print(food_code, price)
    data_all[food_code_str][city_code_str].append([date_str, int(price)])
  print(f + " finished")
#print(data_all)

#sort
for food_code in data_all.keys():
  for city_code in data_all[food_code].keys():
    data_all[food_code][city_code].sort()
    #data_all[food_code][city_code] = sorted(data_all[food_code][city_code].items(), key=lambda x:x[0])
print("データ更新 : OK")

#csvファイルの削除
path = common_path+'everyday-task'  # TODO: file path change for cron
files = os.listdir(path)
files_file = [f for f in files if (os.path.isfile(os.path.join(path, f)))]
for f in files_file:
  zip_without_dot = os.path.splitext(f)[1][1:]
  if (zip_without_dot == 'csv'):
    os.remove(path+'/'+f)
print("csvファイル削除 : OK")

#前日記録の更新
history_w = open(common_path+'everyday-task/history.json', 'w')  # TODO: file path change for cron
json.dump(new_past_files, history_w)
print("json記録書き込み : OK")

#作物ごとスプリット
def dict_slice(data_all, cut):
  itr = iter(data_all)
  for i in range(0, len(data_all), cut):
    yield {k:data_all[k] for k in islice(itr, cut)}
split_data_all = dict_slice(data_all, cut=1)
print("作物ごとでスプリット : OK")

#作物ごとのjsonファイル書き出し
count = 0
for s in split_data_all:
  food_code = (list(data_all.keys()))[count]
  file_data = open(target_dir+'/data/data_{}.json'.format(food_code), 'w')
  json.dump(s, file_data)
  count += 1
print("作物ごとのjsonファイル書き出し : OK")

#jsonファイルの書き出し(更新)
file_data = open(target_dir+'/data_all.json', 'w')
json.dump(data_all, file_data)
file_fcn = open(target_dir+'/food_code_to_name_dict.json', 'w')
json.dump(food_code_to_name_dict, file_fcn)
file_fnc = open(target_dir+'/food_name_to_code_dict.json', 'w')
json.dump(food_name_to_code_dict, file_fnc)
file_ccn = open(target_dir+'/city_code_to_name_dict.json', 'w')
json.dump(city_code_to_name_dict, file_ccn)
file_cnc = open(target_dir+'/city_name_to_code_dict.json', 'w')
json.dump(city_name_to_code_dict, file_cnc)
print("json書き込み : OK")

#更新ファイルの更新
json_open_upd = open(common_path+'everyday-task/update.json', 'r')
update_file = json.load(json_open_upd)
month = dt_now.month
month_str = ""
if (month <= 9): month_str = "0"+str(month)
else: month_str = str(month)
update_file["update"] = str(dt_now.year)+month_str+str(dt_now.day)
json_open_upd = open(common_path+'everyday-task/update.json', 'w')
json.dump(update_file, json_open_upd)
print("更新ファイルの読み込み&書き込み : OK")

print("完了")
