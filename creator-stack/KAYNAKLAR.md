# Araştırma ve seçim

Bu sınırlı kamuya açık örneklem bir popülerlik sıralaması değildir. Sosyal paylaşımları aday bulmak, resmi kaynakları işlev ve sürüm doğrulamak, yerel testleri ise davranışı ölçmek için kullandık.

| Kamuya açık örnek | İlgi ve karar |
| --- | --- |
| [Nate Herk: n8n ile YouTube stratejisti](https://www.youtube.com/watch?v=Ch-AWxvX2Jc) | Planlama otomasyonu iyi bir örnek. Bulut bağımlılığı eklemeden, API'den salt okunur araştırma ve yerel dosyaya taslak üretme tercih edildi. Tanıtımdaki gelir iddiası değerlendirmeye alınmadı. |
| [Evolution with AI: MoneyPrinterTurbo](https://www.youtube.com/watch?v=uBlWbHdTP4Y) | Dikey video üretimi için aday. [6338'in mevcut video kurulumu](https://github.com/oralkaan12345-source/6338/tree/main/video) ayrıdır. Bu paketin ön kontrolü mevcut MP4 ile çalışır; üretim aracı ya da ses hizmeti zorunlu değildir. |
| [LangChain: LangGraph çoklu ajan örneği](https://www.youtube.com/watch?v=JLDLANs_m_w) | Rollerin, girdilerin ve sonlandırma koşullarının açık tanımlandığı daha dar bir akış tercih edildi. [Resmi LangGraph sürümleri](https://github.com/langchain-ai/langgraph/releases). |
| [Made In LowCode: RTK](https://www.youtube.com/watch?v=NTFkjzZe2BQ) | Desteklenen terminal çıktıları için yerel test yapıldı; sosyal medyadaki tasarruf oranları kullanılmadı. [Resmi RTK](https://github.com/rtk-ai/rtk). |
| [Build Things With AI: Ruflo](https://www.youtube.com/watch?v=z5G-iU5bHhs) | Daha geniş ajan orkestrasyonuna bir örnek. Bu kullanımda daha fazla ajan, daha fazla bağlam ve kurulum yükü getirebileceği için eklenmedi. |

Instagram ve TikTok için aynı konularda açıkça doğrulanabilir, repo bağlantısı tespit edilebilen içerik elde edilemedi. Bu, bu platformlarda ilgili paylaşım olmadığı anlamına gelmez. [TikTok'un resmi Effect House eklentisi](https://effecthouse.tiktok.com/learn/guides/effect-house-plugin) AR efektleri içindir, bu YouTube iş akışının bir parçası değildir.

[YouTube'un resmi API örnekleri](https://github.com/youtube/api-samples) referans olarak alındı. Canlı okuma seçeneği mevcut [search.list](https://developers.google.com/youtube/data/reference/rest/v3/search/list) ve [videos.list](https://developers.google.com/youtube/data/reference/rest/v3/videos/list) dokümantasyonuna dayanır; eski örneklerdeki OAuth kodunu çalıştırmaz.
