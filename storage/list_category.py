from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class ListCategory(Base):
    """ List Category """

    __tablename__ = "list_category"

    id = Column(Integer, primary_key=True)
    category_id = Column(String(100), nullable=False)
    category_name = Column(String(100), nullable=False)
    timestamp = Column(String(100), nullable=False)
    images_num = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, category_id, category_name, images_num, timestamp,):
        """ Initialize a list category """
        self.category_id = category_id
        self.category_name = category_name
        self.images_num = images_num
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary Representation of a list category """
        dict = {}
        dict['category_id'] = self.category_id
        dict['category_name'] = self.category_name
        dict['images_num'] = self.images_num
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
