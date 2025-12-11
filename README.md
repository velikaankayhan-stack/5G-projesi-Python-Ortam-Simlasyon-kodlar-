# 5G Dinamik Kaynak Yönetimi ve Enerji Optimizasyonu Projesi

Bu proje, 5G baz istasyonlarında enerji verimliliğini artırmak ve sinyal kalitesini (SINR) korumak amacıyla **LSTM tabanlı trafik tahmini** ve **dinamik frekans atama** algoritmalarını simüle eder.

Proje, Google Antigravity simülasyon ortamında gerçekçi fiziksel formüller (Path Loss, Shannon Kapasitesi) kullanılarak test edilmiştir.

## 📂 Dosya Yapısı

*   `config.py`: Simülasyonun temel parametrelerini (frekans, anten gücü, gürültü vb.) içerir.
*   `physics_engine.py`: 5G sinyal yayılımı, girişim (interference) ve enerji hesaplamalarını yapan fizik motorudur.
*   `user_algo.py`: **Geliştirilen özgün algoritma.** Kaynak atama (Güç/Bant) ve Parazit Önleme mantığını içerir.
*   `data_generator.py`: 5 istasyon için 90 günlük sentetik trafik verisi (günlük/haftalık döngülerle) üretir.
*   `lstm_mock.py` (veya `lstm_train.py`): Trafik verisini işleyerek LSTM modeli ile gelecek yük tahminlerini oluşturur.
*   `simulation_runner.py`: **Ana simülasyon kodu.** Baseline ve Optimized senaryoları çalıştırır ve karşılaştırır.
*   `plot_results.py`: Simülasyon sonuçlarını (CSV) okuyarak karşılaştırmalı analiz grafiklerini çizer.

## 🚀 Çalıştırma Adımları (Jüri İçin)

Projeyi sıfırdan çalıştırmak için aşağıdaki adımları terminalde sırasıyla uygulayınız:

### 1. Adım: Veri Üretimi
Simülasyon için gerekli olan ham trafik verisini oluşturun.
```bash
python data_generator.py
```
*Çıktı:* `5G_90gun_5site_veri.csv` dosyası oluşacaktır.

### 2. Adım: Yapay Zeka (LSTM) Tahmini
Trafik verisini kullanarak gelecek 7 günlük yük tahminlerini yapın.
*(Not: TensorFlow kurulumu yoksa `lstm_mock.py` kullanılabilir, aynı formatta çıktı verir.)*
```bash
python lstm_train.py
```
*Çıktı:* `lstm_predictions.csv` ve `lstm_5site_sonuc.png` grafiği oluşacaktır.

### 3. Adım: Karşılaştırmalı Simülasyonu Başlat
Baseline (Statik) ve Optimized (Dinamik) sistemleri aynı senaryo üzerinde yarıştırın.
```bash
python simulation_runner.py
```
*Çıktı:* `simulation_results_comparison.csv` oluşacaktır. Ekranda anlık işlem logları görünür.

### 4. Adım: Sonuçları Görselleştir
Elde edilen verileri grafiğe dökerek analizi tamamlayın.
```bash
python plot_results.py
```
*Çıktı:* `comparison_graphs.png` dosyası oluşacaktır. Bu grafik Enerji ve SINR farklarını gösterir.

## 📊 Sonuçlar
Simülasyon çıktıları, geliştirilen algoritmanın düşük trafik yoğunluğunda enerji tüketimini azalttığını, yüksek yoğunlukta ise bant genişliğini artırarak servis kalitesini koruduğunu kanıtlamaktadır.
