import csv
import os

from analyzer import AudioAnalyzer
from codec import codec_audio


def is_folder(dir_name):
    return os.path.isdir(dir_name)


def check_folder(dir_name):
    if not is_folder(dir_name):
        print(f"Diretório '{dir_name}' não encontrado")
        return


def create_folder(dir_name):
    if is_folder(dir_name):
        return

    os.mkdir(dir_name)


def analyzer_codec(
    codec_type, encoded_directory_path, decoded_directory_path,
    audio_base_path, audio_analyzer=AudioAnalyzer()
):
    table = []
    fieldnames = [
        "filename",
        "type",
        "original_data_size",
        "original_bitrate",
        "encode_data_size",
        "encode_bitrate",
        "MSE",
        "RMSE",
        "PSNR",
        "PEAQ_ODG",
        "PEAQ_DI"
    ]
    decoded_audio_info_list = [
        {
            "encoded_directory_path": encoded_directory_path,
            "decoded_directory_path": decoded_directory_path,
            "codec_type": codec_type,
        },
    ]
    table.append(audio_analyzer.analyzer(audio_base_path, decoded_audio_info_list))
    try:
        csv_file = f"comparator-kamedo-{codec_type}.csv"
        with open(csv_file, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            for row in table:
                for data in row.values():
                    writer.writerow(data)
    except IOError:
        print("I/O error")


def analyzer_codec_vorbis(dir_name_main, audio_base_path):
    vorbis_encoded_path = f"{dir_name_main}/site_vorbis/"
    vorbis_decoded_path = f"{dir_name_main}/site_vorbis_decoded/"
    check_folder(vorbis_encoded_path)
    create_folder(vorbis_decoded_path)
    codec_type = "vorbis"
    command_vorbis_dec = "oggdec %(audiofile)s --output=%(audiofile_wav)s"
    codec_audio.decode_audios(
        vorbis_encoded_path,
        vorbis_decoded_path,
        command_vorbis_dec,
        ".ogg",
        "Vorbis"
    )
    analyzer_codec(
        codec_type, vorbis_encoded_path, vorbis_decoded_path, audio_base_path)


def analyzer_codec_opus(dir_name_main, audio_base_path):
    opus_encoded_path = f"{dir_name_main}/site_opus/"
    opus_decoded_path = f"{dir_name_main}/site_opus_decoded/"
    check_folder(opus_encoded_path)
    create_folder(opus_decoded_path)
    codec_type = "opus"
    command_opus_dec = "opusdec %(audiofile)s %(audiofile_wav)s"
    codec_audio.decode_audios(
        opus_encoded_path,
        opus_decoded_path,
        command_opus_dec,
        ".html",
        "OPUS"
    )
    analyzer_codec(
        codec_type, opus_encoded_path, opus_decoded_path, audio_base_path)


def __main__():
    dir_name_main = os.path.dirname(os.path.realpath(__file__))
    audio_base_path = f"{dir_name_main}/audio_base/"

    if not os.path.isdir(audio_base_path):
        print("O diretório da base de áudios não foi encontrado")
        exit()

    analyzer_codec_opus(dir_name_main, audio_base_path)
    analyzer_codec_vorbis(dir_name_main, audio_base_path)


__main__()
