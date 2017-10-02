#!/usr/bin/env python

import sys
import os
import numpy as np
import glob
import skimage
import pika
import cPickle

from skimage.viewer import ImageViewer
from matplotlib import pyplot as plt

node_name = os.path.basename(__file__)
print(node_name)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

subscribe_topic = 'images'
channel.exchange_declare(exchange=subscribe_topic,
                         exchange_type='x-lvc')


plt.ion()

#publish
publish_topic = 'filter'
channel.exchange_declare(exchange=publish_topic,
                         exchange_type='x-lvc')

def filter_image(im):
  im = cPickle.loads(im)
  im2 = skimage.filters.gaussian(im,sigma=4)
  channel.basic_publish(exchange=publish_topic,
                        routing_key=publish_topic,
                        body=cPickle.dumps(im2))

# SUBSCRIBE
result = channel.queue_declare(queue=node_name, auto_delete=True)

channel.queue_bind(exchange=subscribe_topic,
                   queue=node_name,
                   routing_key=subscribe_topic)

def callback(ch, method, properties, body):
    print(" [ filtered x] ")
    filter_image(body)
    # from IPython import embed

    # embed() # drop into an IPython session
    # channel.confirm_delivery()
    ch.basic_ack(method.delivery_tag)

channel.basic_consume(callback,
                      queue=node_name)

print(' Waiting...')
channel.start_consuming()

