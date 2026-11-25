# Pocket TTS ile duygulu Türkçe seslendirme

İşlemcide çalışan yapay seslendirme. İlk kurulum paket ve ağırlık indirir; daha sonra metin yerel makinede işlenir. Python 3.12, FFmpeg ve Linux x86-64 üzerinde test edildi. Komutları depo kökünden çalıştır.

```bash
export UV_CACHE_DIR="$PWD/.uv-cache"
uv venv --python 3.12 .pocket-env
uv pip install --python .pocket-env/bin/python \
  --index-url https://download.pytorch.org/whl/cpu 'torch==2.9.1+cpu'
uv pip install --python .pocket-env/bin/python \
  'pocket-tts-turkish==0.1.0' 'pocket-tts==3.3.0'
mkdir -p pocket-model/voices
base=https://huggingface.co/wite-tech/pocket-tts-turkish/resolve/fcbd37c74dc127be846face0ff36062e9a939f7b
for f in config.yaml model.safetensors tokenizer.model voices/male_1.wav voices/female_2.wav voices/male_3.wav; do
  curl --fail --location "$base/$f" -o "pocket-model/$f"
done
(cd pocket-model && sha256sum -c <<'HASHES'
fa60a7799ac09778360ce1aa5c2216fa2ce6f1be06aabb2e0dd4f6ea63a6d3d7  config.yaml
c43b72ed336b64c66adceba8fbbb059e869f753b60de086e3f32bf1b118d5a77  model.safetensors
a6c3a7ca48ecf3c9254bf72dff58e3f09f2798f49effcbd7debcf6f7a87f3568  tokenizer.model
e6538a1f0ce60d08994c3a733946589d327cf9256b35b77e4155c0baefadc81a  voices/male_1.wav
98cd697c9dd6f77f253bd1233675496b6d4882cd9c0ef72434b6a12e06564aa7  voices/female_2.wav
b5bbbca120837cca1b93c3b8d740e70bcc3f32f53c557af04b207fc69a31545e  voices/male_3.wav
HASHES
)
```

Her metin satırı için bir kümülatif bitiş saniyesi gir. İsteğe bağlı ton dosyasında her satırda `ses duygu sabit-tohum` alanları bulunur. `notr`, `sakin`, `surprised`, `sad`, `angry` ve `happy` kullanılabilir.

```bash
printf 'Sessiz ol.\nBu ses nereden geliyor?\n' > metin.txt
printf '3 6\n' > sureler.txt
printf 'male_1 sakin 240\nfemale_2 surprised 338\n' > tonlar.txt
HF_HUB_OFFLINE=1 .pocket-env/bin/python video/narrate-pocket.py \
  metin.txt sureler.txt anlatim.wav --tones tonlar.txt --model pocket-model
```

Örneğin çıktı 6 saniyelik 48 kHz mono WAV'dır. Bir cümle ayrılan süreye sığmazsa metni kısalt veya zaman aralığını büyüt. Çıktı dosyası varsa üzerine yazılmaz. Ağırlıklar, kayıtlar ve sanal ortamı Git'e ekleme. [Paket kaynağı](https://github.com/witetech/pocket-tts-turkish) · [Model ve lisans](https://huggingface.co/wite-tech/pocket-tts-turkish)
