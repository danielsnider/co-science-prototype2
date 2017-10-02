#!/usr/bin/env python

import socket
import datetime
import json
import os
import subprocess as sub
import platform
import tarfile
import hashlib
import io
import glob

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Text, Binary
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
 
Base = declarative_base()


try:
  path = os.path.dirname(os.path.abspath(__file__))
except NameError: # To make work with interpter. TODO: DELETE
  path = os.getcwd()

class Node(Base):
  __tablename__ = 'node'
  id = Column(Integer, primary_key=True)
  name = Column(Text)
  main_file = Column(Text)
  path = Column(Text)
  main_language = Column(Text)
  params = Column(Text)
  platform = Column(Text)
  source_sha1 = Column(Text)
  source_tar = Column(Binary)
  FQDN = Column(Text)
  last_used = Column(DateTime, default=datetime.datetime.utcnow)
  

from sqlalchemy import create_engine
engine = create_engine('sqlite:///test.sqlite')
 
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)


# from launch file
node = {
  'name':'reader',
  'main_file':'reader.py',
  'path':'%s/code' % path,
  'params':'',
  'FQDN': socket.getfqdn(),
  'last_used': datetime.datetime.utcnow()
}

# Node Platform
node_platform={}
node_platform['release'] = platform.release()
node_platform['system'] = platform.system()
node_platform['architecture'] = platform.architecture()
node_platform['dist'] = platform.dist()
node['platform']=json.dumps(node_platform)

# Node Main Language
main_file = '%s/%s' % (node['path'], node['main_file'])
p = sub.Popen(['/usr/bin/file', main_file],stdout=sub.PIPE,stderr=sub.PIPE)
output, errors = p.communicate()
# Cleanup output
# Change this string example: '/home/dan/co-science-prototype2/code/reader.py: Python script, ASCII text executable\n'
# ...into this string: 'Python script, ASCII text executable'
node['main_language']=output.split(':')[1:][0].strip()

## Node Source Hash
for filename in glob.iglob(node['path'] + '/*'):
  # create a hash of of all the file names and file contents for a node's source directory
  node_hash = hashlib.sha1()
  with open(filename, "rb") as node_file:
    print filename
    file_contents = node_file.read()
    sha1Hash = hashlib.sha1(file_contents).hexdigest()
    node_hash.update(filename)
    node_hash.update(file_contents)
    node['source_sha1']=node_hash.hexdigest()


## Node Source Tar
# TODO: add tar compression
file_obj = io.BytesIO() # in memory file to hold tar.bz of node files. Not neccessary to write to disk, it will be written to the database
tar_writter = tarfile.open(mode='w', fileobj=file_obj) # create a tar writer
tar_writter.add(node['path']) # write tar content to file_obj
tar_data = file_obj.getvalue()
# write tar data  to db
node['source_tar'] = tar_data
# If you wish to recover the tar data as a file:
# with open('out.tar', "wb") as outfile:
#   outfile.write(tar_data)
# To untar the archive:
# $ tar -xvf out.tar


s = session()
## Insert Node into Database
n = Node(
  name=node['name'],
  main_file=node['main_file'],
  path=node['path'],
  main_language=node['main_language'],
  params=node['params'],
  platform=node['platform'],
  source_sha1=node['source_sha1'],
  source_tar=node['source_tar'],
  FQDN=node['FQDN']
)
s.add(n)
s.commit()
s.query(Node).all()
