import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import pandas as pd
import json
import os

CONFIG_FILE = 'config.json'

class MappingWizard(ctk.CTkToplevel):
    """Jendela wizard yang bisa memuat, mengedit, dan menyimpan konfigurasi."""
    def __init__(self, parent, existing_config=None):
        super().__init__(parent)
        self.title("Wizard Pemetaan Kolom")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()

        self.mapping_widgets = []
        self.source_columns = []
        self.csv_path = ""

        # --- Frame Utama ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Frame Atas untuk tombol ---
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill="x", padx=5, pady=5)

        self.select_csv_button = ctk.CTkButton(self.top_frame, text="Pilih/Ganti File CSV...", command=self.select_csv_file)
        self.select_csv_button.pack(side="left", padx=10)

        self.csv_path_label = ctk.CTkLabel(self.top_frame, text="Belum ada file dipilih", text_color="gray", anchor="w")
        self.csv_path_label.pack(side="left", fill="x", expand=True)

        # --- Frame Tengah untuk daftar mapping (bisa di-scroll) ---
        self.mapping_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Cocokkan Kolom Anda")
        self.mapping_frame.pack(pady=10, padx=5, fill="both", expand=True)

        # --- Frame Bawah untuk tombol simpan ---
        self.bottom_frame = ctk.CTkFrame(self.main_frame)
        self.bottom_frame.pack(fill="x", padx=5, pady=5)

        self.save_button = ctk.CTkButton(self.bottom_frame, text="Simpan Konfigurasi", command=self.save_configuration, state="disabled")
        self.save_button.pack(pady=10)
        
        # --- PERUBAHAN 1: Logika untuk memuat config yang ada ---
        if existing_config and "last_csv_path" in existing_config:
            self.load_from_config(existing_config)
        else:
             ctk.CTkLabel(self.mapping_frame, text="Pilih file CSV untuk memulai.").pack(pady=20)

    def load_from_config(self, config):
        """Memuat ulang UI dari data config yang sudah ada."""
        self.csv_path = config["last_csv_path"]
        self.source_columns = config["source_columns"]
        
        if not os.path.exists(self.csv_path):
            messagebox.showwarning("File Tidak Ditemukan", f"File CSV terakhir di '{self.csv_path}' tidak ditemukan. Silakan pilih kembali.")
            self.csv_path_label.configure(text="File lama tidak ditemukan, pilih lagi.", text_color="orange")
            return

        self.csv_path_label.configure(text=os.path.basename(self.csv_path))
        self.populate_mapping_ui(self.source_columns, config.get("column_mappings", {}))
        self.save_button.configure(state="normal")


    def select_csv_file(self):
        file_path = filedialog.askopenfilename(
            title="Pilih file exported_order",
            filetypes=(("CSV Files", "*.csv"), ("All files", "*.*"))
        )
        if not file_path:
            return

        self.csv_path = file_path
        self.csv_path_label.configure(text=os.path.basename(self.csv_path))
        
        try:
            df = pd.read_csv(file_path, nrows=0)
            self.source_columns = df.columns.tolist()
            self.populate_mapping_ui(self.source_columns)
            self.save_button.configure(state="normal")
        except Exception as e:
            messagebox.showerror("Error Membaca File", f"Tidak dapat membaca header dari file CSV.\n\nError: {e}")

    def populate_mapping_ui(self, columns, existing_mappings=None):
        if existing_mappings is None:
            existing_mappings = {}
            
        for widget in self.mapping_frame.winfo_children():
            widget.destroy()
        self.mapping_widgets.clear()
        
        header_frame = ctk.CTkFrame(self.mapping_frame)
        header_frame.pack(fill="x", pady=2, padx=5)
        ctk.CTkLabel(header_frame, text="Kolom di File Anda", anchor="w",width=180,font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Nama Kolom Tujuan di DMS", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, fill="x")

        reversed_mappings = {source: dest for dest, source in existing_mappings.items()}

        for col in columns:
            row_frame = ctk.CTkFrame(self.mapping_frame)
            row_frame.pack(fill="x", pady=2, padx=5)

            label = ctk.CTkLabel(row_frame, text=col, anchor="w", width=180)
            label.pack(side="left", padx=10, pady=5)

            entry = ctk.CTkEntry(row_frame, placeholder_text="Ketik nama kolom tujuan...")
            entry.pack(side="left", padx=10, pady=5, fill="x", expand=True)
            
            if col in reversed_mappings:
                entry.insert(0, reversed_mappings[col])
            
            self.mapping_widgets.append({"source": col, "entry": entry})

    def save_configuration(self):
        column_mappings = {}
        for item in self.mapping_widgets:
            source_col = item["source"]
            dest_col = item["entry"].get()
            if dest_col:
                column_mappings[dest_col] = source_col
        
        if not column_mappings:
            messagebox.showwarning("Peringatan", "Tidak ada kolom yang dipetakan. Konfigurasi tidak disimpan.")
            return

        # --- PERUBAHAN 2: Menyimpan path CSV dan kolom sumber ---
        config_data = {
            "last_csv_path": self.csv_path,
            "source_columns": self.source_columns,
            "column_mappings": column_mappings
        }

        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
            messagebox.showinfo("Sukses", f"Konfigurasi berhasil disimpan/diperbarui di '{CONFIG_FILE}'!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error Menyimpan", f"Gagal menyimpan file konfigurasi.\n\nError: {e}")


class AutomationApp(ctk.CTk):
    """Jendela utama aplikasi."""
    def __init__(self):
        super().__init__()
        self.title("IDA.exe - Konfigurasi Cerdas")
        self.geometry("400x200")
        self.resizable(False, False)
        ctk.set_appearance_mode("System")
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.label = ctk.CTkLabel(self.main_frame, text="IDA - Konfigurasi Otomatisasi", font=ctk.CTkFont(size=18, weight="bold"))
        self.label.pack(pady=10)
        self.config_button = ctk.CTkButton(self.main_frame, text="Buat / Edit Konfigurasi Kolom", command=self.open_mapping_wizard)
        self.config_button.pack(pady=20, ipady=10)

    def open_mapping_wizard(self):
        # --- PERUBAHAN 3: Membaca config sebelum membuka wizard ---
        existing_config = None
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    existing_config = json.load(f)
            except (json.JSONDecodeError, IOError):
                messagebox.showerror("Error", f"File '{CONFIG_FILE}' rusak. Hapus file tersebut dan coba lagi.")
                return
        
        wizard = MappingWizard(self, existing_config=existing_config)


def create_dummy_csv_for_testing():
    file_name = "contoh_order_klien.csv"
    if not os.path.exists(file_name):
        sample_data = {'No Unik': ['INV-101'], 'Nama': ['PT Jaya Abadi'], 'Kode Barang': ['BRG-XYZ-01']}
        pd.DataFrame(sample_data).to_csv(file_name, index=False)
        print(f"'{file_name}' dibuat untuk testing.")

if __name__ == "__main__":
    create_dummy_csv_for_testing()
    app = AutomationApp()
    app.mainloop()