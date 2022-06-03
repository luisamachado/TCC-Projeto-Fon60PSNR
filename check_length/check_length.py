import os
import csv
import soundfile
# import matplotlib.pyplot as plt


def _create_table(names_audio_base, table):
    for name in names_audio_base:
        name_audio = name.replace(".wav", "")
        table[name_audio] = {}
        table[name_audio]['filename'] = name_audio
    return table


def _read_directory(path_audios, type_file, names_audio_base, table):
    for namefile in names_audio_base:
        key = namefile.replace(".wav", "")
        if type_file != "wav":
            namefile = namefile.replace(".wav", "") + "-default-codec.wav"
        data, _ = soundfile.read(path_audios + namefile)
        table[key][type_file] = len(data)
        # plot test
        # plt.plot(data[0:500,0])
        # half = int(len(data)/2)
        # plt.plot(data[(half-250):(half+250),0])
        # plt.plot(data[len(data)-500:-1,0])
    return table


dir_name_main = os.path.abspath(os.path.dirname(__file__))
path_audios_dir_base = dir_name_main + '/../audio_base/'
path_audios_dir_decod = dir_name_main + '/../decoded_audio_base/'
path_dir_decod_flac = path_audios_dir_decod + 'audio_flac/'
path_dir_decod_opus = path_audios_dir_decod + 'audio_opus/'
path_dir_decod_vorbis = path_audios_dir_decod + 'audio_vorbis/'

names_audio_base = os.listdir(path_audios_dir_base)
list_partial = names_audio_base#[0:4]
table = {}

_create_table(list_partial, table)

_read_directory(path_audios_dir_base, "wav", list_partial, table)
_read_directory(path_dir_decod_flac, "flac", list_partial, table)
_read_directory(path_dir_decod_opus, "opus", list_partial, table)
_read_directory(path_dir_decod_vorbis, "vorbis", list_partial, table)

csv_file = "compare_file_size.csv"
field_names = ['filename', 'wav', 'flac', 'opus', 'vorbis']

# save csv
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for data in table.values():
            writer.writerow(data)
except IOError:
    print("I/O error")

# plt.ylabel('some numbers')
# plt.show()
# print('')