import unittest
from test_common import *

class FilesTestCase1(unittest.TestCase):
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


if __name__ == '__main__':

    unittest.main(warnings='ignore')
