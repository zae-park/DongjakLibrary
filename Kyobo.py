import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import chromedriver_autoinstaller

country_dict = {'kor': 'https://product.kyobobook.co.kr/KOR',
                'eng': 'https://product.kyobobook.co.kr/ENG'}


class Kyobo:
  def __init__(self, download_path: str = './crawler') -> None:
    self.sele_options = None
    self.download_path = download_path
    self.set_subpages()
  
  def set_subpages(self):
    suboptions_dict = {}
    for k, v in country_dict.items():
      html = requests.get(v)
      soup = BeautifulSoup(html.text, 'html.parser')
      suboptions = soup.select('div.aside_body > div.snb_wrap > ul > li > a')
      
      for suboption in suboptions:
        subname = suboption.text.strip()
        # print(f'getting {k}: {subname}...')
        suboptions_dict[subname] = suboption.get('href')
    
    print(f'Collect {len(suboptions_dict)} suboptions...')
    self.suboptions_dict = suboptions_dict

  @classmethod
  def get_books(cls):
    inst = cls()
    inst.set_subpages()
    inst.check_chrome_version()
    return 1
  
  @classmethod
  def get_reviews():
    return 2

  def init_selenium(self):
    self.sele_options = webdriver.ChromeOptions()
    self.sele_options.add_argument("headless")
    prefs = {"download.default_directory": {"download.default_directory": os.path.abspath(self.download_path)}}
    self.sele_options.add_experimental_option("prefs", prefs)
		
  @staticmethod
  def check_chrome_version(self):
  
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]  # check chrome version (major version is all we need)
    try:
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe')   
    except:
        chromedriver_autoinstaller.install(True)
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe')
    driver.implicitly_wait(10)

  def get_books(self, url):
    with webdriver.ChromeOptions('chromedriver.exe', options=self.sele_options) as driver:
      driver.get(url + '#homeTabAll')
      selector = 'div.list_result_wrap > div.right_area > div:nth-child(2) > button'
      element = driver.find_element_by_css_selector(selector)
      element.click()
      time.sleep(30)  # Waiting for download.
    
    # TODO: implement explicit wiater -> ref) https://swlock.blogspot.com/2022/05/python-selenium-chrome-driver.html

  def download_wait(self, download_root: str, timeout: int = 60):
    assert os.path.isdir(download_root), f'Cannot find download directory -> {download_root}'

    browser=webdriver.Chrome('chromedriver')
    browser.get("C:/Users/selenium_waits.html")

    waiter = WebDriverWait(browser, timeouts=60).until(self.is_downloaded)

    p_tag = WebDriverWait(browser,timeout=5).until(EC.presence_of_element_located((By.TAG_NAME, "p")))
    print("p태그를 찾았습니다.")

    if self.download_path==None:
      print("error can not find download path")
      return -2
    path_to_downloads = self.download_path
    seconds = 0
    WAIT = True
    sum_after = 0

    while WAIT and seconds < timeout:
      time.sleep(5)
      dl_wait = False
      sum_before = sum_after
      sum_after = 0
      for fname in os.listdir(path_to_downloads):
        if fname.endswith('.crdownload'):
          sum_after += os.stat(path_to_downloads+'/'+fname).st_size
          WAIT = True
      if WAIT and seconds > 10 and sum_before == sum_after:
        print("download timeout")
        WAIT = False
        return -1
      seconds += 5
    return seconds


if __name__ == '__main__':
  check_chrome_version()
  
  res = get_suboptions()
  for k, v in res.items():
    tabs = get_books(v)
    break
  
  print('done')
  
  