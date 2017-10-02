#!/usr/bin/env python

import pika
import cPickle
import numpy as np
import glob
import skimage
import time
import requests

import coslib

from skimage.viewer import ImageViewer
from matplotlib import pyplot as plt



connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

publish_topic = 'images'

ex = channel.exchange_declare(exchange=publish_topic,
                         exchange_type='x-lvc')

channel.confirm_delivery()

for filename in glob.iglob('./images/*'):
  print('%s' % filename)
  while True: # wait for queue to be short before publishing
    queue_length = coslib.get_queued_message_count_on_exchange(publish_topic)
    print('queue length: %s' % queue_length)
    if queue_length == 0: # queue is short enough to publish
      break
    time.sleep(1)

  im = skimage.io.imread(filename)
  
  while True: # keep trying to publish until message is confirmed by broker
    message_confirmed = channel.basic_publish(exchange=publish_topic,
                        routing_key=publish_topic,
                        body=cPickle.dumps(im))
    if message_confirmed:
      break
    time.sleep(1) # wait a second and try again
  print('published.')
