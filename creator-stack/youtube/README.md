# YouTube Shorts: çevrimdışı taslak

Üretilmiş bir videoyu yerelde denetler, başlık/açıklama/etiketler için YouTube Studio'ya kopyalanabilir bir taslak oluşturur. **YouTube hesabına bağlanmaz, OAuth/anahtar istemez ve hiçbir videoyu yüklemez, planlamaz veya yayımlamaz.** `private` önerilen görünürlüktür; Studio’da gerçek ayar senin seçiminle değişir.

## Çalıştırma

Python 3.10+ ve PATH üzerinde FFmpeg paketine dahil `ffprobe` gerekli; ek Python bağımlılığı yok. Bu komutu `creator-stack` kökünden çalıştır:

```bash
python3 youtube/prepare_short.py \
  --video "/yerel/klasor/kisa-film.mp4" \
  --title "Ay Evreleri 30 Saniyede" \
  --description "Ayın evreleri ışık ve bakış açısıyla nasıl oluşur?" \
  --tag "Türkçe kısa film" --tag "3D animasyon" --language tr \
  --audience review --output-dir "local-drafts/ay-evreleri"
```

Uzun açıklamayı `--description-file aciklama.txt` ile, isteğe bağlı SRT'yi `--caption-file altyazi.srt` ile ver. `--output-dir` yeni bir klasör olmalı; mevcut bir taslağın üzerine yazılmaz. Windows PowerShell'de komutu tek satırda `py -3` ile çalıştırabilir veya satır devamı için ters tırnak kullanabilirsin.

- `short-draft.json`: Yerel medya boyutu/dönüşü/en-boy oranı/süresi/SHA-256, başlık ve diğer alanlar, görünürlük ve hedef kitle kontrolü. Boyut ve süre kontrolü Shorts sınıflandırmasını garanti etmez.
- `youtube-studio.txt`: İçerik ve paylaşım kararlarını gözden geçirdikten sonra Studio'ya elle kopyalamak için alanlar ve kontrol listesi.
- Başlık karakterleri, açıklamanın UTF-8 bayt sayısı, etiketlerin ayraçlı uzunluğu, geçerli medya yönü ve en fazla 180 saniye kontrol edilir. SRT verilirse zamanlar, sıralama ve süre sınırı kontrol edilir. Hasarlı kareleri yakalamak için tam oynatma/çözümleme ayrıca yapılmalıdır.
- Medya dosyası kopyalanmaz. Başka bilgisayara aktarım için videoyu ve varsa altyazıyı ayrı taşı; hash, dosyanın aynı olup olmadığını denetler.

## Üretimden incelemeye

1. Açılış kancasını ve son cümleyi yaz. Ses/altyazıyı ve ilk/son kareyi kontrol et.
2. Örneğin 1080×1920 H.264/AAC MP4 çıkar. Taslak aracıyla teknik kontrolü çalıştır.
3. Telif, varsa yapay/sentetik içerik beyanı ve çocuklara özel seçeneklerini gözden geçir. Araç kitle tercihini varsaymaz.
4. Yüklemek istersen YouTube Studio'da videoyu kendin seç, taslağı kopyala ve ilk inceleme için `Özel` görünürlüğü seç. Otomatik yayın yoktur.

## Test

```bash
cd youtube
python3 -m unittest -v
```

Testler yalnızca geçici yerel medya üretir (FFmpeg olmadan medya testleri atlanır).

## Birinci taraf kaynaklar

- [YouTube Shorts süre ve en-boy ölçütleri](https://support.google.com/youtube/answer/15424877)
- [YouTube Data API video alanları ve uzunluk sınırları](https://developers.google.com/youtube/v3/docs/videos)
- [YouTube API örnek deposu, sabit referans](https://github.com/youtube/api-samples/tree/07263305b59a7c3275bc7e925f9ce6cabf774022). Arşiv niteliğindeki örnekler yalnızca referanstır. Kaynak bu çalışma alanında `upstream/youtube/api-samples` altında klonlandı, taşınabilir pakete dahil edilmedi ve eski OAuth/yükleme örnekleri çalıştırılmadı.
