import requests
from bs4 import BeautifulSoup
from scrapper import rename

def extract_job(root, html):
  anchor = html.find('a', recursive=False)
  link = root + anchor['href']
  print(anchor)
  title = anchor.find('span', {'class': 'title'}).text
  company = anchor.find('span', {'class': 'company'}).text
  location = rename(anchor.find('span', {'class': 'region company'}).text)
  return {'title': title, 'company': company, 'location': location, 'link': link}
  
def extract_jobs(url, root):
  jobs = []
  result = requests.get(url)
  soup = BeautifulSoup(result.text, 'html.parser')
  sections = soup.find_all('section', {'class': 'jobs'})

  for section in sections:
    articles = section.find('article').find('ul').find_all('li')
    for article in articles:
      if 'view-all' not in article.get('class'):
        jobs.append(extract_job(root, article))
  return jobs

def get_jobs(word):
  root_url = 'https://weworkremotely.com/'
  url = 'https://weworkremotely.com/remote-jobs/search?term=%s' % word
  jobs = extract_jobs(url, root_url)
  return jobs


