from pygame.mixer import Sound, get_init
from array import array
import math

class Note(Sound):
    def __init__(self, frequency, volume=.1, waveform='square'):
        self.frequency = frequency
        self.waveform = waveform
        self.volume = volume
        self.amplitude = 0
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

        
    def build_samples(self):
        period = int(round(get_init()[0] / self.frequency * 2))
        samples = array("h", [0] * period)
        self.amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        if self.waveform == 'square':
            for time in range(period):
                if time < period / 2:
                    samples[time] = self.amplitude
                else:
                    samples[time] = -self.amplitude
        elif self.waveform == 'sine':
            for time in range(period):
                samples[time] = int(self.amplitude * math.sin(2 * math.pi * self.frequency * time / get_init()[0]))
        elif self.waveform == 'triangle':
            for time in range(period):
                samples[time] = int((2 * self.amplitude / math.pi) * math.asin(math.sin((2 * math.pi * self.frequency * time / get_init()[0]))))
        elif self.waveform == 'sawtooth':
            for time in range(period):
                if time == 0:
                    samples[time] = 0
                else:
                    samples[time] = int((2 * self.amplitude / math.pi) * (math.atan(1 / math.tan((math.pi * self.frequency * time / get_init()[0])))))
        return samples
    
    def sound_wave(self, num_seconds):
        for frame in range(round(num_seconds * 44100)):
            time = frame / 44100
            if self.waveform == 'sine':
                self.amplitude = (math.sin(2 * math.pi * self.frequency * time) + 1) / 2  # Adjust amplitude range to [0, 1]
            elif self.waveform == 'square':
                self.amplitude = 1 if math.sin(2 * math.pi * self.frequency * time) > 0 else -1
            elif self.waveform == 'triangle':
                self.amplitude = ((2 / math.pi) * math.asin(math.sin(2 * math.pi * self.frequency * time)) + 1) / 2  # Adjust amplitude range to [0, 1]
            elif self.waveform == 'sawtooth':
                if time == 0:
                    self.amplitude = 0
                else:
                    self.amplitude = (2 / math.pi) * (math.atan(1 / math.tan(math.pi * self.frequency * time)))
            yield round((self.amplitude + 1) / 2 * 255)