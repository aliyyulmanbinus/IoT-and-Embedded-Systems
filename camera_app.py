"""
Developed for: Wrapstation Technical Test - Soal No. 2 (IoT & Embedded Systems)

Kontrol:
  SPACE      : Ambil foto
  B (tahan)  : Burst capture
  + / -      : Atur brightness
  R          : Ganti resolusi
  I          : Tampilkan/sembunyikan info
  Q          : Keluar

Author   : Aliyyulman Jihan
Date     : 21/06/2026
Platform : Windows (OpenCV 4.8.0)
"""
 
import cv2
import os
import time
import ctypes
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
 
 
# Key codes untuk Windows API (GetAsyncKeyState)
VK_SPACE = 0x20
VK_B     = 0x42
VK_Q     = 0x51
 
 
def is_key_held(vk_code: int) -> bool:
    # Cek apakah tombol sedang ditahan saat ini.
    # cv2.waitKey tidak cukup untuk detect hold, jadi pakai Windows API langsung.
    return bool(ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000)
 
 
@dataclass
class CameraConfig:
    # Semua parameter kamera dikumpulkan di sini.
 
    camera_index: int = 0  # 0 = webcam utama, 1 = kamera kedua, dst.
 
    # Pilihan resolusi yang bisa di-cycle pakai tombol R
    resolution_presets: list = field(default_factory=lambda: [
        (640,  360),   # nHD
        (640,  480),   # VGA
        (1280, 720),   # HD
        (1920, 1080),  # Full HD
    ])
    resolution_index: int = 1  # default mulai di VGA
 
    # Shutter speed / exposure — nilai negatif = EV stop (misal -6 ≈ 1/64s)
    # Isi None biar auto, atau isi angka untuk manual.
    exposure: Optional[int] = None
 
    # ISO / gain — rentang biasanya 0-100, tergantung driver kamera
    # None = biarkan auto
    gain: Optional[int] = None
 
    brightness: int = 128       # 0 (gelap) sampai 255 (terang)
    output_dir: str = "captures"
    burst_interval_ms: int = 150  # jeda antar foto saat burst (~6 foto/detik)
 
 
class CameraApp:
 
    def __init__(self, config: CameraConfig):
        self.cfg = config
        self.cap: Optional[cv2.VideoCapture] = None
 
        self.show_info: bool        = True
        self.capture_count: int     = 0
        self.flash_msg: str         = ""
        self.flash_until: float     = 0.0
        self.last_burst_time: float = 0.0
 
        os.makedirs(self.cfg.output_dir, exist_ok=True)
 
    def _open_camera(self) -> bool:
        # CAP_DSHOW = DirectShow backend, paling stabil di Windows
        self.cap = cv2.VideoCapture(self.cfg.camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print(f"[ERROR] Kamera index {self.cfg.camera_index} tidak bisa dibuka.")
            return False
 
        self._apply_resolution()
        self._apply_brightness()
 
        if self.cfg.exposure is not None:
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # matikan auto exposure
            self.cap.set(cv2.CAP_PROP_EXPOSURE, self.cfg.exposure)
            print(f"[INFO] Exposure: {self.cfg.exposure}")
        else:
            print("[INFO] Exposure: AUTO")
 
        if self.cfg.gain is not None:
            self.cap.set(cv2.CAP_PROP_GAIN, self.cfg.gain)
            print(f"[INFO] Gain/ISO: {self.cfg.gain}")
        else:
            print("[INFO] Gain/ISO: AUTO")
 
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"[INFO] Resolusi aktual: {w}x{h}")
        return True
 
    def _apply_resolution(self):
        w, h = self.cfg.resolution_presets[self.cfg.resolution_index]
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
 
    def _apply_brightness(self):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.cfg.brightness)
 
    def _save_frame(self, frame) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        self.capture_count += 1
        filename = f"capture_{timestamp}_{self.capture_count:03d}.jpg"
        filepath = os.path.join(self.cfg.output_dir, filename)
        cv2.imwrite(filepath, frame)
        print(f"[CAPTURE] {filepath}")
        return filename
 
    def _single_capture(self, frame):
        filename = self._save_frame(frame)
        self._set_flash(f"Saved: {filename}")
 
    def _try_burst_capture(self, frame):
        # Hanya simpan frame kalau sudah lewat interval minimum,
        # supaya tidak spam disk terlalu cepat.
        now = time.time()
        elapsed_ms = (now - self.last_burst_time) * 1000
        if elapsed_ms >= self.cfg.burst_interval_ms:
            self._save_frame(frame)
            self.last_burst_time = now
 
    def _set_flash(self, message: str, duration: float = 2.0):
        self.flash_msg   = message
        self.flash_until = time.time() + duration
 
    def _draw_hud(self, frame):
        h, w    = frame.shape[:2]
        rw, rh  = self.cfg.resolution_presets[self.cfg.resolution_index]
        font    = cv2.FONT_HERSHEY_SIMPLEX
 
        # Bar atas - background semi-transparan
        bar = frame.copy()
        cv2.rectangle(bar, (0, 0), (w, 56), (0, 0, 0), -1)
        cv2.addWeighted(bar, 0.45, frame, 0.55, 0, frame)
 
        exp_str  = str(self.cfg.exposure) if self.cfg.exposure is not None else "AUTO"
        gain_str = str(self.cfg.gain)     if self.cfg.gain     is not None else "AUTO"
 
        cv2.putText(frame, f"RES: {rw}x{rh}  BRI: {self.cfg.brightness}",
                    (8, 20), font, 0.48, (0, 220, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"EXP: {exp_str}  ISO/GAIN: {gain_str}",
                    (8, 40), font, 0.48, (0, 220, 255), 1, cv2.LINE_AA)
 
        # Jumlah foto tersimpan (pojok kanan atas)
        saved_text = f"Saved: {self.capture_count}"
        (tw, _), _ = cv2.getTextSize(saved_text, font, 0.48, 1)
        cv2.putText(frame, saved_text, (w - tw - 8, 20),
                    font, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
 
        # Indikator burst aktif
        if is_key_held(VK_B):
            cv2.putText(frame, "● BURST", (w - 90, 40),
                        font, 0.48, (60, 60, 255), 1, cv2.LINE_AA)
 
        # Bar bawah - background semi-transparan untuk instruksi kontrol
        bar2 = frame.copy()
        cv2.rectangle(bar2, (0, h - 28), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(bar2, 0.45, frame, 0.55, 0, frame)
        cv2.putText(frame,
                    "SPACE:Foto  B:Burst(tahan)  +/-:Brightness  R:Resolusi  I:Info  Q:Keluar",
                    (8, h - 10), font, 0.38, (255, 255, 255), 1, cv2.LINE_AA)
 
        # Pesan sementara di tengah layar setelah capture
        if time.time() < self.flash_until:
            (fw, _), _ = cv2.getTextSize(self.flash_msg, font, 0.65, 2)
            fx = (w - fw) // 2
            fy = h // 2
            # shadow biar terbaca di background terang sekalipun
            cv2.putText(frame, self.flash_msg, (fx + 2, fy + 2),
                        font, 0.65, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, self.flash_msg, (fx, fy),
                        font, 0.65, (80, 220, 80), 2, cv2.LINE_AA)
 
    def run(self):
        if not self._open_camera():
            return
 
        window_name = "Camera Preview  |  Q = Keluar"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
 
        print("\nKontrol:")
        print("  SPACE     - Ambil foto")
        print("  B (tahan) - Burst capture")
        print("  + / -     - Brightness")
        print("  R         - Ganti resolusi")
        print("  I         - Toggle info")
        print("  Q         - Keluar\n")
 
        # Dipakai untuk edge-detection tombol SPACE (trigger sekali per tekan)
        space_was_held = False
 
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("[ERROR] Frame tidak terbaca, kamera mungkin terputus.")
                break
 
            # Burst jalan selama tombol B ditahan
            if is_key_held(VK_B):
                self._try_burst_capture(frame)
 
            # Render HUD ke salinan frame, bukan frame asli
            # (frame asli yang bersih dipakai untuk disimpan)
            display = frame.copy()
            if self.show_info:
                self._draw_hud(display)
 
            cv2.imshow(window_name, display)
 
            key = cv2.waitKey(1) & 0xFF
 
            if key == ord('q') or key == ord('Q') or is_key_held(VK_Q):
                break
 
            # Single capture — hanya trigger di momen tombol baru ditekan
            space_held_now = is_key_held(VK_SPACE)
            if space_held_now and not space_was_held:
                self._single_capture(frame)
            space_was_held = space_held_now
 
            if key in (ord('+'), ord('=')):
                self.cfg.brightness = min(255, self.cfg.brightness + 10)
                self._apply_brightness()
 
            elif key == ord('-'):
                self.cfg.brightness = max(0, self.cfg.brightness - 10)
                self._apply_brightness()
 
            elif key in (ord('r'), ord('R')):
                self.cfg.resolution_index = (
                    (self.cfg.resolution_index + 1) % len(self.cfg.resolution_presets)
                )
                self._apply_resolution()
                rw, rh = self.cfg.resolution_presets[self.cfg.resolution_index]
                self._set_flash(f"Resolusi: {rw}x{rh}")
 
            elif key in (ord('i'), ord('I')):
                self.show_info = not self.show_info
 
        self.cap.release()
        cv2.destroyAllWindows()
        print(f"\nSelesai. Total foto tersimpan: {self.capture_count}")
        print(f"Lokasi: ./{self.cfg.output_dir}/")
 
 
def main():
    # Ubah nilai di sini untuk konfigurasi kamera
    config = CameraConfig(
        camera_index      = 0,      # ganti ke 1 kalau pakai kamera eksternal
        resolution_index  = 1,      # 0=nHD  1=VGA  2=HD  3=FHD
        brightness        = 128,    # 0-255
        exposure          = None,   # None = auto, atau isi angka misal -6
        gain              = None,   # None = auto, atau isi angka misal 50
        output_dir        = "captures",
        burst_interval_ms = 150,    # jeda burst dalam ms
    )
 
    app = CameraApp(config)
    app.run()
 
 
if __name__ == "__main__":
    main()