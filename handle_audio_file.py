import audio_metadata
import os
import soundfile

from sklearn.metrics import mean_squared_error as mse

def create_folder(dir_name):
    if os.path.isdir(dir_name):
        return

    os.mkdir(dir_name)

def handle_name_file(name_file):
    return name_file.replace('\'', '\\\'').replace(' ', '\ ').replace(',', '\,').replace('(', '\(').replace(')', '\)')

def encode(path_audios_dir_base, path_dir_encod, names_audio_base, command, extension, file_type):
    dir_encod_len = len(os.listdir(path_dir_encod))
    if dir_encod_len == 40:
        print('Arquivos já codificados em', file_type)
        return

    for name in names_audio_base:
        name_audio = handle_name_file(name)
        name_files = {
            'audiofile': path_dir_encod + name_audio.replace(".wav", extension),
            'audiofile_wav': path_audios_dir_base + name_audio
        }
        erro = os.system(command % name_files)
        if not erro == 0:
            print('Ocorreu algum erro no processo:', str(erro))
            return

def decode(path_dir_cod, path_dir_decod, command, extension, file_type):
    dir_decod_len = len(os.listdir(path_dir_decod))
    if dir_decod_len == 40:
        print('Arquivos já decodificados em', file_type)
        return

    names_audio_encod = os.listdir(path_dir_cod)
    for name in names_audio_encod:
        name_audio = handle_name_file(name)
        name_files = {
            'audiofile': path_dir_cod + name_audio,
            'audiofile_wav': path_dir_decod + name_audio.replace(extension, ".wav")
        }
        erro = os.system(command % name_files)
        if not erro == 0:
            print('Ocorreu algum erro no processo:', str(erro))
            return

def check_length(audio_original, audio_encod):
    metadata_original = audio_metadata.load(audio_original)
    print('Tamanho áudio original', str(metadata_original.streaminfo._size))
    metadata_decod = audio_metadata.load(audio_encod)
    print('Tamanho áudio codificado', str(metadata_decod.streaminfo._size))

def comparator(names_audio_base, path_dir_decod, type):
    names_decod = os.listdir(path_dir_decod)
    for name_original in names_audio_base:
        audio_original = handle_name_file(name_original)
        audiofile = audio_original.replace(".wav", "")
        audio_decod = [ file for file in names_decod if audiofile in handle_name_file(file) ]
        print('Nome do arquivo original:', name_original)
        print('Nome do arquivo decodificado:', audio_decod[0])
        namefile_original = path_audios_dir_base + name_original
        namefile_decod = path_dir_decod + audio_decod[0]
        check_length(namefile_original, namefile_decod)
        data_original, samplerate_original = soundfile.read(namefile_original)
        data_decod, samplerate_decod = soundfile.read(namefile_decod)
        print('RMSE', type, '=', mse(data_original[:len(data_decod)], data_decod, squared=False))
        print('MSE', type, '=', mse(data_original[:len(data_decod)], data_decod))

dir_name_main = os.path.dirname(os.path.realpath(__file__))

path_audios_dir_base = dir_name_main + '/audio_base/'

path_audios_dir_encod = dir_name_main + '/encoded_audio_base/'
path_dir_encod_flac = path_audios_dir_encod + 'audio_flac/'
path_dir_encod_opus = path_audios_dir_encod + 'audio_opus/'
path_dir_encod_vorbis = path_audios_dir_encod + 'audio_vorbis/'

path_audios_dir_decod = dir_name_main + '/decoded_audio_base/'
path_dir_decod_flac = path_audios_dir_decod + 'audio_flac/'
path_dir_decod_opus = path_audios_dir_decod + 'audio_opus/'
path_dir_decod_vorbis = path_audios_dir_decod + 'audio_vorbis/'

create_folder(path_audios_dir_base)

create_folder(path_audios_dir_encod)
create_folder(path_dir_encod_flac)
create_folder(path_dir_encod_opus)
create_folder(path_dir_encod_vorbis)

create_folder(path_audios_dir_decod)
create_folder(path_dir_decod_flac)
create_folder(path_dir_decod_opus)
create_folder(path_dir_decod_vorbis)

names_audio_base = os.listdir(path_audios_dir_base)

### codificadores default
command_flac_enc = "flac %(audiofile_wav)s --output-name=%(audiofile)s"
extension_flac_enc = "-default-codec.flac"
encode(path_audios_dir_base, path_dir_encod_flac, names_audio_base, command_flac_enc, extension_flac_enc, 'FLAC')

command_opus_enc = "opusenc %(audiofile_wav)s %(audiofile)s"
extension_opus_enc = "-default-codec.opus"
encode(path_audios_dir_base, path_dir_encod_opus, names_audio_base, command_opus_enc, extension_opus_enc, 'Opus')

command_vorbis_enc = "oggenc %(audiofile_wav)s --output=%(audiofile)s"
extension_vorbis_enc = "-default-codec.ogg"
encode(path_audios_dir_base, path_dir_encod_vorbis, names_audio_base, command_vorbis_enc, extension_vorbis_enc, 'Vorbis')

### decodificadores default
command_flac_dec = "flac -d %(audiofile)s --output-name=%(audiofile_wav)s"
decode(path_dir_encod_flac, path_dir_decod_flac, command_flac_dec, ".flac", 'FLAC')

command_opus_dec = "opusdec %(audiofile)s %(audiofile_wav)s"
decode(path_dir_encod_opus, path_dir_decod_opus, command_opus_dec, ".opus", 'Opus')

command_vorbis_dec = "oggdec %(audiofile)s --output=%(audiofile_wav)s"
decode(path_dir_encod_vorbis, path_dir_decod_vorbis, command_vorbis_dec, ".ogg", 'Vorbis')

### compara resultado
comparator(names_audio_base, path_dir_decod_flac, 'flac')
comparator(names_audio_base, path_dir_decod_opus, 'opus')
comparator(names_audio_base, path_dir_decod_vorbis, 'vorbis')


#########################################
### codificadores alterando parâmetros
path_dir_encod_flac_compr_lvl_8 = path_audios_dir_encod + 'audio_flac_compr_lvl_8/'
path_dir_encod_opus_comp_8 = path_audios_dir_encod + 'audio_opus_comp_8/'

path_dir_decod_flac_compr_lvl_8 = path_audios_dir_decod + 'audio_flac_compr_lvl_8/'
path_dir_decod_opus_comp_8 = path_audios_dir_decod + 'audio_opus_comp_8/'

create_folder(path_dir_encod_flac_compr_lvl_8)
create_folder(path_dir_encod_opus_comp_8)

create_folder(path_dir_decod_flac_compr_lvl_8)
create_folder(path_dir_decod_opus_comp_8)

### codifica
command_flac_enc = "flac %(audiofile_wav)s --output-name=%(audiofile)s --compression-level-8"
extension_flac_enc = "-compression-level-8-codec.flac"
encode(path_audios_dir_base, path_dir_encod_flac_compr_lvl_8, names_audio_base, command_flac_enc, extension_flac_enc, 'FLAC')

command_opus_enc = "opusenc %(audiofile_wav)s %(audiofile)s --comp 8"
extension_opus_enc = "-comp-8-codec.opus"
encode(path_audios_dir_base, path_dir_encod_opus_comp_8, names_audio_base, command_opus_enc, extension_opus_enc, 'Opus')

### decodifica
command_flac_dec_compr_lvl_8 = "flac -d %(audiofile)s --output-name=%(audiofile_wav)s"
decode(
    path_dir_encod_flac_compr_lvl_8,
    path_dir_decod_flac_compr_lvl_8,
    command_flac_dec_compr_lvl_8,
    ".flac", 'FLAC')

command_opus_dec_comp_8 = "opusdec %(audiofile)s %(audiofile_wav)s"
decode(
    path_dir_encod_opus_comp_8, path_dir_decod_opus_comp_8, command_opus_dec_comp_8, ".opus", 'Opus')

### compara resultado
comparator(names_audio_base, path_dir_decod_flac_compr_lvl_8, 'flac com compression level 8')
comparator(names_audio_base, path_dir_decod_opus_comp_8, 'opus com comp 8')