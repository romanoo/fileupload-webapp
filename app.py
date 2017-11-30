# 
# File Upload web application
# Uses Flask
#
from os import walk, path
import os, math
import sys

sys.path.append(os.path.join(sys.path[0], 'static', 'python-libs'))

from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from datetime import datetime


def gethomedir():
    dir = os.environ['HOME']
    if dir is None or dir == "":
        dir = os.environ['TMPDIR']
        if dir is None or dir == "":
            if sys.platform.startswith('win'):
                dir = "c:\\temp"
            else:
                dir = "/tmp"
    return dir


homedir = gethomedir()

if len(sys.argv) == 2:
    UPLOAD_FOLDER = sys.argv[1];
else:
    homedir = gethomedir();
    UPLOAD_FOLDER = homedir + "/.fileupload-service"

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
    pre = "kMGTPE"[exp - 1] if si else "KMGTPE"[exp - 1]
    size = bytes / math.pow(unit, exp)
    return "%.1f %s" % (size, pre)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    for key in request.form:
        path = os.path.join(app.config['UPLOAD_FOLDER'], key)
        if os.path.exists(path):
            os.remove(path)

    return redirect(url_for('root'))


def numerize(file, i):
    idx = file.filename.rfind(".")
    if idx >= 0:
        return file.filename[:idx] + "-" + str(i) + file.filename[idx:]
    else:
        return file.filename + "-" + str(i)


@app.route('/rename', methods=['PUT'])
def rename():
    if not 'source' in request.form:
        return "missing source", 400
    if not 'target' in request.form:
        return "missing target", 400

    source = request.form['source']
    target = request.form['target']

    print("rename: " + source + " to: " + target)

    source_filepath = os.path.join(app.config['UPLOAD_FOLDER'], source)
    if not os.path.exists(source_filepath):
        return "source file not found: " + source, 400

    target_filepath = os.path.join(app.config['UPLOAD_FOLDER'], target)
    if os.path.exists(target_filepath):
        return "target already exists: " + target, 400

    os.rename(source_filepath, target_filepath)
    return 'OK'

@app.route('/files', defaults={'filename': None}, methods=['GET', 'POST'])
@app.route('/files/<path:filename>', methods=['GET'])
def upload(filename):
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file")
        for file in uploaded_files:
            #
            # file fully loaded in memory.
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

            # Uploads to folder
            file.stream.seek(0)
            contents = file.stream.read()

            # add '-1' or '-2' or '-n' depending if the file name already exists
            content_range = request.headers.get('Content-Range')
            if (content_range is None or content_range.startswith("bytes 0")) and os.path.exists(path):
                i = 1
                while os.path.exists(path):
                    path = os.path.join(app.config['UPLOAD_FOLDER'], numerize(file, i))
                    i += 1
            elif (not (content_range is None or content_range.startswith("bytes 0"))) and os.path.exists(path):
                i = 1
                while os.path.exists(path):
                    path = os.path.join(app.config['UPLOAD_FOLDER'], numerize(file, i))

                    if not os.path.exists(path):
                        path = os.path.join(app.config['UPLOAD_FOLDER'], numerize(file, i))
                        if i - 1 == 0:
                            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                        break
                    i += 1

            # Append to file if Content-Range is first chunk: bytes 0-nnn
            if content_range is None or \
                    (content_range is not None and content_range.startswith('bytes 0-')):
                outfile = open(path, "w+b")
                outfile.write(contents)
                outfile.close()
            else:
                outfile = open(path, "ab")
                outfile.write(contents)
                outfile.close()
        return 'OK'
    elif request.method == 'GET':
        if filename is not None:
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

        files = []
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
        return jsonify({"Files": files})


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0')
