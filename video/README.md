# Bulutta Short üretimi

Seçim: [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo/blob/2dc10e850d78c61264a64ea180def2b7f1f334d8/README-en.md) (MIT, `mpt` 1.3.11, commit `2dc10e850d78c61264a64ea180def2b7f1f334d8`). Hazır metin, fotoğraf/klip, seslendirme ve altyazıyı grafik kartı gerektirmeden birleştiren komut satırı aracı. Otomobil tarihi gibi örneklerde doğru modele ait lisanslı görselleri kendimiz seçeriz. Varsayılan stok aramasına bırakmayız.

[Remotion](https://github.com/remotion-dev/remotion), özel React animasyonlarında daha esnek ama hazır Short akışı değil. [Wan2.2](https://github.com/Wan-Video/Wan2.2), metinden yeni hareketli sahneler üretmek için; model ağırlıkları ve GPU gereken ayrı bir iş. Bu kurulum bu ikisini yüklemez.

## Kurulum ve deneme

Python 3.11+, Git, uv ve FFmpeg gerekir. İstersen `PYTHON_BIN` ile farklı bir Python çalıştırıcısı belirt. Kendi klasöründe kilitli bağımlılıkları kurar; YouTube bağlantısı kurmaz:

```bash
bash video/setup.sh
```

İlk tam deneme için her kenarı en az 480 piksel olan iki kendi görselin ve önceden hazırlanmış bir ses kaydın varsa:

```bash
MPT_HOME="$PWD/.video-tools/data" .video-tools/venv/bin/mpt cli \
  --video-script "Your complete English script." \
  --video-source local --video-materials "first.jpg,second.jpg" \
  --video-aspect 9:16 --video-concat-mode sequential --video-clip-duration 3 \
  --custom-audio-file narration.wav --bgm-type none \
  --no-subtitle-enabled --stop-at video
```

Ses kaydı çok kısaysa tüm görseller görünmeyebilir; kesin sahne süreleri için aşağıdaki çevrimdışı aracı kullan. Bu çağrı bir yapay zekâ API'si, stok erişimi veya yayın gerektirmez. Hazır kayıtla altyazıyı ayrı üretip ekleyebilir veya uygun Whisper modelini ayrıca ayarlayabilirsin. Edge TTS bir API anahtarı istemez ama internete erişim gerektirir. YouTube'a hiçbir şey yüklemek bu kurulumun parçası değildir.

## İnternetsiz FFmpeg kontrolü

```bash
bash video/smoke-test.sh /tmp/video-smoke.mp4
```

Bu kontrol MoneyPrinterTurbo yerine bulut ortamındaki FFmpeg'i test eder. Yerel İngilizce örnek ses (Flite), iki renkli sahne ve gömülü altyazıyla dört saniyelik 1080×1920 H.264/AAC MP4 üretir. FFmpeg derlemesinin `flite`, `subtitles` ve `libx264` desteği olmalı. Fotogerçekçi yapay zekâ sahnesi veya hazır bir YouTube Short değildir.

## Kendi görsellerinle çevrimdışı video

Kurulum sırasında paket indirme engeline takılırsan, Python standart kütüphanesi ve FFmpeg ile kendi görsellerini ve mevcut ses kaydını hemen videoya dönüştürebilirsin:

```bash
python3 video/render.py --audio narration.wav --output preview.mp4 first.jpg second.jpg third.jpg
```

Görsel sırası komuttaki sırayı izler. Dilersen `--subtitles captions.srt` ile altyazı gömebilir, `--scene-seconds 7 8 9` ile 24 saniyelik bir ses kaydına sahne süreleri atayabilirsin. Bu iki seçeneği görsel dosyalarından önce ver; `--scene-seconds` seçeneğinden sonra örnekteki gibi başka bir seçenek (`--output preview.mp4`) gelsin. Kayıt ve görselleri kendin sağlarsın; bu araç ses veya görüntü üretmez, web'e bağlanmaz ve herhangi bir platforma yükleme yapmaz. Mevcut çıktıların üzerine yazmaz.

## Daha doğal İngilizce anlatım

[Kokoro kurulumu](KOKORO-SETUP.md), internet kullanmadan yerel WAV üreten ve sesin süresini sahnelere göre ayarlayan test edilmiş akışı gösterir.

[Türkçe Piper kurulumu](PIPER-TURKISH-SETUP.md), aynı sahne zamanlamasıyla Türkçe WAV üretir.
