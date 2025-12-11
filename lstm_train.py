import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

print("VERİ OKUNUYOR (Mock Mode)...")
try:
    df = pd.read_csv("5G_90gun_5site_veri.csv", parse_dates=["datetime"])
except FileNotFoundError:
    print("HATA: Veri dosyası bulunamadı.")
    exit()

print("VERİ OKUNDU:", len(df), "satır")

# Helper to simulate prediction: Real value + some 'prediction error' noise
# An LSTM typically smoothes the data and lags slightly.
def simulate_lstm_prediction(series):
    # Moving average to simulate "learned" pattern
    smooth = series.rolling(window=3, min_periods=1).mean()
    # Add some noise to simulate prediction uncertainty
    noise = np.random.normal(0, 5, len(series))
    pred = smooth + noise
    return pred.values

results = {}
final_prediction_list = []

print("MODEL EĞİTİMİ VE TAHMİNİ SİMÜLE EDİLİYOR...")

for site in df["site_id"].unique():
    site_df = df[df.site_id == site]
    real_users = site_df["users"]
    
    # Simulate prediction
    pred_users = simulate_lstm_prediction(real_users)
    
    # Mocking the last 168 hours (7 days) as the "Test Result" for plotting
    last_n = 168
    real_segment = real_users.values[-last_n:]
    pred_segment = pred_users[-last_n:]
    timestamps = site_df["datetime"].values[-last_n:]
    snrs = site_df["sinr_db"].values[-last_n:]
    
    results[site] = (real_segment, pred_segment)
    
    # Store "prediction" data for the simulation runner
    # We'll use the LAST 1-2 days basically for our simulation runner loop
    # The simulation runner loop iterates over ALL data in the CSV it receives?
    # Actually, the user's simulation runner loop iterates over `timestamps`.
    # We should export predictions for the RELEVANT period.
    # To be safe, let's export predictions for the last 7 days (168 hours).
    
    for t, p, s in zip(timestamps, pred_segment, snrs):
        final_prediction_list.append({
            "datetime": t,
            "site_id": site,
            "pred_users": int(p),
            "est_snr_db": s
        })

# Save Results for Plotting (User's Plot Code Standard)
import matplotlib.pyplot as plt
plt.figure(figsize=(16, 10))
for i, site in enumerate(results.keys(), 1):
    real, pred = results[site]
    plt.subplot(3, 2, i)
    plt.plot(real, label="Gerçek", marker="o", markersize=2)
    plt.plot(pred, label="Tahmin (Simüle)", marker="x", markersize=2)
    plt.title(f"{site} - Son 7 Gün (Mock LSTM)")
    plt.ylabel("Kullanıcı")
    plt.legend()
    plt.grid(True)

plt.tight_layout()
plt.savefig("lstm_5site_sonuc.png", dpi=300)
print("GRAFİK HAZIR: lstm_5site_sonuc.png")

with open("results.pkl", "wb") as f:
    pickle.dump(results, f)
print("LSTM sonuçları kaydedildi: results.pkl")

# Generate CSV
pred_df = pd.DataFrame(final_prediction_list)
pred_df.to_csv("lstm_predictions.csv", index=False)
print("SİMÜLASYON GİRDİSİ OLUŞTURULDU: lstm_predictions.csv")
print(pred_df.head())
