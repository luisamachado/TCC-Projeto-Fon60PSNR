import os
import subprocess
from handle_folder import handle_folder

def adjust_special_characters(value):
    """ Ajusta os caracteres especiais do nome de arquivo para
        o formato aceito pela linha de comando do Linux

        Args:
            filename: Nome do arquivo

        Returns:
            new_filename: Nome do arquivo ajustado

    """
    new_value = value.replace("\'", "\\\'")
    new_value = new_value.replace(" ", "\ ")
    new_value = new_value.replace(",", "\,")
    new_value = new_value.replace("(", "\(")
    return new_value.replace(")", "\)")


def check_file_exist(filename_list, codec_path):
    """ Verifica se os arquivos codificados/decodificados já existem no diretório

        Args:
            filename_list: Lista com os nomes dos arquivos
            codec_path: Caminho da pasta que será verificada a existência dos
                        arquivos da lista 'filename_list'

        Returns:
            count_exist: Número correspondente a quantidade de arquivos da lista
                         'filename_list' que está presente na pasta 'codec_path'
    """
    codec_path_list = os.listdir(codec_path)
    count_exist = 0
    for name in filename_list:
        name, _ = os.path.splitext(name)
        for name_codec in codec_path_list:
            name_codec, _ = os.path.splitext(name_codec)
            if name_codec == name:
                count_exist = count_exist + 1
    return count_exist


def recursive_audio_encoder(params_coding, encode_config):
    dir_main_path = params_coding["dir_main_path"]
    audio_base_path = params_coding["audio_base_path"]
    codec_dir = params_coding["codec_type"]
    param_codec = params_coding["param_codec"]
    params_value = params_coding["params_value"]
    audio_encode_path = f"{dir_main_path}/{codec_dir}_encode_audio/"
    handle_folder.create_folder(audio_encode_path)
    for value in params_value:
        config_type = param_codec.replace("--", "")
        encode_path = f"{audio_encode_path}{config_type}_{value}/"
        handle_folder.create_folder(encode_path)
        encode_params = {
            "param_codec": param_codec,
            "param_value": value,
        }
        encode_audios(
            audio_base_path, encode_path, encode_config, encode_params)

    print("----------------------------------------------------------------------------")
    print(f"Os diretórios com os arquivos codificados com {codec_dir} se encontram em:\n")
    print(audio_encode_path)
    print("----------------------------------------------------------------------------")
    return audio_encode_path


def encode_audios(audio_base_path, encode_path, encode_config, encode_params):
    """ Codifica todos os áudios no formato wav de um diretório

        Args:
            audio_base_path: Caminho do diretório com os áudios do tipo wav
            encode_path: Caminho do diretório que ficarão os arquivos codificados
            encode_config: Configurações do comando do codificador
            encode_params: Parâmetros de codificação
    """
    command = encode_config["command"]
    extension_codec = encode_config["extension"]
    param_codec = encode_params.get("param_codec", "")
    param_value = encode_params.get("param_value", "")

    filename_list = os.listdir(audio_base_path)
    count_exist = check_file_exist(filename_list, encode_path)
    if count_exist == len(filename_list):
        return

    for name in filename_list:
        original_filename = os.path.join(audio_base_path, name)
        adjusted_filename = adjust_special_characters(name)
        original_adjusted_filename = os.path.join(audio_base_path, adjusted_filename)

        filename, _ = os.path.splitext(adjusted_filename)
        new_filename = f"{filename}{extension_codec}"
        encode_filename = os.path.join(encode_path, new_filename)
        params_command = {
            "audiofile": encode_filename,
            "audiofile_wav": original_adjusted_filename,
            "param_codec": param_codec,
            "param_value": param_value,
        }
        try:
            subprocess.check_call(command % params_command, shell=True, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("----------------------------------------------------------------------------")
            print("Ocorreu algum erro no processo")
            print(f"Verifique o arquivo: '{original_filename}'")
            print("----------------------------------------------------------------------------")


def recursive_audio_decoder(audio_encode_path, params_coding, decode_config):
    dir_main_path = params_coding["dir_main_path"]
    codec_dir = params_coding["codec_type"]
    param_codec = params_coding["param_codec"]
    params_value = params_coding["params_value"]
    audio_decode_path = f"{dir_main_path}/{codec_dir}_decode_audio/"
    for value in params_value:
        config_type = param_codec.replace("--", "")
        encode_path = f"{audio_encode_path}{config_type}_{value}/"
        decoded_path = f"{audio_decode_path}{config_type}_{value}/"
        handle_folder.create_folder(audio_decode_path)
        handle_folder.create_folder(decoded_path)
        decode_audios(encode_path, decoded_path, decode_config)

    print("----------------------------------------------------------------------------")
    print(f"Os diretórios com os arquivos decodificados com {codec_dir} se encontram em:\n")
    print(audio_decode_path)
    print("----------------------------------------------------------------------------")
    return audio_decode_path


def decode_audios(encode_path, decode_path, decode_config):
    """ Decodifica todos os áudios no formato ogg ou opus de um diretório

    Args:
        encode_path: Caminho do diretório com os áudios do tipo ogg ou opus
        decode_path: Caminho do diretório que ficarão os arquivos decodificados
        decode_config: Configurações do comando do decodificador
    """
    command = decode_config["command"]
    dir_decod_len = len(os.listdir(decode_path))
    if dir_decod_len != 0:
        return

    filenames_encod = os.listdir(encode_path)
    for filename in filenames_encod:
        encode_filename = os.path.join(encode_path, filename)
        adjusted_filename = adjust_special_characters(filename)
        filename, _ = os.path.splitext(adjusted_filename)
        new_filename = f"{filename}.wav"
        params_command = {
            "audiofile": os.path.join(encode_path, adjusted_filename),
            "audiofile_wav": os.path.join(decode_path, new_filename),
        }

        try:
            subprocess.check_call(command % params_command, shell=True, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("----------------------------------------------------------------------------")
            print("Ocorreu algum erro no processo")
            print(f"Verifique o arquivo: '{encode_filename}'")
            print("----------------------------------------------------------------------------")

