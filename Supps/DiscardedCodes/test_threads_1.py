import _thread
import time

import _thread
import time

# Define a function for the thread
def print_time( threadName, delay):
   count = 0
   while count < 5:
      time.sleep(delay)
      count += 1
      print ("%s: %s" % ( threadName, time.ctime(time.time()) ))

# Create two threads as follows
try:
   _thread.start_new_thread( print_time, ("Thread-1", 3, ) )
   print("thread-1 launched.")
   _thread.start_new_thread( print_time, ("Thread-2", 10, ) )
   print("thread-2 launched")
except:
   print ("Error: unable to start thread")

while 1:
   pass

