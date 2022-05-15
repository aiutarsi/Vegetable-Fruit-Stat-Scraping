from select import select
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.implicitly_wait(3)
url = "https://www.seisen.maff.go.jp/seisen/bs04b040md001/BS04B040UC020SC001-Evt007.do"
driver.get(url)

dropdown_y = driver.find_element_by_name('s027.year')
select_y = Select(dropdown_y)
len_y = len(select_y.options)

dropdown_m = driver.find_element_by_name('s027.month')
select_m = Select(dropdown_m)
len_m = len(select_m.options)

dropdown_s = driver.find_element_by_name('s027.tendays')
select_s = Select(dropdown_s)
len_s = len(select_s.options)
print(len_y, len_m, len_s)

driver.close()
driver.quit()

for y in range(len_y):
  for m in range(len_m):
    for s in range(len_s):
      print("before", y, m, s)

      driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
      driver.implicitly_wait(3)
      driver.get(url)

      dropdown_y = driver.find_element_by_name('s027.year')
      select_y = Select(dropdown_y)

      dropdown_m = driver.find_element_by_name('s027.month')
      select_m = Select(dropdown_m)

      dropdown_s = driver.find_element_by_name('s027.tendays')
      select_s = Select(dropdown_s)

      try:
        print("try")
        select_y.select_by_index(y)
        print("select_y")
        select_m.select_by_index(m)
        print("select_m")
        select_s.select_by_index(s)
        print("select_s")
        driver.find_element_by_name('CSV').click()
        print("select_csv")
      
      except:
        print("except", y, m, s)

      finally:
        time.sleep(3)
        print("finally")
        driver.close()
        driver.quit()

driver.close()
driver.quit()
