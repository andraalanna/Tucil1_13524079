# Tucil-STIMA-Brute-Force

## a. Penjelasan Program

Program ini adalah solver untuk **Colored Queen Problem** menggunakan algoritma brute force. Program menyelesaikan masalah penempatan ratu (queen) pada papan catur n×n dengan batasan khusus:
- Setiap ratu tidak boleh berada dalam satu baris atau kolom yang sama
- Setiap ratu tidak boleh berada dalam jarak 1 cell dari ratu lain (adjacency)
- Setiap ratu harus ditempatkan pada cell dengan warna yang memiliki ratu

Program dilengkapi dengan antarmuka grafis (GUI) untuk visualisasi hasil solusi.

## b. Requirement dan Instalasi

**Requirement:**
- Python 3.8 atau lebih tinggi
- Tkinter 
**Instalasi:**
1. Clone atau download repository
2. Tidak ada dependency eksternal yang perlu diinstall (hanya library standar Python)

## c. Cara Mengkompilasi

Program ini adalah program Python, tidak perlu dikompilasi. Cukup jalankan langsung dengan Python interpreter.

## d. Cara Menjalankan dan Menggunakan Program

**Menjalankan Program:**
```bash
cd Tuciil-STIMA-Brute-Force
cd src
python gui_visual.py
```
Atau jika sudah berada di folder `Tuciil-STIMA-Brute-Force`:
```bash
cd src
python gui_visual.py
```

**Cara Menggunakan:**
1. **Load File**: Klik tombol "Load File" untuk memilih file input papan (format: txt dengan grid warna)
2. **Solve**: Klik tombol "Solve" untuk menjalankan solver brute force
3. **Visualisasi**: Program akan menampilkan hasil solusi dengan animasi penempatan queen pada board
4. **Output**: Hasil solusi akan disimpan ke folder test, user bisa memilih untuk simpan dalam .txt atau dalam .png

**Format File Input:**
File input harus berisi grid n×n dengan karakter warna (A-Z), contoh untuk papan 4×4:
```
A B C A
B C A B
C A B C
A B C A
```

## e. Author / Identitas Pembuat
**Nama/NIM**: Angelina Andra Alanna/13524079
**Program**: Tuciil-STIMA-Brute-Force  
**Deskripsi**: Solver Colored Queens Problem dengan GUI Visualization  
**Tahun**: 2026
