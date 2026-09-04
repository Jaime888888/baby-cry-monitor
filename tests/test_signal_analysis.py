import tempfile
import unittest
from pathlib import Path

import numpy as np
from scipy.io import wavfile

from cry_detector_publisher import SAMPLE_RATE, analyze_frame, band_energy


class SignalAnalysisTests(unittest.TestCase):
    def write_tone(self, directory: str, frequency_hz: float, amplitude: float = 10_000) -> Path:
        time = np.arange(SAMPLE_RATE, dtype=np.float64) / SAMPLE_RATE
        samples = (amplitude * np.sin(2 * np.pi * frequency_hz * time)).astype(np.int16)
        path = Path(directory) / f"tone-{frequency_hz}.wav"
        wavfile.write(path, SAMPLE_RATE, samples)
        return path

    def test_voice_band_tone_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            detected, energy, voice_ratio, beep_ratio = analyze_frame(
                self.write_tone(directory, 500)
            )

        self.assertTrue(detected)
        self.assertGreater(energy, 0)
        self.assertGreater(voice_ratio, 0.99)
        self.assertLess(beep_ratio, 0.01)

    def test_narrow_beep_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            detected, _energy, voice_ratio, beep_ratio = analyze_frame(
                self.write_tone(directory, 1_000)
            )

        self.assertFalse(detected)
        self.assertGreater(voice_ratio, 0.99)
        self.assertGreater(beep_ratio, 0.99)

    def test_empty_band_returns_zero(self):
        self.assertEqual(0.0, band_energy(np.ones(4), SAMPLE_RATE, 8, 2_000, 1_000))


if __name__ == "__main__":
    unittest.main()
