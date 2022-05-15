import pandas as pd
import os
import json
import bisect
from itertools import islice

path = 'data' #sample
files = os.listdir(path)
files_file = [f for f in files if (os.path.isfile(os.path.join(path, f)))]

data_all = {}
food_code_to_name_dict = {}
food_name_to_code_dict = {}
city_code_to_name_dict = {}
city_name_to_code_dict = {}

remove_food_code_list = ["40000", "40001", "49500", "50000", "50900", "30000", "31550", "39000", "39100", "39200"] #果実総量, 国産果実総量, 他の国産果実, 輸入果実計, 他の輸入果実, 野菜総量, その他の菜類, その他の野菜, 輸入野菜計, 他の輸入野菜
remove_food_code_list.sort()

for f in files_file:
  #print("pre   " + f + " finished")
  if (len(f) < 11 or f[10] == '.'): continue
  df = pd.read_csv(path+'/'+f, encoding="shift-jis")

  before_food_code = "00000"

  for food_code, city_code, food_name, city_name, price, y, m, d in zip(df['品目コード'], df['都市コード'], df['品目名'], df['都市名'], df['価格'], df['年'], df['月'], df['日']):
    #空白判定
    if ((not food_code) or (not city_code) or (not food_name) or (not city_name) or (not price) or (not y) or (not m) or (not d)): continue
    #'-', '...'判定
    if ((food_code == '－') or (city_code == '－') or (food_name == '－') or (city_name == '－') or (price == '－') or (y == '－') or (m == '－') or (d == '－')): continue
    if ((food_code == '…') or (city_code == '…') or (food_name == '…') or (city_name == '…') or (price == '…') or (y == '…') or (m == '…') or (d == '…')): continue
    #print(food_code, price)
    food_code_str = str(food_code)
    city_code_str = str(city_code)
    if (city_code_str == "401"): city_code_str = "0401"
    if (before_food_code == food_code_str): continue
    if (food_name == "　　うち輸入"): continue
    if (food_code_str == remove_food_code_list[bisect.bisect_left(remove_food_code_list, food_code_str)]): continue

    before_food_code = food_code_str

    if (not food_code_str in food_code_to_name_dict):
      #print("not food")
      data_all[food_code_str] = {}
      food_code_to_name_dict[food_code_str] = food_name
      food_name_to_code_dict[food_name] = food_code_str

    if (not city_code_str in data_all[food_code_str]):
      data_all[food_code_str][city_code_str] = {}

    if (not city_code_str in city_code_to_name_dict):
        #print("not city")
        data_all[food_code_str][city_code_str] = {}
        city_code_to_name_dict[city_code_str] = city_name
        city_name_to_code_dict[city_name] = city_code_str
    
    date_str = str(y)
    if (0 <= m <= 9): date_str += "0"
    date_str += str(m)
    if (0 <= d <= 9): date_str += "0"
    date_str += str(d)
    
    data_all[food_code_str][city_code_str][date_str] = int(price)
  
  print(f + " finished")

"""
print(data_all)
print(food_code_to_name_dict)
print(food_name_to_code_dict)
print(city_code_to_name_dict)
print(city_name_to_code_dict)
"""

#sort
for food_code in data_all.keys():
  for city_code in data_all[food_code].keys():
    data_all[food_code][city_code] = sorted(data_all[food_code][city_code].items(), key=lambda x:x[0])

def dict_slice(data_all, cut):
  itr = iter(data_all)
  for i in range(0, len(data_all), cut):
    yield {k:data_all[k] for k in islice(itr, cut)}

split_data_all = dict_slice(data_all, cut=1)

print("==========================================")
#print(data_all)

json_dir = 'json-dir' #sample-json-dir

count = 0
for s in split_data_all:
  food_code = (list(data_all.keys()))[count]
  file_data = open(json_dir+'/data/data_{}.json'.format(food_code), 'w')
  json.dump(s, file_data)
  count += 1
"""
for food_code in data_all.keys():
  file_data = open(json_dir+'/data_{}.json'.format(food_code), 'w')
  json.dump(split_data_all[], file_data)
"""

file_data = open(json_dir+'/data_all.json', 'w')
json.dump(data_all, file_data)
file_fcn = open(json_dir+'/food_code_to_name_dict.json', 'w')
json.dump(food_code_to_name_dict, file_fcn)
file_fnc = open(json_dir+'/food_name_to_code_dict.json', 'w')
json.dump(food_name_to_code_dict, file_fnc)
file_ccn = open(json_dir+'/city_code_to_name_dict.json', 'w')
json.dump(city_code_to_name_dict, file_ccn)
file_cnc = open(json_dir+'/city_name_to_code_dict.json', 'w')
json.dump(city_name_to_code_dict, file_cnc)
