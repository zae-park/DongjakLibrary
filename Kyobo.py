import os
import time
import shutil
import glob
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import chromedriver_autoinstaller


class Kyobo:
  def __init__(self, download_path: str = './crawler') -> None:
    self.domain = 'https://product.kyobobook.co.kr/'
    self.sele_options = None
    self.defualt_download = os.path.join(os.path.expanduser('~'), 'downloads')
    self.download_path = download_path
    self.check_dummy_file()
    self.check_dummy_file(self.download_path, '*.xlsx') if os.path.isdir(self.download_path) else os.mkdir(self.download_path)
    self.driver = None

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
              
              print(f'\tCrawl... {sup_name} - {subpage_name} - {detail_name} - {tab_name}')
              excel_btn = f'#{tab_tag} > div.list_result_wrap > div.right_area > div:nth-child(2) > button'
              excel_btn = driver.find_element(By.CSS_SELECTOR, excel_btn)
              excel_btn.click()
              time.sleep(3)  # Waiting for download.
              self.replace_xlsx(dst=f'{sup_name}_{subpage_name}_{detail_name}_{tab_name}')
        
        else:
          tabs = '#contents > div > div.tab_list_wrap > ul > li'
          tabs = driver.find_elements(By.CSS_SELECTOR, tabs)
          
          for ii, t in enumerate(tabs):
            tab_tag = t.find_element(By.TAG_NAME, 'a').get_attribute('href').split('#')[-1]
            tab_name = t.text
            t.click()
            time.sleep(2)

            print(f'\tCrawl... {sup_name} - {subpage_name} - {tab_name}')
            excel_btn = f'#{tab_tag} > div.list_result_wrap > div.right_area > div:nth-child(2) > button'
            excel_btn = driver.find_element(By.CSS_SELECTOR, excel_btn)
            excel_btn.click()
            time.sleep(3)  # Waiting for download.
            self.replace_xlsx(dst=f'{sup_name}_{subpage_name}_{tab_name}')
  
  def download_csv3(self, DEBUG_mode=False):
    # Go to domain
    self.driver.get(self.domain)
    time.sleep(2) # wait
    
    # Click main menu fold
    main_menu = '#welcome_header_wrap > div.header_inner > nav > div.anb_wrap > button'
    main_menu = self.driver.find_element(By.CSS_SELECTOR, main_menu)
    main_menu.send_keys(Keys.ENTER)
    time.sleep(2) # wait
    
    # Loop - Sup categories
    for i_sup, sup_name in enumerate(['국내도서', '서양도서', '일본도서']):
      # Click sup category tab
      supcategories = self.driver.find_element(By.ID, 'tabAnbCategoryKyobo')
      supcategories = supcategories.find_elements(By.CLASS_NAME, 'tab_item')
      supcategory = None
      for sup in supcategories:
        if sup.text == sup_name:
          supcategory = sup
          break
      supcategory.send_keys(Keys.ENTER)
      time.sleep(2) # wait
      
      # Search sub category
      sub_area = f'#tabAnbCategorySub{i_sup+1:02d} > div.custom_scroll_wrap > div.simplebar-wrapper > div.simplebar-mask > div > div > div > div > div.category_view_area'
      sub_area = self.driver.find_element(By.CSS_SELECTOR, sub_area)
      sub_fold = sub_area.find_elements(By.CLASS_NAME, 'fold_box')  # Fold buttons for every sub-categories.
      
      # Search [Sub & Detail] pages.
      # Loop - Sub categories
      sub_detail_dict = {}
      for area in sub_fold:
        # Unfold sub-category to find detail categories.
        btn = area.find_element(By.CLASS_NAME, 'btn_fold')
        btn.send_keys(Keys.ENTER)
        time.sleep(2) # wait
        
        sub_folded = self.driver.find_element(By.CLASS_NAME, 'fold_box.expanded')
        subpage_name = sub_folded.find_element(By.CLASS_NAME, 'fold_box_header').text.replace('/', '+') # replace '/' to '+' to avoid conflict.
        details = sub_folded.find_elements(By.CLASS_NAME, 'category_item')
        
        # Loop - detail categories
        for detail in details:
          detail_name = detail.text.replace('/', '+') # replace '/' to '+' to avoid conflict.
          sub_detail_dict[f"{subpage_name}_{detail_name}"] = detail.find_element(By.TAG_NAME, 'a').get_attribute('href')   # [sub_detail] : [url]
        
        if DEBUG_mode: break
      
      # Loop - Detail categories
      for sub_detail_name, page_url in sub_detail_dict.items():
        self.driver.get(page_url)
        time.sleep(3) # wait

        # Search tailend categories - sometime it is not exist.
        tailends = self.driver.find_elements(By.CLASS_NAME, 'snb_link')
        tailend_dict = {tail.text.replace('/', '+'): tail.get_attribute('href') for tail in tailends}
        
        # Loop - tailend
        csv_list = []
        if tailend_dict:
          for tailend_name, tailend_url in tailend_dict.items():
            print(f'\tCrawl... {sup_name} - {subpage_name} - {sub_detail_name} - {tailend_name}')
            save_name = f'{sup_name}_{subpage_name}_{sub_detail_name}_{tailend_name}'
            
            self.driver.get(tailend_url)
            time.sleep(3) # wait
            
            # Click review tab
            self.click_btn(self.driver.find_element(By.CSS_SELECTOR, '#ui-id-44'))
            
            # Get # of pages & get all book info.
            try:
              num_page = int(self.driver.find_element(By.CSS_SELECTOR, '#reviewTopPagi > div > a[data-role="last"]').text)
            except NoSuchElementException:
              time.sleep(2)
              num_page = int(self.driver.find_element(By.CSS_SELECTOR, '#reviewTopPagi > div > a[data-role="last"]').text)
            
            # Search all books with reviews
            books = {}
            for i in range(num_page-1):
              if i != 0:
                self.click_btn(self.driver.find_element(By.CSS_SELECTOR, '#reviewTopPagi > button.btn_page.next'))
              
              try:
                book_lst = self.driver.find_elements(By.CSS_SELECTOR, '#homeTabReview > div.switch_prod_wrap.view_type_list > ol > li')
              except NoSuchElementException:
                time.sleep(2)
                book_lst = self.driver.find_elements(By.CSS_SELECTOR, '#homeTabReview > div.switch_prod_wrap.view_type_list > ol > li')
                
              for book_ele in book_lst:
                book_info = book_ele.find_element(By.CLASS_NAME, 'prod_info')
                books[book_info.text] = book_info.get_attribute('href')
              
              if DEBUG_mode: break
            
            # Loop - books
            for book_name, book_url in books.items():
              self.driver.get(book_url)
              
              try:
                btn_review = self.driver.find_element(By.CLASS_NAME, 'btn_go_review')
              except NoSuchElementException:
                continue
              self.click_btn(btn_review)
              score = self.driver.find_element(By.CSS_SELECTOR, '#ReviewList1 > div.klover_review_box > div.klover_box_left > div.box_top > div > div.caption > span > span.val')
              score = float(score.text)
              
              csv_list.append([book_name, score]) # append book - score
              if DEBUG_mode: break
            if DEBUG_mode: break
        else:
          print(f'\tCrawl... {sup_name} - {subpage_name} - {sub_detail_name}')
          save_name = f'{sup_name}_{subpage_name}_{sub_detail_name}'
          
          # Click review tab
          self.click_btn(self.driver.find_element(By.CSS_SELECTOR, '#ui-id-44'))
          
          # Get # of pages & get all book info.
          try:
            num_page = int(self.driver.find_element(By.CSS_SELECTOR, '#reviewTopPagi > div > a[data-role="last"]').text)
          except NoSuchElementException:
            time.sleep(2)
            num_page = int(self.driver.find_element(By.CSS_SELECTOR, '#reviewTopPagi > div > a[data-role="last"]').text)
          
          # Search all books with reviews
          books = {}
          for i in range(num_page-1):
            if i != 0:
              self.click_btn(self.driver.find_element(By.CSS_SELECTOR, '#reviewTopPagi > button.btn_page.next'))
            
            try:
              book_lst = self.driver.find_elements(By.CSS_SELECTOR, '#homeTabReview > div.switch_prod_wrap.view_type_list > ol > li')
            except NoSuchElementException:
              time.sleep(2)
              book_lst = self.driver.find_elements(By.CSS_SELECTOR, '#homeTabReview > div.switch_prod_wrap.view_type_list > ol > li')
              
            for book_ele in book_lst:
              book_info = book_ele.find_element(By.CLASS_NAME, 'prod_info')
              books[book_info.text] = book_info.get_attribute('href')
            
            if DEBUG_mode: break
          
          # Loop - books
          for book_name, book_url in books.items():
            self.driver.get(book_url)
            try:
              btn_review = self.driver.find_element(By.CLASS_NAME, 'btn_go_review')
            except NoSuchElementException:
              continue
            self.click_btn(btn_review)
            score = self.driver.find_element(By.CSS_SELECTOR, '#ReviewList1 > div.klover_review_box > div.klover_box_left > div.box_top > div > div.caption > span > span.val')
            score = float(score.text)
            
            csv_list.append([book_name, score]) # append book - score
            if DEBUG_mode: break
        
        # Save csv
        with open(os.path.join(self.download_path, f'{save_name}.csv'), 'w',newline='\n') as f:
            writer = csv.writer(f)
            for row in csv_list:
              writer.writerow(row)
    
  def click_btn(self, button):
    try:
      button.click()
    except:
      try:
        time.sleep(2)
        button.click()
      except:
          pass
    time.sleep(4)  # Waiting for download.

  def replace_xlsx(self, dst):
    downed = glob.glob(os.path.join(self.defualt_download, '상품목록*.xlsx'))
    if downed:
      _, extension = os.path.splitext(downed[0])
      shutil.copy(downed[0], os.path.join(self.download_path, dst))
      os.remove(downed[0])

  def get_books(self):
    # Initial setting.
    self.set_selenium_option()
    self.check_chrome_version()
    self.driver = webdriver.Chrome(f'./{self.chrome_ver}/chromedriver.exe', options=self.sele_options)

    self.download_csv2()
  
  def get_reviews(self, *args):
    # Initial setting.
    self.set_selenium_option()
    self.check_chrome_version()
    self.driver = webdriver.Chrome(f'./{self.chrome_ver}/chromedriver.exe', options=self.sele_options)

    self.download_csv3(*args)
    return 2


if __name__ == '__main__':
  Kyobo().get_reviews()
  # Kyobo().get_reviews(True) # debug mode
  # Kyobo().get_books()
  print('done')
  
  