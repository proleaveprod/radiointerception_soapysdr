import sys
sys.path.append("./libs")

import time
import wave
import numpy as np
import keyboard
import SoapySDR


#region Configs
SAMPLE_RATE = 2048e3
FREQUENCIES = [ 40.5e6, 37e6 ]	# 40.5 MHz (RED), 37 MHz (BLUE)

FWD_KEY = "w"				# Forward
BWD_KEY = "s"				# Backward
CW_KEY = "d"				# Clockwise
CCW_KEY = "a"				# Counter-clockwise
BUCKET_KEY = "SPACE"		# Bucket
RIGHT_TRACK_FWD_KEY = "q"	# Right track FWD
LEFT_TRACK_FWD_KEY = "e"	# Left track FWD
RIGHT_TRACK_BWD_KEY = "z"	# Right track BWD
LEFT_TRACK_BWD_KEY = "c"	# Left track BWD
RESET_KEY = "ENTER"			# Reset
QUIT_KEY = "ESC"			# Quit

#file_names = [ "FWD", "BWD", "CW", "CCW", "BUCKET", "LEFT_TRACK_FWD", "RIGHT_TRACK_FWD", "LEFT_TRACK_BWD", "RIGHT_TRACK_BWD", "STOP" ]
file_names = [ "UP", "DOWN", "RIGHT", "LEFT", "BUCKET", "RIGHTFORWARD", "LEFTFORWARD", "LEFTBACK", "RIGHTBACK", "STOP" ]
cmd_base_directory = "signals512_1024_2048/4x_2048k"

#endregion


cmd_signals = []
sdr = None
txStream = None
selected_channel = 0


def main():
	print("== BEGIN ==")
	init()

	print("\n\nHint: channel select:\n'1' - RED\n'2' - BLUE\n\n")
	print("Your current channel is:\nRED (ch1, 40.5 Mhz)\n\n")
	print("READY")

	while keyboard.is_pressed(QUIT_KEY) == False:
		if (keyboard.is_pressed(RESET_KEY)):
			reset()
			continue

		if (keyboard.is_pressed("1")):
			swtich_channel(1)
			continue

		if (keyboard.is_pressed("2")):
			swtich_channel(2)
			continue

		data_to_send = keyboard_check()

		if len(data_to_send) > 0:
			send_data(data_to_send)

	dispose()
	print("== END ==")


def keyboard_check():
	if keyboard.is_pressed(FWD_KEY):
		return cmd_signals[0]
	elif keyboard.is_pressed(BWD_KEY):
		return cmd_signals[1]
	elif keyboard.is_pressed(CW_KEY):
		return cmd_signals[2]
	elif keyboard.is_pressed(CCW_KEY):
		return cmd_signals[3]
	elif keyboard.is_pressed(BUCKET_KEY):
		return cmd_signals[4]
	elif keyboard.is_pressed(LEFT_TRACK_FWD_KEY):
		return cmd_signals[5]
	elif keyboard.is_pressed(RIGHT_TRACK_FWD_KEY):
		return cmd_signals[6]
	elif keyboard.is_pressed(LEFT_TRACK_BWD_KEY):
		return cmd_signals[7]
	elif keyboard.is_pressed(RIGHT_TRACK_BWD_KEY):
		return cmd_signals[8]
	else:
		return cmd_signals[9]


def send_data(data):
	status = sdr.writeStream(txStream, [data], data.size, timeoutUs=1000000)
	# print(status)

	time.sleep(data.size / SAMPLE_RATE)


def init():
	print("== Initializing ==")

	load_commands()
	init_lime()

	print("== Initialization complete ==")


def dispose():
	global sdr, txStream

	print("\n== Performing cleanup ==")

	sdr.deactivateStream(txStream)
	sdr.closeStream(txStream)

def reset():
	print("== Resetting ==")
	dispose()
	init_lime()
	print("== Reset complete ==")

def swtich_channel(channel):
	global sdr, selected_channel
	print("== Switching channel ==")

	selected_channel = channel - 1
	sdr.setFrequency(SoapySDR.SOAPY_SDR_TX, 0, FREQUENCIES[selected_channel])

	color = [ "RED", "BLUE" ][channel - 1]
	freq = FREQUENCIES[channel - 1] / 1e6

	print(f"\n== Channel {channel} ({color}, {freq} MHz) selected ==\n")
	return


def init_lime():
	print("== Initializing LimeSDR ==")
	global sdr, txStream

	args = dict(driver="lime")
	sdr = SoapySDR.Device_make(args)
	# sdr = SoapySDR.Device(args)

	print("ANTENAS:")
	print(sdr.listAntennas(SoapySDR.SOAPY_SDR_TX, 0))
	print("GAINS:")
	print(sdr.listGains(SoapySDR.SOAPY_SDR_TX, 0))
	print("FREQUENCIES:")
	freqs = sdr.getFrequencyRange(SoapySDR.SOAPY_SDR_TX, 0)
	for freqRange in freqs: print(freqRange)

	sdr.setSampleRate(SoapySDR.SOAPY_SDR_TX, 0, SAMPLE_RATE)
	print(f"{selected_channel}: {FREQUENCIES[selected_channel]}")
	sdr.setFrequency(SoapySDR.SOAPY_SDR_TX, 0, FREQUENCIES[selected_channel])
	sdr.setBandwidth(SoapySDR.SOAPY_SDR_TX, 0, 100e3)
	sdr.setGain(SoapySDR.SOAPY_SDR_TX, 0, 64)
	sdr.setAntenna(SoapySDR.SOAPY_SDR_TX, name="BAND1", channel=0)

	txStream = sdr.setupStream(SoapySDR.SOAPY_SDR_TX, SoapySDR.SOAPY_SDR_CF32,[0])

	sdr.activateStream(txStream)
	print("== LimeSDR is ready ==")


def load_commands():
	print("== Loading commands from files ==")
	global cmd_signals

	for i in range(0, len(file_names)):
		print(f"{i}/{len(file_names)}")
		cmd_signals.append(load_command(file_names[i]))

	print("== Commands loaded ==")


def load_command(name):
	print(f"Loading command {name}")

	file  = wave.open(f"{cmd_base_directory}/{name}.wav")

	nframes = file.getnframes()
	print(f"Frames: {nframes}")

	command = wav_to_array(file, nframes)

	return command


def wav_to_array(wav_signal, samples):
	frames = wav_signal.readframes(samples)

	sig_int16 = np.frombuffer(frames, dtype=np.int16)
	sig_float32 = sig_int16.astype(np.float32)

	return maximise_func(sig_float32, samples)


def maximise_func(signal, samples):
	gain = 0.02
	max_int16 = 2**15
	signal = signal / max_int16

	for i in range(0, samples):
		if (signal[i] < gain) and (signal[i] > -gain):
			signal[i] = 0

	max_sig = max(signal)
	min_sig = min(signal)

	coefficient = 1 / max(max_sig, -min_sig)

	for i in range(0, samples):
		signal[i] *= coefficient

	return signal.astype(np.complex64)


main()
