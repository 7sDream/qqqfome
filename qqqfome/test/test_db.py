import os
import unittest
import shutil

from zhihu import ZhihuClient

from .. import db


file_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.join(file_dir, 'test')
json_path = os.path.join(file_dir, 'test.json')
author = ZhihuClient(json_path).me()
db_path = os.path.join(test_dir, db.author_to_db_filename(author))


class InitDBTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs(test_dir, exist_ok=True)
        os.chdir(test_dir)

    def tearDown(self):
        self.db.close() if (hasattr(self, 'db') and self.db) else None
        try:
            os.remove(db_path)
        except FileNotFoundError:
            pass

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(test_dir)

    def test_create_db_truely_create_a_file(self):
        self.db = db.create_db(author)
        self.assertTrue(os.path.isfile(db_path))

    def test_create_db_raise_error_when_file_exist(self):
        with open(db_path, 'w') as f:
            f.write('test file')

        with self.assertRaises(FileExistsError):
            self.db = db.create_db(author)

    def test_connect_db_when_file_exist(self):
        # create a db
        self.db = db.create_db(author)
        db.close_db(self.db)

        try:
            self.db = db.connect_db(db_path)
        except FileNotFoundError:
            self.fail("Raise error when try connect a exist database file.")

    def test_connect_db_when_file_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            self.db = db.connect_db(db_path)

    def test_create_table(self):
        self.db = db.create_db(author)
        db.create_table(self.db)
        cursor = self.db.execute(
            """
            select name from sqlite_master where type = 'table';
            """
        )

        self.assertListEqual(list(cursor),
                             [('followers',), ('sqlite_sequence',),
                              ('meta',), ('log',)])

        cursor = self.db.execute(
            """
            select * from followers LIMIT 1;
            """
        )

        row_names = list(map(lambda x: x[0], cursor.description))

        self.assertListEqual(row_names, ['id', 'name', 'in_name'])

    def test_add_one_user_to_db(self):
        self.db = db.create_db(author)
        db.create_table(self.db)
        db.add_user_to_db(self.db, author)

        cursor = self.db.execute(
            """
            SELECT in_name FROM followers;
            """
        )

        for row in cursor:
            self.assertEqual(row[0], author.id)

    def test_is_db_closed_when_closed(self):
        self.db = db.create_db(author)
        self.db.close()
        self.assertTrue(db.is_db_closed(self.db))

    def test_is_db_closed_when_not_closed(self):
        self.db = db.create_db(author)
        self.assertFalse(db.is_db_closed(self.db))

    def test_close_db_when_closed(self):
        self.db = db.create_db(author)
        self.db.close()
        db.close_db(self.db)
        self.assertTrue(db.is_db_closed(self.db))

    def test_close_db_when_not_closed(self):
        self.db = db.create_db(author)
        db.close_db(self.db)
        self.assertTrue(db.is_db_closed(self.db))
