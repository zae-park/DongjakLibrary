import csv

'https://weworkremotely.com/'
'https://stackoverflow.com/jobs'
'https://remoteok.io/'


def csv_writer(name, items):
  with open(name, mode='w') as f:
    writer = csv.writer(f)
    writer.writerow(['title', 'company', 'location', 'link'])
    for item in items:
      writer.writerow(list(item.values()))

def rename(name:str) -> str:
  # Strip some banned character in the received name(str)
  # bans = ['/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.', ' ']
  bans = ['-', ' \r', '\n?']
  for ban in bans:    
    if ban in name: name = name.replace(ban, '')
  return name