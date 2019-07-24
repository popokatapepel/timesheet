from unittest import TestCase
from main import *
from datetime import datetime
from random import randint, choice
from os import remove

def choose_from_ordered_dict(od):
    return od[choice(list(od.keys()))]

class TestTimeSheet(TestCase):
    def setUp(self) -> None:
        self.db_file=str(randint(10000,99999))

    def tearDown(self) -> None:
        try:
            remove(self.db_file)
        except Exception as e:
            pass

    def test_db_init(self):
        db_interaction(self.db_file)

    def test_insert_project(self):
        db = db_interaction(self.db_file)
        db.insert_project(description='abc', name='askflj')

    def test_insert_customer(self):
        db = db_interaction(self.db_file)
        db.insert_customer(abbrev='dfajsdflk', name='dslfkajsdl')

    def test_insert_type(self):
        db = db_interaction(self.db_file)
        db.insert_type(name='dfalksjdf')

    def test_get_projects(self):
        db = db_interaction(self.db_file)
        db.get_projects()

    def test_get_types(self):
        db = db_interaction(self.db_file)
        db.get_types()

    def test_get_customer(self):
        db = db_interaction(self.db_file)
        db.get_customers()

    def test_start_tracking(self):
        db = db_interaction(self.db_file)

        db.insert_project(description='abc', name='askflj')
        db.insert_customer(abbrev='dfajsdflk', name='dslfkajsdl')
        db.insert_type(name='dslkafjsd')

        c=choose_from_ordered_dict(db.get_customers())
        p = choose_from_ordered_dict(db.get_projects())
        t = choose_from_ordered_dict(db.get_types())

        db.start_tacking(customer=c,type=t,description='xxx',project=p)
        db.start_tacking(customer=c, type=t, description='xxx')
        db.start_tacking(customer=c, type=t)

    def test_get_open_entries(self):
        db = db_interaction(self.db_file)

        db.insert_project(description='abc', name='askflj')
        db.insert_customer(abbrev='dfajsdflk', name='dslfkajsdl')
        db.insert_type(name='dflakjsd')

        c = choose_from_ordered_dict(db.get_customers())
        p = choose_from_ordered_dict(db.get_projects())
        t = choose_from_ordered_dict(db.get_types())

        db.start_tacking(customer=c, type=t, description='xxx', project=p)

        a = db.get_open_entries()

        self.assertGreater(len(a), 0)

    def test_stop_tracking(self):
        db = db_interaction(self.db_file)

        db.insert_project(description='abc', name='askflj')
        db.insert_customer(abbrev='dfajsdflk', name='dslfkajsdl')
        db.insert_type(name='dfalskjsdf')

        c=choose_from_ordered_dict(db.get_customers())
        p = choose_from_ordered_dict(db.get_projects())
        t = choose_from_ordered_dict(db.get_types())

        db.start_tacking(customer=c,type=t,description='xxx',project=p)

        a=choose_from_ordered_dict(db.get_open_entries())
        db.stop_tacking(a)

    def test_get_entries(self):
        db = db_interaction(self.db_file)

        db.insert_project(description='abc', name='askflj')
        db.insert_customer(abbrev='dfajsdflk', name='dslfkajsdl')
        db.insert_type(name='lafkjdsl')
        db.insert_project(description='abc', name='askflj')
        db.insert_customer(abbrev='dfajsdflk', name='dslfkajsdl')
        db.insert_type(name='lafkjdsl')

        cs=db.get_customers()
        ps=db.get_projects()
        ts=db.get_types()
        print(cs,'\n',ps,'\n',ts)
        c = choose_from_ordered_dict(cs)
        p = choose_from_ordered_dict(ps)
        t = choose_from_ordered_dict(ts)

        db.start_tacking(customer=c, type=t, description='xxx', project=p)
        db.start_tacking(customer=c, type=t, description='xkfajdslkföxx', project=p)

        od_a=db.get_open_entries()
        print(od_a)
        a = choose_from_ordered_dict(od_a)
        db.stop_tacking(a)

        a=db.get_entries()

        self.assertGreater(len(a), 0)


    def test_getxls(self):
        db = db_interaction(self.db_file)

        db.insert_project(description='abc', name='askflj')
        db.insert_customer(abbrev='dfajsdflk', name='dslfkajsdl')
        db.insert_type(name='flksdjfal')

        c = choose_from_ordered_dict(db.get_customers())
        p = choose_from_ordered_dict(db.get_projects())
        t = choose_from_ordered_dict(db.get_types())

        db.start_tacking(customer=c, type=t, description='xxx', project=p)
        db.start_tacking(customer=c, type=t, description='xxx', project=p)

        a = choose_from_ordered_dict(db.get_open_entries())
        db.stop_tacking(a)
        x = db.get_entries()
        f = getxls(x)
        remove(f)

    def test_check_num(self):
        self.assertEqual(check_num_inp('1'), 1)
 

