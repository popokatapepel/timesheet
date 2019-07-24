import logging
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from os.path import join, realpath, abspath, dirname, isfile
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from collections import OrderedDict
import sys

try:
    approot = dirname(abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    approot = dirname(abspath(sys.argv[0]))

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'CUSTOMER'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    abbreviation = Column(String, nullable=False)

    actions = relationship("Action", back_populates='customer')

    def __repr__(self):
        return '<Customer id: {id} name: {name}>'.format(**self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        return '[{id}] {name}'.format(**self.__dict__)


class Project(Base):
    __tablename__ = 'PROJECT'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    actions = relationship("Action", back_populates='project')

    def __repr__(self):
        return '<Project id: {id} name: {name}>'.format(**self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        return '[{id}] {name}'.format(**self.__dict__)


class Type(Base):
    __tablename__ = 'TYPE'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    actions = relationship("Action", back_populates='type')

    def __repr__(self):
        return '<Type id: {id} name: {name}>'.format(**self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        return '[{id}] {name}'.format(**self.__dict__)


class Action(Base):
    __tablename__ = 'ACTION'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)

    project_id = Column(Integer, ForeignKey('PROJECT.id'))
    customer_id = Column(Integer, ForeignKey('CUSTOMER.id'), nullable=False)
    type_id = Column(Integer, ForeignKey('TYPE.id'), nullable=False)

    project = relationship("Project", back_populates="actions")
    customer = relationship("Customer", back_populates="actions")
    type = relationship("Type", back_populates="actions")
    start = Column(DateTime, nullable=False)
    end = Column(DateTime)

    def __repr__(self):
        return '<Action id: {id} description: {description}>'.format(**self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        return '[{id}] {description}'.format(**self.__dict__)


class db_interaction:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not isfile(join(approot, 'app.db')):
            import init_data
            init_data.import_data(join(approot, 'app.db'))
        self.engine = create_engine("sqlite:///{}".format(join(approot, 'app.db')), echo=True)
        self.session = sessionmaker(bind=self.engine)()

    def insert_customer(self, abbrev, name=''):
        c = Customer(name=name, abbreviation=abbrev)
        self.session.add(c)
        self.session.commit()

    def insert_project(self, description, name):
        c = Project(name=name, description=description)

        self.session.add(c)
        self.session.commit()

    def insert_type(self, name):
        c = Type(name=name)

        self.session.add(c)
        self.session.commit()

    def insert_action(self, **kwargs):
        c = Action(**kwargs)

        self.session.add(c)
        self.session.commit()

    def get_all_entries(self, _type):
        od = OrderedDict()
        for t in self.session.query(_type).order_by(_type.id):
            od[t.id] = t
        return od

    def get_projects(self):
        return self.get_all_entries(Project)

    def get_types(self):
        return self.get_all_entries(Type)

    def get_customers(self):
        return self.get_all_entries(Customer)

    def get_entries(self):
        return self.get_all_entries(Action)

    def start_tacking(self, customer, type, description='', project=None):
        a = Action()
        a.customer = customer
        a.type = type
        a.description = description
        a.start = datetime.now()
        if project:
            a.project = project
        self.session.add(a)
        self.session.commit()

    def stop_tacking(self, action, stop=datetime.now()):
        action.end = stop
        self.session.commit()

    def get_open_entries(self):
        od = OrderedDict()
        for t in self.session.query(Action).filter(Action.end == None).order_by(Action.id):
            od[t.id] = t
        return od


def getxls(od: OrderedDict):
    l = [dict(date=od[k].start.strftime('%d.%m.%Y'),
              start=od[k].start.strftime('%H:%M'),
              end=od[k].end.strftime('%H:%M') if od[k].end else '',
              project=od[k].project.name,
              customer=od[k].customer.abbreviation,
              type=od[k].type.name)
         for k in od]

    outfil = join(approot, '{}-output.xlsx'.format(datetime.now().strftime('%Y%m%d%H%M%S')))
    with pd.ExcelWriter(outfil) as writer:
        pd.DataFrame(l).to_excel(writer, sheet_name="all")

    return outfil


def check_num_inp(s: str):
    try:
        i = int(s)
        return i
    except Exception:
        if s == '':
            return None
        else:
            return False


if __name__ == "__main__":
    db = db_interaction()

    loop = True
    while loop:
        print('-' * 20)
        with open('menu\main.txt') as f:
            print(f.read())
        i = input('choose option: ')
        if i == '1':
            print('following projects are available')
            projects = db.get_projects()
            print('\n'.join([str(projects[k]) for k in projects]))
            project = check_num_inp(input('enter project id: '))
            if project == False:
                print('wrong entry')
                continue
            print('following customers are available')
            customers = db.get_customers()
            print('\n'.join([str(customers[k]) for k in customers]))
            customer = check_num_inp(input('enter customer id: '))
            if customer == False | customer == None:
                print('wrong entry')
                continue
            print('following types are available')
            types = db.get_types()
            print('\n'.join([str(types[k]) for k in types]))
            type = int(input('enter type id: '))
            if type == False | type == None:
                print('wrong entry')
                continue
            description = input('insert description: ')

            db.start_tacking(customer=customers[customer],
                             type=types[type],
                             description=description,
                             project=projects[project])

        elif i == '2':
            actions = db.get_open_entries()
            print('\n'.join([str(actions[k]) for k in actions]))
            id = int(input('enter entry id: '))
            db.stop_tacking(actions[id])
        elif i == '3':
            data = db.get_entries()
            print(getxls(data))
        else:
            print('value not valid')
