import csv
import numpy
import os

from analyzer import AudioAnalyzer
from codec import codec_audio
from handle_folder import handle_folder


def audio_coding(params_coding, encode_params, decode_params):
    dir_main_path = params_coding["dir_main_path"]
    audio_base_path = params_coding["audio_base_path"]
    filename_list = params_coding["audio_base_name"]
    codec_dir = params_coding["codec_dir_name"]
    param_codec = params_coding["param_codec"]
    params_value = params_coding["params_value"]
    audio_encode_path = f"{dir_main_path}/encode_audio_base/"
    audio_decode_path = f"{dir_main_path}/decode_audio_base/"
    handle_folder.create_folder(audio_encode_path)
    for value in params_value:
        encode_path = f"{audio_encode_path}audio_{codec_dir}{value}/"
        handle_folder.create_folder(encode_path)
        options = {
            "param_codec": param_codec,
            "param_value": value,
        }
        codec_audio.encode_audios(
            audio_base_path, encode_path, filename_list, encode_params, options)
        decoded_path = f"{audio_decode_path}audio_{codec_dir}{value}/"
        handle_folder.create_folder(audio_decode_path)
        handle_folder.create_folder(decoded_path)
        codec_audio.decode_audios(encode_path, decoded_path, decode_params)


def audio_analyzer(params_coding, audio_analyzer=AudioAnalyzer()):
    dir_main_path = params_coding["dir_main_path"]
    audio_base_path = params_coding["audio_base_path"]
    codec_dir = params_coding["codec_dir_name"]
    param_codec = params_coding["param_codec"]
    params_value = params_coding["params_value"]
    codec_type = params_coding["codec_type"]
    audio_encode_path = f"{dir_main_path}/encode_audio_base/"
    audio_decode_path = f"{dir_main_path}/decode_audio_base/"
    table = []
    for value in params_value:
        encode_path = f"{audio_encode_path}audio_{codec_dir}{value}/"
        decoded_path = f"{audio_decode_path}audio_{codec_dir}{value}/"
        analysis_params = [
            {
                "enc_dir_path": encode_path,
                "dec_dir_path": decoded_path,
                "codec_type": codec_type,
                "param_codec": param_codec,
                "param_value": value,
            },
        ]
        table.append(audio_analyzer.analyzer(audio_base_path, analysis_params))
    try:
        csv_file = f"comparator-{codec_type}.csv"
        with open(csv_file, "w") as csvfile:
            writer = csv.DictWriter(csvfile, audio_analyzer.fieldnames, delimiter=';')
            writer.writeheader()
            for row in table:
                for data in row.values():
                    writer.writerow(data)
    except IOError:
        print("I/O error")


def __main__():
    dir_main_path = os.path.dirname(os.path.realpath(__file__))
    audio_base_path = f"{dir_main_path}/audio_base/"

    if not handle_folder.is_folder(audio_base_path):
        print("O diretório da base de áudios não foi encontrado")
        exit()

    audio_base_name = os.listdir(audio_base_path)
    codec_dir_name = "vorbis_q"
    param_type = "quality"
    param_codec = "--quality"
    params_value = numpy.arange(-1, 11, 0.5)
    # codec_dir_name = "vorbis_bitrate"
    # param_codec = "--managed -b"
    # params_value = numpy.linspace(250, 256, 3)
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
    encode_audio_params = {
        "command":
            "oggenc %(audiofile_wav)s --output=%(audiofile)s %(param_codec)s %(param_value)s",
        "extension": ".ogg",
        "codec_type": "vorbis",
    }
    decode_audio_params = {
        "command": "oggdec %(audiofile)s --output=%(audiofile_wav)s",
        "extension": ".ogg",
        "codec_type": "vorbis",
    }
    audio_coding(params_audio_coding, encode_audio_params, decode_audio_params)
    audio_analyzer(params_audio_coding, AudioAnalyzer(param_type))

    # codec_dir_name = "opus_bitrate"
    # encode_command = "opusenc %(audiofile_wav)s %(audiofile)s %(param_codec)s %(param_value)s"
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
