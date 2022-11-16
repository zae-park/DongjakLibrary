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

  def click_to_detail(self):
    # Top categories
    domain = 'https://product.kyobobook.co.kr/'
    
    driver = webdriver.Chrome(f'./{self.chrome_ver}/chromedriver.exe', options=self.sele_options)
    driver.get(domain)

    detail_dict = {}
    if not driver.get_issue_message():
      fold_menu = '#welcome_header_wrap > div.header_inner > nav > div.anb_wrap > button'
      fold_menu = driver.find_element(By.CSS_SELECTOR, fold_menu)
      fold_menu.send_keys(Keys.ENTER)

      mainpages = '#tabAnbCategoryKyobo > div.anb_category_inner > div > div.tab_list_wrap > ul > li'
      mainpages = driver.find_elements(By.CSS_SELECTOR, mainpages)

      for mainpage in mainpages:
        time.sleep(1) # wait
        main_name = mainpage.text
        mainpage.send_keys(Keys.ENTER)

        fold_btn = '#tabAnbCategorySub01 > div.custom_scroll_wrap > div.simplebar-wrapper > div.simplebar-mask > div > div > div > div > div.category_view_area > div > div:nth-child(1) > ul > li:nth-child(1) > div.fold_box_header > button'
        fold_btn = driver.find_element(By.CSS_SELECTOR, fold_btn)
        fold_btn.send_keys(Keys.ENTER)
        time.sleep(1) # wait
      
        subpages = '#tabAnbCategorySub01 > div.custom_scroll_wrap.active > div.simplebar-wrapper > div.simplebar-mask > div > div > div > div > div.category_view_area > div > div:nth-child(1) > ul > li.fold_box.expanded > div.fold_box_contents > ul > li'
        subpages = driver.find_elements(By.CSS_SELECTOR, subpages)

        for subpage in subpages:
          time.sleep(1) # wait
          subpage_name = subpage.text
          subpage_url = subpage.find_element(By.TAG_NAME, 'a').get_attribute('href')
          driver.get(subpage_url)
          time.sleep(3) # wait

          details = '#contents > div > aside > div.aside_body > div.snb_wrap > ul > li'
          details = driver.find_elements(By.CSS_SELECTOR, details)
          detail_urls = {u.text: u.get_attribute('href') for u in driver.find_elements(By.CLASS_NAME, 'snb_link')}

          for detail_name, detail_url in detail_urls.items():
            driver.get(detail_url)
            time.sleep(3) # wait

            selector = '#homeTabAll > div.list_result_wrap > div.right_area > div:nth-child(2) > button'
            element = driver.find_element(By.CSS_SELECTOR, selector)
            # element = driver.find_element_by_xpath('//*[@id="homeTabAll"]/div[2]/div[2]/div[2]/button')
            # -------------------------------------------------------------------------------------------------------------------
            
            print(f'\tCrawl... {main_name} - {subpage_name} - {detail_name}')

            excel_btn = '#homeTabAll > div.list_result_wrap > div.right_area > div:nth-child(2) > button'
            excel_btn = driver.find_element(By.CSS_SELECTOR, excel_btn)
            # driver.execute_script(excel_btn.script[0])
            excel_btn.click()

            # try:
            #   btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="homeTabAll"]/div[2]/div[2]/div[2]/button')))
            #   btn.click()
            # except Exception as e:
            #   print("error: ", e)
              
            time.sleep(3)  # Waiting for download.
    else:
      raise AssertionError

  def get_books(self):
    # Initial setting.
    self.set_selenium_option()
    self.check_chrome_version()
    self.click_to_detail()
    
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
  
  