"""
These are the URLs that will give you remote jobs for the word 'python'

https://stackoverflow.com/jobs?r=true&q=python
https://weworkremotely.com/remote-jobs/search?term=python
https://remoteok.io/remote-dev+python-jobs

Good luck!
"""

from flask import Flask, render_template, request, redirect, send_file
from scrapper import csv_writer
import SO, wework, OK

app = Flask("Zae's scrapper")
fake_DB = {}


@app.route('/')
def home():
  return render_template('home.html')


@app.route("/report")
def report():
  word = request.args.get('word')
  if word:
    word = word.lower()
    isexist = fake_DB.get(word)
    if isexist:
      jobs = isexist
    else:
      jobs = SO.get_jobs(word) + wework.get_jobs(word) + OK.get_jobs(word)
      fake_DB[word] = jobs
  else:
    return render_template('/')
  return render_template('report.html', Num_results=len(jobs),
   search_word=word, jobs=jobs)


@app.route("/export")
def export():
  try:
    word = request.args.get('word')
    if not word:
      raise Exception('Cannot find word argument')
    word = word.lower()
    jobs = fake_DB.get(word)
    if not jobs:
      raise Exception('Cannt find item in fake DB')
    csv_writer('jobs.csv', jobs)
    return send_file('jobs.csv', attachment_filename=word+'.csv', as_attachment=True)
  except:
    return redirect('/')


@app.route("/back")
def back():
  return render_template('home.html')


app.run(host = '0.0.0.0')




