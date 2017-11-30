#
# Simple test for the fileupload REST API
#

import sys, tempfile, os, requests, json


def generate_payload(fname, message):
    print("generating file: " + fname + " with content: " + message)
    f = open(os.path.join(tempfile.gettempdir(), fname), 'w')
    f.write(message)
    f.close()
    return f.name


def upload_file(file, url):
    print("uploading file: " + file)
    files = {"file": open(file, "rb")}
    rsp = requests.post(url + "/files", files=files)
    if rsp.status_code != 200:
        raise Exception("unexpected response code: " + str(rsp.status_code))


def delete_uploaded_file(filename, url):
    print("deleting uploaded file: " + filename)
    rsp = requests.post(url + "/delete", data={filename: ''})
    if rsp.status_code != 200:
        raise Exception('unexcepted response code' + str(rsp.status_code))


def list_uploaded_files(url):
    print("listing uploaded files")
    rsp = requests.get(url + "/files")
    if rsp.status_code != 200:
        raise Exception('unexcepted response code' + str(rsp.status_code))
    return json.loads(rsp.text)


def has_file_in_listing(listing, filename):
    for file in listing['Files']:
        if file['name'] == filename:
            return True
    return False


def download_uploaded_file(url, filename, target_filename):
    print("downloading file: " + filename + " into: " + target_filename)
    rsp = requests.get(url + "/files/" + filename)
    if rsp.status_code != 200:
        raise Exception('unexcepted response code' + str(rsp.status_code))
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


def rename_uploaded_file(url, source_filename, target_filename):
    print("renaming file: " + source_filename + " to: " + target_filename)
    rsp = requests.put(url + "/rename", data={"source": source_filename, "target": target_filename})
    if rsp.status_code != 200:
        raise Exception('unexcepted response code' + str(rsp.status_code) + " - " + rsp.text)


def test1(url):
    # generate a text file named foo with content bar
    foo = generate_payload("foo", "bar")

    # upload the file
    upload_file(foo, url)

    # get the listing of uploaded files
    listing = list_uploaded_files(app_url)

    # assert that foo is listed
    if not has_file_in_listing(listing, "foo"):
        raise Exception("'foo' is not listed")
    else:
        print("OK: foo is listed")

    # download foo into foo2
    foo2 = download_uploaded_file(url, "foo", "foo2")

    # assert foo2 contains bar
    if is_text_file_content(foo2, "bar") is False:
        raise Exception("'foo2' does not contain 'bar'")
    else:
        print("OK: foo2 contains 'bar'")

    # delete foo
    delete_uploaded_file("foo", url)

    # get the new listing of uploaded files
    listing2 = list_uploaded_files(app_url)

    # assert that foo is not listed anymore
    if has_file_in_listing(listing2, "foo") is True:
        raise Exception("'foo' is listed")
    else:
        print("OK: foo is not listed")


def test2(url):
    # generate a text file named foo with content bar
    bar = generate_payload("bar", "foo")

    # upload the file twice
    upload_file(bar, url)
    upload_file(bar, url)

    # get the listing of uploaded files
    listing = list_uploaded_files(app_url)

    # assert that 'bar' is listed
    if not (has_file_in_listing(listing, "bar")):
        raise Exception("'bar' is not listed")
    else:
        print("OK: bar is listed")

    # assert that bar-1 is listed
    if not (has_file_in_listing(listing, "bar-1")):
        raise Exception("'bar-1' is not listed")
    else:
        print("OK: 'bar-1' is listed")

    # cleanup
    delete_uploaded_file("bar", url)
    delete_uploaded_file("bar-1", url)


def test3(url):
    # generate a text file named hocus with content pocus
    hocus = generate_payload("hocus", "pocus")

    # upload the file
    upload_file(hocus, url)

    # rename hocus into pocus
    rename_uploaded_file(url, "hocus", "pocus")

    # get the listing of uploaded files
    listing = list_uploaded_files(app_url)

    # assert that pocus is listed
    if not (has_file_in_listing(listing, "pocus")):
        raise Exception("'pocus' is not listed")
    else:
        print("OK: pocus is listed")

    # assert that hocus is not listed
    if has_file_in_listing(listing, "hocus"):
        raise Exception("'hocus' is listed")
    else:
        print("OK: hocus is not listed")

    # cleanup
    delete_uploaded_file("pocus", url)


app_url = "http://localhost:5000"

for arg in sys.argv[1:]:
    if arg.startswith("--url="):
        app_url = arg[6:]
    elif arg.startswith("--test="):
        test_name = arg[7:]
        if test_name == "test1":
            test1(app_url)
        elif test_name == "test2":
            test2(app_url)
        elif test_name == "test3":
            test3(app_url)
        else:
            print("unknown method name: " + test_name)
            sys.exit(1)
