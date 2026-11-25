# 6338 Toolkit

Bilgisayarın kapalıyken bir bulut terminalinde çalıştırılabilen iki ayrı araç. Bu depo kurulum dosyalarını içerir, üçüncü taraf depoları kopyalamaz. YouTube bağlantısı veya otomatik yayın yoktur.

## 1. Video üretimi

[MoneyPrinterTurbo 1.3.11](https://github.com/harry0703/MoneyPrinterTurbo), 9:16 MP4 hazırlamak için seçildi. Hazır görselleri, ses ve altyazıyı birleştirir; kendi başına yeni fotogerçekçi sahne üretmekle aynı şey değildir. Kurulum, sabit kaynak sürümü ve örnek komutlar: [video/README.md](video/README.md).

```bash
bash video/setup.sh
bash video/smoke-test.sh /tmp/video-smoke.mp4
```

FFmpeg testi, MoneyPrinterTurbo kurulmadan da çalışır. Bulut testi: 1080×1920, H.264/AAC, İngilizce örnek ses ve gömülü altyazı. MoneyPrinterTurbo ayrıca bulutta kuruldu ve yerel görsel ile WAV kaydından bir 1080×1920 H.264/AAC MP4 üretti. Bu deneme bir YouTube hesabı bağlamadı ve hiçbir şey yayımlamadı.

Kendi görsellerin ve ses dosyanla çevrimdışı üretim için:

```bash
python3 video/render.py --audio narration.wav --output preview.mp4 first.jpg second.jpg third.jpg
```

## 2. Skill bulma

[Vercel Skills 1.9.0](https://github.com/vercel-labs/skills/releases/tag/v1.9.0) farklı üreticilerin skill'lerini konuya göre bulur. [OpenAI Skills](https://github.com/openai/skills) resmî Codex seçeneklerini kontrol etmek için ilk kaynak. Node.js 22.20.0+ gerekir.

```bash
cd skills
npm ci --ignore-scripts --no-audit --no-fund
DO_NOT_TRACK=1 npm run find -- pdf
```

`pdf` araması gerçek sonuçlarla test edildi. Arama terimi skills.sh hizmetine gider. Arama hiçbir skill kurmaz. Bir sonuç kullanılmadan önce deposunu, lisansını, SKILL.md dosyasını ve varsa betiklerini incele. Kurulum dizinini ve kapsamını kurmadan önce seç.
