import os, sys
from datetime import datetime

from sqlalchemy import (Column, String, create_engine, Integer, ForeignKey)
from sqlalchemy import orm
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.automap import automap_base

from config import DB_PATH, DEBUG

engine = create_engine('sqlite:///{}'.format(DB_PATH), 
        echo=False)#echo=DEBUG)
Base = automap_base()


class Bulletin(Base):
    '''
    An explicit declaration of the automapped class.
    Extra fields:
        block
    '''
    __tablename__ = 'bulletins'
    __mapper_args__ = {
        'exclude_properties': ['block_collection'] 
    }

    txid        = Column(String, primary_key=True)
    author      = Column(String, nullable=False)
    topic       = Column('board', String, default='')
    message     = Column(String, default='')
    timestamp   = Column(Integer)
    blockhash   = Column(String, ForeignKey('blocks.hash'), name="block")
    block       = relationship('BlockHead', uselist=False)

    def __repr__(self):
        t = trim(7)
        s = '<Bltn tx:{0} auth:{3} topic:{1} msg:{2}>'
        return s.format(t(self.txid), t(self.topic), len(self.message), t(self.author))

def trim(l):
    return lambda s: s if len(s) < l else s[:l]


class BlockHead(Base):
    '''
    A BlockHead has fields:
        hash
        prevhash
        height
        bulletin_collection
        prev_block
    '''
    __tablename__ = 'blocks'
    __mapper_args__ = {
        'exclude_properties': ['block_collection']
    }

    hash      = Column(String, primary_key=True)
    height    = Column(Integer)
    timestamp = Column(Integer)
    prevhash  = Column(String, ForeignKey('blocks.hash'))
    prevblock = relationship('BlockHead', uselist=False, single_parent=True)

    def __repr__(self):
        t = trim(12)
        s = '<Blck: hash:{} height:{}>'
        return s.format(t(self.hash), self.height)

    def datetime(self):
        '''
        Returns the reported datetime the block was created at.
        '''
        dt = datetime.fromtimestamp(self.timestamp)
        return dt


# Assert that the DB exists
if not (os.path.isfile(DB_PATH) and os.access(DB_PATH, os.R_OK)):
    print "Cannot access the database please check that the file: %s has been created"\
            % DB_PATH
    sys.exit(1)

# We must introspect the db to properly build out our models
Base.prepare(engine, reflect=True)
db_session = scoped_session(sessionmaker(bind=engine))
Base.query = db_session.query_property()

if __name__ == '__main__':
    blk = db_session.query(BlockHead).limit(1).first()
    bltn = db_session.query(Bulletin).first()

    print blk
    print bltn
