import board
import digitalio
import analogio
import simpleio
import time
import math

import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange

modeSwitch = digitalio.DigitalInOut(board.GP15)
topSwitch = digitalio.DigitalInOut(board.GP14)
pot = None


analogmode = False
topSwitchPos = False

potMin = 272
potMax = 65535

filterAlpha = 0.5
potFiltered = None

lastMidiValue = 0

modeSwitch.direction = digitalio.Direction.INPUT
modeSwitch.pull = digitalio.Pull.UP
topSwitch.direction = digitalio.Direction.INPUT
topSwitch.pull = digitalio.Pull.UP

midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0], in_channel=0, midi_out=usb_midi.ports[1], out_channel=0
)

while True:
    if modeSwitch.value != analogmode:
        analogmode = modeSwitch.value
        if analogmode:
            pot = analogio.AnalogIn(board.A3)
        else:
            if pot != None:
                pot.deinit()
                pot = None
    if topSwitch.value != topSwitchPos and not analogmode:
        topSwitchPos = topSwitch.value
        midi.send(ControlChange(1, 0 if topSwitchPos else 127))

    if pot != None:

        if potFiltered is None:
            potFiltered = pot.value
        else:
            potFiltered = (filterAlpha * pot.value) + ((1 - filterAlpha) * potFiltered)
        midiValue = int(simpleio.map_range(potFiltered, potMin, potMax, 0, 127))
        if midiValue != lastMidiValue:
            midi.send(ControlChange(1, midiValue))
            lastMidiValue = midiValue

    time.sleep(0.1)

