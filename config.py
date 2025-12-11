
# config.py
# Bu dosya, TÜBİTAK projesi kapsamında kullanılan 5G simülasyonunun 
# temel fiziksel ve operasyonel parametrelerini içerir.

# --- SİMÜLASYON AYARLARI ---
SIMULATION_DURATION_HOURS = 24  # 1 günlük simülasyon
TIME_STEP_MINUTES = 60          # Veri çözünürlüğü

# --- BAZ İSTASYONU KONFİGÜRASYONU ---
NUM_BASE_STATIONS = 5
BS_HEIGHT = 30.0  # metre (Baz istasyonu yüksekliği)
UE_HEIGHT = 1.5   # metre (Kullanıcı cihazı yüksekliği)
CARRIER_FREQ_MHZ = 3500.0  # 3.5 GHz (C-Band, 5G standardı)

# --- BASELINE (MEVCUT DURUM) SENARYOSU ---
# Geleneksel/Statik yapı: Sabit güç ve bant genişliği
BASELINE_CONFIG = {
    "bandwidth_mhz": 40.0,   # Sabit 40 MHz
    "tx_power_watt": 40.0,   # Sabit 40 Watt (46 dBm)
    "sleep_mode": False      # Uyku modu yok
}

# --- OPTIMIZED (ÖNERİLEN) SENARYO ---
# LSTM ve Algoritma destekli dinamik yapı
OPTIMIZED_CONFIG = {
    "min_bandwidth_mhz": 10.0,
    "max_bandwidth_mhz": 100.0,
    "min_power_watt": 5.0,   # Uyku modu/Düşük trafik
    "max_power_watt": 60.0,  # Yoğun trafik
    "sleep_mode_threshold_users": 5, # 5 kullanıcının altındaysa uyku modu
    "hysteresis_margin_mhz": 5.0    # Kararlılık için histerezis bandı
}

# --- FİZİKSEL SABİTLER ---
NOISE_FLOOR_DBM_HZ = -174.0  # Termal gürültü tabanı
NOISE_FIGURE_DB = 9.0        # Alıcı gürültü şekli
PATH_LOSS_EXPONENT = 3.5     # Şehir içi (Urban) ortam sönümleme katsayısı
REFERENCE_DISTANCE_M = 1.0   # Referans uzaklığı
