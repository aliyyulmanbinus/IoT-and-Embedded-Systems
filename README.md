# IoT and Embedded Systems — Camera Control Script

Script sederhana buat mengakses dan mengontrol kamera/webcam lewat OpenCV. Dibuat sebagai bagian dari Technical Test Full Stack Developer di Wrapstation.

---

## Cara Pakai

Pastikan Python dan pip sudah terinstall, lalu:

```bash
pip install opencv-python
python camera_app.py
```

Foto hasil capture otomatis tersimpan di folder `captures/`.

---

## Kontrol Keyboard

| Tombol | Fungsi |
|---|---|
| `SPACE` | Ambil foto |
| `B` (tahan) | Burst capture — foto terus sampai tombol dilepas |
| `+` / `=` | Naikkan brightness |
| `-` | Turunkan brightness |
| `R` | Ganti resolusi |
| `I` | Tampilkan/sembunyikan info overlay |
| `Q` | Keluar |

---

## Konfigurasi

Buka `camera_app.py`, cari bagian `main()`, dan ubah nilai di `CameraConfig`:

```python
config = CameraConfig(
    camera_index      = 0,      # 0 = webcam bawaan, 1 = kamera eksternal
    resolution_index  = 1,      # 0=nHD  1=VGA  2=HD  3=Full HD
    brightness        = 128,    # 0 sampai 255
    exposure          = None,   # None = auto, atau isi angka misal -6 (≈ 1/64s)
    gain              = None,   # None = auto, atau isi angka misal 50
    burst_interval_ms = 150,    # jeda antar foto saat burst (dalam ms)
)
```

### Pilihan Resolusi

| Index | Resolusi |
|---|---|
| 0 | 640 × 360 (nHD) |
| 1 | 640 × 480 (VGA) — default |
| 2 | 1280 × 720 (HD) |
| 3 | 1920 × 1080 (Full HD) |

### Catatan soal Exposure & Gain

Tidak semua webcam support kontrol manual untuk exposure dan gain — tergantung driver-nya. Kalau diisi tapi tidak berpengaruh, berarti kamera kamu tidak support fitur ini via DirectShow. Script tetap jalan normal dengan mode auto.

---

## Spesifikasi Sistem

| | |
|---|---|
| **OS** | Windows 11 Version 23H2 (OS Build 22631.6199) |
| **CPU** | Intel Core i5-7300HQ @ 2.50GHz |
| **RAM** | 16 GB |
| **GPU** | NVIDIA GeForce GTX 1050 + Intel HD Graphics 630 |
| **Python** | 3.10+ |
| **OpenCV** | 4.13.x |

---

## Struktur Folder

```
IoT-and-Embedded-Systems/
├── camera_app.py
├── requirements.txt
├── README.md
└── captures/           ← dibuat otomatis saat pertama kali capture
```

---

## Author

Aliyyulman Jihan