from os import walk, path
import os, math, sys, tempfile
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from datetime import datetime

script_dir = os.path.dirname(os.path.realpath(__file__))
src_dir = os.path.join(os.path.join(script_dir, os.pardir))
frontend_dir = os.path.abspath(os.path.join(src_dir, "frontend"))

repo_dir_parent = os.environ['HOME']
if repo_dir_parent is None or repo_dir_parent == "":
    repo_dir_parent = tempfile.gettempdir()
repo_dir = os.path.join(repo_dir_parent, ".fileupload-service")

app = Flask(__name__, static_url_path='', static_folder=frontend_dir)
app.config['UPLOAD_FOLDER'] = repo_dir
debug = False

for arg in sys.argv[1:]:
    if arg.startswith("--repo-dir="):
        app.config['UPLOAD_FOLDER'] = arg[11:]
    elif arg.startswith("--debug"):
        debug = True

def human_readable_bytecount(bytes, si=False):
    unit = 1000 if si else 1024
    if bytes < unit:
        return str(bytes) + " B"
    exp = int(math.log1p(bytes) / math.log1p(unit))
    pre = "kMGTPE"[exp - 1] if si else "KMGTPE"[exp - 1]
    size = bytes / math.pow(unit, exp)
    return "%.1f %s" % (size, pre)


def file_exists_in_repo(fname):
    if os.path.exists(get_repo_path(fname)):
        return True
    return False


def get_repo_path(fname):
    return os.path.join(app.config['UPLOAD_FOLDER'], fname)


def numerize_filename(filename, i):
    idx = filename.rfind(".")
    if idx >= 0:
        return filename[:idx] + "-" + str(i) + filename[idx:]
    else:
        return filename + "-" + str(i)


def numerize_file(file):
    parent_dir = os.path.abspath(os.path.join(file, os.pardir))
    path = file;
    i = 1
    while os.path.exists(path):
        path = os.path.join(parent_dir, numerize_filename(os.path.basename(file), i))
        i += 1
    return path, i


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/files', methods=['POST'])
def upload_files():
    if request.files is None:
        return "'files' required", 400

    for file in request.files.getlist("file"):

        file.stream.seek(0)
        contents = file.stream.read()
        content_range = request.headers.get('Content-Range')
        is_first_chunk = (content_range is None or content_range.startswith("bytes 0"))

        original_path = get_repo_path(file.filename)
        path, i = numerize_file(original_path)

        if not is_first_chunk and os.path.exists(path):
            # not the first chunk, need to append to a file
            # append to the last file created for that name
            # XXX this assumes no concurrent requests and needs to be fixed
            if i == 1:
                path = original_path
            else:
                path = numerize_filename(original_path, i - 1)

        if is_first_chunk:
            outfile = open(path, "w+b")
        else:
            # append if not first chunk
            outfile = open(path, "ab")
        outfile.write(contents)
        outfile.close()

    return 'Created', 201


@app.route('/files/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/files', methods=['GET'])
def list_files():
    files_list = []
    for (rootdir, dirnames, filenames) in walk(app.config['UPLOAD_FOLDER']):
        for filename in filenames:
            filepath = os.path.join(rootdir, filename)
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
            files_list.append(file)
    return jsonify({"Files": files_list})


@app.route('/files/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    if filename is None:
        return "Missing filepath", 400

    if not file_exists_in_repo(filename):
        return "File not found: " + filename, 404

    os.remove(get_repo_path(filename))
    return "File deleted", 200


@app.route('/files/<path:filename>', methods=['PUT'])
def update_file(filename):
    # rename a file
    if 'newname' in request.form:
        new_filename = request.form['newname']

        if not file_exists_in_repo(filename):
            return "Source file not found: " + filename, 400

        if file_exists_in_repo(new_filename):
            return "Target file already exists: " + new_filename, 400

        os.rename(get_repo_path(filename), get_repo_path(new_filename))
        return 'Renamed', 200

    # update a file
    else:

        if request.files is None:
            return "'files' required", 400

        _files = request.files.getlist("file")
        if len(_files) != 1:
            return "'file' is required", 400

        contents = _files[0].stream.read()
        content_range = request.headers.get('Content-Range')
        is_first_chunk = (content_range is None or content_range.startswith("bytes 0"))

        path = get_repo_path(filename)

        if is_first_chunk:
            outfile = open(path, "w+b")
        else:
            # append if not first chunk
            outfile = open(path, "ab")
        outfile.write(contents)
        outfile.close()
        return "Updated", 200


def run():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', debug=debug)


if __name__ == "__main__":
    run()
