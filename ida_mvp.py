# ------- Import Library -------
import json
import os
import threading
import time
import pandas as pd
import customtkinter as ctk
from pandas._config import config
import pyautogui
from tkinter import messagebox


# ------- Konfigurasi Awal -------
CONFIG_FILE = 'config.json'
SOURCE_CSV = 'exported_order.csv'
DEST_CSV = 'dms_order.csv'

class AutomationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IDA - MVP Version")
        self.geometry("400x300")
        self.resizable(False, False)
        ctk.set_appearance_mode("System")

        # ------- Frame Utama -------
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(padx=20,pady=20, fill="both", expand=True)

        # ------- Widgets -------
        self.label = ctk.CTkLabel(self.main_frame, text="IDA - MVP Version", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=10)

        self.button = ctk.CTkButton(self.main_frame, text="Run", command=self.run_automation)
        self.button.pack(pady=10)

        self.setup_button = ctk.CTkButton(self.main_frame, text="1. Buat File Contoh & Config", command=self.create_sample_config)
        self.setup_button.pack(pady=10)

        self.run_button = ctk.CTkButton(self.main_frame, text="2. Jalankan Otomatisasi", command=self.start_automation_thread, fg_color="#28a745", hover_color="#218838")
        self.run_button.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Status: Menunggu...", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_label.pack(pady=10)


    def create_sample_config(self):
        """Membuat file-file contoh untuk pertama kali."""
     
        self.status_label.configure(text="Status: Membuat file contoh...", text_color="oranges")
        self.update_idletasks()

        # 1. Buat file contoh config.json
        sample_data = {
            'order_id': ['ORD-1', 'ORDER-2'],
            'customer_name': ['Fisal', "rahma"],
            'product_sku': ['SKU-1', 'SKU-2'],
            'quantity': [1, 2],
            'price': [100000, 200000],
            'total_price': [100000, 200000]
        }

        pd.DataFrame(sample_data).to_csv(CONFIG_FILE, index=False)

        # 2. Buat file contoh exported_order.csv
        sample_order_data = {
            'order_id': ['ORD-1', 'ORDER-2'],
            'customer_name': ['Fisal', "rahma"],
            'product_sku': ['SKU-1', 'SKU-2'],
            'quantity': [1, 2],
            'price': [100000, 200000],
            'total_price': [100000, 200000]
        }
        config_data = {
            'column_mappings': {
                "Nomor Pesanan": "order_id",
                "Nama Pelanggan": "customer_name",
                "SKU": "product_sku",
                "Jumlah": "quantity",
                "Harga": "price",
                "Total Harga": "total_price"
            },
            "rpa_steps": [
                {
                    "action": "click",
                    "image": "notepad_file_menu.png",
                    "description": "Klik menu File pada Notepad"
                },
                {
                    "action": "click",
                    "image":"notepad_edit_menu.png",
                    "description": "Klik menu Edit pada Notepad"
                },
                {
                    "action": "type_from_csv",
                    "data_to_type":"Nomor Pesanan: {Nomor Pesanan}, Nama Pelanggan: {Nama Pelanggan}, SKU: {SKU}, Jumlah: {Jumlah}, Harga: {Harga}, Total Harga: {Total Harga}",
                }
            ]
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)



        
        self.status_label.configure(text="Status: File contoh berhasil dibuat!", text_color="green")
        messagebox.showinfo("Sukses", f"File '{SOURCE_csv}' dan '{CONFIG_FILE}' berhasil dibuat.\n\nSEKARANG, siapkan file gambar 'notepad_file_menu.png' dan 'notepad_edit_menu.png' sesuai instruksi.")

    def start_automation_thread(self):
        """Memulai proses otomisasi di thread terpisah agar GUI tidak freeze."""

        self.run_button.configure(state="disabled")
        self.status_label.configure(text="Status: Memulai otomisasi...", text_color="orange")

        # Jalankan di thread baru
        automation_thread = threading.Thread(target=self.run_automation_logic)
        automation_thread.daemon = True
        automation_thread.start()

def run_automation_logic(self):
        """Logika utama untuk transformasi data dan RPA."""
        try:
            # ... (kode sebelum RPA tetap sama) ...

            # --- Tahap 2: RPA Visual ---
            self.status_label.configure(text="Status: Menjalankan RPA...")
            messagebox.showinfo("Mulai RPA", "Otomatisasi akan dimulai dalam 3 detik. Pastikan aplikasi NOTEPAD sudah terbuka dan terlihat di layar.", icon='info')
            time.sleep(3)

            rpa_steps = config['rpa_steps']
            
            # Loop untuk setiap baris di file hasil transformasi
            for index, row in pd.read_csv(DEST_CSV).iterrows():
                # ===== PERUBAHAN DI SINI =====
                # Ganti baris ini:
                # pyautogui.alert(f'Akan memproses baris {index + 1}:\n{row["Nomor Pesanan"]}', 'Info Proses')
                # Menjadi baris ini:
                messagebox.showinfo('Info Proses', f'Akan memproses baris {index + 1}:\n{row["Nomor Pesanan"]}')
                # =============================
                
                for step in rpa_steps:
                    self.status_label.configure(text=f"Status: {step['description']}")
                    
                    if step['action'] == 'click':
                        try:
                            location = pyautogui.locateCenterOnScreen(step['image'], confidence=0.8)
                            if location:
                                pyautogui.click(location)
                                time.sleep(0.5)
                            else:
                                raise Exception(f"Gambar '{step['image']}' tidak ditemukan di layar.")
                        except Exception as e:
                            raise Exception(f"Gagal mencari gambar '{step['image']}'. Pastikan file ada dan terlihat jelas di layar.")
                    
                    elif step['action'] == 'type_from_csv':
                        text_to_type = step['data_to_type'].format(**row.to_dict())
                        pyautogui.typewrite(text_to_type, interval=0.05)
                        time.sleep(0.5)

            self.status_label.configure(text="Status: Otomatisasi Selesai!", text_color="green")
            messagebox.showinfo("Sukses", "Semua data berhasil diproses ke Notepad.")

        except Exception as e:
            self.status_label.configure(text=f"Status: Error!", text_color="red")
            messagebox.showerror("Error", str(e))
        finally:
            self.run_button.configure(state="normal")
    # def run_automation_logic(self):
    #     """Logika utama untuk transformasi data dan RPA."""

    #     # ---- Tahap 1: Transformasi Data ----
    #     self.status_label.configure(text="Status: Membaca config...")
    #     if not os.path.exists(CONFIG_FILE) or not os.path.exists(SOURCE_csv):
    #         raise FileNotFoundError("Config atau Source CSV tidak ditemukan. Klik tombol 1 dulu.")

    #     with open(CONFIG_FILE, 'r') as f:
    #         config = json.load(f)

    #     self.status_label.configure(text="Status: Mengubah data...")
    #     df_source = pd.read_csv(SOURCE_csv)
    #     df_dest = pd.DataFrame()

    #     for dest_col, source_col in config['column_mappings'].items():
    #         df_dest[dest_col] = df_source[source_col]

    #     df_dest.to_csv(DEST_csv, index=False)
    #     time.sleep(1)

    #     # ---- Tahap 2: RPA Visual ----
    #     self.status_label.configure(text="Status: Menjalankan RPA....")
    #     messagebox.showinfo("Mulai RPA", "Otomatisasi akan dimulai dalam 3 detik. Pastikan aplikasi NOTEPAD sudah terbuka dan terlihat dilayar", icon='info')
    #     time.sleep(3)

    #     rpa_steps = config['rpa_steps']

    #    # Loop untuk setiap baris di file hasil transformasi
    #     for index, row in pd.read_csv(DEST_csv).iterrows():
    #             pyautogui.alert(f'Akan memproses baris {index + 1}:\n{row["Nomor Pesanan"]}', 'Info Proses')
                
    #             for step in rpa_steps:
    #                 self.status_label.configure(text=f"Status: {step['description']}")
                    
    #                 if step['action'] == 'click':
    #                     try:
    #                         # Cari gambar di layar
    #                         location = pyautogui.locateCenterOnScreen(step['image'], confidence=0.8)
    #                         if location:
    #                             pyautogui.click(location)
    #                             time.sleep(0.5)
    #                         else:
    #                             raise Exception(f"Gambar '{step['image']}' tidak ditemukan di layar.")
    #                     except Exception as e:
    #                         raise Exception(f"Gagal mencari gambar '{step['image']}'. Pastikan file ada dan terlihat jelas di layar.")
                    
    #                 elif step['action'] == 'type_from_csv':
    #                     # Format string dengan data dari baris CSV saat ini
    #                     text_to_type = step['data_to_type'].format(**row.to_dict())
    #                     pyautogui.typewrite(text_to_type, interval=0.05)
    #                     time.sleep(0.5)

    #     self.status_label.configure(text="Status: Otomatisasi Selesai!", text_color="green")
    #     messagebox.showinfo("Sukses", "Semua data berhasil diproses ke Notepad.")

    #     except Exception as e:
    #         self.status_label.configure(text=f"Status: Error!", text_color="red")
    #         messagebox.showerror("Error", str(e))
    #     finally:
    #         self.run_button.configure(state="normal")


if __name__ == "__main__":
    app = AutomationApp()
    app.mainloop()


        
        