import pyaudio
import array
import numpy
import random
import math

# Initialize pyaudio

CHANNELS = 1
RATE = 48000
MS_PER_UPDATE = 20
FORMAT = pyaudio.paFloat32

CHUNK = math.ceil((MS_PER_UPDATE / 1000) * RATE)
pa_manager = pyaudio.PyAudio()
stream = pyaudio.Stream(pa_manager, RATE, CHANNELS, FORMAT, input=True, frames_per_buffer=CHUNK)

# Initialize variables

sample_time_sec = 60
display_width = 100

average_samples = math.ceil((sample_time_sec * 1000) / 20)
volume_list = array.array('f')

picking = True

out_arr = []
arr = []

while picking:
	print('\nSelected outputs:')
	for i in range(len(arr)):
		print('Path: ' + out_arr[i][0] + ' | Maximum: ' + str(arr[i][1]))
	
	print("\nEnter file path and enter 'done' when finished")
	
	inputled = str(input())
	
	if inputled == 'done':
		picking = False
	else:
		print("\nEnter maximum value of " + inputled + " (Integer)")
		
		maxbright = int(input())
		
		out_arr.append([inputled, maxbright])
		
		file = open(inputled, 'w')
		file.write(str(maxbright))
		file.close()

for i in range(len(out_arr)):
	arr.append(i)

# Main loop

while True:
	
	# Grab audio string and convert to array
	
	databin = stream.read(CHUNK, exception_on_overflow = False)
	data = array.array('f')
	data.fromstring(databin)
	
	# Eradicate negatives
	
	for i in range(len(data)):
		data[i] = abs(data[i])
	
	# Find current volume
	
	volume = numpy.mean(data)
	
	# Discard volume data during silence
	
	if volume == 0:
		volume_list = array.array('f')
	
	# Make list of last n volumes
	
	volume_list.insert(0, volume)
	
	if len(volume_list) > average_samples:
		volume_list.pop(average_samples)
	
	# Find average volume
	
	average = numpy.mean(volume_list)
	
	# Set intensity if volume is above average
	
	if volume > average:
		intensity = (volume - average) / (average)
	else:
		intensity = 0
		random.shuffle(arr)
	
	# Display intensity
	
	#print('[', end='')
	#for i in range(math.ceil(min(intensity, 1) * display_width)):
	#	print('|', end='')
	#for i in range(display_width - math.ceil(min(intensity, 1) * display_width)):
	#	print(' ', end='')
	#print(']')
	
	# Set led brightness to intensity
	
	
	for b in range(len(out_arr)):
		i = arr[b]
		file = open(out_arr[b][0], 'w')
		file.write(str(min(max(int(math.ceil((1 / (1 - (i / len(arr)))) * (intensity - (i / len(arr))) * out_arr[i][1])), 0), out_arr[i][1])))
		file.close()
