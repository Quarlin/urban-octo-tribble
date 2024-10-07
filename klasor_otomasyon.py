import os
import shutil
from pathlib import Path
import time
import psutil
import stat

# Masaüstü yolunu belirleyin
masaustu = Path.home() / 'Desktop'

def dosya_kullaniliyor_mu(dosya_yolu):
    """Belirtilen dosyanın kullanımda olup olmadığını kontrol eder."""
    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
        try:
            if proc.info['open_files']:
                for f in proc.info['open_files']:
                    if f.path == str(dosya_yolu):
                        return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def dosyalari_dosyalandir(kaynak_dizin):
    dosya_turleri = {
        'Resimler': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        'Belgeler': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx'],
        'Videolar': ['.mp4', '.mkv', '.mov', '.avi'],
        'Muzikler': ['.mp3', '.wav', '.ogg'],
        'Sıkıştırılmış': ['.zip', '.rar', '.7z'],
        'Yürütülebilir': ['.exe', '.bat', '.msi', '.com', '.cmd'],
        'Diğer': []
    }

    for dosya in os.listdir(kaynak_dizin):
        dosya_yolu = kaynak_dizin / dosya

        if dosya_yolu.is_file() and not dosya.startswith('.') and dosya_yolu.suffix:  # Gizli dosyaları ve uzantısı olmayanları atla
            proc = dosya_kullaniliyor_mu(dosya_yolu)
            if proc:
                print(f"{dosya} kullanımda olduğu için taşınamadı.")
                continue

            dosya_uzantisi = dosya_yolu.suffix.lower()
            hedef_klasor = 'Diğer'

            # Dosya türüne uygun klasörü bul
            for klasor, uzantilar in dosya_turleri.items():
                if dosya_uzantisi in uzantilar:
                    hedef_klasor = klasor
                    break

            hedef_dizin = kaynak_dizin / hedef_klasor
            hedef_dizin.mkdir(exist_ok=True)

            # Dosyayı ilgili klasöre taşı
            yeni_dosya_yolu = hedef_dizin / dosya
            sayac = 1
            while yeni_dosya_yolu.exists():
                yeni_dosya_adi = f"{dosya_yolu.stem}_{sayac}{dosya_yolu.suffix}"
                yeni_dosya_yolu = hedef_dizin / yeni_dosya_adi
                sayac += 1

            try:
                # Dosya izinlerini değiştirmeyi dene
                os.chmod(dosya_yolu, stat.S_IWRITE)
                shutil.move(str(dosya_yolu), str(yeni_dosya_yolu))
                print(f"{dosya} başarıyla {hedef_klasor} klasörüne taşındı.")
            except PermissionError:
                print(f"{dosya} taşınırken izin hatası oluştu. Yönetici olarak çalıştırmayı deneyin.")
            except Exception as e:
                print(f"{dosya} taşınırken bir hata oluştu: {e}")

if __name__ == '__main__':
    try:
        import psutil
    except ImportError:
        print("psutil modülü yüklü değil. Lütfen 'pip install psutil' komutuyla yükleyin.")
    else:
        dosyalari_dosyalandir(masaustu)
        print("Masaüstünüzdeki dosyalar türlerine göre sınıflandırıldı.")