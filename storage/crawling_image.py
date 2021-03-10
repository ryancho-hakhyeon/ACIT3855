from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class CrawlingImage(Base):
    """ Crawling List """

    __tablename__ = "crawling_image"

    id = Column(Integer, primary_key=True)
    image_id = Column(String(100), nullable=False)
    image_name = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    dir_path = Column(String(250), nullable=False)
    dir_size = Column(String(100), nullable=True)

    def __init__(self, image_id, image_name, dir_path, dir_size):
        """ Initialize a crawling list """
        self.image_id = image_id
        self.image_name = image_name
        self.date_created = datetime.datetime.now()
        self.dir_path = dir_path
        self.dir_size = dir_size


    def to_dict(self):
        """ Dictionary Representation of a crawling list """
        dict = {}
        dict['image_id'] = self.image_id
        dict['image_name'] = self.image_name
        dict['date_created'] = self.date_created
        dict['features'] = {}
        dict['features']['dir_path'] = self.dir_path
        dict['features']['dir_size'] = self.dir_size

        return dict