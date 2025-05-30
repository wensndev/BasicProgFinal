#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sims 1960 - MS-DOS Edition
Bir terminal tabanlı hayat simülasyonu oyunu
"""

import sys
import os
import time
import traceback
import atexit
import argparse
from models.game import Game
from models.network import Network, SERVER_LOCK_FILE

# Uygulama kapanışında çağrılacak fonksiyon
def cleanup():
    """Uygulama kapanışında temizlik işlemleri"""
    # Kilit dosyasını temizle
    try:
        if os.path.exists(SERVER_LOCK_FILE):
            os.remove(SERVER_LOCK_FILE)
            print(f"\nSunucu kilit dosyası kaldırıldı: {SERVER_LOCK_FILE}")
    except Exception as e:
        print(f"\nKilit dosyası kaldırılırken hata: {e}")
    
    print("\nTemizlik işlemleri tamamlandı.")

def main():
    """Ana program fonksiyonu"""
    # Command line argümanlarını parse et
    parser = argparse.ArgumentParser(description='Sims 1960 - MS-DOS Edition')
    parser.add_argument('-dev', '--developer', action='store_true', 
                       help='Developer modunu aktif eder (hızlı yükleme)')
    args = parser.parse_args()
    
    try:
        # Çıkış işlemlerini kaydet
        atexit.register(cleanup)
        
        # Başlangıçta kilit dosyasını kontrol et ve temizle
        if os.path.exists(SERVER_LOCK_FILE):
            print(f"Eski sunucu kilit dosyası bulundu. Temizleniyor: {SERVER_LOCK_FILE}")
            os.remove(SERVER_LOCK_FILE)
        
        # Oyun nesnesini oluştur (dev mode ile)
        game = Game(dev_mode=args.developer)
        
        if args.developer:
            print("🚀 Developer modu aktif - Hızlı yükleme etkinleştirildi!")
        
        # Oyunu başlat
        game.start()
        
    except KeyboardInterrupt:
        print("\nOyundan çıkılıyor...")
        cleanup()  # Elle temizlik yap
        sys.exit(0)
    except Exception as e:
        print(f"\nBir hata oluştu: {e}")
        print("Hata detayları:")
        traceback.print_exc()
        cleanup()  # Elle temizlik yap
        sys.exit(1)

if __name__ == "__main__":
    main() 