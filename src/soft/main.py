import PySimpleGUI as sg
from note import Note
import pygame
from pygame.mixer import pre_init
from threading import Thread
import time
import wave
import math
from run import analyze_wav
from send import send_file_to_com_port
import serial

com_port = '/dev/ttyUSB1'

pygame.init()
pre_init(44100, -16, 1, 1024)
recording_music = False
start_time = 0
last_end_time = 0
music_data = []

# Layout for the Music Input tab
layout_music_input = [
    [sg.Text('Music Input')],
    [sg.Text('', size=(1, 1))] + [sg.Button('C#', size=(3, 4), button_color=('black'))] + [sg.Button('D#', size=(3, 4), button_color=('black'))] + [sg.Text('', size=(3, 1))] + [sg.Button('F#', size=(3, 4), button_color=('black'))] + [sg.Button('G#', size=(3, 4), button_color=('black'))] + [sg.Button('A#', size=(3, 4), button_color=('black'))],
    [sg.Button('C', size=(3, 6), button_color=('black', 'white'))] + [sg.Button('D', size=(3, 6), button_color=('black', 'white'))] + [sg.Button('E', size=(3, 6), button_color=('black', 'white'))] + [sg.Button('F', size=(3, 6), button_color=('black', 'white'))] + [sg.Button('G', size=(3, 6), button_color=('black', 'white'))] + [sg.Button('A', size=(3, 6), button_color=('black', 'white'))] + [sg.Button('B', size=(3, 6), button_color=('black', 'white'))], 
    [sg.Text('Waveform'), sg.DropDown(['square', 'sine', 'triangle', 'sawtooth'], default_value='square', key='waveform')],
    [sg.Text('Note Duration'), sg.Slider(range=(0.1, 2), default_value=0.4, key='note_time', resolution=0.1, enable_events=True, orientation='horizontal')],
    [sg.Text('Volume'), sg.Slider(range=(0.1, 1.0), default_value=0.5, key='volume', resolution=0.1, enable_events=True, orientation='horizontal')],
    [sg.Button('Record', key='record_music'), sg.Button('Send', key='send_music')]
]

# Layout for the Text Input tab with choice male or female
layout_text_input = [
    [sg.Text('Text Input')],
    [sg.Text('Input text:'), sg.InputText(key='input_text')],
    [sg.Radio('Male', 'sex', key='male', default=True), sg.Radio('Female', 'sex', key='female', default=False)],
    [sg.Checkbox('Transcribe', key='transcribe', default=False)],
    [sg.Button('Send', key='send_text')],
]

# Layout for the File Upload tab
layout_file_upload = [
    [sg.Text('File Upload')],
    [sg.Text('Select a file:'), sg.InputText(key='file_path'), sg.FileBrowse(file_types=(("WAV Files", "*.wav"),))],
    [sg.Button('Send', key='send_file')]
]

# Create the tab group layout
layout = [[sg.TabGroup([
    [sg.Tab('Music Input', layout_music_input, key='music_input')],
    [sg.Tab('Text Input', layout_text_input, key='text_input')],
    [sg.Tab('File Upload', layout_file_upload, key='file_upload')]
], key='tab_group')]]

sg.theme('DarkBlue')

notes_freq = {
    'C': 261.63,
    'C#': 277.18,
    'D': 293.66,
    'D#': 311.13,
    'E': 329.63,
    'F': 349.23,
    'F#': 369.99,
    'G': 392.00,
    'G#': 415.30,
    'A': 440.00,
    'A#': 466.16,
    'B': 493.88,
}

def sound_wave(frequency, num_seconds):
    for frame in range(round(num_seconds * 44100)):
        time = frame / 44100
        amplitude = math.sin(2 * math.pi * frequency * time)
        yield round((amplitude + 1) / 2 * 255)

window = sg.Window('BSH Challenge', layout, return_keyboard_events=True)

def play_note_thread(note_freq, volume, duration, waveform, start_time, wf, last_end_time, record):
    note = Note(note_freq, volume, waveform)
    note.play(-1)
    note_start = time.time() - start_time
    pygame.time.delay(int(duration * 1000))  # Delay in milliseconds
    note.stop()
    note_end = time.time() - start_time

    # Calculate the duration of the pause since the last note
    pause_duration = note_start - last_end_time

    # If there is a pause, insert silence into the WAV file
    if record:
        if pause_duration > 0.35:
            num_frames_silence = int(pause_duration * wf.getframerate())
            silence_data = b'\x00' * num_frames_silence * wf.getsampwidth()
            wf.writeframes(silence_data)

        # Append the recorded audio to the WAV file
        wf.writeframes(bytes(note.sound_wave(duration)))

    return (note_freq, note_start, note_end)

wf = wave.open('./output.wav', 'wb')
wf.setnchannels(1)
wf.setsampwidth(1)
wf.setframerate(44100)

while True:
    event, values = window.read()
    active_tab = window['tab_group'].Get()

    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    if (event == 'record_music'):
        recording_music = True
        music_data = []
        start_time = time.time()

    if event == 'send_music':
        if recording_music:
            wf.close()
            analyze_wav('output.wav', 0.1, 'output.txt')
            send_file_to_com_port('output.txt', com_port)
    elif event == 'send_text':
        text = values['input_text']
        is_female = values['female'] == True
        transcribe = values['transcribe'] == True
        text = str(int(transcribe)) + str(int(is_female)) + text
        print(text)
        ser = serial.Serial(com_port, baudrate=9600, timeout=1)
        ser.write(text.encode())
        ser.close()
    elif event == 'send_file':
        file_path = values['file_path']
        print(file_path)
        analyze_wav(file_path, 0.1, 'output.txt')
        send_file_to_com_port('output.txt', com_port)

    if active_tab == 'music_input':
        note_time = values['note_time']
        if event == 'note_time':
            note_time = values['note_time']

        if event in notes_freq:
            # Start a thread for playing the note and appending audio
            Thread(target=play_note_thread, args=(notes_freq[event], values['volume'], note_time, values['waveform'], start_time, wf, last_end_time, recording_music)).start()
            last_end_time = time.time() - start_time  # Update the last end time after playing the note

        if event == 'w':
            window['C'].click()
        elif event == 'e':
            window['D'].click()
        elif event == 'r':
            window['E'].click()
        elif event == 't':
            window['F'].click()
        elif event == 'y':
            window['G'].click()
        elif event == 'u':
            window['A'].click()
        elif event == 'i':
            window['B'].click()
        elif event == '3':
            window['C#'].click()
        elif event == '4':
            window['D#'].click()
        elif event == '6':
            window['F#'].click()
        elif event == '7':
            window['G#'].click()
        elif event == '8':
            window['A#'].click()

wf.close()
window.close()
