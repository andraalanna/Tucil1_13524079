from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
import time

@dataclass
class HasilSolusi:
    solusi : Optional[List[List[str]]]
    jumlah_kasus : int
    waktu_eksekusi_ms: float
    found: bool

class SolverUtama:
    def __init__(self, papan: List[List[str]], n: int):
        self.papan_awal = papan
        self.n =  n
        self.jumlah_kasus = 0

        self.lokasi_warna = self._bangun_lokasi_warna()

        self.warna_ada_queen = set()

        self.papan_solusi = [row[:] for row in papan]

    def _bangun_lokasi_warna(self) -> Dict[str, List[Tuple[int, int]]]:
        map_warna = {}
        for row in range(self.n):
            for col in range(self.n):
                warna = self.papan_awal[row][col]
                if warna not in map_warna:
                    map_warna[warna] = []
                map_warna[warna].append((row , col))

        return map_warna
    
    def _bisa_lanjut(self, row: int, col: int, posisi_queenn: List[Tuple[int, int]]) -> bool:
        warna = self.papan_awal[row][col]
        for rowQ, colQ in posisi_queenn:
            if rowQ == row or colQ == col:
                return False
            if (abs(rowQ - row) <= 1) and (abs(colQ - col) <= 1):
                return False
            if (self.papan_awal[rowQ][colQ] == warna):
                return False
        return True

    def _backtrack(self, row: int, posisi_queen: List[Tuple[int, int]], progress_callback: Optional[Callable] = None) -> bool:
        if row == self.n:
            return True 
        
        for col in range(self.n):
            self.jumlah_kasus += 1

            if self._bisa_lanjut(row, col, posisi_queen):
                warna = self.papan_awal[row][col]
                self.warna_ada_queen.add(warna)
                posisi_queen.append((row, col))
                self.papan_solusi[row][col] = '#'

                if progress_callback and self.jumlah_kasus % 100 == 0:
                    tampilin_progress_papan = self._papan_ke_str()
                
                if self._backtrack(row+1, posisi_queen, progress_callback):
                    return True 
                
                posisi_queen.pop()
                self.warna_ada_queen.remove(warna)
                self.papan_solusi[row][col] = self.papan_awal[row][col]
        return False
            
    def _papan_ke_str(self) -> str:
        return '\n'.join(''.join(row) for row in self.papan_solusi)

    
    def solve(self, progress_callback: Optional[Callable[[str, int], None]] = None) -> HasilSolusi:
        waktu_mulai = time.time()
        self.jumlah_kasus = 0
        posisi_queen = []
        result = self._backtrack(0, posisi_queen, progress_callback)

        waktu_eksekusi = (time.time() - waktu_mulai) * 1000 # s ke ms
        if result: 
            return HasilSolusi(
                solusi = self.papan_solusi,
                jumlah_kasus = self.jumlah_kasus,
                waktu_eksekusi_ms = waktu_eksekusi,
                found = True,
            )
        else:
            return HasilSolusi(
                solusi = None,
                jumlah_kasus = self.jumlah_kasus,
                waktu_eksekusi_ms = waktu_eksekusi,
                found = False,
            ) 
            
    def solve_visual_callback(self, visual_callback: Optional[Callable[[str, int, List[Tuple[int, int]]], None]] = None) -> HasilSolusi:
        waktu_mulai = time.time()
        self.jumlah_kasus = 0

        posisi_queen = []
        hasil = self._backtrack_visual(0, posisi_queen, visual_callback)

        waktu_eksekusi = (time.time() - waktu_mulai) * 1000

        if hasil:
            return HasilSolusi(
                solusi = self.papan_solusi,
                jumlah_kasus = self.jumlah_kasus,
                waktu_eksekusi_ms = waktu_eksekusi,
                found = True
            )
        else:
            return HasilSolusi(
                solusi = None,
                jumlah_kasus = self.jumlah_kasus,
                waktu_eksekusi_ms = waktu_eksekusi,
                found = False
            )


    def _backtrack_visual(self, row: int, posisi_queen: List[Tuple[int, int]], visual_callback: Optional[Callable] = None) -> bool:
        if row == self.n:
            return True
        
        for col in range(self.n):
            self.jumlah_kasus += 1

            if self._bisa_lanjut(row, col, posisi_queen):
                warna = self.papan_awal[row][col]
                posisi_queen.append((row, col))
                self.warna_ada_queen.add(warna)
                self.papan_solusi[row][col] = '#'

                if visual_callback:
                    board_snapshot = self._papan_ke_str()
                    visual_callback(board_snapshot, self.jumlah_kasus, posisi_queen[:])

                if self._backtrack_visual(row+1, posisi_queen, visual_callback):  # ✅ FIX: Parameter diperbaiki!
                    return True
                
                posisi_queen.pop()
                self.warna_ada_queen.remove(warna)
                self.papan_solusi[row][col] = self.papan_awal[row][col]

                if visual_callback:
                    board_snapshot  = self._papan_ke_str()
                    visual_callback(board_snapshot, self.jumlah_kasus, posisi_queen[:])

        return False
            

def validasi_ukuran_papan(papan: List[List[str]], n: int) -> Tuple[bool, str]:
    for i, row in enumerate(papan):
        if len(row) != n:
            return False, f"Row {i+1} punya panjang {len(row)}, seharusnya {n}"
        
    for row in range(n):
        for col in range(n):
            if not papan[row][col].isalpha() or not papan[row][col].isupper():  # ✅ FIX: Tambahkan ()
                return False, f"Papan tidak sesuai di posisi ({row}, {col}), hanya menerima huruf kapital A-Z!"

    return True, ""

def validasi_warna_papan(papan: List[List[str]], n: int) -> Dict[str, any]:
    semua_warna = set()
    map_jum_warna = {}

    for row in papan:
        for warna in row:
            semua_warna.add(warna)
            if warna not in map_jum_warna: 
                map_jum_warna[warna] = 1
            else:
                map_jum_warna[warna]+= 1

    jum_warna = len(semua_warna)
    
    mungkin_ada_solusi = (jum_warna >= n) 
    warning = ""
    if jum_warna < n:
        warning = (f"Papan cuman punya {jum_warna} warna tapi ada {n} queens. "
                  f"Tiap warna cuman bisa 1 queen, Tidak ada solusi")
    elif jum_warna > n:
        warning = (f"Papan punya {jum_warna} warna untuk {n} queens. "
                  f"{jum_warna - n} warna akan kosong. Kemungkinan aman, bisa ada solusi.")
        
    return {
        'jum_warna': jum_warna,
        'semua_warna': semua_warna,
        'map_jum_warna' : map_jum_warna,
        'mungkin_ada_solusi': mungkin_ada_solusi,
        'pesan_warning': warning
    }
    