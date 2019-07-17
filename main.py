import logging
from sqlalchemy import create_engine
from datetime import datetime
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
        data=dict(customer=customer,
                  type=type,
                  description="\"{}\"".format(description),
                  project='NULL' if project==None else project,
                  start=(datetime.now() - datetime(1970, 1, 1)).total_seconds())

        connection = self.engine.connect()
        sqlcmd="INSERT INTO TIMESHEET" \
               "(CUSTOMER,TYPE,DESCRIPTION,PROJECT,START) " \
               "VALUES ({customer},{type},{description},{project},{start});".format(**data)
        r=connection.execute(sqlcmd)
        id=r.lastrowid
        connection.close()
        return id

    def stop_tacking(self, id):
        data=dict(id=id,
                  end=(datetime.now() - datetime(1970,1,1)).total_seconds())
        connection = self.engine.connect()
        sqlcmd="UPDATE TIMESHEET SET END={end} WHERE ID={id};".format(**data)
        connection.execute(sqlcmd)
        connection.close()




if __name__=="__main__":
    db = db_interaction()
    print('create new entry')
    print('following projects are available')
    print(db.get_projects())
    project=int(input('enter project id'))

    print('following customers are available')
    print(db.get_customer())
    customer = int(input('enter customer id'))

    print('following types are available')
    print(db.get_types())
    type = int(input('enter type id'))

    description=input('insert description')

    id=db.start_tacking(customer=customer,type=type, description=description, project=project)

    input('press enter when your done')

    db.stop_tacking(id)