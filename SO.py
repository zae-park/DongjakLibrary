import requests
from bs4 import BeautifulSoup

def get_last_page(url):
  result = requests.get(url)
  soup = BeautifulSoup(result.text, "html.parser")
  pages = soup.find("div", {"class": "s-pagination"})
  if pages:
    pages = pages.find_all('a')
    last_page = pages[-2].get_text(strip=True)
  else:
    last_page = 0
  return int(last_page)

def extract_job(url, html):
  title = html.find('h2').find('a')["title"]
  company, location = html.find('h3').find_all('span', recursive=False)
  company = company.get_text(strip=True)
  location = location.get_text(strip=True).strip("-").strip(' \r').strip('\n')
  job_id = html['data-jobid']
  return {'title': title, 'company': company, 'location': location, 'link': url+job_id}

def extract_jobs(url, last_page):
  jobs = []
  for page in range(last_page):
    print('Scrapping SO: page %d / %d' % (page + 1, last_page))
    result = requests.get(url+'&pg=%d' % (page + 1))
    soup = BeautifulSoup(result.text, 'html.parser')
    results = soup.find_all('div', {'class': '-job'})
    for result in results:
      job = extract_job(url, result)
      jobs.append(job)
  return jobs

def get_jobs(word):
  url = 'https://stackoverflow.com/jobs?q=%s&sort=i' % word
  last_page = get_last_page(url)
  if last_page == 0:
    return []
  else:
    jobs = extract_jobs(url, last_page)
    return jobs


