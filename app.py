# 
# File Upload web application for Parzee Cloud Services
# Uses Flask
#
from os import walk, path
import os,math
import sys
sys.path.append(os.path.join(sys.path[0], 'static', 'python-libs'))


from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from datetime import datetime
#/import boto.s3
import getpass
import csv

AWS_ACCESS_KEY_ID = 'XXXXXXXXXXXXXXXXXXXX'
AWS_SECRET_ACCESS_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
#conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
#                       AWS_SECRET_ACCESS_KEY)

def getUserName():
  user = getpass.getuser()
  if user == None or user == "":
    user = "guest"
  return user

def getHomeDir():
  homedir = os.environ['HOME']
  if homedir == None or homedir == "":
     homedir = os.environ['TMPDIR']
     if homedir == None or homedir == "":
        if sys.platform.startswith('win'):
          homedir = "c:\\temp"
        else:
          homedir = "/tmp"
  return homedir

username = getUserName()
homedir = getHomeDir()
#bucket_name = "parzee-" + username
#Generate a new bucket
#bucket = conn.create_bucket(bucket_name)

if len(sys.argv) == 2:
  UPLOAD_FOLDER = sys.argv[1];
else:
  homedir = getHomeDir();
  UPLOAD_FOLDER = homedir + "/parzee-files"


app = Flask(__name__, static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def root():
  return app.send_static_file('index.html')

def human_readable_bytecount(bytes, si=False):
  unit = 1000 if si else 1024
  if bytes < unit:
    return str(bytes) + " B"
  exp = int(math.log1p(bytes) / math.log1p(unit))
  pre = "kMGTPE"[exp-1] if si else "KMGTPE"[exp-1]
  size = bytes / math.pow(unit, exp)
  return ("%.1f %s" % (size, pre))

def find_extension(description):
  if description.lower().startswith('ascii text'):
    sniffer = csv.Sniffer()
    return '.txt'
  elif description.lower().startswith('dos/mbr boot sector'):
    return '.iso'
  else:
    return '.xxx'

@app.route('/delete', methods=['GET','POST'])
def delete():
  for key in request.form:
    path = os.path.join(app.config['UPLOAD_FOLDER'], key)
    if os.path.exists(path):
      os.remove(path)

  return redirect(url_for('root'))

def root():
  return app.send_static_file('index.html')

@app.route('/files', defaults={'filename': None},methods=['GET','POST'])
@app.route('/files/<path:filename>',methods=['GET'])
def upload(filename):
  if request.method == 'POST':
    uploaded_files = request.files.getlist("file")
    for file in uploaded_files:
      #
      # file fully loaded in memory.

      #k = Key(bucket)
      #k.key = file.filename
      path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

      # Uploads to folder
      file.stream.seek(0)
      contents = file.stream.read()

      #add '-1' or '-2' or '-n' depending if the file name already exists
      content_range = request.headers.get('Content-Range')
      if (content_range == None or content_range.startswith("bytes 0")) and os.path.exists(path):
        i = 1
        while os.path.exists(path):
          path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename[:file.filename.rfind(".")] + "-" + str(i) + file.filename[file.filename.rfind("."):])
          i+=1
      elif (not (content_range == None or content_range.startswith("bytes 0"))) and os.path.exists(path):
        i = 1
        while os.path.exists(path):
          path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename[:file.filename.rfind(".")] + "-" + str(i) + file.filename[file.filename.rfind("."):])

          if not os.path.exists(path):
            path = os.path.join(app.config['UPLOAD_FOLDER'],file.filename[:file.filename.rfind(".")] + "-" + str(i-1) + file.filename[file.filename.rfind("."):])
            if i-1 == 0:
              path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            break
          i += 1

      #check if file is csv or txt
      if file.filename[-4] != '.' or file.filename[-3:] == 'txt' or file.filename[-3:] == 'csv':
        sniffer = csv.Sniffer()
        try:
          dialect = sniffer.sniff(str(contents,'utf-8'))
          if dialect.delimiter == ',' and file.filename[-3:] != 'csv':
            path += '.csv'
          elif dialect.delimiter != ',' and file.filename[-3:] == 'csv':
            path += '.txt'
        except:
          pass

      # Append to file if Content-Range is first chunk: bytes 0-nnn
      if content_range == None or \
         (content_range != None and content_range.startswith ('bytes 0-')):
        outfile = open(path, "w+b")
        outfile.write(contents)
        outfile.close()
      else:
        outfile = open(path, "ab")
        outfile.write(contents)
        outfile.close()


          #file.stream.seek(0)
      #contents = file.stream.read()

      #k.set_contents_from_string(contents)
      #k.set_acl('public-read')
    return 'OK'
  elif request.method == 'GET':
    if filename != None:
      #link = "https://s3.amazonaws.com/" + bucket_name + "/" + filename.replace(" ", "+")
      #f = requests.get(link)
      #return f.text
      return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


    files = []
    '''
    for key in bucket.list():
      size = human_readable_bytecount(key.size)
      last_modified_date = boto.utils.parse_ts(key.last_modified)

      file = {
        "name": key.name,
        "size": size,
        "modified": last_modified_date,
        "link": "https://s3.amazonaws.com/" + bucket_name + "/" + key.name.replace(" ", "+")
      }
      files.append(file)
    '''
    for (root, dirnames, filenames) in walk(app.config['UPLOAD_FOLDER']):
      for filename in filenames:
        filepath = os.path.join(root, filename)
        size = human_readable_bytecount(os.stat(filepath).st_size)
        try:
          mtime = os.path.getmtime(filepath)
        except OSError:
          mtime = 0
        last_modified_date = datetime.fromtimestamp(mtime).strftime('%m/%d/%Y %H:%M:%S')
        file = {
          "name": filename,
          "size": size,
          "modified": last_modified_date
        }
        files.append(file)

    return jsonify({ "Files" : files})

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
      os.makedirs(UPLOAD_FOLDER)
    # TODO what to do if upload_folder already exists...
    #  else delete the UPLOAD_FOLDER and recreate it???
    #app.run()
    app.run(host='0.0.0.0')
