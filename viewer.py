#!/usr/bin/env python


import time
import sys
import numpy as np
import glob
import skimage
import pika
import cPickle


from skimage.viewer import ImageViewer
from matplotlib import pyplot as plt

subscribe_topic = sys.argv[1]
print('Listening on topic: %s' % subscribe_topic)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange=subscribe_topic,
                         exchange_type='x-lvc')

result = channel.queue_declare(exclusive=True, auto_delete=True) # exclusive is required for LVC exchange to work
queue_name = result.method.queue
# queue_name = subscribe_topic

channel.queue_bind(exchange=subscribe_topic,
                   queue=queue_name,
                   routing_key=subscribe_topic)


plt.ion()

def display_image(im):
  im = cPickle.loads(im)
  plt.clf()
  plt.imshow(im)
  plt.pause(0.001)
  plt.show(block=False)

# # CHECK LAST MESSAGE
# method_frame, header_frame, body = channel.basic_get(queue=queue_name)
# print(" [lvc] %s" % method_frame)
# if method_frame:
#   display_image(body)

# LISTEN FOR NEW MESSAGES
def callback(chan, method, properties, body):
  print("\n [x] ")
  display_image(body)
  chan.basic_ack(method.delivery_tag)
  print(" [ack] ")


channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=False)

print(' Waiting...')
channel.start_consuming()

