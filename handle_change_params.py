import csv
import numpy
import os

from codec import codec_audio
from analyzer import AudioAnalyzer


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


def audio_encoding(
    audio_base_path, path_dir_encod, names_audio_base, encoder_command,
    encoder_extension, codec_type, param_codec, param_value
):
    encode_audio_params = {
        "audio_base_path": audio_base_path,
        "encode_path": path_dir_encod,
        "audio_name_list": names_audio_base,
        "command": encoder_command,
        "param_codec": param_codec,
        "param_value": param_value,
        "extension": encoder_extension,
        "codec_type": codec_type,
    }
    codec_audio.encode_audios(encode_audio_params)


def audio_encoding_opus(
    audio_base_path, path_dir_encod, names_audio_base, param_codec="", param_value=""
):
    encoder_command = "opusenc %(audiofile_wav)s %(audiofile)s %(param_codec)s %(param_value)s"
    codec_type = "opus"
    encoder_extension = f".{codec_type}"
    audio_encoding(
        audio_base_path, path_dir_encod, names_audio_base, encoder_command,
        encoder_extension, codec_type, param_codec, param_value
    )


def audio_encoding_vorbis(
    encode_path, audio_base_path, names_audio_base, param_codec="", param_value=""
):
    encoder_command = (
        "oggenc %(audiofile_wav)s --output=%(audiofile)s %(param_codec)s %(param_value)s")
    codec_type = "vorbis"
    encoder_extension = ".ogg"
    audio_encoding(
        audio_base_path, encode_path, names_audio_base, encoder_command,
        encoder_extension, codec_type, param_codec, param_value
    )


def audio_decoding_vorbis(decoded_path, encode_path, codec_dir_name, param_value):
    decode_command = "oggdec %(audiofile)s --output=%(audiofile_wav)s"
    codec_type = "vorbis"
    encoder_extension = ".ogg"
    codec_audio.decode_audios(
        encode_path, decoded_path, decode_command, encoder_extension, codec_type)
    return decoded_path


def audio_coding(params_audio_coding, audio_analyzer=AudioAnalyzer()):
    dir_main_path = params_audio_coding["dir_main_path"]
    audio_base_path = params_audio_coding["audio_base_path"]
    audio_base_name = params_audio_coding["audio_base_name"]
    codec_dir_name = params_audio_coding["codec_dir_name"]
    param_codec = params_audio_coding["param_codec"]
    params_value = params_audio_coding["params_value"]
    codec_type = params_audio_coding["codec_type"]
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
    table = []
    for value in params_value:
        audio_encode_path = f"{dir_main_path}/encode_audio_base/"
        encode_path = f"{audio_encode_path}audio_{codec_dir_name}{value}/"
        create_folder(audio_encode_path)
        create_folder(encode_path)
        audio_encoding_vorbis(
            encode_path, audio_base_path, audio_base_name, param_codec, value
        )
        audio_decode_path = f"{dir_main_path}/decode_audio_base/"
        decoded_path = f"{audio_decode_path}audio_{codec_dir_name}{value}/"
        create_folder(audio_decode_path)
        create_folder(decoded_path)
        audio_decoding_vorbis(decoded_path, encode_path, codec_dir_name, value)
        decoded_audio_info_list = [
            {
                "encoded_directory_path": encode_path,
                "decoded_directory_path": decoded_path,
                "codec_type": codec_type,
                "param_codec": param_codec,
                "param_value": value,
            },
        ]
        table.append(audio_analyzer.analyzer(audio_base_path, decoded_audio_info_list))
    try:
        csv_file = f"comparator-{codec_type}.csv"
        with open(csv_file, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            for row in table:
                for data in row.values():
                    writer.writerow(data)
    except IOError:
        print("I/O error")


def __main__():
    dir_main_path = os.path.dirname(os.path.realpath(__file__))
    audio_base_path = f"{dir_main_path}/audio_base/"

    if not is_folder(audio_base_path):
        print("O diretório da base de áudios não foi encontrado")
        exit()

    audio_base_name = os.listdir(audio_base_path)

    codec_dir_name = "vorbis_q"
    param_codec = "--quality"
    params_value = numpy.linspace(-1, 10, 12)
    codec_type = "vorbis"
    params_audio_coding = {
        "dir_main_path": dir_main_path,
        "audio_base_path": audio_base_path,
        "audio_base_name": audio_base_name,
        "codec_dir_name": codec_dir_name,
        "param_codec": param_codec,
        "params_value": params_value,
        "codec_type": codec_type,
    }
    audio_coding(params_audio_coding)

    # codec_dir_name = "opus_bitrate"
    # encode_command = "opusenc %(audiofile_wav)s %(audiofile)s %(param_codec)s %(params_value)s"
    # decode_command = "opusdec %(audiofile)s %(audiofile_wav)s"
    # extension = ".opus"
    # param_codec = "--bitrate"
    # params_value = numpy.linspace(-1, 10, 12)
    # codec_type = "opus"
    # audio_coding(
    #     dir_main_path, codec_dir_name, encode_command, decode_command,
    #     extension, param_codec, params_value, codec_type
    # )


__main__()
