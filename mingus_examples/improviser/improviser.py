#!/usr/bin/env python
"""

*** Description ***

	Converts a progression to chords, orchestrates them and plays 
	them using fluidsynth.

	Make sure you have a fluidsynth server listening at port 9800
	for this example to work.
	
	Based on play_progression.py

"""

from mingus.core import progressions, intervals
from mingus.core import chords as ch
from mingus.containers import NoteContainer, Note
from mingus.extra import fluidsynth
import time, sys
from random import random, choice, randrange

progression = ["I", "vi", "ii", "iii7",
               "I7", "viidom7", "iii7", "V7"]

key = 'C'

# If True every second iteration will be played 
# in double time, starting on the first
double_time = True


# Orchestrates every second iteration with an additional instrument
# If False, orchestrates every iteration
orchestrate_second = True

swing = True
play_solo = True
play_drums = True
play_bass = True
play_chords = True

bar_length = 2.0
song_end = 1000

# Control beginning of solos and chords
solo_start = 0
solo_end = song_end

chord_start = 0
chord_end = song_end

# Channels
chord_channel = 1
chord_channel2 = 7
chord_channel3 = 3
bass_channel = 4
solo_channel = 13

random_solo_channel = False

if not fluidsynth.init_fluidsynth():
	print "Couldn't connect to FluidSynth server at port 9800."
	sys.exit(1)

chords = progressions.to_chords(progression, key)
loop = 1
while loop < song_end:
	i = 0 

	if random_solo_channel:
		solo_channel = choice(range(5,8) + [11])

	for chord in chords:
		c = NoteContainer(chords[i])
		l = Note(c[0].name)
		n = Note('C')
		l.octave_down()
		l.octave_down()

		print ch.determine(chords[i])[0]


		# Play chord
		if not swing and play_chords and loop > chord_start and loop < chord_end:
			fluidsynth.play_NoteContainer(c, randrange(50,75), chord_channel)

		if play_chords and loop > chord_start and loop < chord_end:
			if orchestrate_second:
				if loop % 2 == 0:
					fluidsynth.play_NoteContainer(c, randrange(50,75), chord_channel2)
			else:
				fluidsynth.play_NoteContainer(c, randrange(50,75), chord_channel2)


		# Create random solo over chord
		if double_time:
			beats = [ random() > 0.5 for x in range((loop % 2 + 1) * 8)]
		else:
			beats = [ random() > 0.5 for x in range(8)]
		t = 0
		for beat in beats:

			# Play random note
			if beat and play_solo and loop > solo_start and loop < solo_end:
				fluidsynth.stop_Note(n)
				if t % 2 == 0:
					n = Note(choice(c).name)
					
				elif random() > 0.5:
					if random() < 0.46:
						n = Note(intervals.second(choice(c).name, key))
					elif random() < 0.46:
						n = Note(intervals.seventh(choice(c).name, key))
					else:
						n = Note(choice(c).name)

					if t > 0 and t < len(beats) - 1:
						if beats[t-1] and not beats[t+1]:
							n = Note(choice(c).name)
				fluidsynth.play_Note(n, randrange(80, 110), solo_channel)
				print n

			# Repeat chord on half of the bar
			if play_chords and t != 0 and loop > chord_start and loop < chord_end:
				if swing and random() > 0.95:
					fluidsynth.play_NoteContainer(c, randrange(20, 75), chord_channel3)
				elif t % (len(beats) / 2) == 0 and t != 0:
					fluidsynth.play_NoteContainer(c, randrange(20, 75), chord_channel3)

			# Play bass note
			if play_bass and t % 4 == 0 and t != 0:
				l = Note(choice(c).name)
				l.octave_down()
				l.octave_down()
				fluidsynth.play_Note(l, randrange(50,75), bass_channel)
			elif play_bass and t == 0:
				fluidsynth.play_Note(l, randrange(50,75), bass_channel)

			# Drums
			if play_drums and loop > 0:
				if t % (len(beats) / 2) == 0 and t != 0:
					fluidsynth.play_Note(Note("E", 2), randrange(50,100), 9) # snare
				else:
					if random() > 0.8 or t == 0:
						fluidsynth.play_Note(Note("C", 2), randrange(20,100), 9) # bass

				if t == 0 and random() > 0.75:
					fluidsynth.play_Note(Note("C#", 3), randrange(60,100), 9) # crash

				if swing:
					if random() > 0.9:
						fluidsynth.play_Note(Note("A#", 2), randrange(50,100), 9) # hihat open
					elif random() > 0.6:
						fluidsynth.play_Note(Note("G#", 2), randrange(100,120), 9) # hihat closed
					if random() > 0.95:
						fluidsynth.play_Note(Note("E", 2), 100, 9) # snare
				elif t % 2 == 0: 
					fluidsynth.play_Note(Note("A#", 2), 100, 9) # hihat open
				else:
					if random() > 0.9:
						fluidsynth.play_Note(Note("E", 2), 100, 9) # snare
	
			if swing:
				if t % 2 == 0:
					time.sleep( (bar_length / (len(beats) * 3)) * 4)
				else:
					time.sleep( (bar_length / (len(beats) * 3)) * 2)
			else:
				time.sleep( bar_length / len(beats))
			t += 1

		fluidsynth.stop_NoteContainer(c, chord_channel)
		fluidsynth.stop_NoteContainer(c, chord_channel2)
		fluidsynth.stop_NoteContainer(c, chord_channel3)
		fluidsynth.stop_Note(l, bass_channel)
		fluidsynth.stop_Note(n, solo_channel)
		i += 1
	print "-" * 20
	loop += 1
