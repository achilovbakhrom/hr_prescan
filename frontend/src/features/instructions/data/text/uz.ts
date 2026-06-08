import type { GuideText } from '../guide.types'

const uz: GuideText = {
  title: 'Bu qanday ishlaydi',
  subtitle:
    'PreScreen AI bo‘yicha bosqichma-bosqich qo‘llanma — vakansiya joylashdan tortib baholangan nomzodlarni ko‘rishgacha, hamda nomzod nimani ko‘rishigacha. To‘liq ko‘rish uchun istalgan skrinshotni bosing.',
  onThisPage: 'Ushbu sahifada',
  forHr: 'HR uchun',
  forCandidates: 'Nomzodlar uchun',
  flows: {
    'create-vacancy': {
      title: 'Vakansiya yaratish',
      summary:
        'Lavozim va nomzodlarga qo‘yiladigan talablarni belgilang — qolgani shunga quriladi.',
      steps: [
        {
          title: '“Vakansiyalar” sahifasini oching',
          description:
            'Yon menyudan “Vakansiyalar”ga o‘ting. Bu yerda barcha vakansiyalar holati va arizalar soni bilan ko‘rinadi. Saralash yo‘lagini boshlash uchun “Yangi vakansiya”ni bosing.',
          alt: '“Yangi vakansiya” tugmasi bilan vakansiyalar ro‘yxati',
        },
        {
          title: 'Vakansiya ma’lumotlarini to‘ldiring',
          description:
            '“Asosiy” bo‘limida nomi, tavsifi, talablar va majburiyatlarni kiriting. Ularni o‘zingiz yozishingiz yoki AI yordamida yaratishingiz mumkin.',
          alt: 'Nomi va tavsifi bilan saralash yo‘lagini yaratish shakli',
        },
        {
          title: 'Saqlang va vakansiyani oching',
          description:
            'Saqlaganda vakansiya qoralama sifatida yaratiladi va uning sahifasi ochiladi — u yerda dastlabki saralash, suhbat va e’lon qilish sozlanadi.',
          alt: 'Ma’lumot va bo‘limlar menyusi bilan vakansiya sahifasi',
        },
      ],
    },
    'setup-prescreen': {
      title: 'Dastlabki saralashni sozlash',
      summary: 'AIga nimani tekshirish va har bir nomzodni qanday baholashni ayting.',
      steps: [
        {
          title: 'AI ko‘rsatmalarini yozing',
          description:
            '“Dastlabki saralash” bo‘limini oching. Har bir nomzod ariza berganidan so‘ng AI bilan suhbatlashadi. Saralash tilini tanlang va e’tibor qaratish kerak bo‘lgan jihatlarni yozing.',
          alt: 'AI ko‘rsatmalari va saralash tili',
        },
        {
          title: 'Baholash mezonlarini ko‘rib chiqing',
          description:
            'AI javoblarni vaznli mezonlar bo‘yicha baholaydi. Maqbul standart mezonlar mavjud, ularni qo‘shish yoki vaznini o‘zgartirish mumkin.',
          alt: 'Vaznlari bilan dastlabki saralash mezonlari ro‘yxati',
        },
      ],
    },
    'setup-interview': {
      title: 'AI suhbatini sozlash',
      summary: 'Saralashdan o‘tgan nomzodlar uchun ixtiyoriy chuqurroq suhbat qo‘shing.',
      steps: [
        {
          title: 'Ikkinchi bosqich suhbatini yoqing',
          description:
            '“Sozlamalar” bo‘limida “Ikkinchi bosqich AI suhbati”ni yoqing. Bu kuchli nomzodlar uchun chuqurroq suhbatni ochadi.',
          alt: 'AI suhbati o‘tkazgichi bilan sozlamalar bo‘limi',
        },
        {
          title: 'Suhbatni sozlang',
          description:
            '“Suhbat” bo‘limida formatni (video yoki chat), davomiylikni va AI uchun nimani so‘rash va tekshirish bo‘yicha ko‘rsatmalarni belgilang.',
          alt: 'Suhbat formati, davomiyligi va AI ko‘rsatmalari',
        },
        {
          title: 'Suhbat mezonlarini belgilang',
          description:
            'Suhbatni baholash uchun vaznli mezonlarni qo‘shing. Rezyume, saralash va suhbat ballari nomzodning umumiy reytingiga birlashadi.',
          alt: 'Suhbatni baholash mezonlari ro‘yxati',
        },
      ],
    },
    'candidate-results': {
      title: 'Nomzod natijalarini ko‘rish',
      summary: 'Har bir nomzodning ballari, javoblari va AI tavsiyasi bir joyda.',
      steps: [
        {
          title: 'Nomzodlar doskasini oching',
          description:
            '“Nomzodlar”ga o‘ting va voronkani ko‘ring — Ariza berdi, Saralangan, Suhbatdan o‘tgan, Shortlist — rezyume va saralash ballari bilan.',
          alt: 'Voronka ustunlari bilan nomzodlar kanban doskasi',
        },
        {
          title: 'Nomzodni oching',
          description:
            'Nomzod sahifasi “Umumiy” yorlig‘ida ochiladi; bu yerda umumiy ball rezyume mosligi va saralashga ajratilgan kartochka ko‘rinadi.',
          alt: 'Umumiy ball kartochkasi bilan nomzod sharhi',
        },
        {
          title: 'Saralash natijalarini o‘qing',
          description:
            '“Saralash” yorlig‘i AI ballari va xulosasini ko‘rsatadi — tavsiya, kuchli tomonlar, xavflar, keyingi qadam — hamda butun yozishmalarni.',
          alt: 'Saralash ballari, tavsiya, kuchli tomonlar va xavflar',
        },
        {
          title: 'Umumiy tahlilni ko‘ring',
          description:
            '“Tahlil” yorlig‘i rezyume, saralash va suhbatni yagona xulosaga birlashtiradi va aniq tavsiya beradi — kimni davom ettirishni hal qilasiz.',
          alt: 'Umumiy tavsiya bilan jamlangan tahlil',
        },
      ],
    },
    'pass-prescreen': {
      title: 'Nomzod saralashdan qanday o‘tadi',
      summary: 'Nomzod nimani ko‘radi — ro‘yxatdan o‘tmasdan, hammasi bitta havola orqali.',
      steps: [
        {
          title: 'Havola orqali ariza berish',
          description:
            'Nomzod ommaviy havolani ochadi, ism, e-pochta va telefonni kiritadi va ixtiyoriy ravishda rezyume yuklaydi. Ro‘yxatdan o‘tish shart emas.',
          alt: 'Nomzod ariza shakli',
        },
        {
          title: 'Saralashni boshlash',
          description:
            'Yuborgach tasdiq ko‘rinadi va AI saralashni darhol boshlash yoki saqlangan havola orqali keyinroq yakunlash mumkin.',
          alt: 'Boshlash tugmasi bilan saralashga tayyorlik ekrani',
        },
        {
          title: 'AI bilan suhbat',
          description:
            'Nomzod AI savollariga matn yoki ovoz bilan javob beradi. Suhbat moslashadi, javoblar esa fonda avtomatik baholanadi.',
          alt: 'Nomzodning AI bilan saralash suhbati',
        },
        {
          title: 'Yakunlash',
          description:
            'Suhbat tugagach nomzod yakun ekranini ko‘radi, javoblar ko‘rib chiqishga yuboriladi. Baholangan natijalar nomzodlar doskasida paydo bo‘ladi.',
          alt: 'Saralash yakunlangani ekrani',
        },
      ],
    },
    'ai-assistant': {
      title: 'Hammasini AI yordamchisi orqali bajaring',
      summary:
        'Oddiy tilda so‘rang — yordamchi nomzodlarni topadi, vakansiya tayyorlaydi va voronkani tahlil qiladi.',
      steps: [
        {
          title: 'Yordamchini oching',
          description:
            'HR yordamchisini ochish uchun “AI’dan so‘rash”ni bosing. Tezkor amal kartochkalari nimani qila olishini ko‘rsatadi — nomzod topish, vakansiya yaratish, vakansiyalar bilan ishlash yoki voronkani tahlil qilish.',
          alt: 'Tezkor amal kartochkalari bilan AI yordamchisi',
        },
        {
          title: 'Oddiy tilda so‘rang',
          description:
            'So‘rovni yozing — yordamchi ishni bajaradi: ma’lumotlaringizni o‘qiydi, amallarni bajaradi va aniq javob hamda keyingi qadam bilan javob beradi.',
          alt: 'AI yordamchisi HR savoliga javob bermoqda',
        },
      ],
    },
  },
}

export default uz
