import sys, tempfile, os, requests, json

app_url = "http://localhost:5000"

def generate_payload(fname, message):
    print("generating file: " + fname + " with content: " + message)
    f = open(os.path.join(tempfile.gettempdir(), fname), 'w')
    f.write(message)
    f.close()
    return f.name


def upload_file(file):
    print("uploading file: " + file)
    files = [('file', open(file, "rb"))]
    rsp = requests.post(app_url + "/files", files=files)
    if rsp.status_code != 201:
        raise Exception("unexpected response code: " + str(rsp.status_code))


def delete_uploaded_file(filename):
    print("deleting uploaded file: " + filename)
    rsp = requests.delete(app_url + "/files/" + filename)
    if rsp.status_code != 200:
        raise Exception('unexcepted response code ' + str(rsp.status_code))


def list_uploaded_files():
    print("listing uploaded files")
    rsp = requests.get(app_url + "/files")
    if rsp.status_code != 200:
        raise Exception('unexcepted response code ' + str(rsp.status_code))
    listing = json.loads(rsp.text)
    return listing['Files']


def has_file_in_listing(listing, filename):
    for file in listing:
        if file['name'] == filename:
            return True
    return False


def delete_all_files():
    listing = list_uploaded_files()
    for file in listing:
        delete_uploaded_file(file['name'])


def download_uploaded_file(filename, target_filename):
    print("downloading file: " + filename + " into: " + target_filename)
    rsp = requests.get(app_url + "/files/" + filename)
    if rsp.status_code != 200:
        raise Exception('unexcepted response code ' + str(rsp.status_code))
    f = open(os.path.join(tempfile.gettempdir(), target_filename), 'wb')
    f.write(rsp.content)
    f.close()
    return f.name


def is_text_file_content(filename, content):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    if lines[0] != content:
        return False
    return True


def rename_uploaded_file(source_filename, target_filename):
    print("renaming file: " + source_filename + " to: " + target_filename)
    rsp = requests.put(app_url + "/files/" + source_filename, data={"newname": target_filename})
    if rsp.status_code != 200:
        raise Exception('unexcepted response code ' + str(rsp.status_code) + " - " + rsp.text)


def update_uploaded_file(filename, newfile):
    print("update file: " + filename)
    rsp = requests.put(app_url + "/files", files={"file": open(newfile, "rb")})
    if rsp.status_code != 200:
        raise Exception("unexpected response code: " + str(rsp.status_code))