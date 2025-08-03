## 🌐 Language | Dil
[English](#english) | [Türkçe](#turkce)

<a name="english"></a>
## 🇬🇧 English Version

## Installation and Setup

```bash
git clone https://github.com/MyyTimes/BTK-Hackathon.git
cd BTK-Hackathon
pip install -r requirements.txt
python app.py
```

### Set Up Environment Variables:

- Create a file named **.env** in the project's root directory.
- Add your Google Gemini API key to this file:

```
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

Then open [**http://127.0.0.1:5000**](http://127.0.0.1:5000) in your web browser.

---

# AI-Powered LGS Exam Coach

This project is a web application designed to provide a personalized learning experience for students preparing for the LGS (High School Entrance System) exam in Turkey. Built with Flask, this application acts as an AI coach (powered by Google Gemini), analyzing students' mock exam results to offer custom study schedules, resource recommendations, and general success strategies.

---

## Key Features

- **AI Chat Interface:** A dynamic chat panel allowing students to interact directly with the AI to ask questions, receive advice, and give commands.
- **Personalized Study Schedule Generation:** Analyzes the student's strengths and weaknesses based on their exam scores (entered into an Excel file) to create a weekly study schedule. This schedule is also available for download as an .xlsx file.
- **Smart Book Recommendations:** Recommends the most suitable test books for the student's achievement level, based on a predefined list of books and their difficulty levels.
- **Exam Score Tracking:** Allows users to input their mock exam scores for various subjects into the system.
- **Performance Visualization:**
  - A bar chart on the main page shows overall success rates by subject.
  - A line chart on the "Add Exam" page tracks the net score progression for each subject across all mock exams.
- **Data Persistence:** All student data, including exam results, the weekly schedule, and the book list, is stored in Excel files for easy management and persistence.

---

## Technology Stack

- **Backend:** Python, Flask
- **AI & LLM:** Google Gemini, LangChain
- **Frontend:** HTML, CSS, JavaScript
- **Data Processing & Storage:** Pandas, Openpyxl (for Excel files)
- **Charting Library:** Chart.js
- **Environment Variables:** python-dotenv

---

## Project Structure and File Descriptions

```
.
├── app.py                  # Main Flask application. Manages routing and server logic.
├── connect_ai.py           # Manages all interactions with the Google Gemini AI model using LangChain and performs intent analysis.
├── excel_operations.py     # Handles all Excel read/write operations.
├── lesson_functions.py     # Contains constants (e.g., max number of questions) and helper functions related to the lessons.
├── templates/
│   ├── index.html          # The main page. Contains the success chart, weekly schedule, and AI chat panel.
│   └── add_exam.html       # The page for adding new exam scores and viewing subject-specific progress charts.
├── static/
│   └── style.css           # Modern and responsive design styles for all HTML pages.
├── weekly_schedule.xlsx    # The file where the AI-generated weekly study schedule is saved.
├── exam_results.xlsx       # The database file that stores all user-entered mock exam scores.
└── test_book_list.xlsx     # A list of available books and their difficulty levels, used for AI recommendations.
```

---

## How It Works (Application Architecture)

### **Data Entry and Management:**

- The user enters the name and subject scores of a new mock exam via the add\_exam.html page.
- The `/process_new_exam` route in **app.py** receives this data and calls the `add_new_exam_result` function from **excel\_operations.py**.
- This function writes the data to the **exam\_results.xlsx** file. It updates the entry if an exam with the same name exists; otherwise, it appends it as a new row.

### **Data Visualization:**

- The main page (**index.html**) and the "Add Exam" page (**add\_exam.html**) read data from **exam\_results.xlsx** using functions from **excel\_operations.py**.
- This data (average success percentages and per-exam net scores) is then rendered into dynamic charts on the front end using Chart.js.

### **AI Interaction (Core Logic):**

- The user sends a message from the chat panel on **index.html**.
- The `/send_chat_message` route in **app.py** forwards this request to the `ai_answer` function in **connect\_ai.py**.
- **Intent Detection (Router Chain):** The `ai_answer` function first runs a "Router" chain built with LangChain. This chain analyzes the user's input to determine its primary intent, classifying it as **book** (book recommendation), **schedule** (schedule creation), **advice** (general advice), or **default**.
- **Routing (RunnableBranch):** Based on the router's output, a RunnableBranch structure directs the request to the appropriate specialized chain:
  - **schedule\_chain:** Handles requests for creating a study schedule. It injects the student's data (`get_personal_data`) into the prompt and asks the AI to generate output in a specific format. The generated text is then piped directly to the `create_schedule` function, which creates the **weekly\_schedule.xlsx** file.
  - **book\_advice\_chain:** Handles requests for book recommendations. It injects the student's data and the available book list (`get_test_book_list`) into the prompt to generate the most suitable recommendations.
  - **advice\_chain / default\_chain:** Generate more general responses for all other queries.
- The final response from the AI is sent back to the user interface in JSON format.

---

<a name="turkce"></a>
## 🇹🇷 Türkçe Sürüm

### Kurulum

```bash
git clone https://github.com/MyyTimes/BTK-Hackathon.git
cd BTK-Hackathon
pip install -r requirements.txt
python app.py
```

`.env` dosyası oluşturun ve Google Gemini API anahtarınızı ekleyin:

```
GOOGLE_API_KEY="ANAHTARINIZ"
```

Sonrasında tarayıcınızda [**http://127.0.0.1:5000**](http://127.0.0.1:5000) adresini girin.

---

# LGS Yapay Zeka Destekli Sınav Koçu

Bu proje, Türkiye'deki LGS (Liseye Geçiş Sınavı) sınavına hazırlanan öğrenciler için kişiselleştirilmiş bir öğrenme deneyimi sunmayı amaçlayan bir web uygulamasıdır. Flask ile geliştirilen bu uygulama, Google Gemini destekli bir yapay zekâ koçu olarak çalışır; öğrencilerin deneme sınavı sonuçlarını analiz eder, kişiye özel haftalık çalışma programları, ders bazlı başarı oranlarına uygun kaynak önerileri ve genel başarı stratejileri sunar.

### Temel Özellikler
- **Yapay Zeka Sohbet Arayüzü:** Öğrencilerin doğrudan yapay zekâ ile sohbet ederek soru sorabildiği, tavsiye alabildiği dinamik bir panel.
- **Kişiselleştirilmiş Çalışma Programı Oluşturma:** Öğrencinin sınav netlerine göre güçlü ve zayıf yönlerini analiz ederek haftalık çalışma programı oluşturur. Program ayrıca .xlsx formatında indirilebilir.
- **Akıllı Kitap Önerileri:** Öğrencinin başarı seviyesine göre en uygun test kitaplarını önerir.
- **Deneme Sınavı Takibi:** Öğrenciler deneme sınavı netlerini sisteme girebilir.
- **Performans Görselleştirme:**
  - Ana sayfada derslere göre genel başarı oranlarını gösteren çubuk grafik.
  - “Yeni Net Ekle” sayfasında her dersin netlerinin zaman içindeki değişimini gösteren çizgi grafik.
- **Veri Saklama:** Tüm öğrenci verileri (sınav sonuçları, haftalık program ve kitap listesi) Excel dosyalarında tutulur.

### Teknoloji Yığını
- **Backend:** Python, Flask
- **Yapay Zeka & LLM:** Google Gemini, LangChain
- **Frontend:** HTML, CSS, JavaScript
- **Veri İşleme ve Saklama:** Pandas, Openpyxl (Excel dosyaları için)
- **Grafik Kütüphanesi:** Chart.js
- **Ortam Değişkenleri:** python-dotenv

## Dosya Yapısı ve Açıklamaları

```
.
├── app.py                  # Flash uygulamları: Sunucu ve routing mekanizmasının yönetilmesi
├── connect_ai.py           # LangChain kullanarak Google Gemini AI modeliyle tüm etkileşimleri yönetir ve niyet analizi gerçekleştirir.
├── excel_operations.py     # Tüm Excel okuma/yazma işlemlerini yönetir.
├── lesson_functions.py     # Derslerle ilgili değişken sabitleri (örneğin, maksimum soru sayısı) ve yardımcı fonksiyonları içerir.
├── templates/
│   ├── index.html          # Ana sayfa. Başarı çizelgesini, haftalık programı ve AI sohbet panelini içerir.
│   └── add_exam.html       # Yeni sınav puanları ekleme ve konu bazlı ilerleme çizelgelerini görüntüleme sayfası.
├── static/
│   └── style.css           # Tüm HTML sayfaları için modern ve duyarlı tasarım stilleri.
├── weekly_schedule.xlsx    # Yapay zeka tarafından oluşturulan haftalık çalışma programının kaydedildiği dosya.
├── exam_results.xlsx       # Kullanıcıların girdiği tüm deneme sınav puanlarını depolayan veritabanı dosyası.
└── test_book_list.xlsx     # Yapay zeka önerileri için kullanılan, mevcut kitapların ve zorluk seviyelerinin bir listesi.
```
