import logging
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from os.path import join, realpath, abspath, dirname
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker

try:
    approot = dirname(abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    import sys

    approot = dirname(abspath(sys.argv[0]))


Base=declarative_base()

class Customer(Base):
    __tablename__='CUSTOMER'

    id=Column(Integer, primary_key=True)
    name=Column(String)
    abbreviation=Column(String)

    actions = relationship("Action", back_populates='customer')

    def __repr__(self):
        return f'<{self.name}>'


class Project(Base):
    __tablename__ = 'PROJECT'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    actions = relationship ("Action", back_populates = 'project')

    def __repr__(self):
        return f'<{self.name}>'

class Type(Base):
    __tablename__='TYPE'

    id=Column(Integer, primary_key=True)
    name=Column(String)
    actions = relationship("Action", back_populates='type')

    def __repr__(self):
        return f'<{self.name}>'

class Action(Base):
    __tablename__ = 'ACTION'

    id = Column(Integer, primary_key=True)
    description = Column(String)

    project_id = Column(Integer, ForeignKey('PROJECT.id'))
    customer_id = Column(Integer, ForeignKey('CUSTOMER.id'))
    type_id = Column(Integer, ForeignKey('TYPE.id'))

    project = relationship("Project", back_populates="actions")
    customer = relationship("Customer", back_populates="actions")
    type = relationship("Type", back_populates="actions")
    start = Column(DateTime)
    end = Column(DateTime)

    def __repr__(self):
        return f'<{self.name}>'



class db_interaction:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.engine = create_engine("sqlite:///abc.db".format(join(approot, 'app.db')),echo=True)
        Base.metadata.create_all(self.engine)
        self.session=sessionmaker(bind=self.engine)

        #initiale daten

        c1=Customer(abbreviation='DA', name='thyssenkrupp Bilstein GmbH')
        self.insert_customer('DA', 'thyssenkrupp Bilstein GmbH')
        self.insert_customer('CT', 'thyssenkrupp Components Technologies')
        self.insert_customer('SP', 'thyssenkrupp Springs and Stabilizers')

        p1=Project(name='ST-3970', description='working with old models')

        self.insert_project(name='ST-3628',description='Creating advance versions')

        self.insert_type('Arbeitsweg')
        self.insert_type('Administration')

        self.insert_action(description='abcde', start=datetime.now(), customer=c1, project=p1)

    def insert_customer(self,abbrev, name=''):
        c=Customer(name=name,abbreviation=abbrev)
        s=self.session()
        s.add(c)
        s.commit()

    def insert_project(self,description, name):
        c=Project(name=name,description=description)
        s=self.session()
        s.add(c)
        s.commit()

    def insert_type(self, name):
        c=Type(name=name)
        s=self.session()
        s.add(c)
        s.commit()

    def insert_action(self,**kwargs):
        c=Action(**kwargs)
        s=self.session()
        s.add(c)
        s.commit()


    @staticmethod
    def convert2uts(dt: datetime):
        return (dt - datetime(1970, 1, 1)).total_seconds()

    @staticmethod
    def convert2dt(uts: int):
        if not uts:
            return None
        return datetime(1970, 1, 1) + timedelta(seconds=uts)

    def resultProxy2dicts(self, rp):
        l = []
        for r in rp:
            l.append({})
            for k in r.keys():
                if k == 'START' or k == 'END':
                    l[-1][k] = self.convert2dt(r[k])
                else:
                    l[-1][k] = r[k]
        return l

    def get_all_from_table(self, tablemane: str):
        connection = self.engine.connect()
        sqlcmd = "select * from {}".format(tablemane)
        result = connection.execute(sqlcmd)
        data = self.resultProxy2dicts(result)
        connection.close()
        return data

    def get_projects(self):
        return self.get_all_from_table('PROJECT')

    def get_types(self):
        return self.get_all_from_table('TYPE')

    def get_customer(self):
        return self.get_all_from_table('CUSTOMER')

    def start_tacking(self, customer, type, description='', project=None):
        data = dict(customer=customer,
                    type=type,
                    description="\"{}\"".format(description),
                    project='NULL' if project == None else project,
                    start=(datetime.now() - datetime(1970, 1, 1)).total_seconds())

        connection = self.engine.connect()
        sqlcmd = "INSERT INTO TIMESHEET" \
                 "(CUSTOMER,TYPE,DESCRIPTION,PROJECT,START) " \
                 "VALUES ({customer},{type},{description},{project},{start});".format(**data)
        r = connection.execute(sqlcmd)
        id = r.lastrowid
        connection.close()
        return id

    def stop_tacking(self, id):
        data = dict(id=id,
                    end=(datetime.now() - datetime(1970, 1, 1)).total_seconds())
        connection = self.engine.connect()
        sqlcmd = "UPDATE TIMESHEET SET END={end} WHERE ID={id};".format(**data)
        connection.execute(sqlcmd)
        connection.close()

    def get_open_entries(self):
        connection = self.engine.connect()
        sqlcmd = "select ID, DESCRIPTION, START from TIMESHEET where END is NULL;"
        result = connection.execute(sqlcmd)
        data = self.resultProxy2dicts(result)
        connection.close()
        return data

    def get_entries(self):
        connection = self.engine.connect()
        sqlcmd = "select c.name CUSTOMER, t.name TYPE, ts.DESCRIPTION, p.name PROJECT, c.name CUSTOMER, ts.START, ts.END " \
                 "from TIMESHEET ts, PROJECT p, TYPE t, CUSTOMER c " \
                 "where p.ID=ts.PROJECT " \
                 "and t.ID=ts.TYPE " \
                 "and c.ID=ts.CUSTOMER;"

        result = connection.execute(sqlcmd)
        data = self.resultProxy2dicts(result)
        connection.close()

        return data


def cre_table_str(l: list):
    s = ''
    for d in l:
        if 'ID' in d:
            s += '[{ID}]'
        for k in d.keys():
            if k != 'ID':
                s += '  +  {' + k + '}'
        s += '\n'
        s = s.format(**d)
    return s


def getxls(l: list):
    for d in l:
        d['DATE']=d['START'].strftime('%d.%m.%Y')
        d['START']=d['START'].strftime('%H:%M')
        d['END'] = d['END'].strftime('%H:%M') if d['END'] else ''

    outfil=join(approot, '{}-output.xlsx'.format(datetime.now().strftime('%Y%m%d%H%M%S')))
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
            print(cre_table_str(db.get_projects()))
            project = check_num_inp(input('enter project id: '))
            if project == False:
                print('wrong entry')
                continue
            print('following customers are available')
            print(cre_table_str(db.get_customer()))
            customer = check_num_inp(input('enter customer id: '))
            if customer == False | customer == None:
                print('wrong entry')
                continue
            print('following types are available')
            print(cre_table_str(db.get_types()))
            type = int(input('enter type id: '))
            if type == False | type == None:
                print('wrong entry')
                continue
            description = input('insert description')

            id = db.start_tacking(customer=customer, type=type, description=description, project=project)
        elif i == '2':
            print(cre_table_str(db.get_open_entries()))
            id = int(input('enter entry id: '))
            db.stop_tacking(id)
        elif i == '3':
            data=db.get_entries()
            print(cre_table_str(data))
            print(getxls(data))
        else:
            print('value not valid')
