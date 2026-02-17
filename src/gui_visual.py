import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
import queue
import time
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import subprocess, tempfile, os


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solver_core import HasilSolusi,SolverUtama, validasi_warna_papan, validasi_ukuran_papan, cek_konek_warna
from io_code import baca_file_papan, tulis_file_solusi, cek_folder

class QueenGUIVisual:
    COLORS = {
    'A': '#E57373', 'B': '#F06292', 'C': '#BA68C8', 'D': '#9575CD',
    'E': '#7986CB', 'F': '#64B5F6', 'G': '#4FC3F7', 'H': '#4DD0E1',
    'I': '#4DB6AC', 'J': '#81C784', 'K': '#AED581', 'L': '#DCE775',
    'M': '#FFF176', 'N': '#FFD54F', 'O': '#FFB74D', 'P': '#FF8A65',
    'Q': '#A1887F', 'R': '#90A4AE', 'S': '#F48FB1', 'T': '#CE93D8',
    'U': '#B39DDB', 'V': '#9FA8DA', 'W': '#80DEEA', 'X': '#A5D6A7',
    'Y': '#FFE082', 'Z': '#FFAB91'
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("Penyelesaian Queens Berwarna + Animasi")
        self.root.geometry("1200x800") # formatnya ("lebarxtinggi+x+y") -> x + y itu kek lokasi
        root.minsize(1000,700)

        self.papan = None
        self.n = 0
        self.solver = None
        self.solver_thread = None
        self.is_solving = False
        self.animation_speed = 0.05

        self.update_queue = queue.Queue()

        self.cell_size = 50
        self.canvas_cells =  {}

        self._create_widgets()
        self._perbaikan_layout()

        self._process_queue()

    def _create_widgets(self):
        self.title_label = tk.Label(
            self.root,
            text = "Penyelesaian Queens Warna + Animasi",
            font = ("Arial", 16, "bold"),
            pady = 10
        )

        self.left_panel = ttk.Frame(self.root)
        self.input_frame = ttk.LabelFrame(self.left_panel, text = "Input", padding = 10)

        self.select_file_btn = ttk.Button(
            self.input_frame,
            text = "Pilih File Papan (.txt)",
            command=self._select_file
        )

        self.file_label = tk.Label(
            self.input_frame,
            text="Tidak ada file yang dipilih",
            fg = "gray",
            wraplength=250
        )

        self.info_frame = ttk.LabelFrame(self.left_panel, text = "Info Papan")

        self.info_text = tk.Text(
            self.info_frame,
            width = 35,
            height = 8,
            font = ("Arial", 9),
            wrap = tk.WORD
        )

        self.info_text.config(state=tk.DISABLED)

        self.speed_frame = ttk.LabelFrame(self.left_panel, text = "Kecepatan Animasi", padding = 10)

        self.speed_value_label = tk.Label(
            self.speed_frame,
            text = "Sedang",
            font = ("Arial", 9, "bold")
        )

        self.scale_kecepatan = ttk.Scale(
            self.speed_frame,
            from_ = 100,
            to = 1,  
            orient = tk.HORIZONTAL,
            command = self._update_speed 
        )

        self.scale_kecepatan.set(25)
        self.control_frame = ttk.LabelFrame(self.left_panel, text="Controls", padding = 10)

        self.solve_btn = ttk.Button(
            self.control_frame,
            text = "Solve dengan Animasi",
            command = self._start_solving,
            state = tk.DISABLED,
        )

        self.save_btn = ttk.Button(
            self.control_frame,
            text = "Save Solusi",
            command =self._save_solution,
            state = tk.DISABLED
        )

        self.stats_frame = ttk.LabelFrame(self.left_panel, text="Statistik", padding = 10)

        self.stats_text = tk.Text(
            self.stats_frame,
            width = 35,
            height = 6,
            font = ("Courier", 9),
            wrap = tk.WORD
        )

        self.stats_text.config(state=tk.DISABLED)

        self.right_panel = ttk.Frame(self.root)

        self.canvas_frame = ttk.LabelFrame(self.right_panel, text="Papan Visualisasi Real-Time", padding = 10)

        self.canvas_container = ttk.Frame(self.canvas_frame)

        self.canvas = tk.Canvas(
            self.canvas_container,
            bg = "white",
        )

        self.v_scrollbar = ttk.Scrollbar(
            self.canvas_container,
            orient=tk.VERTICAL,
            command = self.canvas.yview
        )

        self.h_scrollbar = ttk.Scrollbar(
            self.canvas_container,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview
        )

        self.canvas.configure(
            yscrollcommand = self.v_scrollbar.set,
            xscrollcommand = self.h_scrollbar.set
        )

        self.status_label = tk.Label(
            self.right_panel,
            text = "Ready",
            font = ("Arial", 10),
            anchor =tk.W,
            pady = 5

        )


        self.legenda_frame = ttk.LabelFrame(self.right_panel, text = "Legenda", padding=5)
        self.legenda_text = tk.Label(self.legenda_frame,
                                     text = "# = Tempat Ratu | ☐ = Kotak Kosong | Warna = Pembeda Wilayah",
                                     font = ("Arial", 9),
                                     justify=tk.LEFT
                                     )
    def _perbaikan_layout(self):
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky=tk.EW)
        
        self.left_panel.grid(row=1, column=0, padx=10, pady=5, sticky=tk.NSEW)
        
        self.input_frame.pack(fill=tk.X, pady=5)
        self.select_file_btn.pack(pady=5)
        self.file_label.pack(pady=5)
        
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        self.speed_frame.pack(fill=tk.X, pady=5)
        self.speed_value_label.pack()
        self.scale_kecepatan.pack(fill=tk.X, pady=5)
        self.speed_value_label.pack()
        
        self.control_frame.pack(fill=tk.X, pady=5)
        self.solve_btn.pack(fill=tk.X, pady=2)
        self.save_btn.pack(fill=tk.X, pady=2)
        
        self.stats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        self.right_panel.grid(row=1, column=1, padx=10, pady=5, sticky=tk.NSEW)
        
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.v_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.h_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        
        self.canvas_container.grid_rowconfigure(0, weight=1)
        self.canvas_container.grid_columnconfigure(0, weight=1)
        
        self.legenda_frame.pack(fill=tk.X, pady=5)
        self.legenda_text.pack()
        
        self.status_label.pack(fill=tk.X, pady=2)

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)  
        self.root.rowconfigure(1, weight=1)
    

    def _select_file(self):
        filepath = filedialog.askopenfilename(
            title = "Pilih File",
            initialdir="../test",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*") ]
        )

        if not filepath:
            return
        
        try:
            self.papan, self.n = baca_file_papan(filepath)
            
            self.cur_file = filepath
            is_valid, error_massage = validasi_ukuran_papan(self.papan, self.n)
            koneksi_valid, warna_terpisah = cek_konek_warna(self.papan)
            if not koneksi_valid:
                messagebox.showerror("Papan Tidak Valid", "Ada Warna yang terputus")
            if not is_valid:
                messagebox.showerror("Papan Tidak Valid", error_massage)
                return
            
            analisis_warna = validasi_warna_papan(self.papan, self.n)
            print(f"Hasil analisis warna papan: {analisis_warna}")

            self.file_label.config(
                text = f" {os.path.basename(filepath)}\n{self.n}x{self.n} papan",
                fg = "green"
            )

            self._display_info(analisis_warna)
            self._draw_board(self.papan, queens=None)

            self.solve_btn.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca file:\n{str(e)}")
    def _display_info(self, analisis_warna):

        self.info_text.config(state = tk.NORMAL)
        self.info_text.delete(1.0, tk.END)

        info = f"Ukuran Papan: {self.n} x {self.n} \n"
        info += f"Warna Unik : {analisis_warna['jum_warna']}\n"
        info += f"Semua Warna: {','.join(sorted(analisis_warna['semua_warna']))}\n\n"
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)

    def _update_speed(self, value):
        speed = float(value)

        if speed < 20:
            self.animation_speed = 0.001
            label = "Sangat Cepat"

        elif speed < 40:
            self.animation_speed = 0.01
            label = "Cepat"
        
        elif speed < 60:
            self.animation_speed = 0.05
            label = "Sedang"

        elif speed < 80:
            self.animation_speed = 0.1
            label = "Lambat"

        else:
            self.animation_speed = 0.2
            label = "Sangat Lambat"

        self.speed_value_label.config(text=label)

    def _draw_board(self, papan, queens=None):
        self.canvas.delete("all")
        self.canvas_cells.clear()

        if not papan:
            return
        n = len(papan)

        max_ukuran_canva = 600
        self.cell_size = min(50, max_ukuran_canva // n)

        for row in range(n):
            for col in range(n):
                # Koordinat tiap satuan kotak
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                char_warna = papan[row][col]
                fill_warna = self.COLORS.get(char_warna, 'white')

                cell_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill = fill_warna,
                    outline = 'black',
                    width = 1
                )

                self.canvas.create_text(
                    x1 + 5, y1 + 5,
                    text = char_warna,
                    font  =("Times New Roman", 6, "bold"),
                    anchor = tk.NW,
                    fill = 'black'
                )

                self.canvas_cells[(row, col)] = cell_id

        if queens:
            for row, col in queens:
                self._taruh_queen(row, col)

        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _taruh_queen(self, row, col):
        x = col * self.cell_size + self.cell_size //2
        y = row * self.cell_size + self.cell_size // 2

        self.canvas.create_text(
            x, y,
            text = "#",
            font = ("Arial", int(self.cell_size * 0.6)),
            tags ="queen"
        )

    def _update_board_visual(self, state_papan, posisi_queen):
        self._draw_board(self.papan, posisi_queen)

    def _start_solving(self):
        if self.is_solving:
            return
        
        self.is_solving = True
        self.result = None
        self.solve_btn.config(state=tk.DISABLED)
        self.select_file_btn.config(state=tk.DISABLED)

        self.status_label.config(text="Dalam proses penyelesaian")
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.config(state=tk.DISABLED)

        self.solver_thread = Thread(target=self._solver_worker,daemon=True )
        self.solver_thread.start()


    def _solver_worker(self):
        try:
            solver = SolverUtama(self.papan, self.n)
            def progress_callback(state_papan, kasus, posisi_queen):
                if not self.is_solving:
                    return
                
                self.update_queue.put(('visual_update', posisi_queen, kasus))
                time.sleep(self.animation_speed)

            result = solver.solve_visual_callback(progress_callback)
            self.update_queue.put(('done', result))

        except Exception as e:
            self.update_queue.put(('error', str(e)))

    def _process_queue(self):
        try:
            while True:
                msg = self.update_queue.get_nowait()

                if msg[0]=='visual_update':
                    _, posisi_queen, kasus = msg
                    self._update_board_visual(None, posisi_queen)
                    self._update_stats(kasus)

                elif msg[0] == 'done':
                    _, result = msg
                    self._finish_solving(result)
                
                elif msg[0] == 'error':
                    _, error = msg
                    self._handle_error(error)

        except queue.Empty:
            pass
        self.root.after(50, self._process_queue) 

    def _update_stats(self, kasus):
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, f"Ekspolore Kasus: {kasus:,}\n\n")
        self.stats_text.config(state=tk.DISABLED)

    def _finish_solving(self, result: HasilSolusi):
        self.is_solving = False
        self.result = result

        self.solve_btn.config(state=tk.NORMAL)
        self.select_file_btn.config(state=tk.NORMAL)

        if result.found:
            self.status_label.config(text="Solusi ditemukan!")

            posisi_queen = []
            for row in range(self.n):
                for col in range(self.n):
                    if result.solusi[row][col]=="#":
                        posisi_queen.append((row,col))

            self._draw_board(self.papan, posisi_queen)
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            stats = f"SELESAI!\n\n"
            stats += f"Time: {result.waktu_eksekusi_ms:.2f} ms\n"
            stats += f"Cases: {result.jumlah_kasus:,}\n\n"
            stats += f"Queens placed: {self.n}"
            self.stats_text.insert(1.0, stats)
            self.stats_text.config(state=tk.DISABLED)
            
            self.save_btn.config(state=tk.NORMAL)
            messagebox.showinfo("SUSKES!!!", f"DITEMUKAN SOLUSI!\n\nWaktu Pencarian: {result.waktu_eksekusi_ms:.3f} ms\n Banyak Kasus yang Ditinjau {result.jumlah_kasus} kasus.")

        else:
            self.status_label.config(text="Tidak Ditemukan Solusi")
            
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            stats = f"TIDAK ADA SOLUSI!\n"
            stats += f"Time: {result.waktu_eksekusi_ms:.2f} ms\n"
            stats += f"Cases: {result.jumlah_kasus:,}\n\n"
            stats += "Puzzle ini tidak dapat diselesaikan!\nTidak ada solusi."
            self.stats_text.insert(1.0, stats)
            self.stats_text.config(state=tk.DISABLED)
            
            messagebox.showwarning("Tidak ada Solusi!!!", f"Tidak ditemukan solusi\n\nWaktu Pencarian: {result.waktu_eksekusi_ms:.3f} ms\n Banyak Kasus yang Ditinjau {result.jumlah_kasus} kasus.")
    
    def _handle_error(self, error_msg: str):
        self.is_solving=False

        self.solve_btn.config(state=tk.NORMAL)
        self.select_file_btn.config(state=tk.NORMAL)
        
        self.status_label.config(text="Terjadi Error")
        messagebox.showerror("Error", f"Solver error:\n{error_msg}")

    def _save_solution(self):
        if not self.result or not self.result.found:
            messagebox.showwarning("Peringatan", "Belum ada solusi untuk disimpan!")
            return
        
        choice = messagebox.askquestion(
            "Format File",
            "Simpan sebagai:\n\nYes = Text (.txt)\nNo = Gambar (.png)"
        )
        
        if choice == 'yes':
            filepath = filedialog.asksaveasfilename(
                title="Simpan Solusi",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            
            if not filepath:
                return
            
            try:
                from io_code import tulis_file_solusi
                tulis_file_solusi(
                    filepath,
                    self.result.solusi,
                    self.result.waktu_eksekusi_ms,
                    self.result.jumlah_kasus
                )
                messagebox.showinfo("Berhasil", f"Solusi disimpan ke:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan:\n{str(e)}")
        
        else:
            filepath = filedialog.asksaveasfilename(
                title="Simpan Gambar",
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")]
            )
            
            if not filepath:
                return
            
            try:
                self._save_canvas_screenshot(filepath)

                messagebox.showinfo("Berhasil", f"Gambar disimpan ke:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan gambar:\n{str(e)}")
                
    def _save_canvas_screenshot(self, filepath: str):
        n = self.n
        scale = 2
        cell = self.cell_size * scale
        img_w = n * cell
        img_h = n * cell

        img = Image.new("RGB", (img_w, img_h), "white")
        draw = ImageDraw.Draw(img)

        try:
            font_label = ImageFont.truetype("arialbd.ttf", int(cell * 0.2))
            font_queen = ImageFont.truetype("arialbd.ttf", int(cell * 0.7))
        except:
            font_label = ImageFont.load_default()
            font_queen = font_label

        queen_positions = {
            (int(self.canvas.coords(q)[1] // self.cell_size),
            int(self.canvas.coords(q)[0] // self.cell_size))
            for q in self.canvas.find_withtag("queen")
        }

        for row in range(n):
            for col in range(n):
                x1, y1 = col * cell, row * cell
                x2, y2 = x1 + cell, y1 + cell

                fill = self.COLORS.get(self.papan[row][col], "white")
                draw.rectangle([x1, y1, x2, y2], fill=fill, outline="black")

                draw.text((x1 + 5, y1 + 5),
                        self.papan[row][col],
                        fill="black",
                        font=font_label)

                if (row, col) in queen_positions:
                    draw.text((x1 + cell//2, y1 + cell//2),
                            "#",
                            fill="black",
                            font=font_queen,
                            anchor="mm")

        img.save(filepath)

def main():

    root = tk.Tk()
    app = QueenGUIVisual(root)
    root.mainloop()

if __name__ == "__main__":
    main()