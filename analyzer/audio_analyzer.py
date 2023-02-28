import audio_metadata
import locale
import os
import soundfile

from sklearn.metrics import mean_squared_error as mse
from skimage.metrics import peak_signal_noise_ratio as psnr

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

class AudioAnalyzer:
    def __init__(self, param_type="param_type"):
        self.param_type = param_type
        self.fieldnames = [
            "filename",
            self.param_type,
            "original_data_size",
            "original_bitrate",
            "enc_data_size",
            "enc_bitrate",
            "MSE",
            "RMSE",
            "PSNR",
            "PEAQ_ODG",
            "PEAQ_DI"
        ]

    def _find_filename(self, filename_list, partial_filename):
        for filename in filename_list:
            if partial_filename in filename:
                return filename

    def _mount_file_path(self, filename_list, dir_path, partial_filename):
        filename = self._find_filename(filename_list, partial_filename)
        return f"{dir_path}{filename}"

    def _convert_number_to_locale(self, number):
        number_float = float(number)
        number_locale = locale.str(number_float)
        return number_locale

    def _save_metadata(self, filename, info_list, file_type):
        metadata_original = audio_metadata.load(filename)
        info_list[f"{file_type}_data_size"] = self._convert_number_to_locale(
            metadata_original.streaminfo._size)
        info_list[f"{file_type}_bitrate"] = self._convert_number_to_locale(
            metadata_original.streaminfo.bitrate)

    def _read_file(self, filename):
        data, _ = soundfile.read(filename)
        return data

    def calculator(self, original_data, dec_data, info_list):
        info_list["PSNR"] = self._convert_number_to_locale(psnr(original_data, dec_data))
        info_list["MSE"] = self._convert_number_to_locale(mse(original_data, dec_data))
        info_list["RMSE"] = self._convert_number_to_locale(
            mse(original_data, dec_data, squared=False))

    @staticmethod
    def adjust_special_characters(value):
        new_value = value.replace("\'", "\\\'")
        new_value = new_value.replace(" ", "\ ")
        new_value = new_value.replace(",", "\,")
        new_value = new_value.replace("(", "\(")
        return new_value.replace(")", "\)")

    def comparator_peaq(self, original_file_path, dec_file_path, info_list):
        command_odg = (
            "./peaqb -r %(original_file_path)s -t %(dec_file_path)s " +
            "| grep ODG | sed -n -e 's/^.*ODG: //p' " +
            "| awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'"
        )
        command_di = (
            "./peaqb -r %(original_file_path)s -t %(dec_file_path)s " +
            "| grep DI | sed -n -e 's/^.*DI: //p' " +
            "| awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'"
        )
        name_files = {
            "original_file_path": self.adjust_special_characters(original_file_path),
            "dec_file_path": self.adjust_special_characters(dec_file_path)
        }
        pipe_odg = os.popen(command_odg % name_files)
        result_command_odg = pipe_odg.read().replace("\n", "")
        info_list["PEAQ_ODG"] = self._convert_number_to_locale(result_command_odg)
        pipe_odg.close()
        pipe_di = os.popen(command_di % name_files)
        result_command_di = pipe_di.read().replace("\n", "")
        info_list["PEAQ_DI"] = self._convert_number_to_locale(result_command_di)
        pipe_di.close()

    def extract_infos(self, audio_info):
        self.enc_dir_path = audio_info["enc_dir_path"]
        self.dec_dir_path = audio_info["dec_dir_path"]
        self.codec_type = audio_info["codec_type"]
        self.param_codec = audio_info.get("param_codec", "")
        self.param_value = audio_info.get("param_value")
        self.dec_filename_list = os.listdir(self.dec_dir_path)
        self.enc_filename_list = os.listdir(self.enc_dir_path)

    def _read_dir(
        self, audio_base_dir_path, audio_base_filename_list, spreadsheet, audio_info
    ):
        self.extract_infos(audio_info)
        for original_filename in audio_base_filename_list:
            info_list = {}
            partial_filename = original_filename.replace(".wav", "")
            info_list["filename"] = partial_filename
            info_list[self.param_type] = self.param_value
            codec_params = (
                f"{self.codec_type} {self.param_codec} {self.param_value}"
                if self.param_codec and f"{self.param_value}"
                else f"{self.codec_type}"
            )
            original_file_path = f"{audio_base_dir_path}{original_filename}"
            enc_file_path = (
                self._mount_file_path(self.enc_filename_list, self.enc_dir_path, partial_filename))
            dec_file_path = (
                self._mount_file_path(self.dec_filename_list, self.dec_dir_path, partial_filename))
            self._save_metadata(original_file_path, info_list, "original")
            self._save_metadata(enc_file_path, info_list, "enc")
            original_data = self._read_file(original_file_path)
            dec_data = self._read_file(dec_file_path)
            self.calculator(original_data, dec_data, info_list)
            self.comparator_peaq(original_file_path, dec_file_path, info_list)
            line_name = f"{partial_filename}{codec_params}"
            spreadsheet[line_name] = info_list

    def analyzer(self, audio_base_dir_path, audio_info_list):
        audio_base_filename_list = os.listdir(audio_base_dir_path)
        spreadsheet = {}
        for audio_info in audio_info_list:
            self._read_dir(
                audio_base_dir_path, audio_base_filename_list,
                spreadsheet, audio_info
            )
        return spreadsheet
