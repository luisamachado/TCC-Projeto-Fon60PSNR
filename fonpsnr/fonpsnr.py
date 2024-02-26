import numpy as np
from scipy import (interpolate, signal)
from skimage.metrics import peak_signal_noise_ratio as psnr


class FonPSNR:
    def __init__(self, fon=60):
        self.f, self.af, self.Lu, self.Tf = self._return_const_iso_226_2003()
        self.fir = self.create_fir_filter(fon)

    @staticmethod
    def _return_const_iso_226_2003():
        """Retorna as constantes determionadas pela ISO 226 de 2003"""
        f = np.array([
            20,   25, 31.5,   40,   50,   63,   80,   100,   125,  160,
            200,  250,  315,  400,  500,  630,  800,  1000,  1250, 1600,
            2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500
        ])

        af = np.array([
            0.532, 0.506, 0.480, 0.455, 0.432, 0.409, 0.387, 0.367, 0.349, 0.330,
            0.315, 0.301, 0.288, 0.276, 0.267, 0.259, 0.253, 0.250, 0.246, 0.244,
            0.243, 0.243, 0.243, 0.242, 0.242, 0.245, 0.254, 0.271, 0.301
        ])

        Lu = np.array([
            -31.6, -27.2, -23.0, -19.1, -15.9, -13.0, -10.3,  -8.1, -6.2, -4.5,
            -3.1,  -2.0,  -1.1,  -0.4,   0.0,   0.3,   0.5,   0.0, -2.7, -4.1,
            -1.0,   1.7,   2.5,   1.2,  -2.1,  -7.1, -11.2, -10.7, -3.1
        ])

        Tf = np.array([
            78.5, 68.7, 59.5, 51.1, 44.0, 37.5, 31.5, 26.5, 22.1, 17.9,
            14.4, 11.4,  8.6,  6.2,  4.4,  3.0,  2.2,  2.4,  3.5,  1.7,
            -1.3, -4.2, -6.0, -5.4, -1.5,  6.0, 12.6, 13.9, 12.3
        ])
        return f, af, Lu, Tf

    def _equal_loudness_contour(self, fon, frequencies=None): 
        """ Retorna uma curva isofônica.
    
            Args:
                fon (float): Valor fon da curva.
                frequencies (:obj:`np.ndarray`, optional): Frequências para
                    avaliar. Se não for aprovado, todos os 29 pontos do
                    padrão ISO serão retornados. Quaisquer frequências não
                    presentes no padrão são encontradas através de
                    interpolação spline.

            Returns:
                Lp (np.ndarray): valores em db SPL.
        """
        assert 0 <= fon <= 90, f"{fon} is not [0, 90]"
        Af = (
            4.47e-3 * (10 ** (0.025 * fon) - 1.15)
            + (0.4 * 10 ** (((self.Tf + self.Lu) / 10) - 9)) ** self.af
        )
        Lp = ((10.0 / self.af) * np.log10(Af)) - self.Lu + 94

        if frequencies is not None:
            assert frequencies.min() >= self.f.min(), "Frequencies are too low"
            assert frequencies.max() <= self.f.max(), "Frequencies are too high"
            tck = interpolate.splrep(self.f, Lp, s=0)
            Lp = interpolate.splev(frequencies, tck, der=0)
        return Lp

    def _generate_curva_fon(self, fon):
        x = self.f
        curve_fon = self._equal_loudness_contour(fon, x)

        x = np.insert(x, 0, 0)
        x = np.append(x, 22050)
        curve_fon = np.insert(curve_fon, 0, curve_fon[0])
        curve_fon = np.append(curve_fon, 0)

        return x, curve_fon

    def create_fir_filter(self, fon=60):
        x, curve = self._generate_curva_fon(fon)
        fs = 44100.0
        gain = 10**((fon - curve) / 20)
        freq = x / (fs / 2)
        gain[0] = 0
        gain[-1] = 0
        numtaps = 101
        fir = signal.firwin2(
            numtaps, freq, gain, window=("kaiser", 0.5), antisymmetric=False)
        return fir

    def fonpsnr(self, original_data, dec_data):
        original_filtered = signal.filtfilt(self.fir, 1, original_data)
        coded_filtered = signal.filtfilt(self.fir, 1, dec_data)
        data_range = original_filtered.max() - original_filtered.min()
        result = psnr(original_filtered, coded_filtered, data_range=data_range)
        return result
