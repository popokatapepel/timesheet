import logging
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from os.path import join, realpath, abspath, dirname

try:
    approot = dirname(abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    import sys

    approot = dirname(abspath(sys.argv[0]))


class db_interaction:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.engine = create_engine("sqlite:///{}".format(join(approot, 'app.db')))

    @staticmethod
    def convert2uts(dt: datetime):
        return (dt - datetime(1970, 1, 1)).total_seconds()

    @staticmethod
    def convert2dt(uts: int):
        return datetime(1970, 1, 1) + timedelta(seconds=uts)

    def get_all_from_table(self, tablemane: str):
        connection = self.engine.connect()
        sqlcmd = "select * from {}".format(tablemane)
        result = connection.execute(sqlcmd)
        data = [r for r in result]
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
        data = [dict(id=r.ID,
                     description=r.DESCRIPTION,
                     start=self.convert2dt(r.START)) for r in result]
        connection.close()
        return data


def cre_table_str(l: list):
    s = ''
    for d in l:
        if 'id' in d:
            s += '[{id}]'
        for k in d.keys():
            if k != 'id':
                s += '  +  {'+k+'}'
        s += '\n'
        s = s.format(**d)
    return s


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
            project = int(input('enter project id: '))
            print('following customers are available')
            print(cre_table_str(db.get_customer()))
            customer = int(input('enter customer id: '))

            print('following types are available')
            print(db.get_types())
            type = int(input('enter type id: '))

            description = input('insert description')

            id = db.start_tacking(customer=customer, type=type, description=description, project=project)
        if i == '2':
            print(cre_table_str(db.get_open_entries()))
            id = int(input('enter entry id: '))
            db.stop_tacking(id)
        else:
            print('value not valid')
