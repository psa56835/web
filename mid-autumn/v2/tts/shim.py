import torch, torchaudio, soundfile as sf
def _load(path, *a, **k):
    d, sr = sf.read(path, dtype='float32', always_2d=True)
    return torch.from_numpy(d.T.copy()), sr
def _save(path, wav, sr, *a, **k):
    sf.write(path, wav.detach().cpu().numpy().T, sr)
torchaudio.load = _load; torchaudio.save = _save
