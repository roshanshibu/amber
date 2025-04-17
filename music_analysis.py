import librosa
import numpy as np


def extract_temporal_features(y, sr):
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):  # https://github.com/librosa/librosa/issues/1867
        tempo = tempo[0]

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    return {
        "tempo": tempo,
        "onset_strength_mean": np.mean(onset_env),
        "onset_strength_std": np.std(onset_env),
    }


def analyze_spectral_features(y, sr):
    S = np.abs(librosa.stft(y))

    spec_centroid = librosa.feature.spectral_centroid(S=S, sr=sr)
    spec_bandwidth = librosa.feature.spectral_bandwidth(S=S, sr=sr)
    spec_rolloff = librosa.feature.spectral_rolloff(S=S, sr=sr)
    spec_flatness = librosa.feature.spectral_flatness(S=S)
    spec_contrast = librosa.feature.spectral_contrast(S=S, sr=sr)

    raw_features = {
        "spectral_centroid": spec_centroid,
        "spectral_bandwidth": spec_bandwidth,
        "spectral_rolloff": spec_rolloff,
        "spectral_flatness": spec_flatness,
        "spectral_contrast": spec_contrast,
    }

    features = {}
    for feat_name, feat_value in raw_features.items():
        average_value = (
            np.mean(feat_value, axis=1) if feat_value.ndim > 1 else np.mean(feat_value)
        )
        if feat_name != "spectral_contrast":
            features[feat_name] = average_value[0]
        else:
            features[feat_name] = average_value.tolist()

    return features


def extract_energy_features(y):
    rms_energy = librosa.feature.rms(y=y).mean()

    zcr_values = librosa.feature.zero_crossing_rate(y)
    zcr = float(np.mean(zcr_values))

    return {"rms_energy": rms_energy, "zcr": zcr}


def analyze_harmonic_and_pitch_features(y, sr):
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
    mean_chroma = np.mean(chroma_stft, axis=1)

    return mean_chroma


def analyse_song(file_path):
    y, sr = librosa.load(file_path, sr=None)
    temporal = extract_temporal_features(y, sr)
    spectral = analyze_spectral_features(y, sr)
    energy = extract_energy_features(y)
    mean_chroma = analyze_harmonic_and_pitch_features(y, sr)

    return {
        "temporal": temporal,
        "spectral": spectral,
        "energy": energy,
        "mean_chroma": mean_chroma,
    }
