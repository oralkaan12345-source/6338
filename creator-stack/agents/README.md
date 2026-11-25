# Yerel YouTube rol grafiği

LangGraph'ın açık kaynak [StateGraph API'si](https://docs.langchain.com/oss/python/langgraph/graph-api) ile üç rol: **araştırma → senaryo → kalite kontrol**. LangGraph `1.2.24` [yayını](https://pypi.org/project/langgraph/1.2.24/) sabittir; [resmî GitHub etiketi](https://github.com/langchain-ai/langgraph/tree/1.2.24) commit'i `58a6e1cc5b7dfc3619fc6e7e7573b040d554649b`. Bağımlılıklar `uv.lock` içinde pinli.

- **Varsayılan çevrimdışı mod:** Yerel JSON notlarını düzenleyen deterministik rol grafiği. Model çalıştırmaz, web'de arama yapmaz, API anahtarı istemez, yükleme/yayınlama/mesajlaşma yapmaz.
- **Opsiyonel yerel model modu:** Hazır çalışan Ollama modelinle sıralama, taslak yazımı ve ayrı model eleştirisi. En fazla üç istek, yalnızca `http://127.0.0.1:11434/api/chat`; yönlendirme, HTTP proxy, model araçları veya bulut alternatifi yok. URL'ler kaynak metaverisi olarak kalır; uygulama onları ziyaret etmez. Model çıktısı doğrulanmış haber veya yayına hazır içerik sayılmaz.
- Agent SDK yerine bu kurulumda LangGraph seçildi: sabit ve incelenebilir yürütme sırası, model bağlı olmadan test edilebiliyor.

## Windows PowerShell

Python 3.12 ve [uv](https://docs.astral.sh/uv/getting-started/installation/) kurulu olmalı. Depo içindeki `creator-stack\agents` yolundan çalıştır:

```powershell
Set-Location creator-stack\agents
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
uv sync --locked --python 3.12
.\.venv\Scripts\python.exe -m unittest -v
.\.venv\Scripts\python.exe pipeline.py --brief examples\gece-treni.json --output taslak.json
```

Linux/macOS:

```sh
cd creator-stack/agents
UV_CACHE_DIR="$PWD/.uv-cache" uv sync --locked --python 3.12
.venv/bin/python -m unittest -v
.venv/bin/python pipeline.py --brief examples/ay-evreleri.json --output taslak.json
```

Paket kurulumu PyPI erişimi ister, ilk kurulumdan sonra varsayılan çalışma tamamen çevrimdışı. Kendi girdin için `examples/gece-treni.json` dosyasını örnek al: `topic`, `audience`, `kind`, `hook` ve 3–8 `notes` nesnesi. Her not `text`, `visual` ve olgusal (`factual`) işlerde `source_url` verir. Olgusal örnek notlar [NASA Ay evreleri sayfasına](https://science.nasa.gov/moon/moon-phases/) dayanır. Kurgu (`fiction`) ayrı etiketlenir. YouTube aramasından yalnızca başlığı ve URL'i bilinen videoları olgusal iddia olarak aktarma; önce not ve kaynak iddia incelemesini yap.

## İsteğe bağlı: Windows'ta mevcut Ollama modelin

Daha önce indirdiğin modeli `ollama list` ile kontrol et. **Sunucuda bulutu kapat:** [Ollama'nın yerel çalışma ayarlarına](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features) göre `%USERPROFILE%\.ollama\server.json` içindeki mevcut ayarları koruyarak `"disable_ollama_cloud": true` ekle ve Ollama'yı yeniden başlat. Alternatif: GUI uygulamasından çık, yeni bir PowerShell'de `$env:OLLAMA_NO_CLOUD = "1"` ve ardından `ollama serve`. Sunucu günlüğünde `Ollama cloud disabled: true` gör; bağlanma adresi varsayılan loopback olarak kalsın. Bu araç model indirmez ve daemon ayarını değiştirmez; yerel modu daemon başlatılırken ayarlaman gerekir.

```powershell
.\.venv\Scripts\python.exe pipeline.py --brief examples\gece-treni.json --model gemma4:12b --output yerel-taslak.json
```

Yalnızca belirlediğin yerel Ollama modeli kullanılır. Model gelmez veya geçersiz JSON dönerse işlem durur; gizli ücretli çağrı ya da sessiz alternatif yok. Yerel rota ve üç çağrı sınırı gerçek ağ kullanılmadan sahte Ollama yanıtlarıyla doğrulandı. Belirli modelin kendi Windows bilgisayarındaki hız/doğruluğu burada test edilmedi.

## Çıktı

Dört sahne; zaman aralıkları, seslendirme, dikey görsel önerisi ve kaynak bağlantısı kimlikleri. QA süre/kelime bütçesi ve kaynak kimliği bağlarını denetler, olguları doğrulamaz. `DRAFT_OK` sadece yapısal kontrolün sonucudur; tüm çıktılar insan incelemesi gereken taslaktır. `--output` yoksa JSON ekrana yazılır. Var olan dosyanın üzerine yazılmaz. Çıkış kodları: `0` yapısal başarı, `2` geçersiz girdi/yerel köprü hatası, `3` kayıtlı ama revizyon gereken taslak.
