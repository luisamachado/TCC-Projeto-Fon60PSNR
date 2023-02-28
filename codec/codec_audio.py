import os

def adjust_special_characters(value):
    new_value = value.replace("\'", "\\\'")
    new_value = new_value.replace(" ", "\ ")
    new_value = new_value.replace(",", "\,")
    new_value = new_value.replace("(", "\(")
    return new_value.replace(")", "\)")

def encode_audios(audio_base_path, encode_path, filename_list, encode_params, options):
    command = encode_params["command"]
    extension = encode_params["extension"]
    codec_type = encode_params["codec_type"]
    param_codec = options.get("param_codec", "")
    param_value = options.get("param_value", "")

    dir_encod_len = len(os.listdir(encode_path))
    if dir_encod_len == len(filename_list):
        print("Arquivos já codificados em", codec_type.title())
        return

    for name in filename_list:
        adjusted_filename = adjust_special_characters(name)
        new_filename = adjusted_filename.replace(".wav", f"{extension}")
        params_command = {
            "audiofile": f"{encode_path}{new_filename}",
            "audiofile_wav": f"{audio_base_path}{adjusted_filename}",
            "param_codec": param_codec,
            "param_value": param_value,
        }
        erro = os.system(command % params_command)
        if not erro == 0:
            print("Ocorreu algum erro no processo:", str(erro))
            return

def decode_audios(encod_path, decod_path, decode_params):
    command = decode_params["command"]
    extension = decode_params["extension"]
    codec_type = decode_params["codec_type"]
    dir_decod_len = len(os.listdir(decod_path))
    if dir_decod_len != 0:
        print("Arquivos já decodificados em", codec_type.title())
        return

    filenames_encod = os.listdir(encod_path)
    for filename in filenames_encod:
        adjusted_filename = adjust_special_characters(filename)
        new_filename = adjusted_filename.replace(f".{extension}", ".wav")
        params_command = {
            "audiofile": f"{encod_path}{adjusted_filename}",
            "audiofile_wav": f"{decod_path}{new_filename}",
        }
        erro = os.system(command % params_command)
        if not erro == 0:
            print("Ocorreu algum erro no processo:", str(erro))
            return
