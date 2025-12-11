# simulation_runner.py
import pandas as pd
import numpy as np
import random
from config import *
from physics_engine import PhysicsEngine
import user_algo  # The user's specific algorithms

# --- VERİ YÜKLEME (DATA GENERATOR -> LSTM -> CSV) ---
def load_prediction_data():
    """
    LSTM modelinden (veya mock) üretilmiş 'lstm_predictions.csv' dosyasını okur.
    Beklenen Format: datetime, site_id, pred_users, est_snr_db
    """
    print(">>> Tahmin verileri yükleniyor: lstm_predictions.csv")
    try:
        df = pd.read_csv("lstm_predictions.csv", parse_dates=["datetime"])
    except FileNotFoundError:
        print("HATA: 'lstm_predictions.csv' bulunamadı! Lütfen önce lstm eğitimi kodunu çalıştırın.")
        exit()
        
    # İstasyonların konumları (x, y) - METRE cinsinden (Kullanıcı İsteği)
    locations = {
        "Site_1": (0, 0),
        "Site_2": (0, 400),
        "Site_3": (400, 400), 
        "Site_4": (400, 0),
        "Site_5": (200, 200)
    }
    
    # Internal ID mapping
    id_map = {
        "Site_1": 1, "Site_2": 2, "Site_3": 3, "Site_4": 4, "Site_5": 5
    }

    # Internal ID column
    df['_internal_id'] = df['site_id'].map(id_map)
    
    # Konumları ekle
    df['_pos_x'] = df['site_id'].map(lambda x: locations.get(x, (0,0))[0])
    df['_pos_y'] = df['site_id'].map(lambda x: locations.get(x, (0,0))[1])
    
    return df

# --- SİMÜLASYON DÖNGÜSÜ ---
def run_comparison_simulation():
    print(">>> 5G Optimizasyon Simülasyonu Başlatılıyor (Konumlar: Metre)...")
    
    # 1. Veri Hazırlığı
    traffic_df = load_prediction_data()
    physics = PhysicsEngine(CARRIER_FREQ_MHZ)
    
    results = []
    
    # Benzersiz zaman damgaları
    timestamps = traffic_df['datetime'].unique()
    timestamps = sorted(timestamps)
    
    print(f"Toplam {len(timestamps)} zaman adımı simüle edilecek.")
    
    for ts in timestamps:
        hourly_data = traffic_df[traffic_df['datetime'] == ts].copy()
        
        # --- DURUM TANIMLAMA (SNAPSHOT) ---
        bs_states_baseline = []
        bs_states_optimized = [] 
        
        # A) BASELINE SENARYOSU (Sabit)
        for _, row in hourly_data.iterrows():
            bs_states_baseline.append({
                'id': row['_internal_id'],
                'site_name': row['site_id'], 
                'tx_power': BASELINE_CONFIG['tx_power_watt'],
                'bandwidth': BASELINE_CONFIG['bandwidth_mhz'],
                'center_freq': CARRIER_FREQ_MHZ, 
                'users': row['pred_users'],
                'x': row['_pos_x'],
                'y': row['_pos_y']
            })
            
        # B) OPTIMIZED SENARYOSU (User Algorithm)
        # Adım 1: Kaynak Atama
        opt_data_rows = []
        for _, row in hourly_data.iterrows():
            req_bw = user_algo.needed_bw_mhz(row['pred_users'], row['est_snr_db'])
            req_power = user_algo.power_w(row['pred_users'], req_bw)
            
            opt_data_rows.append({
                'site_id': row['site_id'],
                'freq': CARRIER_FREQ_MHZ,
                'bw': req_bw,
                'power': req_power,
                'users': row['pred_users'],
                'snr': row['est_snr_db'],
                '_internal_id': row['_internal_id'],
                '_pos_x': row['_pos_x'],
                '_pos_y': row['_pos_y']
            })
            
        opt_df = pd.DataFrame(opt_data_rows)
        
        # Adım 2: Parazit Önleme
        opt_df_final = user_algo.parazit_onleyici(opt_df)
        
        for _, row in opt_df_final.iterrows():
            bs_states_optimized.append({
                'id': row['_internal_id'],
                'site_name': row['site_id'],
                'tx_power': row['power'],
                'bandwidth': row['bw'],
                'center_freq': row['freq'],
                'users': row['users'],
                'x': row['_pos_x'],
                'y': row['_pos_y']
            })

        # C) FİZİKSEL HESAPLAMALAR
        # Hedef Site: Site_1 (0,0)
        try:
            target_bl = next(x for x in bs_states_baseline if x['site_name'] == 'Site_1')
            target_opt = next(x for x in bs_states_optimized if x['site_name'] == 'Site_1')
        except StopIteration:
            continue
        
        # Kullanıcı Konumu (Metre)
        # Site 1'e 150m mesafede (150, 0) olsun
        user_pos_x = target_bl['x'] + 150.0
        user_pos_y = target_bl['y'] + 0.0
        
        user_dist_map_bl = {}
        user_dist_map_opt = {}
        
        # Mesafeleri hesapla (Metre)
        for bs in bs_states_baseline:
            d = np.sqrt((bs['x'] - user_pos_x)**2 + (bs['y'] - user_pos_y)**2)
            user_dist_map_bl[bs['id']] = max(1.0, d)
            
        for bs in bs_states_optimized:
             d = np.sqrt((bs['x'] - user_pos_x)**2 + (bs['y'] - user_pos_y)**2)
             user_dist_map_opt[bs['id']] = max(1.0, d)

        # Hedef istasyona gerçek uzaklık
        target_dist = user_dist_map_bl[target_bl['id']]

        # 1. Baseline Metrics
        int_watt_bl = physics.calculate_interference(target_bl, bs_states_baseline, user_dist_map_bl)
        rx_dbm_bl = physics.calculate_received_power(target_bl['tx_power'], target_dist)
        sinr_bl = physics.calculate_sinr(rx_dbm_bl, int_watt_bl, target_bl['bandwidth']*1e6)
        energy_bl = physics.calculate_energy_consumption(target_bl['tx_power'], 1) 
        
        # 2. Optimized Metrics
        int_watt_opt = physics.calculate_interference(target_opt, bs_states_optimized, user_dist_map_opt)
        rx_dbm_opt = physics.calculate_received_power(target_opt['tx_power'], target_dist)
        sinr_opt = physics.calculate_sinr(rx_dbm_opt, int_watt_opt, target_opt['bandwidth']*1e6)
        energy_opt = physics.calculate_energy_consumption(target_opt['tx_power'], 1)

        results.append({
            "Time": ts,
            "Site": "Site_1",
            "Users": target_bl['users'],
            "SINR_Baseline_dB": round(sinr_bl, 2),
            "SINR_Optimized_dB": round(sinr_opt, 2),
            "Energy_Baseline_kWh": round(energy_bl, 3),
            "Energy_Optimized_kWh": round(energy_opt, 3),
            "BW_Optimized_MHz": round(target_opt['bandwidth'], 1),
            "Power_Optimized_W": round(target_opt['tx_power'], 1),
            "Freq_Optimized_MHz": round(target_opt['center_freq'], 1)
        })

    # Kaydet
    results_df = pd.DataFrame(results)
    results_df.to_csv("simulation_results_comparison.csv", index=False)
    print(">>> Sonuçlar 'simulation_results_comparison.csv' dosyasına kaydedildi.")
    print("\nÖrnek Sonuçlar:")
    print(results_df.head())

if __name__ == "__main__":
    run_comparison_simulation()
