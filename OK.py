import requests
from bs4 import BeautifulSoup

agent = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

def extract_job(root, html):

  td = html.find('td', {'class': 'company position company_and_position'})
  span = td.find('span', {'class':'companyLink'})
  company = span.find('h3').text
  anchor = td.find('a', {'class':'preventLink'})
  title = anchor.find('h2').text
  location = td.find('div', {'class': 'location tooltip'}).text
  link = anchor['href']
  return {'title': title, 'company': company, 'location': location, 'link': link}
  
def extract_jobs(url, root):
  jobs = []
  result = requests.get(url, headers=agent)
  soup = BeautifulSoup(result.text, 'html.parser')
  in_page = soup.find('body').select_one('div.page')
  if in_page is None: return []
  container = in_page.select_one('div.container')
  table = container.find('table', {'id': 'jobsboard'})
  trs = table.find_all('tr')
  for tr in trs:
    try:
      check = tr['data-url']
      if check:
        jobs.append(extract_job(root, tr))
    except: pass
  return jobs

def get_jobs(word):
  root_url = 'https://remoteok.com/'
  url = 'https://remoteok.com/remote-%s-jobs/' % word
  jobs = extract_jobs(url, root_url)
  return jobs


