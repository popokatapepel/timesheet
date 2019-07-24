from unittest import TestCase
from main import *
from datetime import datetime

class TestTimesheet(TestCase):
    def test_db_init(self):
        db=db_interaction()

    def test_get_projects(self):
        db = db_interaction()
        db.get_projects()

    def test_get_types(self):
        db = db_interaction()
        db.get_types()

    def test_get_customer(self):
        db = db_interaction()
        db.get_customers()

    def test_start_tracking(self):
        db = db_interaction()
        c=db.get_customers()[0]
        p = db.get_projects()[0]
        t = db.get_types()[0]
        db.start_tacking(customer=c,type=t,description='xxx',project=p)
        db.start_tacking(customer=c, type=t, description='xxx')
        db.start_tacking(customer=c, type=t)

    def test_stop_tracking(self):
        db = db_interaction()
        a=db.get_open_entries()[0]
        db.stop_tacking(a)

    def test_get_open_entries(self):
        db=db_interaction()
        db.get_open_entries()

    def test_get_entries(self):
        db=db_interaction()
        db.get_entries()

