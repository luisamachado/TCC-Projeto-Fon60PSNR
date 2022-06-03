import os
import soundfile
import audio_metadata

from sklearn.metrics import mean_squared_error as mse
from skimage.metrics import peak_signal_noise_ratio as psnr


class AudioAnalyzer:
    def _create_table(self, base_audio_names):
        table = {}
        for name in base_audio_names:
            filename = name.replace(".wav", "")
            table[filename] = {}
            table[filename]["filename"] = filename
        return table

    def _find_filename(self, filename_list, partial_filename):
        for filename in filename_list:
            if partial_filename in filename:
                return filename

    def _read_file(self, filename_original, filename_decod, filename_encod, table, key):
        original_data, _ = soundfile.read(filename_original)
        metadata_original = audio_metadata.load(filename_original)
        table[key]["original_data_size"] = metadata_original.streaminfo._size
        table[key]["original_bitrate"] = metadata_original.streaminfo.bitrate
        metadata_encode = audio_metadata.load(filename_encod)
        table[key]["encode_data_size"] = metadata_encode.streaminfo._size
        table[key]["encode_bitrate"] = metadata_encode.streaminfo.bitrate
        decoded_data, _ = soundfile.read(filename_decod)
        return original_data, decoded_data

    def calculator(self, original_data, decoded_data, table, key):
        table[key]["MSE"] = mse(original_data, decoded_data)
        table[key]["RMSE"] = mse(
            original_data, decoded_data, squared=False)
        table[key]["PSNR"] = psnr(original_data, decoded_data)

    @staticmethod
    def adjust_special_characters(value):
        new_value = value.replace("\'", "\\\'")
        new_value = new_value.replace(" ", "\ ")
        new_value = new_value.replace(",", "\,")
        new_value = new_value.replace("(", "\(")
        return new_value.replace(")", "\)")

    def comparator_peaq(
        self, original_file_path, decoded_file_path, table, key
    ):
        command_odg = (
            "./peaqb -r %(original_file_path)s -t %(decoded_file_path)s " +
            "| grep ODG | sed -n -e 's/^.*ODG: //p' " +
            "| awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'"
        )
        command_di = (
            "./peaqb -r %(original_file_path)s -t %(decoded_file_path)s " +
            "| grep DI | sed -n -e 's/^.*DI: //p' " +
            "| awk '{ sum += $1; n++ } END { if (n > 0) print sum / n; }'"
        )
        name_files = {
            "original_file_path": self.adjust_special_characters(original_file_path),
            "decoded_file_path": self.adjust_special_characters(decoded_file_path)
        }
        pipe_odg = os.popen(command_odg % name_files)
        result_command_odg = pipe_odg.read()
        table[key]["PEAQ_ODG"] = result_command_odg.replace("\n", "")
        pipe_odg.close()
        pipe_di = os.popen(command_di % name_files)
        result_command_di = pipe_di.read()
        table[key]["PEAQ_DI"] = result_command_di.replace("\n", "")
        pipe_di.close()

    def _read_directory(
        self, audio_base_directory_path, audio_base_filename_list, table, audio_info
    ):
        encoded_directory_path = audio_info["encoded_directory_path"]
        decoded_directory_path = audio_info["decoded_directory_path"]
        codec_type = audio_info["codec_type"]
        param_codec = audio_info.get("param_codec", "")
        param_value = audio_info.get("param_value")
        decoded_filename_list = os.listdir(decoded_directory_path)
        encoded_filename_list = os.listdir(encoded_directory_path)
        for original_filename in audio_base_filename_list:
            partial_filename = original_filename.replace(".wav", "")
            table[partial_filename]["type"] = (
                f"{codec_type} {param_codec} {param_value}"
                if param_codec and param_value
                else f"{codec_type}"
            )
            decoded_filename = self._find_filename(
                decoded_filename_list, partial_filename)
            encoded_filename = self._find_filename(
                encoded_filename_list, partial_filename)
            original_file_path = audio_base_directory_path + original_filename
            decoded_file_path = decoded_directory_path + decoded_filename
            encoded_file_path = encoded_directory_path + encoded_filename
            original_data, decoded_data = self._read_file(
                original_file_path, decoded_file_path, encoded_file_path,
                 table, partial_filename
            )
            self.comparator_peaq(
                original_file_path, decoded_file_path, table, partial_filename)
            self.calculator(original_data, decoded_data, table, partial_filename)

    def analyzer(self, audio_base_directory_path, audio_info_list):
        audio_base_filename_list = os.listdir(audio_base_directory_path)
        table = self._create_table(audio_base_filename_list)
        for audio_info in audio_info_list:
            self._read_directory(
                audio_base_directory_path, audio_base_filename_list, table, audio_info)
        return table
