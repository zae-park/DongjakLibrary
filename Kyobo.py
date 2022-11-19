import os
import time
import shutil
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
    self.domain = 'https://product.kyobobook.co.kr/'
    self.sele_options = None
    self.defualt_download = os.path.join(os.path.expanduser('~'), 'downloads')
    self.download_path = download_path
    self.check_dummy_file()
    self.check_dummy_file(self.download_path, '*.xlsx') if os.path.isdir(self.download_path) else os.mkdir(self.download_path)

  def check_dummy_file(self, root: str = None, stereo: str = None):
    if root is None:
      root = self.defualt_download
    if stereo is None:
      stereo = '상품목록*.xlsx'
    bag = glob.glob(os.path.join(root, stereo))
    print(f'Find {len(bag)} of dummy files in {root}.')
    for b in bag:
      print('\tremove -> ' + b)
      os.remove(b)
  
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

  def download_csv(self):
    # Top categories
    driver = webdriver.Chrome(f'./{self.chrome_ver}/chromedriver.exe', options=self.sele_options)
    driver.get(self.domain)

    detail_dict = {}
    if not driver.get_issue_message():
      fold_menu = '#welcome_header_wrap > div.header_inner > nav > div.anb_wrap > button'
      fold_menu = driver.find_element(By.CSS_SELECTOR, fold_menu)
      fold_menu.send_keys(Keys.ENTER)

      mainpages = '#tabAnbCategoryKyobo > div.anb_category_inner > div > div.tab_list_wrap > ul > li'
      mainpages = driver.find_elements(By.CLASS_NAME, 'tab_link')
      # mainpage_urls = {mp.text.replace('/', '+'): mp.get_attribute('href') for mp in driver.find_elements(By.CLASS_NAME, 'tab_link ui-tabs-anchor')}

      for mainpage in mainpages:
        time.sleep(1) # wait
        main_name = mainpage.text
        mainpage.send_keys(Keys.ENTER)

        fold_btn = '#tabAnbCategorySub01 > div.custom_scroll_wrap > div.simplebar-wrapper > div.simplebar-mask > div > div > div > div > div.category_view_area > div > div:nth-child(1) > ul > li:nth-child(1) > div.fold_box_header > button'
        fold_btn = driver.find_element(By.CSS_SELECTOR, fold_btn)
        fold_btn.send_keys(Keys.ENTER)
        time.sleep(0.5) # wait
      
        subpages = '#tabAnbCategorySub01 > div.custom_scroll_wrap.active > div.simplebar-wrapper > div.simplebar-mask > div > div > div > div > div.category_view_area > div > div:nth-child(1) > ul > li.fold_box.expanded > div.fold_box_contents > ul > li'
        subpages = driver.find_elements(By.CSS_SELECTOR, subpages)
        subpage_urls = {sub.text.replace('/', '+'): sub.get_attribute('href') for sub in driver.find_elements(By.CLASS_NAME, 'category_link')}
        
        for subpage_name, subpage_url in subpage_urls.items():
          time.sleep(1) # wait
          # subpage_url = subpage.find_element(By.TAG_NAME, 'a').get_attribute('href')
          driver.get(subpage_url)
          time.sleep(3) # wait

          details = '#contents > div > aside > div.aside_body > div.snb_wrap > ul > li'
          details = driver.find_elements(By.CSS_SELECTOR, details)
          detail_urls = {u.text.replace('/', '+'): u.get_attribute('href') for u in driver.find_elements(By.CLASS_NAME, 'snb_link')}

          for detail_name, detail_url in detail_urls.items():
            driver.get(detail_url)
            time.sleep(3) # wait

            selector = '#homeTabAll > div.list_result_wrap > div.right_area > div:nth-child(2) > button'
            element = driver.find_element(By.CSS_SELECTOR, selector)
            
            print(f'\tCrawl... {main_name} - {subpage_name} - {detail_name}')

            excel_btn = '#homeTabAll > div.list_result_wrap > div.right_area > div:nth-child(2) > button'
            excel_btn = driver.find_element(By.CSS_SELECTOR, excel_btn)
            excel_btn.click()
            time.sleep(3)  # Waiting for download.
            
            downed = glob.glob(os.path.join(self.defualt_download, '상품목록*.xlsx'))
            if downed:
              _, extension = os.path.splitext(downed[0])
              shutil.copy(downed[0], os.path.join(self.download_path, f'{main_name}_{subpage_name}_{detail_name}' + extension))
              os.remove(downed[0])
    else:
      raise AssertionError

  def download_csv2(self):
    # Top categories
    driver = webdriver.Chrome(f'./{self.chrome_ver}/chromedriver.exe', options=self.sele_options)
    
    for i_sup, sup_name in enumerate(['국내도서', '서양도서']):
      driver.get(self.domain)
      time.sleep(2) # wait
      
      fold_menu = '#welcome_header_wrap > div.header_inner > nav > div.anb_wrap > button'
      fold_menu = driver.find_element(By.CSS_SELECTOR, fold_menu)
      fold_menu.send_keys(Keys.ENTER)
      time.sleep(2) # wait

      supcategories = driver.find_element(By.ID, 'tabAnbCategoryKyobo')
      supcategories = supcategories.find_elements(By.CLASS_NAME, 'tab_item')
      supcategory = None
      for sup in supcategories:
        if sup.text == sup_name:
          supcategory = sup
          break
      supcategory.send_keys(Keys.ENTER)
      time.sleep(2) # wait
      
      view_area = f'#tabAnbCategorySub{i_sup+1:02d} > div.custom_scroll_wrap > div.simplebar-wrapper > div.simplebar-mask > div > div > div > div > div.category_view_area'
      view_area = driver.find_element(By.CSS_SELECTOR, view_area)
      
      subpage_dict = {}
      for area in view_area.find_elements(By.CLASS_NAME, 'fold_box'):
        btn = area.find_element(By.CLASS_NAME, 'btn_fold')
        btn.send_keys(Keys.ENTER)
        time.sleep(2) # wait
        
        subpage = driver.find_element(By.CLASS_NAME, 'fold_box.expanded')
        subpage_name = subpage.find_element(By.CLASS_NAME, 'fold_box_header').text.replace('/', '+')
        details = subpage.find_elements(By.CLASS_NAME, 'category_item')
        for detail in details:
          subpage_dict[f"{subpage_name}_{detail.text}".replace('/', '+')] = detail.find_element(By.TAG_NAME, 'a').get_attribute('href')
      
      for subpage_name, subpage_url in subpage_dict.items():
        time.sleep(1) # wait
        # subpage_url = subpage.find_element(By.TAG_NAME, 'a').get_attribute('href')
        driver.get(subpage_url)
        time.sleep(3) # wait

        detail_urls = {u.text.replace('/', '+'): u.get_attribute('href') for u in driver.find_elements(By.CLASS_NAME, 'snb_link')}

        if detail_urls:
          for detail_name, detail_url in detail_urls.items():
            driver.get(detail_url)
            time.sleep(3) # wait

            tabs = '#contents > div > div.tab_list_wrap > ul > li'
            tabs = driver.find_elements(By.CSS_SELECTOR, tabs)
            
            for ii, t in enumerate(tabs):
              tab_tag = t.find_element(By.TAG_NAME, 'a').get_attribute('href').split('#')[-1]
              tab_name = t.text
              t.click()
              time.sleep(2)
              
              excel_btn = f'#{tab_tag} > div.list_result_wrap > div.right_area > div:nth-child(2) > button'
              excel_btn = driver.find_element(By.CSS_SELECTOR, excel_btn)
              print(f'\tCrawl... {sup_name} - {subpage_name} - {detail_name} - {tab_name}')
              excel_btn.click()
              time.sleep(5)  # Waiting for download.
              
              downed = glob.glob(os.path.join(self.defualt_download, '상품목록*.xlsx'))
              if downed:
                _, extension = os.path.splitext(downed[0])
                shutil.copy(downed[0], os.path.join(self.download_path, f'{sup_name}_{subpage_name}_{detail_name}_{tab_name}' + extension))
                os.remove(downed[0])
        else:
          tabs = '#contents > div > div.tab_list_wrap > ul > li'
          tabs = driver.find_elements(By.CSS_SELECTOR, tabs)
          
          for ii, t in enumerate(tabs):
            tab_tag = t.find_element(By.TAG_NAME, 'a').get_attribute('href').split('#')[-1]
            tab_name = t.text
            t.click()
            time.sleep(2)
            
            excel_btn = f'#{tab_tag} > div.list_result_wrap > div.right_area > div:nth-child(2) > button'
            excel_btn = driver.find_element(By.CSS_SELECTOR, excel_btn)
            print(f'\tCrawl... {sup_name} - {subpage_name} - {tab_name}')
            excel_btn.click()
            time.sleep(3)  # Waiting for download.
            
            downed = glob.glob(os.path.join(self.defualt_download, '상품목록*.xlsx'))
            if downed:
              _, extension = os.path.splitext(downed[0])
              shutil.copy(downed[0], os.path.join(self.download_path, f'{sup_name}_{subpage_name}_{tab_name}' + extension))
              os.remove(downed[0])
  
  def get_books(self):
    # Initial setting.
    self.set_selenium_option()
    self.check_chrome_version()
    self.download_csv2()
  
  @classmethod
  def get_reviews():
    # TODO: 동작구 도서관에서 대여자 - 도서 목록을 응답할 경우.
    return 2


if __name__ == '__main__':
  Kyobo().get_books()
  print('done')
  
  