import pandas as pd
import numpy as np

print("5G Trafik Verisi Üretiliyor...")

# Rastgelelik kontrolü
np.random.seed(42)

# Simülasyon parametreleri
days = 90  # 3 ay
sites = 5  # 5 baz istasyonu
hours = days * 24
idx = pd.date_range("2025-04-01", periods=hours, freq="h")

# Parametre aralıkları
base_users = [80, 130, 200, 250, 300]  # şehir yoğunlukları
energy_base = [100, 120, 140, 160, 180]

data = []

for site in range(sites):
    site_name = f"Site_{site + 1}"

    # Günlük trafik dalgası (gündüz artar, gece azalır)
    daily_wave = 180 * (np.sin(2 * np.pi * ((idx.hour - 7) / 24)) + 1)
    # Haftasonu etkisi (cumartesi-pazar)
    weekend_boost = 80 * ((idx.dayofweek >= 5).astype(int))
    # Gürültü
    noise = np.random.normal(0, 25, hours)

    users = np.clip(base_users[site] + daily_wave + weekend_boost + noise, 30, 900).astype(int)

    # Ortalama kullanıcı başı hız (Mb/sn)
    mbps_per_user = 2.5 + 0.7 * np.sin(2 * np.pi * idx.hour / 24)
    throughput = users * mbps_per_user + np.random.normal(0, 60, hours)
    throughput = np.clip(throughput, 50, None)

    # Parazit modelleme (komşu istasyon yükü etkisi)
    if site > 0:
        interference = 0.035 * data[site - 1]["users"].values
    else:
        interference = np.zeros(hours)

    # SINR: kullanıcı ve parazit etkisine göre
    sinr = 32 - 0.035 * users - 0.015 * interference + np.random.normal(0, 1.5, hours)
    sinr = np.clip(sinr, 8, 32)

    # Enerji tüketimi (baz yüküne orantılı)
    energy = energy_base[site] + 1.5 * users + np.random.normal(0, 10, hours)
    energy = np.clip(energy, 100, None)

    df_site = pd.DataFrame({
        "datetime": idx,
        "site_id": site_name,
        "users": users,
        "throughput_mbps": np.round(throughput, 2),
        "sinr_db": np.round(sinr, 2),
        "energy_w": np.round(energy, 2)
    })
    data.append(df_site)

# Tüm siteleri birleştir
df = pd.concat(data)
df.reset_index(drop=True, inplace=True)

# Kaydet
df.to_csv("5G_90gun_5site_veri.csv", index=False)
print("Veri Hazır: 5G_90gun_5site_veri.csv")

# Hızlı kontrol
print(df.head(10))
print(df.describe())
