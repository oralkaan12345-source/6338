# Creator Stack · YouTube Shorts

Yerel bir akış: **konu araştırması → araştırmacı / senarist / kalite kontrol → hazır MP4'ü denetle → YouTube Studio için yerel taslak**. Video render etmez. YouTube'a video yüklemez, planlamaz veya yayımlamaz.

## Windows x64: ilk kurulum

Bu dosyanın bulunduğu klasörü PowerShell'de aç. Python 3.11–3.13 kullan; örnekte 3.13 seçildi. Ajanlar için [uv](https://docs.astral.sh/uv/getting-started/installation/), videoyu kontrol etmek için PATH üzerinde FFmpeg/`ffprobe`, RTK'nın Git örneği için Git gerekir.

```powershell
uv sync --locked --project .\agents --python 3.13
.\agents\.venv\Scripts\python.exe .\agents\pipeline.py --brief .\agents\examples\ay-evreleri.json
py -3.13 .\research\youtube_public.py --self-test
.\token\install-windows.ps1
```

Linux/WSL karşılığı:

```bash
uv sync --locked --project agents --python 3.13
agents/.venv/bin/python agents/pipeline.py --brief agents/examples/ay-evreleri.json
python3 research/youtube_public.py --self-test
bash token/install-linux.sh
bash token/test-rtk.sh
```

### Diğer Codex sohbetlerinde skill'i kullan

Windows'ta kullanıcı hesabına bu paketin **yalnızca skill** dosyasını kurmak için, komut dosyasını inceledikten sonra:

```powershell
.\install-codex-skill.ps1
```

Bu, `$HOME/.agents/skills/creator-stack/SKILL.md` konumunu kullanır ve farklı bir mevcut sürümün üzerine yazmaz. Codex'te `$creator-stack` ile çağırabilir, yerel paket klasörünün yolunu verebilirsin. Bu ayar aynı kullanıcı ve bilgisayardaki yerel Codex projelerini kapsar. Başka bir bilgisayara veya yalıtılmış bir bulut çalışmasına dosya taşımaz. [Codex skill kapsamları](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

## Kullanım

**Ajanlar:** LangGraph 1.2.24. Varsayılan akış, verdiğin JSON notlarıyla internetsiz çalışır; canlı araştırma veya model yanıtı taklidi yapmaz. Model kullanmayı seçersen mevcut yerel Ollama modeliyle `--model gemma4:12b` gibi bir seçenek geçir. Ajan başına en çok bir çağrı, toplam en çok üç çağrı; çıktı ve kaynaklar insan incelemesi gerektirir. Ollama seçeneği otomatik olarak model indirmez veya bulut hizmeti kullanmaz.

**Canlı YouTube araştırması (isteğe bağlı):** YouTube Data API v3 etkinleştirilmiş ve bu API ile sınırlandırılmış bir anahtarı kendi terminal ortamında `YOUTUBE_API_KEY` olarak ayarla. Anahtarı sohbete, GitHub'a veya çıktıya koyma.

```powershell
py -3.13 .\research\youtube_public.py "ocean mystery stories" --region US --lang en --days 90
```

Sonuç yalnızca herkese açık video metaverisi ve gözlem anındaki izlenme bilgilerini içerir. Bunlar özel kanal analitiği değildir; süre filtresi tek başına bir videonun Shorts olduğunu kanıtlamaz. Kaynakları gözden geçirip işe yarayan bulguları ajan brief'ine not olarak geçir; video başlığını doğrulanmış olgu gibi kullanma.

**Tek komutla ortak taslak** (çıktı klasörü yeni olmalı):

```powershell
.\agents\.venv\Scripts\python.exe .\run_draft.py --brief .\agents\examples\ay-evreleri.json --video "C:\Videos\ornek.mp4" --title "Ay Evreleri" --description "Ayın evreleri nasıl oluşur?" --output-dir .\local-drafts\ay-ornek
```

Çıktılar: `editorial-draft.json`, `studio/short-draft.json`, `studio/youtube-studio.txt`. Ajanlar revizyon isterse Studio taslağı üretilmez. `--model` yoksa kural tabanlı mod çalışır. [MP4 ve altyazı ön kontrolü](youtube/README.md).

**Token tasarrufu:** [RTK kurulum ve ölçüm](token/README.md). Ayarlar ve API trafiği değiştirilmez; RTK yalnızca kendisiyle açıkça başlatılan komutların terminal çıktısını kısaltır. Genel token kotasında aynı oranda tasarruf garanti değildir.

[Araştırma, kaynaklar ve seçim gerekçesi](KAYNAKLAR.md)
