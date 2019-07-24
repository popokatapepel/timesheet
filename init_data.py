"""
This file is called if a new db is generated and can be used to init the data
"""

from main import *


def import_data(dbfile):
    engine = create_engine("sqlite:///{}".format(dbfile), echo=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add_all(
        [Type(name='Administration'),
         Type(name='Arbeitsweg'),
         Type(name='Meeting'),
         Type(name='Projekt'),
         Type(name='Reisezeit'),
         Type(name='Schulung'),
         Type(name='Bildung'),
         Type(name='Trackingpunkte'),
         Project(name='ST-3970'),
         Project(name='DA-eNB'),
         Project(name='ST-3599'),
         Project(name='DA-STEP'),
         Project(name='DA-IntegrationAM'),
         Customer(abbreviation='DA', name='thyssenkrupp Bilstein GmbH'),
         Customer(abbreviation='ST', name='thyssenkrupp Presta AG'),
         Customer(abbreviation='CT', name='thyssenkrupp Components Technology'),
         Customer(abbreviation='SP', name='thyssenkrupp Springs and Stabilizers')
         ]
    )
    session.commit()
