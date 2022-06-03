import os

def adjust_special_characters(value):
    new_value = value.replace("\'", "\\\'")
    new_value = new_value.replace(" ", "\ ")
    new_value = new_value.replace(",", "\,")
    new_value = new_value.replace("(", "\(")
    return new_value.replace(")", "\)")

def encode_audios(encode_audio_params):
    audio_base_path = encode_audio_params["audio_base_path"]
    encode_path = encode_audio_params["encode_path"]
    audio_name_list = encode_audio_params["audio_name_list"]
    command = encode_audio_params["command"]
    param_codec = encode_audio_params["param_codec"]
    param_value = encode_audio_params["param_value"]
    extension = encode_audio_params["extension"]
    codec_type = encode_audio_params["codec_type"]

    dir_encod_len = len(os.listdir(encode_path))
    if dir_encod_len == len(audio_name_list):
        print("Arquivos já codificados em", codec_type.title())
        return

    for name in audio_name_list:
        name_audio = adjust_special_characters(name)
        params_command = {
            "audiofile": encode_path + name_audio.replace(".wav", f"{extension}"),
            "audiofile_wav": audio_base_path + name_audio,
            "param_codec": param_codec,
            "param_value": param_value,
        }
        erro = os.system(command % params_command)
        if not erro == 0:
            print("Ocorreu algum erro no processo:", str(erro))
            return

def decode_audios(path_dir_encod, path_dir_decod, command, extension, codec_type):
    dir_decod_len = len(os.listdir(path_dir_decod))
    if dir_decod_len != 0:
        print("Arquivos já decodificados em", codec_type.title())
        return

    names_audio_encod = os.listdir(path_dir_encod)
    for name in names_audio_encod:
        name_audio = adjust_special_characters(name)
        params_command = {
            "audiofile": path_dir_encod + name_audio,
            "audiofile_wav": path_dir_decod + name_audio.replace(f".{extension}", ".wav")
        }
        erro = os.system(command % params_command)
        if not erro == 0:
            print("Ocorreu algum erro no processo:", str(erro))
            return
