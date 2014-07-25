from sqlalchemy import (Column, String, create_engine, Integer, ForeignKey)
from sqlalchemy import orm
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.automap import automap_base

from config import DB_PATH, DEBUG

engine = create_engine('sqlite:///{}'.format(DB_PATH), echo=DEBUG)
Base = automap_base()
Session = sessionmaker(bind=engine)


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
    topic       = Column(String, default='')
    message     = Column(String, default='')
    blockhash   = Column(String, ForeignKey('blocks.hash'), name="block")
    block       = relationship('BlockHead', uselist=False)

    def __repr__(self):
        s = '<Bulletin: txid:{} topic:{} msg:{}>'
        return s.format(self.txid, self.topic, len(self.message))

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
    prevhash  = Column(String, ForeignKey('blocks.hash'))
    prevblock = relationship('BlockHead', uselist=False, single_parent=True)

    def __repr__(self):
        s = '<BlockHead: hash:{} height:{}>'
        return s.format(self.hash, self.height)

def prep_models():
    Base.prepare(engine, reflect=True)


if __name__ == '__main__':
    prep_models()
    session = Session()
    blk = session.query(BlockHead).limit(1).first()
    bltn = session.query(Bulletin).first()

    print blk
    print bltn
