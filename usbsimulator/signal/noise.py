import numpy as np
from scipy.ndimage import gaussian_filter1d


def f(signal: list[float]):
    """Function to simulate noise on the USB Bus.
    This is used in the CTF challenge, but might not be representative
    of the reality.

    :param signal: the signal to apply the noise on
    :type signal: list[float]
    :returns: the noisy signal
    :rtype: list[float]
    """

    output = []
    signal = np.array(signal)
    output = signal
    output += np.clip(gaussian_filter1d(signal, sigma=10, order=1), -0.5, 0.5)
    output += np.clip(np.random.normal(0, 0.05, len(signal)), -0.03, 0.03)
    output = gaussian_filter1d(output, sigma=0.7)
    return output
