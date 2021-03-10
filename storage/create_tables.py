import sqlite3

conn = sqlite3.connect('readings_crawling.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE crawling_image
          (id INTEGER PRIMARY KEY ASC, 
           image_id VARCHAR(100) NOT NULL, 
           image_name VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           dir_path VARCHAR(250) NOT NULL,
           dir_size VARCHAR(100))
          ''')

c.execute('''
          CREATE TABLE list_category
          (id INTEGER PRIMARY KEY ASC, 
           category_id VARCHAR(100) NOT NULL, 
           category_name VARCHAR(100) NOT NULL,
           images_num INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
