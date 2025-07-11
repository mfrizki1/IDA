import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import pandas as pd
import json
import os

CONFIG_FILE = "config.json"
# Ini adalah kolom tujuan standar di DMS kita. Pengguna akan memetakan ke daftar ini.
DESTINATION_COLUMNS = [
    "Tidak Digunakan",
    "Nomor Pesanan",
    "Nama Pelanggan",
    "SKU Produk",
    "Jumlah",
    "Nomor Telepon",
    "Tanggal Pesanan",
]


class MappingWizard(ctk.CTkToplevel):
    """Jendela wizard untuk memetakan kolom CSV."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Wizard Pemetaan Kolom")
        self.geometry("600x500")
        self.transient(parent)  # Membuat window ini selalu diatas window utama
        self.grab_set()  # Fokus input hanya ke window ini

        self.mapping_widgets = []

        # --- Frame Utama ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Frame Atas untuk tombol ---
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill="x", padx=5, pady=5)

        self.select_csv_button = ctk.CTkButton(
            self.top_frame, text="Pilih File CSV...", command=self.select_csv_file
        )
        self.select_csv_button.pack(side="left", padx=10)

        self.csv_path_label = ctk.CTkLabel(
            self.top_frame, text="belum ada file dipilih", text_color="gray", anchor="w"
        )
        self.csv_path_label.pack(side="left", fill="x", expand=True)

        # --- Frame Tengah untuk daftar mapping (bisa di scroll ) ---
        self.mapping_frame = ctk.CTkScrollableFrame(
            self.main_frame, label_text="Cocokkan Kolom Anda"
        )
        self.mapping_frame.pack(pady=10, padx=5, fill="both", expand=True)

        # -- Frame Bawah untuk tombol simpan ---
        self.bottom_frame = ctk.CTkFrame(self.main_frame)
        self.bottom_frame.pack(fill="x", padx=5, pady=5)

        self.save_button = ctk.CTkButton(
            self.bottom_frame,
            text="Simpan Konfigurasi",
            command=self.save_configuration,
            state="disabled",
        )
        self.save_button.pack(pady=10)

    def select_csv_file(self):
        """Membuka dialog untuk memilih file CSV dan memuat headernya."""
        file_path = filedialog.askopenfilename(
            title="Pilih file exported_order",
            filetypes=(("CSV Files", "*.csv"), ("All files", "*.*")),
        )
        if not file_path:
            return

        self.csv_path_label.configure(text=os.path.basename(file_path))

        try:
            df = pd.read_csv(file_path, nrows=0)  # Hanya baca header
            self.populate_mapping_ui(df.columns)
            self.save_button.configure(state="normal")
        except Exception as e:
            messagebox.showerror(
                "Error Membaca File",
                f"Tidak dapat membaca header dari file CSV.\n\nError: {e}",
            )

    def populate_mapping_ui(self, columns):
        """Membuat baris UI untuk setiap kolom dari CSV."""
        # Bersihkan frame sebelum mengisi
        for widget in self.mapping_frame.winfo_children():
            widget.destroy()
        self.mapping_widgets.clear()

        # Buat header table
        header_frame = ctk.CTkFrame(self.mapping_frame)
        header_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(
            header_frame, text="Kolom di File Anda", font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=15, pady=5, expand=True)
        ctk.CTkLabel(
            header_frame, text="Data untuk DMS", font=ctk.CTkFont(weight="bold")
        ).pack(side="right", padx=15, pady=5, expand=True)

        for col in columns:
            row_frame = ctk.CTkFrame(self.mapping_frame)
            row_frame.pack(fill="x", pady=2)

            label = ctk.CTkLabel(row_frame, text=col, anchor="w")
            label.pack(side="left", padx=15, pady=5, expand=True)

            combo = ctk.CTkComboBox(row_frame, values=DESTINATION_COLUMNS)
            combo.pack(side="right", padx=15, pady=5, expand=True)
            combo.set("Tidak Digunakan") # Nilai Default

            # Simpan referensi ke label dan combobox untuk dibaca saat menyimpan
            self.mapping_widgets.append({"source":col, "combo":combo})


    def save_configuration(self):
        """Membaca pilihan pengguna dan menyimpan ke config.json."""
        column_mappings = {}
        for item in self.mapping_widgets:
            source_col = item["source"]
            dest_col = item["combo"].get()

            if dest_col != "Tidak Digunakan":
                column_mappings[dest_col] = source_col

        if not column_mappings:
            messagebox.showwarning("Peringatan", "tidak ada kolom yang dipetakan. Konfigurasi tidak disimpan")
            return

        config_data = {"column_mappings": column_mappings}

        try: 
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
            messagebox.showinfo("Sukses", f"Konfigurasi berhasil disimpan ke '{CONFIG_FILE}'")
            self.destroy() # Tutup jendela wizard setelah berhasil menyimpan
        except Exception as e:
            messagebox.showerror("Error Menyimpan", f"Gagal menyimpan file konfigurasi.\n\nError: {e}")


class AutomationApp(ctk.CTk):
    """Jendela utama aplikasi"""
    def __init__(self):
        super().__init__()

        self.title("IDA.exe - Tahap 1")
        self.geometry("400x200")
        self.resizable(False, False)
        ctk.set_appearance_mode("System")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.label = ctk.CTkLabel(self.main_frame, text="IDA - Konfigurasi Otomatisasi", font=ctk.CTkFont(size=18, weight="bold"))
        self.label.pack(pady=10)

        self.config_button=ctk.CTkButton(self.main_frame, text="Buat / Edit Konfigurasi Kolom", command=self.open_mapping_wizard)
        self.config_button.pack(pady=20, padx=20)

    def open_mapping_wizard(self):
        wizard = MappingWizard(self)

def create_dummy_csv_for_testing():
    """Membuat file CSV dummy jika belum ada, untuk memudahkan testing."""
    file_name = "contoh_order_klien.csv"
    if not os.path.exists(file_name):
        sample_data = {
            'No Unik': ['INV-101', 'INV-102'],
            'Nama': ['PT Jaya Abadi', 'CV Mundur Keniscayaan'],
            'Kode Barang': ['BRG-XYZ-01', 'BRG-ABC-09'],
            'Pcs': [10, 5],
            'Alamat Kirim': ['Jl. Sudirman No. 1, Jakarta', 'Jl. Thamrin No. 2, Jakarta'],
            'Kontak': ['08123456789', '08987654321'],
            'Tgl Order': ['2025-07-10', '2025-07-11']
        }
        pd.DataFrame(sample_data).to_csv(file_name, index=False)
        print(f"'{file_name}' dibuat untuk testing.")

if __name__ == "__main__":
    create_dummy_csv_for_testing()
    app = AutomationApp()
    app.mainloop()

            

