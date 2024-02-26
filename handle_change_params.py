import os

from analyzer import AudioAnalyzer
from codec import codec_audio
from handle_folder import handle_folder


def handle_codec_vorbis(dir_main_path, audio_base_path):
    codec_type = "vorbis"
    param_type = "bitrate [kbps]"
    param_codec = "--bitrate"
    params_value = [45, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 500,]
    params_audio_coding = {
        "dir_main_path": dir_main_path,
        "audio_base_path": audio_base_path,
        "param_codec": param_codec,
        "params_value": params_value,
        "codec_type": codec_type,
    }
    encode_audio_config = {
        "command":
            "oggenc %(audiofile_wav)s --output=%(audiofile)s %(param_codec)s %(param_value)s",
        "extension": ".ogg",
        "codec_type": codec_type,
    }
    decode_audio_config = {
        "command": "oggdec %(audiofile)s --output=%(audiofile_wav)s",
        "extension": ".ogg",
        "codec_type": codec_type,
    }
    audio_encode_path = codec_audio.recursive_audio_encoder(
        params_audio_coding, encode_audio_config)
    audio_decode_path = codec_audio.recursive_audio_decoder(
        audio_encode_path, params_audio_coding, decode_audio_config)
    audio_analyzer = AudioAnalyzer(param_type)
    audio_analyzer.audio_analyzer(audio_decode_path, params_audio_coding)


def handle_codec_opus(dir_main_path, audio_base_path):
    codec_type = "opus"
    param_type = "bitrate [kbps]"
    param_codec = "--bitrate"
    params_value = [45, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 500,]
    params_audio_coding = {
        "dir_main_path": dir_main_path,
        "audio_base_path": audio_base_path,
        "param_codec": param_codec,
        "params_value": params_value,
        "codec_type": codec_type,
    }
    encode_audio_config = {
        "command":
            "opusenc %(audiofile_wav)s %(audiofile)s %(param_codec)s %(param_value)s",
        "extension": ".opus",
        "codec_type": codec_type,
    }
    decode_audio_config = {
        "command": "opusdec %(audiofile)s %(audiofile_wav)s",
        "extension": ".opus",
        "codec_type": codec_type,
    }

    audio_encode_path = codec_audio.recursive_audio_encoder(
        params_audio_coding, encode_audio_config)
    audio_decode_path = codec_audio.recursive_audio_decoder(
        audio_encode_path, params_audio_coding, decode_audio_config)
    audio_analyzer = AudioAnalyzer(param_type)
    audio_analyzer.audio_analyzer(audio_decode_path, params_audio_coding)


def __main__():
    print("""
          --------------------------------------------------------------------------------
          Projeto desenvolvido para codificar e analisar áudios do diretório 'audio_base'
          --------------------------------------------------------------------------------
          Os áudios do diretório 'audio_base' são codificados e decodificados
          usando os codecs Vorbis e Opus variando a taxa de bits (bitrate).
          Em seguida, cada áudio em seu formato original e decodificado passa
          pelas métricas do analisador e os resultados são registrados em uma
          planilha para análise posterior.
          --------------------------------------------------------------------------------
    """)
    dir_main_path = os.path.dirname(os.path.realpath(__file__))
    audio_base_path = f"{dir_main_path}/audio_base/"

    print(f"O diretório {audio_base_path} será analisado\n")

    if not handle_folder.is_folder(audio_base_path):
        print(f"O diretório {audio_base_path} não foi encontrado\n")
        exit()

    handle_codec_opus(dir_main_path, audio_base_path)
    handle_codec_vorbis(dir_main_path, audio_base_path)


__main__()
