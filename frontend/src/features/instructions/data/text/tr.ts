import type { GuideText } from '../guide.types'

const tr: GuideText = {
  title: 'Nasıl çalışır',
  subtitle:
    'PreScreen AI için adım adım kılavuz — bir ilan yayınlamaktan puanlanmış adayları incelemeye, ayrıca adayların gördüklerine kadar. Tam boyutta görmek için herhangi bir ekran görüntüsüne tıklayın.',
  onThisPage: 'Bu sayfada',
  forHr: 'İK için',
  forCandidates: 'Adaylar için',
  flows: {
    'create-vacancy': {
      title: 'İlan oluşturma',
      summary: 'Diğer her şeyin üzerine kurulduğu rolü ve aday gereksinimlerini tanımlayın.',
      steps: [
        {
          title: 'İlanlar sayfasını açın',
          description:
            'Kenar menüsünden İlanlar’a gidin. Tüm roller durumu ve başvuru sayısıyla listelenir. Bir eleme akışı başlatmak için “Yeni İlan”a tıklayın.',
          alt: '“Yeni İlan” düğmesiyle ilan listesi',
        },
        {
          title: 'İlan ayrıntılarını doldurun',
          description:
            'Temel Bilgiler sekmesinde başlık, açıklama, gereksinimler ve sorumlulukları girin. Bunları kendiniz yazabilir veya yapay zekâ ile oluşturabilirsiniz.',
          alt: 'Başlık ve açıklamayla eleme akışı oluşturma formu',
        },
        {
          title: 'Kaydedin ve ilanı açın',
          description:
            'Kaydetme ilanı taslak olarak oluşturur ve ön eleme, mülakat ve yayınlamayı yapılandırdığınız ayrıntı sayfasını açar.',
          alt: 'İş bilgisi ve bölüm menüsüyle ilan ayrıntı sayfası',
        },
      ],
    },
    'setup-prescreen': {
      title: 'Ön elemeyi ayarlama',
      summary: 'Yapay zekâya neyi araştıracağını ve her adayı nasıl puanlayacağını söyleyin.',
      steps: [
        {
          title: 'Yapay zekâ talimatlarını yazın',
          description:
            'Ön Eleme bölümünü açın. Her aday başvurudan sonra yapay zekâ ile sohbet eder. Eleme dilini seçin ve nelere odaklanacağını yazın.',
          alt: 'Yapay zekâ talimatları ve eleme dili',
        },
        {
          title: 'Puanlama ölçütlerini gözden geçirin',
          description:
            'Yapay zekâ yanıtları ağırlıklı ölçütlere göre puanlar. Makul varsayılanlar gelir; kendi ölçütlerinizi ekleyebilir veya ağırlıklarını değiştirebilirsiniz.',
          alt: 'Ağırlıklarıyla ön eleme puanlama ölçütleri listesi',
        },
      ],
    },
    'setup-interview': {
      title: 'Yapay zekâ mülakatını ayarlama',
      summary: 'Ön elemeyi geçen adaylar için isteğe bağlı daha derin bir mülakat ekleyin.',
      steps: [
        {
          title: 'İkinci adım mülakatı etkinleştirin',
          description:
            'Ayarlar bölümünde “İkinci Adım Yapay Zekâ Mülakatı”nı açın. Bu, güçlü adaylar için daha derin bir mülakatı açar.',
          alt: 'Yapay zekâ mülakatı anahtarıyla ayarlar bölümü',
        },
        {
          title: 'Mülakatı yapılandırın',
          description:
            'Mülakat bölümünde biçimi (video veya sohbet), süreyi ve neyin sorulup doğrulanacağına dair yapay zekâ talimatlarını ayarlayın.',
          alt: 'Mülakat biçimi, süresi ve yapay zekâ talimatları',
        },
        {
          title: 'Mülakat ölçütlerini tanımlayın',
          description:
            'Mülakatı puanlamak için ağırlıklı ölçütler ekleyin. CV, ön eleme ve mülakat puanları adayın genel sıralamasında birleşir.',
          alt: 'Mülakat puanlama ölçütleri listesi',
        },
      ],
    },
    'candidate-results': {
      title: 'Aday sonuçlarını inceleme',
      summary: 'Her adayın puanları, yanıtları ve yapay zekâ önerisi tek bir yerde.',
      steps: [
        {
          title: 'Adaylar panosunu açın',
          description:
            'Adaylar’a gidip akış panosunu görün — Başvurdu, Ön Elendi, Mülakat, Kısa Liste — CV ve ön eleme puanlarıyla.',
          alt: 'Akış sütunlarıyla adaylar kanban panosu',
        },
        {
          title: 'Bir adayı açın',
          description:
            'Aday sayfası Genel Bakış’ta açılır; genel puanı CV uyumu ve ön elemeye ayıran bir puan kartı bulunur.',
          alt: 'Genel puan kartıyla aday genel bakışı',
        },
        {
          title: 'Ön eleme sonuçlarını okuyun',
          description:
            'Ön Eleme sekmesi yapay zekânın puanlarını ve özetini gösterir — öneri, güçlü yönler, riskler, sonraki adım — ve tüm sohbet dökümünü.',
          alt: 'Ön eleme puanları, öneri, güçlü yönler ve riskler',
        },
        {
          title: 'Genel analizi inceleyin',
          description:
            'Analiz sekmesi CV, ön eleme ve mülakatı net bir öneriyle tek bir karara birleştirir; böylece kimi ilerleteceğinize karar verirsiniz.',
          alt: 'Genel öneriyle birleşik analiz',
        },
      ],
    },
    'pass-prescreen': {
      title: 'Bir aday ön elemeyi nasıl geçer',
      summary: 'Adayın gördüğü — hesap gerekmez, her şey tek bir bağlantıyla çalışır.',
      steps: [
        {
          title: 'Bağlantıyla başvurun',
          description:
            'Aday herkese açık başvuru bağlantısını açar; adını, e-postasını ve telefonunu girer ve isteğe bağlı CV yükler. Kayıt gerekmez.',
          alt: 'Aday başvuru formu',
        },
        {
          title: 'Ön elemeyi başlatın',
          description:
            'Gönderdikten sonra bir onay görür ve yapay zekâ ön elemesini hemen başlatabilir veya kayıtlı bağlantıyla sonra bitirebilir.',
          alt: 'Başlat düğmesiyle ön elemeye hazır ekranı',
        },
        {
          title: 'Yapay zekâ ile sohbet edin',
          description:
            'Aday yapay zekânın sorularını metin veya sesle yanıtlar. Sohbet uyum sağlar ve yanıtlar arka planda otomatik puanlanır.',
          alt: 'Adayın yapay zekâ ile ön eleme sohbeti',
        },
        {
          title: 'Bitirin',
          description:
            'Sohbet bitince aday bir tamamlanma ekranı görür ve yanıtları incelemeye gönderilir. Puanlanan sonuçlar Adaylar panonuzda görünür.',
          alt: 'Ön eleme tamamlandı ekranı',
        },
      ],
    },
    'ai-assistant': {
      title: "Her şeyi yapay zekâ asistanıyla yapın",
      summary: "Sade bir dille sorun — asistan aday bulur, ilan hazırlar ve huninizi analiz eder.",
      steps: [
        { title: "Asistanı açın", description: "İK asistanını açmak için “Yapay Zekâya Sor”a tıklayın. Hızlı eylem kartları neler yapabileceğini gösterir — aday bulma, ilan oluşturma, ilanlarla çalışma veya işe alım huninizi analiz etme.", alt: "Hızlı eylem kartlarıyla yapay zekâ asistanı" },
        { title: "Sade bir dille sorun", description: "Bir istek yazın, asistan işi yapar: verilerinizi okur, eylemleri gerçekleştirir ve net bir yanıt ile sonraki adımı verir.", alt: "İK sorusunu yanıtlayan yapay zekâ asistanı" },
      ],
    },
  },
}

export default tr
