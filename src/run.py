import librosa
import numpy as np

def analyze_wav(filename, duration, output_file):
    # Загрузка аудиофайла
    y, sr = librosa.load(filename, sr=None)

    # Разбивка аудиофайла на сегменты длительностью duration секунд
    samples_per_segment = int(sr * duration)
    num_segments = len(y) // samples_per_segment

    frequencies = []

    for i in range(num_segments):
        # Выборка сегмента
        segment = y[i * samples_per_segment: (i + 1) * samples_per_segment]

        # Вычисление частоты
        freqs = np.fft.rfftfreq(len(segment), d=1/sr)
        mag = np.abs(np.fft.rfft(segment))
        peak_freq = freqs[np.argmax(mag)]

        # Преобразование частоты в целое число
        peak_freq_int = int(round(peak_freq))

        # Добавление частоты в список
        frequencies.append(peak_freq_int)

    # Сохранение частот в файл
    with open(output_file, 'w') as f:
        # Запись интовой константы
        f.write("1000 - ")
        # Запись частот
        for freq in frequencies:
            f.write(f"{freq} - 100 - ")

# Вызов функции с указанием имени аудиофайла, длительности сегмента и имени выходного файла
analyze_wav('audio.wav', 0.1, 'output.txt')