# Yerel Kokoro seslendirme

Kokoro modeli işlemcide çalışır. Kurulum paket ve model indirmek için internet ister; sonrasında metni dışarı göndermeden WAV üretir. Komutları depo kökünden çalıştır. Python 3.12 ve FFmpeg ile doğrulandı. Bu bir yapay zekâ sesidir, insan kaydı değildir.

```bash
export UV_CACHE_DIR="$PWD/.uv-cache"
uv venv --python 3.12 .kokoro-env
uv pip install --python .kokoro-env/bin/python \
  kokoro-onnx==0.6.1 onnxruntime==1.24.4 numpy==2.5.5
mkdir -p kokoro-model
base=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
curl --fail --location "$base/kokoro-v1.0.int8.onnx" -o kokoro-model/kokoro-v1.0.int8.onnx
curl --fail --location "$base/voices-v1.0.bin" -o kokoro-model/voices-v1.0.bin
(cd kokoro-model && sha256sum -c <<'HASHES'
6e742170d309016e5891a994e1ce1559c702a2ccd0075e67ef7157974f6406cb  kokoro-v1.0.int8.onnx
bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d  voices-v1.0.bin
HASHES
)
```

Her satır bir sahne. `--ends` her sahnenin kümülatif bitiş saniyesini alır:

```bash
.kokoro-env/bin/python video/narrate-kokoro.py script.txt narration.wav \
  --model kokoro-model/kokoro-v1.0.int8.onnx --voices kokoro-model/voices-v1.0.bin \
  --voice af_heart --ends 5.6 11.9 18.1 26.3 30
```

Çıktı 48 kHz mono PCM WAV. Araç mevcut çıktı dosyasının üzerine yazmaz; ayrılan süreye sığması için kısa bir hız düzeltmesi, ses seviyesi normalizasyonu ve sahne sonu boşlukları kullanır. Model, WAV ve sanal ortamı depoya ekleme.
