import os
from typing import List, Tuple

def baca_file_papan(filepath: str) -> Tuple[List[List[str]], int]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' tidak dapat ditemukan!")
    
    with open(filepath, 'r') as file:
        lines = file.readlines()

    lines = [line.strip() for line in lines if line.strip()]

    if not lines:
        raise ValueError(f"File tidak boleh kosong!")
    
    papan = []
    for line in lines:
        row = list(line)
        papan.append(row)

    n = len(papan)
    if n == 0:
        raise ValueError(f"Papan gak boleh kosong!")
    
    return papan, n

def tulis_file_solusi(filepath: str, solusi: List[List[str]], waktu_eksekusi_ms: float, jumlah_kasus: int):
    with open(filepath, 'w') as file:
        for row in solusi:
            file.write(''.join(row) + '\n')

        file.write(f'\nWaktu pencarian: {waktu_eksekusi_ms:.2f} ms\n')
        file.write(f'Banyak kasus yang ditinjau: {jumlah_kasus} kasus\n')


def papan_ke_str(papan: List[List[str]]) -> str:
    return '\n'.join(''.join(row) for row in papan)


def txt_in_folder(folder: str) -> List[str]:
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if f.endswith('.txt')]


def cek_folder(folder: str):
    if not os.path.exists(folder):
        os.makedirs(folder)
