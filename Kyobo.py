import os
import time
import requests
import glob
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import chromedriver_autoinstaller


class Kyobo:
  def __init__(self, download_path: str = './crawler') -> None:
    self.sele_options = None
    self.defualt_download = os.path.join(os.path.expanduser('~'), 'downloads')
    self.download_path = download_path
    if not os.path.isdir(self.download_path): os.mkdir(self.download_path)
    self.set_subpages()
  
  def set_selenium_option(self):
    self.sele_options = webdriver.ChromeOptions()
    self.sele_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    self.sele_options.add_argument("--log-level=3")
	
  def check_chrome_version(self):
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]  # check chrome version (major version is all we need)
    self.chrome_ver = chrome_ver
    try:
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=webdriver.ChromeOptions().add_argument("headless"))   
    except:
        chromedriver_autoinstaller.install(True)
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=webdriver.ChromeOptions().add_argument("headless"))
    driver.implicitly_wait(10)
  
  # TODO: main -> sub -> detail page의 url까지 획득해야 함.
  def set_subpages(self):
    # Top categories
    mainpages = {'국내': 'https://product.kyobobook.co.kr/KOR', '서양': 'https://product.kyobobook.co.kr/ENG', '일본': 'https://product.kyobobook.co.kr/JAP'}
    
    subpages_dict = {}
    for k, v in mainpages.items():
      html = requests.get(v)
      soup = BeautifulSoup(html.text, 'html.parser')
      suboptions = soup.select('div.aside_body > div.snb_wrap > ul > li > a')
      
      for suboption in suboptions:
        subname = suboption.text.strip()
        # print(f'getting {k}: {subname}...')
        subpages_dict[f'{k}-{subname}'] = suboption.get('href')
    
    print(f'Collect {len(subpages_dict)} subpages...')
    self.subpages_dict = subpages_dict

  def get_books(self):
    # Initial setting.
    self.set_selenium_option()
    self.check_chrome_version()
    
    # init browser
    driver = webdriver.Chrome(f'./{self.chrome_ver}/chromedriver.exe', options=self.sele_options)
    for k, v in self.subpages_dict.items():
      # goto mainpage
      driver.get(v)
      
      # click tab & goto subpage
      tab = driver.find_element_by_css_selector(
        '#contents > div.tab_wrap.type_line.ui-tabs.ui-corner-all.ui-widget.ui-widget-content > div.tab_list_wrap > ul > li:nth-child(2)')
      tab.send_keys(Keys.ENTER)
      time.sleep(3) # wait
      
      # TODO: -------------------------------------------------------------------------------------------------------------
      # 어떤 Tab은 전체보기 ('#homeTabAll')이 없음.
      # mainpage -> subpage -> details 까지 내려가서 excel 다운로드하는 것으로 해결 (tab click -> detail list click)
      
      selector = '#homeTabAll > div.list_result_wrap > div.right_area > div:nth-child(2) > button'
      xpath = '//*[@id="homeTabAll"]/div[2]/div[2]/div[2]/button'
      element = driver.find_element_by_css_selector(selector)
      # element = driver.find_element_by_xpath('//*[@id="homeTabAll"]/div[2]/div[2]/div[2]/button')
      # -------------------------------------------------------------------------------------------------------------------
      
      print(f'\tCrawl... {k}')
      try:
        btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTabAll"]/div[2]/div[2]/div[2]/button')))
        btn.click()
      except Exception as e:
        print("error: ", e)
        
      time.sleep(10)  # Waiting for download.
  
  @classmethod
  def get_reviews():
    # TODO: 동작구 도서관에서 대여자 - 도서 목록을 응답할 경우.
    return 2


if __name__ == '__main__':
  Kyobo().get_books()
  
  res = get_suboptions()
  for k, v in res.items():
    tabs = get_books(v)
    break
  
  print('done')
  
  