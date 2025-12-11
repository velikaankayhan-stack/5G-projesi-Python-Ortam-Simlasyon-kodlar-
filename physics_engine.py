
# physics_engine.py
import numpy as np
import math

class PhysicsEngine:
    """
    Bu sınıf, 5G ağındaki sinyal yayılımını ve girişim (interference) 
    mekanizmalarını fiziksel formüllere dayalı olarak hesaplar.
    
    Kullanılan Yöntemler:
    - Log-Distance Path Loss Model (Şehir içi yayılım için)
    - Shannon-Hartley Kapasite Teoremi
    - Overlap-Based Interference Model (Çakışma tabanlı girişim)
    """

    def __init__(self, carrier_freq_mhz):
        self.freq_hz = carrier_freq_mhz * 1e6
        # Işık hızı
        self.c = 3e8

    def calculate_path_loss(self, distance_m, path_loss_exp=3.5):
        """
        Log-Distance Path Loss Modeli.
        Şehir içi ortamlarda sinyalin mesafeye bağlı güç kaybını hesaplar.
        """
        if distance_m <= 0: distance_m = 1.0 # Sıfıra bölünme hatası önlemi
        
        # Basitleştirilmiş Log-Normal Gölgeleme Modeli
        # PL(d) = PL(d0) + 10 * n * log10(d/d0)
        # PL(d0): Serbest uzay kaybı (Friis denklemi)
        lambda_wave = self.c / self.freq_hz
        pl_ref = 20 * np.log10(4 * np.pi * 1.0 / lambda_wave) # d0 = 1m
        
        loss_db = pl_ref + 10 * path_loss_exp * np.log10(distance_m)
        return loss_db

    def calculate_received_power(self, tx_power_watt, distance_m):
        """
        Alınan Sinyal Gücünü (RSRP) hesaplar.
        Pr = Pt - PathLoss
        """
        tx_power_dbm = 10 * np.log10(tx_power_watt * 1000)
        path_loss_db = self.calculate_path_loss(distance_m)
        rx_power_dbm = tx_power_dbm - path_loss_db
        
        return rx_power_dbm # dBm cinsinden

    def calculate_interference(self, current_bs, other_bs_list, user_distance_map):
        """
        Overlap-Based Interference Model:
        Diğer baz istasyonlarının frekans bantlarının, mevcut baz istasyonuyla
        ne kadar çakıştığını ve bunun yarattığı gürültüyü hesaplar.
        """
        total_interference_watt = 0.0
        
        current_bw_min = current_bs['center_freq'] - (current_bs['bandwidth'] / 2)
        current_bw_max = current_bs['center_freq'] + (current_bs['bandwidth'] / 2)

        for other in other_bs_list:
            if other['id'] == current_bs['id']: continue
            
            # Diğer istasyonun frekans aralığı
            other_bw_min = other['center_freq'] - (other['bandwidth'] / 2)
            other_bw_max = other['center_freq'] + (other['bandwidth'] / 2)
            
            # Kesişim (Overlap) hesabı
            overlap_min = max(current_bw_min, other_bw_min)
            overlap_max = min(current_bw_max, other_bw_max)
            overlap_amount = max(0, overlap_max - overlap_min)
            
            if overlap_amount > 0:
                # Çakışma Oranı (Overlap Ratio)
                overlap_ratio = overlap_amount / min(current_bs['bandwidth'], other['bandwidth'])
                
                # Girişim Gücü Hesabı
                # Diğer istasyonun kullanıcının olduğu noktadaki sinyal gücü
                dist_to_user = user_distance_map.get(other['id'], 500.0) # Varsayılan uzaklık
                rx_power_other_dbm = self.calculate_received_power(other['tx_power'], dist_to_user)
                rx_power_other_watt = (10**(rx_power_other_dbm/10)) / 1000
                
                # Girişim = (Gelen Güç) * (Çakışma Oranı) * (Ağırlık Faktörü)
                interference_watt = rx_power_other_watt * overlap_ratio * 0.8
                total_interference_watt += interference_watt
                
        return total_interference_watt

    def calculate_sinr(self, rx_power_dbm, interference_watt, bandwidth_hz, noise_figure_db=9.0):
        """
        SINR (Signal-to-Interference-plus-Noise Ratio) Hesabı.
        """
        # Termal Gürültü (Thermal Noise)
        k_boltzmann = 1.38e-23
        temp_kelvin = 290
        thermal_noise_watt = k_boltzmann * temp_kelvin * bandwidth_hz
        
        # Gürültü Faktörü eklenmiş toplam gürültü
        noise_factor = 10**(noise_figure_db/10)
        total_noise_watt = thermal_noise_watt * noise_factor
        
        # Pr (Watt)
        rx_power_watt = (10**(rx_power_dbm/10)) / 1000
        
        # SINR = S / (I + N)
        sinr_linear = rx_power_watt / (interference_watt + total_noise_watt)
        
        if sinr_linear <= 0: return -20.0 # Hata durumu için alt sınır
        
        sinr_db = 10 * np.log10(sinr_linear)
        return sinr_db

    def calculate_energy_consumption(self, tx_power_watt, active_time_hours):
        """
        Baz istasyonu enerji tüketimi hesabı.
        Sadece yayın gücü değil, donanım soğutma vb. dahil yaklaşık tüketim.
        P_total = N_trx * (P0 + Delta_p * P_out)
        Burada basitleştirilmiş model kullanıyoruz:
        """
        # Verimlilik faktörü ve sabit operasyonel yük
        base_load = 150.0 # Watt (Soğutma, işlemci vs sabit)
        efficiency_factor = 2.5 # Güç amplifikatörü verimsizliği
        
        total_power_draw = base_load + (tx_power_watt * efficiency_factor)
        energy_kwh = (total_power_draw * active_time_hours) / 1000.0
        return energy_kwh
