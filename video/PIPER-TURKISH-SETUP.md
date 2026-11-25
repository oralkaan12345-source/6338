# Piper ile çevrimdışı Türkçe anlatım

Piper Türkçe DFKI medium modeli yerel işlemcide metinden WAV oluşturur. Aşağıdaki indirmelerden sonra seslendirme çevrimdışı çalışır. Komutları depo kökünden çalıştır. Python 3.12.14 ve FFmpeg ile doğrulandı. Bu bir yapay zekâ seslendirmesidir. Kurulum geçici bir sanal ortam kullanır; modeli veya üretilen kayıtları Git'e ekleme.

```bash
export UV_CACHE_DIR="$PWD/.uv-cache"
uv venv --python 3.12 .piper-env
uv pip install --python .piper-env/bin/python \
  'piper-tts==1.8.0' 'onnxruntime==1.24.4' 'numpy==2.5.5'
mkdir -p piper-model
source=https://huggingface.co/rhasspy/piper-voices/resolve/217ddc7/tr/tr_TR/dfki/medium
for file in tr_TR-dfki-medium.onnx tr_TR-dfki-medium.onnx.json; do
  curl --fail --location "$source/$file" -o "piper-model/$file"
done
(cd piper-model && sha256sum -c <<'HASHES'
2844717f524ab965d3fe86e60562cbb601d3e456836efcc2196cc3a14112a8fb  tr_TR-dfki-medium.onnx
13ebd7810f1b61b5027583cf3131a0a233b6ea81c38f2200ebc4ff41c3cca039  tr_TR-dfki-medium.onnx.json
HASHES
)
```

Metindeki her dolu satır için kümülatif bir bitiş zamanı ver. Örneğin üç cümle için:

```bash
.piper-env/bin/python video/narrate-piper.py metin.txt anlatim.wav \
  --model piper-model/tr_TR-dfki-medium.onnx --ends 4 8 12
```

Bu örneğin çıktısı 12 saniyelik 48 kHz mono PCM WAV. Çok kısa bir aralığa sığmayan cümleler için betik hata verir; cümleyi kısalt veya aralığı genişlet. Aynı çıktı dosyasının üzerine yazılmaz. [Piper kaynak kodu](https://github.com/OHF-Voice/piper1-gpl) · [Model kaynağı](https://huggingface.co/rhasspy/piper-voices/tree/217ddc7/tr/tr_TR/dfki/medium)
