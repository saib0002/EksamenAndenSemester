import ColorWho
import time

winner = ColorWho.start_threaded_spin()
for i in range(10):
    print("Doing some work...",i)
    time.sleep(.5)
time.sleep(6)
