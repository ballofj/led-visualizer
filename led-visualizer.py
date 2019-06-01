import pyaudio
import array
import numpy
import os
import random
import math

# Initialize pyaudio

CHANNELS = 1
RATE = 48000
CHUNK = 1024
FORMAT = pyaudio.paFloat32

pa_manager = pyaudio.PyAudio()
stream = pyaudio.Stream(pa_manager, RATE, CHANNELS, FORMAT, input=True, frames_per_buffer=CHUNK)

# Initialize variables

display_width = 100
average_samples = 100
entry_barrier = 0.01
brightness_multiplier = 10

volume_list = array.array('f')

first = True
picking = True

arr = []
pre_arr = []

# Get led names and max brightness

for i in os.listdir('/sys/class/leds'):
	file = open('/sys/class/leds/' + i + '/max_brightness', 'r')
	pre_arr.append([i, int(file.read()), 0])
	file.close()

pre_arr.sort()

# User select leds

while picking:
	
	print('\nSelected leds:')
	for i in range(len(arr)):
		print(arr[i][0])
	
	print('\nOptions:')
	for i in range(len(pre_arr)):
		print(pre_arr[i][0] + ': ' + str(i))
	print("\nType led number and put 'done' when finished")
	
	inputled = input()
	
	if inputled == 'done':
		picking = False
	else:
		
		file = open('/sys/class/leds/' + pre_arr[int(inputled)][0] + '/brightness', 'w')
		file.write(str(pre_arr[int(inputled)][1]))
		file.close()
		
		arr.append(pre_arr[int(inputled)])
		
		pre_arr.pop(int(inputled))

# Main loop

while True:
	
	# Grab audio string and convert to array
	
	databin = stream.read(CHUNK)
	data = array.array('f')
	data.fromstring(databin)
	
	# Eradicate negatives
	
	for i in range(len(data)):
		data[i] = abs(data[i])
	
	# Find current volume
	
	volume = numpy.mean(data)
	volume = volume ** 2
	
	# Make list of last n volumes
	
	volume_list.insert(0, volume)
	
	if len(volume_list) > average_samples:
		volume_list.pop(average_samples)
	
	# Find average volume
	
	average = numpy.mean(volume_list)
	
	# Increase intensity if volume is above average
	
	if volume > average:
		intensity = volume-average
	else:
		intensity = 0
		random.shuffle(arr)
		for i in range(len(arr)):
			arr[i][2] = random.random()
	
	# Display intensity
	
	print('[', end='')
	for i in range(math.ceil(intensity * display_width)):
		print('|', end='')
	for i in range(display_width - math.ceil(intensity * display_width)):
		print(' ', end='')
	print(']')
	
	# Set led brightness to intensity
	
	for i in range(len(arr)):
		file = open('/sys/class/leds/' + arr[i][0] + '/brightness', 'w')
		file.write(str(max(int(math.ceil((intensity * arr[i][1] - (i * entry_barrier)) * arr[i][2] * brightness_multiplier)), 0)))
		file.close()
