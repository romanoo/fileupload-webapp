import unittest
import sys, tempfile, os, requests, json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://localhost:5000')
parser.add_argument('unittest_args', nargs='*')
args = parser.parse_args()
app_url = args.url

proxies = {
    "http": None,
    "https": None,
}

def generate_payload(fname, message):
    print("generating file: " + fname + " with content: " + message)
    f = open(os.path.join(tempfile.gettempdir(), fname), 'w')
    f.write(message)
    f.close()
    return f.name


def upload_file(file):
    print("uploading file: " + file)
    files = [('file', open(file, "rb"))]
    rsp = requests.post(app_url + "/files", files=files, proxies=proxies)
    if rsp.status_code != 201:
        raise Exception("unexpected response code: " + str(rsp.status_code) + " - " + rsp.text)


def delete_uploaded_file(filename):
    print("deleting uploaded file: " + filename)
    rsp = requests.delete(app_url + "/files/" + filename, proxies=proxies)
    if rsp.status_code != 200:
        raise Exception('unexcepted response code ' + str(rsp.status_code) + " - " + rsp.text)


def list_uploaded_files():
    print("listing uploaded files")
    rsp = requests.get(app_url + "/files", proxies=proxies)
    if rsp.status_code != 200:
        raise Exception('unexcepted response code ' + str(rsp.status_code) + " - " + rsp.text)
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
    rsp = requests.get(app_url + "/files/" + filename, proxies=proxies)
    if rsp.status_code != 200:
        raise Exception('unexcepted response code ' + str(rsp.status_code) + " - " + rsp.text)
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
    rsp = requests.put(app_url + "/files/" + source_filename, data={"newname": target_filename}, proxies=proxies)
    if rsp.status_code != 200:
        raise Exception('unexcepted response code ' + str(rsp.status_code) + " - " + rsp.text)


def update_uploaded_file(filename, newfile):
    print("update file: " + filename)
    rsp = requests.put(app_url + "/files/" + filename, files={'file': open(newfile, "rb")}, proxies=proxies)
    if rsp.status_code != 200:
        raise Exception('unexcepted response code ' + str(rsp.status_code) + " - " + rsp.text)


class FilesTestCase(unittest.TestCase):
    def test_upload(self):
        # delete all files
        delete_all_files()
        self.assertEqual(len(list_uploaded_files()), 0)

        # generate a text file named foo with content bar
        foo = generate_payload("foo", "bar")

        # upload the file
        upload_file(foo)

        # assert that foo is listed
        listing1 = list_uploaded_files()
        self.assertEqual(len(listing1), 1)
        self.assertTrue(has_file_in_listing(listing1, "foo"))

    def test_download(self):
        # delete all files
        delete_all_files()
        self.assertEqual(len(list_uploaded_files()), 0)

        # generate a text file named foo with content bar
        foo = generate_payload("foo", "bar")

        # upload the file
        upload_file(foo)

        # download foo into foo2
        foo2 = download_uploaded_file("foo", "foo2")

        # assert foo2 contains bar
        self.assertTrue(is_text_file_content(foo2, "bar"))

    def test_numerize(self):
        # delete all files
        delete_all_files()
        self.assertEqual(len(list_uploaded_files()), 0)

        # generate a text file named foo with content bar
        bar = generate_payload("bar", "foo")

        # upload the file twice
        upload_file(bar)
        upload_file(bar)
        upload_file(bar)

        # assert that foo is listed
        listing1 = list_uploaded_files()
        self.assertEqual(len(listing1), 3)
        self.assertTrue(has_file_in_listing(listing1, "bar"))
        self.assertTrue(has_file_in_listing(listing1, "bar-1"))
        self.assertTrue(has_file_in_listing(listing1, "bar-2"))

    def test_rename(self):
        # delete all files
        delete_all_files()
        self.assertEqual(len(list_uploaded_files()), 0)

        # generate a text file named hocus with content pocus
        hocus = generate_payload("hocus", "pocus")

        # upload the file
        upload_file(hocus)

        # assert that hocus is listed
        listing1 = list_uploaded_files()
        self.assertEqual(len(listing1), 1)
        self.assertTrue(has_file_in_listing(listing1, "hocus"))

        # rename hocus into pocus
        rename_uploaded_file("hocus", "pocus")

        # assert that pocus is listed
        listing2 = list_uploaded_files()
        self.assertEqual(len(listing2), 1)
        self.assertTrue(has_file_in_listing(listing2, "pocus"))

    def test_update(self):
        # delete all files
        delete_all_files()
        self.assertEqual(len(list_uploaded_files()), 0)

        # generate a text file named foo with content bar
        foo = generate_payload("foo", "bar")

        # upload the file
        upload_file(foo)

        # assert that there is only one file
        listing1 = list_uploaded_files()
        self.assertEqual(len(listing1), 1)

        # generate a text file named foo2 with content bar2
        foo2 = generate_payload("foo2", "bar2")

        update_uploaded_file("foo", foo2)

        # assert that there is only one file
        listing1 = list_uploaded_files()
        self.assertEqual(len(listing1), 1)

        # download foo into foo3
        foo3 = download_uploaded_file("foo", "foo3")

        # assert foo3 contains bar2
        self.assertTrue(is_text_file_content(foo3, "bar2"))

if __name__ == '__main__':
    sys.argv[1:] = args.unittest_args
    unittest.main(warnings='ignore')
