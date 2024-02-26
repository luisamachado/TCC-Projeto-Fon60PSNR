import audiofile
import csv
import locale
import os

from sklearn.metrics import mean_squared_error as mse
from skimage.metrics import peak_signal_noise_ratio as psnr

from fon60psnr import Fon60PSNR

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

class AudioAnalyzer:
    def __init__(self, param_type="param_type"):
        self.fon60psnr = Fon60PSNR()
        self.param_type = param_type
        self.fieldnames = [
            "filename",
            self.param_type,
            "Fon60PSNR",
            "PSNR",
            "PEAQ_ODG",
            "PEAQ_DI",
            "MSE",
        ]

    @staticmethod
    def adjust_special_characters(value):
        new_value = value.replace("\'", "\\\'")
        new_value = new_value.replace(" ", "\ ")
        new_value = new_value.replace(",", "\,")
        new_value = new_value.replace("(", "\(")
        return new_value.replace(")", "\)")

    def _convert_number_to_locale(self, number):
        number_float = float(number)
        number_locale = locale.str(number_float)
        return number_locale

    def _read_file(self, filename):
        data, _ = audiofile.read(filename)
        return data

    def calculator(self, original_data, dec_data, info_list):
        if original_data.size == dec_data.size:
            psnr_result = psnr(original_data, dec_data)
            info_list["PSNR"] = self._convert_number_to_locale(psnr_result)
            mse_result = mse(original_data, dec_data)
            info_list["MSE"] = self._convert_number_to_locale(mse_result)
            fon60psnr_result = self.fon60psnr.fon60psnr(original_data, dec_data)
            info_list["Fon60PSNR"] = self._convert_number_to_locale(fon60psnr_result)

    def comparator_peaq(self, original_file_path, dec_file_path, info_list):
        command_peaqb = (
            "./peaqb -r %(original_file_path)s -t %(dec_file_path)s > peaq-result.txt"
        )
        command_odg = (
            "cat peaq-result.txt | grep ODG | sed -n -e 's/^.*ODG: //p' " +
            "| awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'"
        )
        command_di = (
            "cat peaq-result.txt | grep DI | sed -n -e 's/^.*DI: //p' " +
            "| awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'"
        )
        name_files = {
            "original_file_path": self.adjust_special_characters(original_file_path),
            "dec_file_path": self.adjust_special_characters(dec_file_path)
        }
        run_peaqb = os.popen(command_peaqb % name_files)
        run_peaqb.close()
        pipe_odg = os.popen(command_odg)
        result_command_odg = pipe_odg.read().replace("\n", "")
        info_list["PEAQ_ODG"] = self._convert_number_to_locale(result_command_odg)
        pipe_odg.close()
        pipe_di = os.popen(command_di)
        result_command_di = pipe_di.read().replace("\n", "")
        info_list["PEAQ_DI"] = self._convert_number_to_locale(result_command_di)
        pipe_di.close()
        run_peaq_result = os.popen("rm peaq-result.txt")
        run_peaq_result.close()

    def extract_infos(self, audio_info):
        self.dec_dir_path = audio_info["dec_dir_path"]
        self.codec_type = audio_info["codec_type"]
        self.param_codec = audio_info.get("param_codec", "")
        self.param_value = audio_info.get("param_value")
        self.dec_filename_list = os.listdir(self.dec_dir_path)

    def generate_csv(self, codec_type, partial_filename, table):
        try:
            csv_file = f"comparator-{codec_type}-{partial_filename}.csv"
            with open(csv_file, "w") as csvfile:
                writer = csv.DictWriter(csvfile, self.fieldnames, delimiter=';')
                writer.writeheader()
                for row in table:
                    for data in row.values():
                        writer.writerow(data)
        except IOError:
            print("I/O error")

    def analyzer(self, original_filename, audio_base_dir_path, audio_info):
        spreadsheet = {}
        self.extract_infos(audio_info)
        info_list = {}
        partial_filename, _ = os.path.splitext(original_filename)
        info_list["filename"] = partial_filename
        info_list[self.param_type] = self.param_value
        codec_params = (
            f"{self.codec_type} {self.param_codec} {self.param_value}"
            if self.param_codec and f"{self.param_value}"
            else f"{self.codec_type}"
        )
        original_file_path = os.path.join(audio_base_dir_path, original_filename)
        dec_file_path = os.path.join(self.dec_dir_path, original_filename)
        original_data = self._read_file(original_file_path)
        dec_data = self._read_file(dec_file_path)
        self.calculator(original_data, dec_data, info_list)
        self.comparator_peaq(original_file_path, dec_file_path, info_list)
        line_name = f"{partial_filename} {codec_params}"
        spreadsheet[line_name] = info_list
        return spreadsheet

    def handle_analyzer(
            self, audio_decode_path, params_coding, table, original_filename, audio_base_path):
        param_codec = params_coding["param_codec"]
        params_value = params_coding["params_value"]
        codec_type = params_coding["codec_type"]
        for value in params_value:
            config_type = param_codec.replace("--", "")
            decoded_path = f"{audio_decode_path}{config_type}_{value}/"
            analysis_params = {
                "dec_dir_path": decoded_path,
                "codec_type": codec_type,
                "param_codec": param_codec,
                "param_value": value,
            }
            table.append(self.analyzer(original_filename, audio_base_path, analysis_params))

    def audio_analyzer(self, audio_decode_path, params_coding):
        audio_base_path = params_coding["audio_base_path"]
        audio_base_filename_list = os.listdir(audio_base_path)
        for original_filename in audio_base_filename_list:
            table = []
            partial_filename, _ = os.path.splitext(original_filename)
            self.handle_analyzer(
                audio_decode_path, params_coding, table, original_filename, audio_base_path)
            self.generate_csv(params_coding["codec_type"], partial_filename, table)
