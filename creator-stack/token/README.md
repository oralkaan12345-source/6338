# RTK: terminal çıktısını yerelde küçült

Resmî [rtk-ai/rtk OSS v1.2.1](https://github.com/rtk-ai/rtk/releases/tag/v1.2.1) sürümü sabitlendi. Buradaki kullanım, seçtiğin terminal komutunun çıktısını Codex okumadan önce özetler. Global ayar, otomatik hook, PATH değişikliği veya LLM/API proxy kurulmaz. Yerel istatistik dosyası `.state/` içindedir. Örneklerde telemetri kapalıdır.

## Linux x64 / WSL x64

```bash
bash creator-stack/token/install-linux.sh
bash creator-stack/token/rtk-local.sh git status
bash creator-stack/token/rtk-local.sh gain --text
bash creator-stack/token/test-rtk.sh
```

Kurulum arşivin SHA-256 değerini [GitHub sürüm bilgisine](https://api.github.com/repos/rtk-ai/rtk/releases/tags/v1.2.1) göre doğrular. Çalıştırıcı bulunduğun dizini değiştirmez; `git status` kullanırken kendi Git proje dizininde ol ve çalıştırıcıya gerekirse mutlak yol ver.

## Windows x64 PowerShell

```powershell
# Depo kökünden, kaynak kodunu okuyup onayladıktan sonra:
.\creator-stack\token\install-windows.ps1
$state = Join-Path (Resolve-Path .\creator-stack\token).Path '.state'
New-Item -ItemType Directory -Path $state -Force | Out-Null
$env:RTK_TELEMETRY_DISABLED = '1'
$env:RTK_DB_PATH = Join-Path $state 'rtk.sqlite'
.\creator-stack\token\bin\rtk.exe telemetry status
.\creator-stack\token\bin\rtk.exe git status
.\creator-stack\token\bin\rtk.exe gain --text
```

Bu ortam Linux olduğu için Windows çalıştırılmadı; resmî Windows ZIP'i ayrıca indirildi, SHA-256 ve `rtk.exe` içeriği doğrulandı. Git komutu için yerel Git gerekir. PowerShell betik çalıştırma ilkelerini değiştirmek gerekirse bunu otomatik olarak atlama; resmi sürüm ZIP'ini elle indirip hash'i doğrulayarak açmak da mümkün.

## Codex ile kullanma ve ölçüm

Agent'a, desteklenen salt okunur terminal komutlarından önce yerel RTK çalıştırıcısını kullanmasını söyle. Tam çıktı gerektiğinde RTK olmadan aynı güvenli komutu tekrar çalıştır. Resmî [Codex CLI entegrasyonu](https://github.com/rtk-ai/rtk/blob/v1.2.1/docs/guide/getting-started/supported-agents.md#codex-cli) proje içi `rtk init --codex` seçeneği de sunuyor; bunun `.codex/hooks.json`, `AGENTS.md` ve `RTK.md` üzerine etkisini `--dry-run` ile doğruladık fakat kurmadık. Kurulu olmayan işlevi etkin sayma.

Linux'ta sentetik video/test dosyalarıyla gerçek Git testi:

| Ölçüm | Normal Git | RTK |
| --- | ---: | ---: |
| Çıktı | 885 bayt | 475 bayt |
| Satır | 33 | 23 |
| RTK'nin yaklaşık token sayımı | 222 | 119 |

Bu denemede çıktı baytları **%46,33** azaldı; verim komuta ve çıktıya göre değişir. Bu oran toplam Codex kotası, model yanıtları veya ücretlerde aynı tasarrufu garanti etmez. RTK video üretimini ya da işleme süresini iyileştirmez. Düzenleme, güvenlik incelemesi ve hata ayıklamada eksiksiz log/diff gerekiyorsa filtre kullanma; kritik ayrıntılar özetten elenebilir.
