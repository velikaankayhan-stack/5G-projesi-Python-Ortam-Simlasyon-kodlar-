import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_comparison():
    # Load data
    try:
        df = pd.read_csv("simulation_results_comparison.csv")
    except FileNotFoundError:
        print("CSV dosyası bulunamadı!")
        return

    # Set style
    sns.set(style="whitegrid")
    
    # Create Figure with 2 subplots
    fig, axes = plt.subplots(2, 1, figsize=(10, 10))
    
    # Plot 1: SINR Comparison
    axes[0].plot(df['Time'], df['SINR_Baseline_dB'], label='Baseline (Sabit 40W)', color='red', linestyle='--', marker='o')
    axes[0].plot(df['Time'], df['SINR_Optimized_dB'], label='Optimized (LSTM + Algoritma)', color='green', linewidth=2, marker='s')
    axes[0].set_title('SINR Karşılaştırması (Sinyal Kalitesi)', fontsize=14)
    axes[0].set_ylabel('SINR (dB)')
    axes[0].legend()
    # X-axis cleanup (show fewer labels if too many)
    axes[0].set_xticks(range(0, len(df), 4)) # Show every 4th label
    axes[0].tick_params(axis='x', rotation=45)

    # Plot 2: Energy Comparison
    axes[1].plot(df['Time'], df['Energy_Baseline_kWh'], label='Baseline (Sabit)', color='red', linestyle='--')
    axes[1].plot(df['Time'], df['Energy_Optimized_kWh'], label='Optimized (Dinamik)', color='blue', linewidth=2)
    axes[1].set_title('Enerji Tüketimi Karşılaştırması', fontsize=14)
    axes[1].set_ylabel('Enerji Tüketimi (kWh)')
    axes[1].set_xlabel('Zaman (Saat)')
    axes[1].legend()
    axes[1].set_xticks(range(0, len(df), 4))
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig("comparison_graphs.png")
    print("Grafik kaydedildi: comparison_graphs.png")

if __name__ == "__main__":
    plot_comparison()
