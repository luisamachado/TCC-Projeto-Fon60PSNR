import csv
import os

from analyzer import AudioAnalyzer
from codec import codec_audio
from handle_folder import handle_folder


def analyzer_codec(
    codec_type, encoded_directory_path, decoded_directory_path,
    audio_base_path, audio_analyzer=AudioAnalyzer()
):
    decoded_audio_info_list = [
        {
            "enc_dir_path": encoded_directory_path,
            "dec_dir_path": decoded_directory_path,
            "codec_type": codec_type,
        },
    ]
    spreadsheet = audio_analyzer.analyzer(audio_base_path, decoded_audio_info_list)
    try:
        csv_file = f"comparator-kamedo-{codec_type}.csv"
        with open(csv_file, "w") as csvfile:
            writer = csv.DictWriter(csvfile, audio_analyzer.fieldnames, delimiter=';')
            writer.writeheader()
            for data in spreadsheet.values():
                writer.writerow(data)
    except IOError:
        print("I/O error")


def handle_codec(dir_name_main, audio_base_path, dir_encode, dir_decode, config_codec):
    encoded_path = f"{dir_name_main}{dir_encode}"
    decoded_path = f"{dir_name_main}{dir_decode}"
    handle_folder.check_folder(encoded_path)
    handle_folder.create_folder(decoded_path)
    codec_audio.decode_audios(encoded_path, decoded_path, config_codec)
    analyzer_codec(
        config_codec["codec_type"], encoded_path, decoded_path, audio_base_path)


def __main__():
    dir_name_main = os.path.dirname(os.path.realpath(__file__))
    audio_base_path = f"{dir_name_main}/audio_base/"

    if not os.path.isdir(audio_base_path):
        print("O diretório da base de áudios não foi encontrado")
        exit()

    opus_dir_encode = "/site_opus/"
    opus_dir_decode = "/site_opus_decoded/"
    opus_config_codec = {
        "command": "opusdec %(audiofile)s %(audiofile_wav)s",
        "extension": ".html",
        "codec_type": "opus",
    }
    handle_codec(
        dir_name_main, audio_base_path, opus_dir_encode, opus_dir_decode, opus_config_codec)
    
    vorbis_dir_encode = "/site_vorbis/"
    vorbis_dir_decode = "/site_vorbis_decoded/"
    vorbis_config_codec = {
        "command": "oggdec %(audiofile)s --output=%(audiofile_wav)s",
        "extension": ".ogg",
        "codec_type": "vorbis",
    }
    handle_codec(
        dir_name_main, audio_base_path, vorbis_dir_encode, vorbis_dir_decode, vorbis_config_codec)


__main__()
