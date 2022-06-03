import os

from codec import codec_audio
from analyzer import AudioAnalyzer


def create_folder(dir_name):
    if os.path.isdir(dir_name):
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
    audio_base_path, path_dir_encod, names_audio_base,
    suffix, param_codec="", param_value=""
):
    encoder_command = "opusenc %(audiofile_wav)s %(audiofile)s %(param_codec)s %(param_value)s"
    codec_type = "opus"
    encoder_extension = f"{suffix}.{codec_type}"
    audio_encoding(
        audio_base_path, path_dir_encod, names_audio_base, encoder_command,
        encoder_extension, codec_type, param_codec, param_value
    )


def audio_encoding_vorbis(
    audio_base_path, path_dir_encod, names_audio_base,
    suffix, param_codec="", param_value=""
):
    encoder_command = (
        "oggenc %(audiofile_wav)s --output=%(audiofile)s %(param_codec)s %(param_value)s")
    codec_type = "vorbis"
    encoder_extension = f"{suffix}.ogg"
    audio_encoding(
        audio_base_path, path_dir_encod, names_audio_base, encoder_command,
        encoder_extension, codec_type, param_codec, param_value
    )


def audio_decoding(path_dir_encod, decoded_path, decoded_command, extension, codec_type):
    codec_audio.decode_audios(
        path_dir_encod, decoded_path, decoded_command, extension, codec_type)

def __main__():
    dir_name_main = os.path.dirname(os.path.realpath(__file__))
    audio_base_path = f"{dir_name_main}/audio_base/"

    if not os.path.isdir(audio_base_path):
        print("O diretório da base de áudios não foi encontrado")
        exit()

    names_audio_base = os.listdir(audio_base_path)
    suffix_default = "-default-codec."

    path_audios_dir_encod = f"{dir_name_main}/encoded_audio_base/"
    create_folder(path_audios_dir_encod)

    path_dir_encod_opus = f"{path_audios_dir_encod}audio_opus/"
    create_folder(path_dir_encod_opus)
    audio_encoding_opus(
        audio_base_path, path_dir_encod_opus, names_audio_base, suffix_default)

    path_dir_encod_vorbis = f"{path_audios_dir_encod}audio_vorbis/"
    create_folder(path_dir_encod_vorbis)
    audio_encoding_vorbis(
        audio_base_path, path_dir_encod_vorbis, names_audio_base, suffix_default)

    path_dir_encod_opus_comp_8 = f"{path_audios_dir_encod}audio_opus_comp_8/"
    create_folder(path_dir_encod_opus_comp_8)
    suffix_comp_8 = "-comp-8-codec."
    param_codec = "--comp"
    param_value = 8
    audio_encoding_opus(
        audio_base_path, path_dir_encod_opus_comp_8, names_audio_base,
        suffix_comp_8, param_codec, param_value
    )

    path_audios_dir_decod = f"{dir_name_main}/decoded_audio_base/"
    create_folder(path_audios_dir_decod)

    opus_decoded_path = f"{path_audios_dir_decod}audio_opus/"
    create_folder(opus_decoded_path)
    command_opus_dec = "opusdec %(audiofile)s %(audiofile_wav)s"
    codec_type = "opus"
    extension = f".{codec_type}"
    audio_decoding(
        path_dir_encod_opus, opus_decoded_path, command_opus_dec, extension, codec_type)

    opus_decoded_path_comp_8 = f"{path_audios_dir_decod}audio_opus_comp_8/"
    create_folder(opus_decoded_path_comp_8)
    audio_decoding(
        path_dir_encod_opus_comp_8, opus_decoded_path_comp_8,
        command_opus_dec, extension, codec_type
    )

    vorbis_decoded_path = f"{path_audios_dir_decod}audio_vorbis/"
    create_folder(vorbis_decoded_path)
    command_vorbis_dec = "oggdec %(audiofile)s --output=%(audiofile_wav)s"
    codec_type = "vorbis"
    extension = ".ogg"
    audio_decoding(
        path_dir_encod_vorbis, vorbis_decoded_path, command_vorbis_dec, extension, codec_type)

    decoded_audio_info_list = [
        {
            "decoded_directory_path": opus_decoded_path,
            "codec_type": "opus"
        },
        {
            "decoded_directory_path": vorbis_decoded_path,
            "codec_type": "vorbis"
        },
        {
            "decoded_directory_path": opus_decoded_path_comp_8,
            "codec_type": "opus"
        },
    ]
    audio_analyzer = AudioAnalyzer()
    audio_analyzer.analyzer(audio_base_path, decoded_audio_info_list)

__main__()
