import unittest
from test_common import *

class FilesTestCase2(unittest.TestCase):
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

    unittest.main(warnings='ignore')
