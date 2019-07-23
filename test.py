from unittest import TestCase
from main import *
from datetime import datetime

class TestTimesheet(TestCase):
    def test_db_init(self):
        db=db_interaction()

    def test_convert_uts(self):
        db = db_interaction()
        dt=datetime.now()
        uts=db.convert2uts(dt)
        dt1=db.convert2dt(uts)
        self.assertEqual(dt1,dt)

    def test_get_projects(self):
        db = db_interaction()
        db.get_projects()

    def test_get_types(self):
        db = db_interaction()
        db.get_types()

    def test_get_customer(self):
        db = db_interaction()
        db.get_customer()

    def test_start_tracking(self):
        db = db_interaction()
        db.start_tacking(1,2)

    def test_stop_tracking(self):
        db = db_interaction()
        i=db.start_tacking(1, 2)
        db.stop_tacking(i)

    def test_get_open_entries(self):
        db=db_interaction()
        db.get_open_entries()

    def test_get_entries(self):
        db=db_interaction()
        db.get_entries()




