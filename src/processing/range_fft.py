import os
import numpy as np
import utils.save_adc_data as sd
import utils.utility as utility
from utils.singlechip_raw_data_reader_example import TI_PROCESSOR
import matplotlib.pyplot as plt
import argparse

current_dir = os.getcwd()

# ----------------------------------------------------------------------------------------- #
#                                     Processing functions                                  #
# ----------------------------------------------------------------------------------------- #

def rangefft(raw_data):
    """
    Performs a range FFT on the raw data.

    Parameters
    ----------
    raw_data : np.ndarray
        The raw data from FMCW radar. (Size: frames x tx x rx x adc_samples)

    Returns
    -------
    fft_data : np.ndarray
        The range fft of the same size as input.
    """
    fft_data = np.fft.fft(raw_data, axis=-1)
    return fft_data


def compute_snr(fft_data):
    """
    Computes the SNR of the range FFT.
    SNR = peak power / mean noise power (excluding peak bin)

    Parameters
    ----------
    fft_data : np.ndarray
        Range FFT data (frames x tx x rx x adc_samples)

    Returns
    -------
    snr_db : float
        SNR in dB
    """
    power = abs(np.squeeze(np.sum(fft_data, axis=(0, 2, 1)))) ** 2
    peak_idx = np.argmax(power)
    peak_power = power[peak_idx]

    # noise = everything except the peak bin
    noise = np.delete(power, peak_idx)
    noise_power = np.mean(noise)

    snr_db = 10 * np.log10(peak_power / noise_power)
    return snr_db


def plot_rangefft(fft_data, range_res, exp_name, save_path=None):
    """
    Plots and optionally saves the range FFT.

    Parameters
    ----------
    fft_data : np.ndarray
        Range FFT data (frames x tx x rx x adc_samples)
    range_res : float
        Range resolution in meters
    exp_name : str
        Experiment name (used for plot title and filename)
    save_path : str, optional
        If provided, saves the plot to this path
    """
    power = abs(np.squeeze(np.sum(fft_data, axis=(0, 2, 1)))) ** 2
    ranges = np.arange(fft_data.shape[-1]) * range_res

    snr_db = compute_snr(fft_data)

    plt.figure(figsize=(10, 5))
    plt.plot(ranges, power)
    plt.xlabel('Distance (m)')
    plt.ylabel('Power')
    plt.title(f'Range FFT — {exp_name} | SNR: {snr_db:.2f} dB')
    plt.grid(True)
    plt.tight_layout()

    if save_path:
        os.makedirs(save_path, exist_ok=True)
        filename = os.path.join(save_path, f'{exp_name}_range_fft.png')
        plt.savefig(filename)
        print(f"[SAVED] Plot saved to {filename}")

    plt.show(block=True)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Range FFT processing for radar experiments.")
    parser.add_argument("--config", type=str, default='scripts/1843_config_lowres',
                        help="Path to Lua config script (without .lua).")
    parser.add_argument("--exp_name", type=str, default='test',
                        help="Experiment name (e.g. exp1_sitting_still).")
    parser.add_argument("--save", action="store_true",
                        help="Save the plot to results/ folder.")
    return parser.parse_args()


# ----------------------------------------------------------------------------------------- #
#                                        Main function                                      #
# ----------------------------------------------------------------------------------------- #

def main(args):
    # path to experiment data folder
    exp_path = os.path.join(current_dir, 'data', args.exp_name)

    if not os.path.isdir(exp_path):
        print(f"[ERROR] Experiment folder not found: {exp_path}")
        print("Make sure you ran setup_experiments.py --setup and captured data first.")
        return

    # path to lua scripts
    json_filename = os.path.join(current_dir, 'scripts')

    # read radar parameters from lua config
    chirp_dict = utility.read_radar_params(args.config + '.lua')
    print(f"Range resolution: {chirp_dict['range_res']} m")

    processor = TI_PROCESSOR()

    # process JSON files for chirp parameters
    mmwave_dict, setup_dict, mmwave_filename, setup_filename = sd.process_json_files(
        json_filename, chirp_dict, exp_path, args.exp_name
    )

    # read binary data into array (frames x tx x rx x adc_samples)
    adc_data = processor.rawDataReader(setup_dict, mmwave_dict, os.path.join(exp_path, args.exp_name), 'tmp_rdc.mat')
    adc_data = np.stack(adc_data, axis=-1)
    adc_data = np.reshape(adc_data, (adc_data.shape[0], adc_data.shape[1], adc_data.shape[2], adc_data.shape[3]))

    print("Captured %d frames | %d TX | %d RX | %d ADC samples" % adc_data.shape)

    # compute range FFT
    fft_data = rangefft(adc_data)

    # compute and print SNR
    snr = compute_snr(fft_data)
    print(f"SNR: {snr:.2f} dB")

    # plot and optionally save
    save_path = os.path.join(current_dir, 'results') if args.save else None
    plot_rangefft(fft_data, chirp_dict['range_res'], args.exp_name, save_path)


if __name__ == "__main__":
    args = parse_args()
    main(args)