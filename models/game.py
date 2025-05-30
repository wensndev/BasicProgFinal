import os
import sys
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from models.sim import Sim
from models.actions import Actions
from models.events import Events
from models.network import Network
from models.ui import SimsUI
from models.stats_display import StatsDisplay
from models.jobs import JobFactory
from models.gambling import GamblingGames
from rich.align import Align
from models.character_types import CharacterFactory
import inquirer

class Game:
    def __init__(self, dev_mode: bool = False):
        self.sim = None
        self.event_generator = None
        self.day_counter = 1
        self.quit_game = False
        self.quit_lobby = False  # Lobby'den çıkmak için flag
        self._game_started = False  # Multiplayer oyun başlama flag'i
        self._game_started_lock = threading.Lock()  # Thread-safe flag kontrolü
        self.is_multiplayer = False
        self.players = []  # Çok oyunculu mod için oyuncu listesi
        self.dev_mode = dev_mode  # Developer modu
        self.ui = SimsUI(self, dev_mode=dev_mode)
        self.stats_display = StatsDisplay(self)  # Yeni stats_display nesnesi
        self.actions = Actions(self)
        self.events = Events(self)
        self.gambling = GamblingGames(self.ui)  # Bahis oyunları sistemi
        self.network: Optional[Network] = None  # Ağ bağlantısı
        
        # Multiplayer özel özellikler
        self.is_host = False
        self.auto_sync_enabled = True
        self.last_player_update = time.time()
        self.player_update_interval = 2  # 2 saniyede bir oyuncu durumu güncelle
        
        # Sabit zaman (1960 yılında sabit bir zaman)
        self.game_time = datetime(1960, 1, 1, 6, 0)
    
    def format_time(self):
        """Oyun zamanını formatlar"""
        return self.game_time.strftime("%d %B %Y, %H:%M")
    
    def _dev_sleep(self, normal_duration: float):
        """Dev mode'a göre uyku süresi ayarlar"""
        if self.dev_mode:
            time.sleep(min(0.1, normal_duration * 0.1))  # Dev modda 10x hızlı, maksimum 0.1 saniye
        else:
            time.sleep(normal_duration)
    
    def start(self):
        """Oyunu başlatır"""
        # Intro ekranını göster
        self.ui.show_intro()
        
        # Ana menüyü göster
        self.show_main_menu()
        
        while not self.quit_game:
            if self.sim:
                self.handle_game_actions()
            else:
                break
    
    def show_main_menu(self):
        """Ana menüyü gösterir"""
        # Oyun modu seçimi
        mode = self.ui.show_main_menu()
        
        if mode == "Çıkış":
            self.quit_game = True
            sys.exit(0)
        
        # Ağ bağlantısı
        if mode == "Sunucu Başlat":
            # Aktif sunucu kontrolü (ek güvenlik için)
            if Network.is_server_active():
                self.ui.show_notification("Zaten aktif bir sunucu çalışıyor! İşlem iptal edildi.", "error")
                self._dev_sleep(2)
                self.show_main_menu()
                return
                
            self.is_multiplayer = True
            self.is_host = True
            self.network = Network(self, is_server=True)
            if not self.network.start_server():
                self._dev_sleep(2)
                self.show_main_menu()
                return
            # Sunucu lobisini göster
            self.show_multiplayer_lobby(is_server=True)
            return
        elif mode == "Sunucuya Bağlan":
            self.is_multiplayer = True
            self.is_host = False
            
            # IP ve Port girişi al
            connection_questions = [
                inquirer.Text('host',
                             message="Sunucu IP adresi (localhost için boş bırakın)",
                             default="localhost",
                             validate=lambda _, x: len(x.strip()) > 0 or "Boş olamaz!"),
                inquirer.Text('port',
                             message="Port numarası",
                             default="5000",
                             validate=lambda _, x: x.isdigit() and 1 <= int(x) <= 65535 or "Geçerli port numarası girin (1-65535)!")
            ]
            
            connection_answers = inquirer.prompt(connection_questions)
            if not connection_answers:
                self.show_main_menu()
                return
                
            host = connection_answers['host'].strip()
            port = int(connection_answers['port'])
            
            # Network objesini oluştur
            self.network = Network(self, is_server=False, host=host, port=port)
            
            # Bağlantı denemesi
            if not self.network.connect_to_server():
                self.ui.show_notification("Sunucuya bağlanılamadı! Ana menüye dönülüyor...", "error")
                self._dev_sleep(3)
                self.show_main_menu()
                return
                
            # İstemci lobisini göster
            self.show_multiplayer_lobby(is_server=False)
            return
        else:
            self.is_multiplayer = False
            self.is_host = False
            self.network = None
        
        # Oyun menüsü
        choice = self.ui.show_game_menu()
        
        if choice == "Geri Dön":
            if self.network:
                self.network.disconnect()
            self.show_main_menu()
        elif choice == "Yeni Oyun":
            self.create_new_sim() if not self.is_multiplayer else self.create_multiplayer_game()
        elif choice == "Kayıtlı Oyun Yükle":
            self.load_saved_game()
    
    def show_multiplayer_lobby(self, is_server=False):
        """Multiplayer lobisini gösterir ve yönetir - geliştirilmiş versiyon"""
        # Eğer henüz bir sim yoksa, karakter oluştur
        if not self.sim:
            if is_server:
                # Sunucu için de bir karakter oluştur
                self.create_multiplayer_game(auto_join=True)
            else:
                # İstemci için karakter oluştur
                self.create_multiplayer_game(auto_join=True)
        
        # Lobby güncelleme thread'i başlat
        lobby_thread = threading.Thread(target=self._lobby_updater)
        lobby_thread.daemon = True
        lobby_thread.start()
        
        # Lobby döngüsü
        self.quit_lobby = False  # Flag'i sıfırla
        self._game_started = False  # Oyun başlama flag'i
        
        while not self.quit_game and not self.quit_lobby:
            # Thread-safe _game_started kontrolü
            with self._game_started_lock:
                if self._game_started:
                    break
                    
            if not self.network or not self.network.is_connected():
                self.ui.show_notification("Ağ bağlantısı kesildi!", "error")
                self._dev_sleep(2)
                self.show_main_menu()
                return
            
            action = self.ui.show_multiplayer_lobby(is_server=is_server)
            
            # Oyun başladı sinyali geldi mi?
            if action == "Oyun Başladı":
                break
            
            if action == "Oyuncu Listesini Yenile":
                # Oyuncu listesi zaten otomatik yenileniyor, sadece ekranı yenile
                continue
            elif action == "Chat Gönder":
                # Chat mesajı gönderme
                message = self.ui.get_chat_input()
                if message and self.network and self.sim:
                    self.network.send_chat_message(self.sim.name, message)
            elif action == "Oyunu Başlat" and is_server:
                # Sunucu oyunu başlatmak istediğinde
                if len(self.network.players) > 1:  # En az 2 oyuncu
                    if self._start_multiplayer_game():
                        self._game_started = True  # Oyun başlatıldı flag'i
                        break  # Lobby döngüsünden çık
                else:
                    self.ui.show_notification("Oyunu başlatmak için en az 2 oyuncu olmalı!", "error")
                    self._dev_sleep(2)
            elif action == "Lobiden Ayrıl":
                # Bağlantıyı kapat ve ana menüye dön
                self._leave_lobby()
                return
        
        # Lobby'den çıktıktan sonra
        if self._game_started and not self.quit_game:
            # Oyun başlamışsa direkt oyun döngüsüne geç
            if not self.is_host:
                # İstemci için ek bildirim
                self.ui.show_notification("🎮 Multiplayer oyun başlıyor!", "success")
                self._dev_sleep(1)
            self._start_multiplayer_game_loop()
    
    def _lobby_updater(self):
        """Lobby'deki oyuncu listesini düzenli olarak günceller"""
        last_player_count = 0
        
        while (self.is_multiplayer and self.network and 
               self.network.is_connected() and not self.quit_lobby):
            # Sadece oyuncu sayısı değiştiğinde log yaz
            if hasattr(self.network, 'players') and self.network.players:
                current_count = len(self.network.players)
                if current_count != last_player_count:
                    player_names = list(self.network.players.keys())
                    print(f"🎮 Lobby güncellendi: {current_count} oyuncu - {player_names}")
                    last_player_count = current_count
            
            self._dev_sleep(2)  # 2 saniyede bir kontrol et
    
    def _start_multiplayer_game(self) -> bool:
        """Multiplayer oyunu başlatır"""
        try:
            if not self.is_host or not self.network:
                return False
                
            # Tüm oyunculara oyun başlama mesajı gönder
            start_message = {
                'type': 'game_start',
                'message': 'Oyun başlıyor!',
                'host': self.sim.name if self.sim else 'Sunucu'
            }
            self.network._broadcast(start_message)
            
            self.ui.show_notification("Multiplayer oyun başlatılıyor...", "info")
            self._dev_sleep(1)
            
            # Server için de oyun başlatma flag'ini ayarla (thread-safe)
            with self._game_started_lock:
                self._game_started = True
            return True
            
        except Exception as e:
            self.ui.show_notification(f"Oyun başlatılırken hata: {str(e)}", "error")
            return False
    
    def _start_multiplayer_game_loop(self):
        """Multiplayer oyun döngüsü"""
        # Auto-sync thread'i başlat
        if self.is_host:
            sync_thread = threading.Thread(target=self._auto_sync_players)
            sync_thread.daemon = True
            sync_thread.start()
        
        # Normal oyun döngüsüne geç ama multiplayer özelliklerle
        while not self.quit_game and self.sim and self.network and self.network.is_connected():
            self.handle_multiplayer_game_actions()
    
    def _auto_sync_players(self):
        """Oyuncu durumlarını otomatik olarak senkronize eder"""
        while (self.is_multiplayer and self.network and 
               self.network.is_connected() and self.auto_sync_enabled):
            
            current_time = time.time()
            if current_time - self.last_player_update > self.player_update_interval:
                if self.sim:
                    self._sync_player_state()
                self.last_player_update = current_time
            
            self._dev_sleep(1)
    
    def _sync_player_state(self):
        """Kendi oyuncu durumunu diğerlerine gönderir"""
        if not self.network or not self.sim:
            return
            
        player_data = {
            'mood': self.sim.mood,
            'energy': self.sim.energy,
            'hunger': self.sim.hunger,
            'hygiene': self.sim.hygiene,
            'social': self.sim.social,
            'money': self.sim.money,
            'job': self.sim.job,
            'job_level': getattr(self.sim, 'job_level', 1),
            'job_experience': getattr(self.sim, 'job_experience', 0),
            'job_satisfaction': getattr(self.sim, 'job_satisfaction', 50),
            'location': getattr(self.sim, 'location', 'Ev'),
            'activity': getattr(self.sim, 'current_activity', 'Boşta')
        }
        
        self.network.send_player_update(self.sim.name, player_data)
    
    def _refresh_multiplayer_state(self):
        """Multiplayer durumunu yeniler ve senkronize eder"""
        if not self.network or not self.sim:
            return
        
        # Kendi durumunu güncelle
        self.sim.calculate_mood()
        
        # Durumu diğer oyunculara gönder
        self._sync_player_state()
        
        # Başarı mesajı göster
        player_count = self.network.get_player_count()
        self.ui.show_notification(f"🔄 Durum yenilendi! {player_count} oyuncu bağlı.", "success")
    
    def _leave_lobby(self):
        """Lobby'den ayrılır"""
        if self.network:
            self.ui.show_notification("Lobiden ayrılıyorsunuz...", "info")
            self.network.disconnect()
            self.network = None
            self.is_multiplayer = False
            self.is_host = False
            self._dev_sleep(1)
        
        # Ana menüye dön
        self.show_main_menu()
    
    def _handle_game_start(self):
        """Client tarafında oyun başlatma mesajını işler"""
        self.ui.show_notification("🎮 Oyun başlıyor! Multiplayer moda geçiliyor...", "success")
        
        # Thread-safe flag ayarlama
        with self._game_started_lock:
            self._game_started = True
        
        # Kullanıcıya bilgi ver
        self.ui.console.print("\n[bright_green]✅ Devam etmek için enter'a basınız...[/bright_green]")
    
    def create_new_sim(self):
        """Yeni bir Sim oluşturur."""
        # UI üzerinden karakter oluşturma
        answers = self.ui.create_new_sim()
        
        # Karakter tipi factory kullanarak oluştur
        self.sim = CharacterFactory.create_character(
            answers['character_type'],
            answers['name'], 
            answers['gender'], 
            int(answers['age'])
        )
        
        # Yeni job sistemi ile meslek atama
        self.sim.change_job(answers['job'])
        self.sim.game_time = self.game_time  # Başlangıç zamanını ayarla
        
        # Karakter tipi bilgisini göster
        self.ui.show_notification(
            f"{answers['character_type']} tipinde {self.sim.name} oluşturuldu!", 
            "success"
        )

    def save_game(self):
        """Oyunu kaydeder."""
        if self.is_multiplayer:
            self.ui.show_notification("Multiplayer modda oyun kaydetme desteklenmiyor!", "warning")
            return
            
        filename = f"save_{self.sim.name}.json"
        success = self.sim.save()
        
        # Kaydetme onay ekranını göster
        self.ui.show_save_confirmation(filename, success)

    def load_saved_game(self):
        """Kaydedilmiş oyunu yükler."""
        # Kayıtlı oyunları bul
        saved_games = []
        for file in os.listdir("."):
            if file.startswith("save_") and file.endswith(".json"):
                saved_games.append(file[5:-5])  # "save_" ve ".json" kısmını çıkar
        
        # UI üzerinden kayıtlı oyun seçimi
        save_name = self.ui.load_saved_game(saved_games)
        
        if not save_name:
            # Ana menüye dön
            self.show_main_menu()
            return
        
        self.sim = Sim.load(save_name)
        if self.sim:
            # Sim'den yüklenen zamanı Game'e senkronize et
            if self.sim.game_time:
                self.game_time = self.sim.game_time
            else:
                # Eğer kayıtlı zamansız ise varsayılan zamanı ata ve senkronize et
                self.sim.game_time = self.game_time
            
            # Ruh halini güncelle (statların güncel görünmesi için)
            self.sim.calculate_mood()
            self.ui.show_notification(f"{self.sim.name} başarıyla yüklendi!", "success")
        else:
            self.ui.show_notification("Oyun yüklenirken bir hata oluştu!", "error")
            self._dev_sleep(2)
            self.show_main_menu()
    
    def handle_game_actions(self):
        """Tek oyunculu oyun aksiyonları"""
        while not self.quit_game and self.sim:
            # Ölüm kontrolü
            if not self.sim.is_alive:
                self._handle_death()
                return
                
            # Önce ekranı temizle
            self.ui.console.clear()
            
            # Oyuncu statlarını kompakt şekilde göster
            self.stats_display.display_stats(compact=True)
            
            # Eylem menüsünü göster
            action = self.ui.show_action_menu()
            
            self._process_game_action(action)
    
    def handle_multiplayer_game_actions(self):
        """Multiplayer oyun aksiyonları"""
        while not self.quit_game and self.sim and self.network and self.network.is_connected():
            # Ölüm kontrolü
            if not self.sim.is_alive:
                self._handle_multiplayer_death()
                return
                
            # Önce ekranı temizle
            self.ui.console.clear()
            
            # Multiplayer stats göster (diğer oyuncuları da dahil et)
            self.stats_display.display_multiplayer_stats(self.network.players)
            
            # Multiplayer eylem menüsünü göster
            action = self.ui.show_multiplayer_action_menu()
            
            # Emoji'leri temizle ve eylem ismini al
            clean_action = action
            if "🔄" in action:
                clean_action = "Yenile"
            elif "💬" in action:
                clean_action = "Chat Gönder"
            elif "📊" in action:
                clean_action = "Oyuncu Listesi"
            elif "🔌" in action:
                clean_action = "Bağlantıyı Kes"
            elif "🍽️" in action:
                clean_action = "Ye"
            elif "😴" in action or "Uyu" in action:
                clean_action = "Uyu"
            elif "🚿" in action:
                clean_action = "Banyo Yap"
            elif "💼" in action:
                clean_action = "İş"
            elif "👥" in action:
                clean_action = "Sosyalleş"
            elif "🎲" in action:
                clean_action = "Bahis Oyunları"
            elif "💾" in action:
                clean_action = "Oyunu Kaydet"
            
            if clean_action == "Yenile":
                # Ekranı yenile ve oyuncu durumunu senkronize et
                self._refresh_multiplayer_state()
                continue  # Döngüyü tekrar başlat
            elif clean_action == "Chat Gönder":
                message = self.ui.get_chat_input()
                if message and self.network and self.sim:
                    self.network.send_chat_message(self.sim.name, message)
            elif clean_action == "Oyuncu Listesi":
                self.ui.show_detailed_player_list(self.network.get_players_list())
            elif clean_action == "Bağlantıyı Kes":
                self._leave_multiplayer_game()
                return
            else:
                # Normal oyun aksiyonlarını işle
                self._process_game_action(clean_action)
    
    def _process_game_action(self, action: str):
        """Oyun aksiyonlarını işler (hem tek hem multiplayer için)"""
        if action == "Oyunu Kaydet":
            self.save_game()
        elif action == "Ana Menüye Dön":
            self._return_to_main_menu()
        elif action == "İş":
            self.handle_job_actions()
        elif action == "Ye":
            self.perform_action(self.actions.eat)
        elif action == "Uyu":
            self.perform_action(self.actions.sleep)
        elif action == "Banyo Yap":
            self.perform_action(self.actions.take_bath)
        elif action == "Sosyalleş":
            self.handle_social_actions()
        elif action == "Bahis Oyunları":
            self.handle_gambling_actions()
    
    def _return_to_main_menu(self):
        """Ana menüye dönüş işlemi"""
        if self.network:
            self.network.disconnect()
        
        # Ana menüyü göster
        mode = self.ui.show_main_menu()
        
        if mode == "Çıkış":
            self.quit_game = True
        elif mode in ["Sunucu Başlat", "Sunucuya Bağlan", "Tek Oyunculu"]:
            # Ağ bağlantısı işlemleri
            if mode == "Sunucu Başlat":
                self.is_multiplayer = True
                self.is_host = True
                self.network = Network(self, is_server=True)
                if not self.network.start_server():
                    self._dev_sleep(2)
                    return
                self.show_multiplayer_lobby(is_server=True)
            elif mode == "Sunucuya Bağlan":
                self.is_multiplayer = True
                self.is_host = False
                self.network = Network(self, is_server=False)
                if not self.network.connect_to_server():
                    self._dev_sleep(2)
                    return
                self.show_multiplayer_lobby(is_server=False)
            else:
                self.is_multiplayer = False
                self.is_host = False
                self.network = None
                
                # Oyun menüsü
                choice = self.ui.show_game_menu()
                
                if choice == "Geri Dön":
                    return
                elif choice == "Yeni Oyun":
                    self.create_new_sim()
                elif choice == "Kayıtlı Oyun Yükle":
                    self.load_saved_game()
    
    def _leave_multiplayer_game(self):
        """Multiplayer oyundan ayrılır"""
        self.ui.show_notification("Multiplayer oyundan ayrılıyorsunuz...", "info")
        if self.network:
            self.network.disconnect()
            self.network = None
        self.is_multiplayer = False
        self.is_host = False
        self._dev_sleep(1)
        self.show_main_menu()

    def handle_job_actions(self):
        """İş ile ilgili aksiyonları yönetir"""
        job_action = self.ui.show_job_menu()
        
        if job_action == "İşe Git":
            self.perform_action(self.actions.go_to_work)
        elif job_action == "İş Ara":
            self.perform_action(self.actions.find_job)
        elif job_action == "İstifa Et":
            self.perform_action(self.actions.quit_job)
    
    def handle_social_actions(self):
        """Sosyalleşme aksiyonlarını yönetir"""
        if self.is_multiplayer and self.network:
            # Multiplayer sosyal aksiyonlar
            social_action = self.ui.show_multiplayer_social_menu(self.network.get_players_list())
        else:
            # Tek oyunculu sosyal aksiyonlar
            social_action = self.ui.show_social_menu()
        
        if social_action == "Arkadaşlarla Buluş":
            self.perform_action(self.actions.meet_friends)
        elif social_action == "Flört Et":
            self.perform_action(self.actions.flirt)
        elif social_action == "Partiye Git":
            self.perform_action(self.actions.go_to_party)
        elif social_action.startswith("Oyuncuyla Sosyalleş:"):
            # Multiplayer özel: Belirli oyuncuyla sosyalleşme
            target_player = social_action.split(":")[1].strip()
            self._socialize_with_player(target_player)
    
    def _socialize_with_player(self, target_player: str):
        """Belirli bir oyuncuyla sosyalleşme"""
        if not self.network or not self.sim:
            return
            
        # Sosyalleşme mesajı gönder
        social_message = {
            'type': 'social_interaction',
            'from_player': self.sim.name,
            'to_player': target_player,
            'interaction_type': 'chat',
            'message': f"{self.sim.name} ile sosyalleşiyor"
        }
        
        self.network._broadcast(social_message)
        
        # Kendi social değerini artır
        self.sim.social = min(100, self.sim.social + 10)
        self.ui.show_notification(f"{target_player} ile sosyalleştiniz! (+10 Sosyal)", "success")
        
        # Multiplayer'da durumu güncelle
        self._sync_player_state()

    def perform_action(self, action_func):
        """Bir aksiyonu gerçekleştirir ve sonuçları gösterir"""
        # Karakter canlı mı kontrol et
        if not self.sim.can_perform_action():
            self.ui.show_notification("💀 Karakter öldü! Aksiyon yapılamaz.", "error")
            return
            
        # Aksiyon zaten devam ediyorsa işleme
        if self.events.is_action_in_progress:
            return
        
        # Aksiyonu çalıştır
        result = action_func(self.sim)
        
        # Aktivite ilerlemesi göster
        if isinstance(result, dict) and 'duration' in result:
            self.ui.show_activity_progress(
                result.get('name', 'Aktivite'), 
                result.get('duration', 3),
                lambda i, total: self.sim.update_stats_during_activity(result, i, total)
            )
            
            # Zamanı ilerlet
            hours_passed = result.get('duration', 0)
            self.game_time += timedelta(hours=hours_passed)
            self.sim.game_time = self.game_time  # Sim'in zamanını da güncelle
        
        # Çok oyunculu modda durumu güncelle
        if self.is_multiplayer and self.network:
            self._sync_player_state()
    
    def create_multiplayer_game(self, auto_join=False):
        """Çok oyunculu mod için yeni oyun oluşturur."""
        if not self.network:
            self.ui.show_notification("Ağ bağlantısı bulunamadı!", "error")
            self._dev_sleep(2)
            self.show_main_menu()
            return
            
        # UI üzerinden karakter oluşturma
        answers = self.ui.create_new_sim()
        
        # Karakter tipi factory kullanarak oluştur
        self.sim = CharacterFactory.create_character(
            answers['character_type'],
            answers['name'], 
            answers['gender'], 
            int(answers['age'])
        )
        
        # Yeni job sistemi ile meslek atama
        self.sim.change_job(answers['job'])
        self.sim.game_time = self.game_time
        
        # Oyuna katıl
        player_data = {
            'name': self.sim.name,
            'gender': self.sim.gender,
            'age': self.sim.age,
            'job': self.sim.job,
            'mood': self.sim.mood,
            'energy': self.sim.energy,
            'hunger': self.sim.hunger,
            'hygiene': self.sim.hygiene,
            'social': self.sim.social,
            'money': self.sim.money
        }
        
        if self.network.join_game(self.sim.name, player_data):
            self.ui.show_notification(f"{self.sim.name} oluşturuldu ve lobiye katıldı!", "success")
        else:
            self.ui.show_notification("Lobiye katılırken hata oluştu!", "error")
    
    def get_connected_players(self) -> List[Dict]:
        """Bağlı oyuncuların listesini döndürür"""
        if self.network:
            return self.network.get_players_list()
        return []
    
    def is_multiplayer_host(self) -> bool:
        """Bu oyuncu multiplayer host mu?"""
        return self.is_multiplayer and self.is_host
    
    def get_network_status(self) -> Dict:
        """Ağ bağlantısı durumunu döndürür"""
        if not self.network:
            return {'connected': False, 'player_count': 0, 'is_host': False}
        
        return {
            'connected': self.network.is_connected(),
            'player_count': self.network.get_player_count(),
            'is_host': self.is_host,
            'server_info': 'Host' if self.is_host else 'Client'
        }
    
    def __del__(self):
        """Oyun kapatılırken bağlantıları temizle"""
        if self.network:
            self.network.disconnect()

    def _handle_death(self):
        """Tek oyunculu modda ölümü işler"""
        death_info = self.sim.get_death_info()
        
        # Ölüm ekranını göster
        choice = self.ui.show_death_screen(death_info)
        
        # Emoji'yi temizle
        clean_choice = choice
        if "🔄" in choice:
            clean_choice = "Yeni Oyun Başlat"
        elif "📊" in choice:
            clean_choice = "Ölüm İstatistiklerini Kaydet"
        elif "🚪" in choice:
            clean_choice = "Ana Menüye Dön"
        elif "❌" in choice:
            clean_choice = "Oyundan Çık"
        
        if clean_choice == "Yeni Oyun Başlat":
            self.sim = None
            self.create_new_sim()
        elif clean_choice == "Ölüm İstatistiklerini Kaydet":
            self._save_death_statistics(death_info)
            self._handle_death()  # Tekrar ölüm ekranını göster
        elif clean_choice == "Ana Menüye Dön":
            self.sim = None
            self.show_main_menu()
        elif clean_choice == "Oyundan Çık":
            self.quit_game = True
            sys.exit(0)
    
    def _handle_multiplayer_death(self):
        """Multiplayer modda ölümü işler"""
        death_info = self.sim.get_death_info()
        
        # Diğer oyunculara ölüm haberini gönder
        if self.network:
            death_message = {
                'type': 'player_death',
                'player_name': self.sim.name,
                'death_reason': death_info['death_reason'],
                'death_time': death_info['death_time']
            }
            
            if self.is_host:
                self.network._broadcast(death_message)
            else:
                try:
                    self.network._send_to_socket(self.network.client_socket, death_message)
                except:
                    pass
        
        # Ölüm ekranını göster
        choice = self.ui.show_death_screen(death_info)
        
        # Emoji'yi temizle
        clean_choice = choice
        if "🔄" in choice:
            clean_choice = "Yeni Oyun Başlat"
        elif "📊" in choice:
            clean_choice = "Ölüm İstatistiklerini Kaydet"
        elif "🚪" in choice:
            clean_choice = "Ana Menüye Dön"
        elif "❌" in choice:
            clean_choice = "Oyundan Çık"
        
        if clean_choice == "Yeni Oyun Başlat":
            # Multiplayer'da yeni karakter oluştur
            self.sim = None
            self.create_multiplayer_game(auto_join=True)
        elif clean_choice == "Ölüm İstatistiklerini Kaydet":
            self._save_death_statistics(death_info)
            self._handle_multiplayer_death()  # Tekrar ölüm ekranını göster
        elif clean_choice == "Ana Menüye Dön":
            self._leave_multiplayer_game()
        elif clean_choice == "Oyundan Çık":
            if self.network:
                self.network.disconnect()
            self.quit_game = True
            sys.exit(0)
    
    def _save_death_statistics(self, death_info: dict):
        """Ölüm istatistiklerini kaydeder"""
        try:
            import json
            from datetime import datetime
            
            # Ölüm kayıtları dosyası
            filename = "death_records.json"
            
            # Mevcut kayıtları yükle
            death_records = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        death_records = json.load(f)
                except:
                    death_records = []
            
            # Yeni ölüm kaydını ekle
            death_record = {
                'timestamp': datetime.now().isoformat(),
                'player_name': death_info['name'],
                'death_reason': death_info['death_reason'],
                'death_time': death_info['death_time'],
                'age_at_death': death_info['age_at_death'],
                'final_money': death_info['final_stats']['money'],
                'final_job': death_info['final_stats']['job'],
                'relationships_count': death_info['final_stats']['relationships'],
                'game_mode': 'Multiplayer' if self.is_multiplayer else 'Tek Oyunculu'
            }
            
            death_records.append(death_record)
            
            # Dosyaya kaydet
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(death_records, f, ensure_ascii=False, indent=2)
            
            self.ui.show_notification("💾 Ölüm istatistikleri death_records.json dosyasına kaydedildi!", "success")
            
        except Exception as e:
            self.ui.show_notification(f"❌ Ölüm istatistikleri kaydedilirken hata: {str(e)}", "error")

    def handle_gambling_actions(self):
        """Bahis oyunları ile ilgili aksiyonları yönetir"""
        if not self.sim.can_perform_action():
            self.ui.show_notification("💀 Ölü karakterler bahis yapamaz!", "error")
            return
            
        gambling_action = self.ui.show_gambling_menu()
        
        if gambling_action == "Bahis Oyunu (Şans)" or gambling_action == "Şans":
            # Bahis miktarı al
            bet_amount = self.ui.get_bet_amount_input(self.sim.money)
            if bet_amount > 0:
                # Bahis oyununu oyna
                result = self.gambling.play_bet_game(bet_amount)
                if result['success']:
                    # Para güncelle
                    self.sim.money += result['winnings']
                    self.sim.money = max(0, self.sim.money)  # Negatif para olmayacak
                    
                    # Mood etkisi
                    if result['winnings'] > 0:
                        self.sim.mood = min(100, self.sim.mood + 10)  # Kazanınca mutlu
                    else:
                        self.sim.mood = max(0, self.sim.mood - 15)    # Kaybedince üzgün
                    
                    # Zaman geçişi
                    if 'duration' in result:
                        hours_passed = result['duration']
                        self.game_time += timedelta(hours=hours_passed)
                        self.sim.game_time = self.game_time
                        self.sim.advance_time(hours_passed)
                    
                    # Sonuç sonrası durumu güncelle
                    if self.is_multiplayer and self.network:
                        self._sync_player_state()
                        
                else:
                    self.ui.show_notification(result['message'], "error")
        
        elif gambling_action == "Slot Makinesi" or gambling_action == "Makinesi":
            # Slot makinesi için bahis miktarı al
            bet_amount = self.ui.get_bet_amount_input(self.sim.money)
            if bet_amount > 0:
                # Slot oyununu oyna
                result = self.gambling.play_slots(bet_amount)
                if result['success']:
                    # Para güncelle
                    self.sim.money += result['winnings']
                    self.sim.money = max(0, self.sim.money)  # Negatif para olmayacak
                    
                    # Mood etkisi
                    if result['winnings'] > 0:
                        # Büyük kazançlarda daha çok mutluluk
                        if result['winnings'] >= bet_amount * 5:
                            self.sim.mood = min(100, self.sim.mood + 20)  # Büyük kazanç
                        else:
                            self.sim.mood = min(100, self.sim.mood + 10)  # Normal kazanç
                    else:
                        self.sim.mood = max(0, self.sim.mood - 15)    # Kaybedince üzgün
                    
                    # Zaman geçişi
                    if 'duration' in result:
                        hours_passed = result['duration']
                        self.game_time += timedelta(hours=hours_passed)
                        self.sim.game_time = self.game_time
                        self.sim.advance_time(hours_passed)
                    
                    # Sonuç sonrası durumu güncelle
                    if self.is_multiplayer and self.network:
                        self._sync_player_state()
                        
                else:
                    self.ui.show_notification(result['message'], "error")
        
        elif gambling_action == "Bahis İstatistikleri" or gambling_action == "İstatistikleri":
            # Bahis istatistiklerini göster
            stats = self.gambling.get_gambling_stats()
            self.ui.show_gambling_stats(stats)
            
        # Devam etmek için bekle
        self._dev_sleep(1)
        input("\n[Devam etmek için Enter'a basın...]")