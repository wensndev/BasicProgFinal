import os
import time
import inquirer
import pyfiglet
from datetime import datetime
from typing import List, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.align import Align
from rich.style import Style
from rich.box import ROUNDED, HEAVY

class SimsUI:
    def __init__(self, game, dev_mode: bool = False):
        self.game = game
        self.console = Console()
        self.is_showing_menu = False
        self.notification = None
        self.notification_time = None
        self.dev_mode = dev_mode  # Developer modu
        
        # Renk stilleri
        self.styles = {
            "title": Style(color="bright_white", bold=True),
            "header": Style(color="bright_cyan", bold=True),
            "normal": Style(color="bright_white"),
            "highlight": Style(color="bright_yellow", bold=True),
            "good": Style(color="bright_green"),
            "warning": Style(color="bright_yellow"),
            "danger": Style(color="bright_red", bold=True),
            "info": Style(color="bright_blue"),
            "money": Style(color="bright_green", bold=True),
            "time": Style(color="bright_magenta"),
        }
        
    def show_intro(self):
        """EA logosu ile oyun başlangıç ekranını gösterir"""
        self.console.clear()
        
        # EA logosu
        ea_logo = pyfiglet.figlet_format("SEA GAMES", font="big")
        self.console.print(Align.center(ea_logo, vertical="middle"), style="bright_blue")
        self.console.print(Align.center("[bright_white]challenge Timuçin hoca[/bright_white]", vertical="middle"))
        
        if self.dev_mode:
            # Dev modda hızlı geçiş
            self.console.print(Align.center("[bright_yellow]🚀 DEV MODE - Hızlı Yükleme[/bright_yellow]", vertical="middle"))
            time.sleep(0.1)
        else:
            time.sleep(1)
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
        ) as progress:
            task = progress.add_task("[cyan]Yükleniyor...", total=100)
            for i in range(101):
                if self.dev_mode:
                    time.sleep(0.001)  # Dev modda çok hızlı
                else:
                    time.sleep(0.02)
                progress.update(task, completed=i)
                
        if self.dev_mode:
            time.sleep(0.1)
        else:
            time.sleep(0.5)
        self.console.clear()
        
        # Sims logosu
        sims_logo = pyfiglet.figlet_format("SIMS 1960", font="slant")
        self.console.print(Align.center(sims_logo, vertical="middle"), style="bright_yellow")
        self.console.print(Align.center("[bright_white]MS-DOS Edition[/bright_white]", vertical="middle"))
        
        if self.dev_mode:
            time.sleep(0.2)
        else:
            time.sleep(2)
        
    def show_notification(self, message, style="info", duration=3):
        """Ekranın altında geçici bildirim gösterir"""
        self.notification = message
        self.notification_style = style
        self.notification_time = datetime.now()
        
        # Dev mode'da bildirimleri daha kısa göster
        if self.dev_mode:
            self.notification_duration = min(0.5, duration * 0.2)
        else:
            self.notification_duration = duration
        
        # Konsola da yazdır
        style_map = {
            "info": "bright_blue",
            "success": "bright_green", 
            "warning": "bright_yellow",
            "error": "bright_red"
        }
        style_code = style_map.get(style, "bright_white")
        self.console.print(f"[{style_code}]{message}[/{style_code}]")
        
    def show_main_menu(self):
        """Ana menüyü gösterir"""
        self.console.clear()
        
        # Sims logosu
        sims_logo = pyfiglet.figlet_format("SIMS 1960", font="slant")
        self.console.print(Align.center(sims_logo, vertical="middle"), style="bright_yellow")
        
        # Eğer aktif bir sim varsa, durumunu göster
        if self.game.sim:
            # StatsDisplay sınıfını kullanarak detaylı statları göster
            self.game.stats_display.display_stats(compact=False)
        
        # Aktif sunucu kontrolü
        from models.network import Network
        
        # Oyun modu seçimi
        mode_choices = [
            "Tek Oyunculu",
            "Sunucu Başlat",
            "Sunucuya Bağlan",
            "Çıkış"
        ]
        
        mode_questions = [
            inquirer.List('mode',
                         message="Oyun modunu seçin:",
                         choices=mode_choices),
        ]
        
        self.console.print(Panel(
            "[bright_white]MS-DOS Edition[/bright_white]",
            border_style="bright_yellow",
            box=ROUNDED
        ))
        
        # Eğer aktif bir sunucu varsa, uyarı göster
        if Network.is_server_active():
            self.console.print(Panel(
                "[bright_red]DİKKAT: Zaten aktif bir sunucu çalışıyor! 'Sunucu Başlat' seçeneği kullanılamaz.[/bright_red]",
                border_style="bright_red",
                box=ROUNDED
            ))
        
        mode_answer = inquirer.prompt(mode_questions)
        selected_mode = mode_answer['mode']
        
        # Eğer sunucu başlat seçilirse ve aktif sunucu varsa, hata mesajı göster
        if selected_mode == "Sunucu Başlat" and Network.is_server_active():
            self.console.clear()
            self.console.print(Panel(
                "[bright_red]HATA: Zaten aktif bir sunucu çalışıyor![/bright_red]\n\n"
                "[bright_yellow]Aynı anda sadece bir sunucu çalıştırabilirsiniz.[/bright_yellow]\n"
                "[bright_white]Mevcut sunucuyu kapatmak için önce o sunucudan çıkmanız gerekiyor.[/bright_white]",
                title="Sunucu Hatası",
                border_style="bright_red",
                box=ROUNDED
            ))
            time.sleep(3)
            return self.show_main_menu()
            
        return selected_mode
        
    def show_game_menu(self):
        self.console.clear()
        """Oyun menüsünü gösterir"""
        choices = [
            "Yeni Oyun",
            "Kayıtlı Oyun Yükle",
            "Geri Dön"
        ]
        
        self.console.print(Panel(
            f"[bold]{'Çok' if self.game.is_multiplayer else 'Tek'} Oyunculu Mod[/bold]", 
            border_style="bright_cyan",
            box=ROUNDED
        ))
        
        questions = [
            inquirer.List('choice',
                         message="",
                         choices=choices),
        ]
        
        answer = inquirer.prompt(questions)
        return answer['choice']
        
    def create_new_sim(self):
        """Yeni bir Sim oluşturma arayüzü"""
        self.console.clear()
        
        self.console.print(Panel(
            "[bold]Yeni Karakter Oluştur[/bold]",
            border_style="bright_green",
            box=ROUNDED
        ))
        
        questions = [
            inquirer.Text('name', message="Karakterinizin adı nedir?"),
            inquirer.List('gender',
                          message="Karakterinizin cinsiyeti nedir?",
                          choices=["Erkek", "Kadın", "Diğer"]),
            inquirer.Text('age', 
                          message="Karakterinizin yaşı nedir? (18-80)", 
                          validate=lambda _, x: x.isdigit() and 18 <= int(x) <= 80)
        ]
        
        answers = inquirer.prompt(questions)
        
        # Karakter tipi seçimi
        self.console.print(Panel(
            "[bold]Karakter Tipi[/bold]",
            border_style="bright_magenta",
            box=ROUNDED
        ))
        
        from models.character_types import CharacterFactory
        
        # Karakter tiplerini ve açıklamalarını göster
        for char_type in CharacterFactory.get_available_types():
            description = CharacterFactory.get_type_description(char_type)
            self.console.print(f"[bright_yellow]{char_type}:[/bright_yellow] {description}")
        
        character_questions = [
            inquirer.List('character_type',
                          message="Karakter tipinizi seçin:",
                          choices=CharacterFactory.get_available_types()),
        ]
        
        character_answer = inquirer.prompt(character_questions)
        answers['character_type'] = character_answer['character_type']
        
        # İş seçimi
        self.console.print(Panel(
            "[bold]Meslek Seçimi[/bold]",
            border_style="bright_cyan",
            box=ROUNDED
        ))
        
        job_questions = [
            inquirer.List('job',
                          message="Karakterinizin mesleği nedir?",
                          choices=["Yazılımcı", "Öğretmen", "Doktor", "Sanatçı", "Mühendis", "İşsiz"]),
        ]
        
        job_answer = inquirer.prompt(job_questions)
        answers['job'] = job_answer['job']
        
        # Karakter oluşturma animasyonu
        self.console.print(Panel(
            "[bright_green]Karakter oluşturuluyor...[/bright_green]",
            border_style="bright_yellow",
            box=ROUNDED
        ))
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
        ) as progress:
            task = progress.add_task("[cyan]Karakter oluşturuluyor...", total=100)
            for i in range(101):
                if self.dev_mode:
                    time.sleep(0.001)  # Dev modda çok hızlı
                else:
                    time.sleep(0.02)
                progress.update(task, completed=i)
                
        self.console.print(Panel(
            f"[bright_green]Tebrikler! {answers['name']} başarıyla oluşturuldu![/bright_green]",
            border_style="bright_green",
            box=ROUNDED
        ))
        
        if self.dev_mode:
            time.sleep(0.2)
        else:
            time.sleep(1.5)
        return answers
        
    def load_saved_game(self, saved_games):
        """Kayıtlı oyun yükleme arayüzü"""
        self.console.clear()
        
        self.console.print(Panel(
            "[bold]Kayıtlı Oyun Yükle[/bold]",
            border_style="bright_blue",
            box=ROUNDED
        ))
        
        if not saved_games:
            self.console.print(Panel(
                "[bright_red]Kayıtlı oyun bulunamadı![/bright_red]",
                border_style="bright_red",
                box=ROUNDED
            ))
            if self.dev_mode:
                time.sleep(0.3)
            else:
                time.sleep(2)
            return None
            
        saved_games.append("Ana Menüye Dön")
        
        questions = [
            inquirer.List('save',
                          message="Hangi kayıtlı oyunu yüklemek istersiniz?",
                          choices=saved_games),
        ]
        
        answer = inquirer.prompt(questions)
        
        if answer['save'] == "Ana Menüye Dön":
            return None
            
        # Yükleme animasyonu
        self.console.print(Panel(
            "[bright_blue]Oyun yükleniyor...[/bright_blue]",
            border_style="bright_yellow",
            box=ROUNDED
        ))
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
        ) as progress:
            task = progress.add_task("[cyan]Oyun yükleniyor...", total=100)
            for i in range(101):
                if self.dev_mode:
                    time.sleep(0.001)  # Dev modda çok hızlı
                else:
                    time.sleep(0.02)
                progress.update(task, completed=i)
                
        return answer['save']
        
    def show_action_menu(self):
        """Eylem menüsünü gösterir"""
        self.is_showing_menu = True
        
        actions = [
            "💼 İş",
            "🍽️ Ye",
            "💤 Uyu",
            "🚿 Banyo Yap",
            "👥 Sosyalleş",
            "🎲 Bahis Oyunları"
        ]
        
        if self.game.is_multiplayer and self.game.network:
            actions.append("👪 Oyuncu Listesi")
            
        actions.extend([
            "💾 Oyunu Kaydet",
            "🚪 Ana Menüye Dön"
        ])
        
        # Menü kısmını daha kompakt hale getir
        self.console.print("\n")  # Bir satır boşluk
        
        questions = [
            inquirer.List('action',
                         message="Ne yapmak istersiniz?",
                         choices=actions),
        ]
        
        answer = inquirer.prompt(questions)
        self.is_showing_menu = False
        
        # Emoji'yi kaldır
        return answer['action'].split(" ", 1)[1] if " " in answer['action'] else answer['action']
    
    def show_gambling_menu(self):
        """Bahis oyunları menüsünü gösterir"""
        self.is_showing_menu = True
        
        gambling_actions = [
            "🎲 Bahis Oyunu (Şans)",
            "🎰 Slot Makinesi",
            "📊 Bahis İstatistikleri",
            "🚪 Geri Dön"
        ]
        
        self.console.clear()
        self.console.print(Panel(
            "[bold bright_red]🎰 VEGAS 🎰[/bold bright_red]\n"
            "[bright_yellow]Şansınızı deneyin! Büyük kazançlar sizi bekliyor![/bright_yellow]\n",
            border_style="bright_red",
            box=ROUNDED
        ))
        
        questions = [
            inquirer.List('gambling_action',
                         message="Hangi oyunu oynamak istersiniz?",
                         choices=gambling_actions),
        ]
        
        answer = inquirer.prompt(questions)
        self.is_showing_menu = False
        
        # Emoji'yi kaldır
        return answer['gambling_action'].split(" ", 1)[1] if " " in answer['gambling_action'] else answer['gambling_action']
    
    def get_bet_amount_input(self, current_money: float) -> float:
        """Bahis miktarı girişi alır"""
        self.console.print(f"[bright_green]Mevcut paranız: {current_money}₺[/bright_green]")
        
        while True:
            try:
                questions = [
                    inquirer.Text('bet_amount',
                                 message="Bahis miktarını girin (₺)",
                                 validate=lambda _, x: self._validate_bet_amount(x, current_money))
                ]
                
                answer = inquirer.prompt(questions)
                if answer:
                    return float(answer['bet_amount'])
                else:
                    return 0
                    
            except (ValueError, KeyboardInterrupt, EOFError):
                self.console.print("[bright_red]Geçersiz miktar! Lütfen tekrar deneyin.[/bright_red]")
                return 0
    
    def _validate_bet_amount(self, amount_str: str, current_money: float) -> bool:
        """Bahis miktarını doğrular"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                return "Bahis miktarı 0'dan büyük olmalı!"
            elif amount > current_money:
                return f"Yeterli paranız yok! (Maks: {current_money}₺)"
            elif amount > 10000:
                return "Maksimum bahis 10,000₺!"
            return True
        except ValueError:
            return "Geçerli bir sayı girin!"
    
    def show_gambling_stats(self, stats_text: str):
        """Bahis istatistiklerini gösterir"""
        self.console.clear()
        
        self.console.print(Panel(
            stats_text,
            title="🎲 BAHİS İSTATİSTİKLERİ",
            border_style="bright_cyan",
            box=ROUNDED
        ))
        
        self.console.print("\n[bright_yellow]Devam etmek için Enter tuşuna basın...[/bright_yellow]")
        input()
        
    def show_job_menu(self):
        """İş menüsünü gösterir"""
        self.is_showing_menu = True
        
        job_actions = [
            "İşe Git",
            "İş Ara",
            "İstifa Et",
            "Geri Dön"
        ]
        
        questions = [
            inquirer.List('job_action',
                         message="İş ile ilgili ne yapmak istersiniz?",
                         choices=job_actions),
        ]
        
        answer = inquirer.prompt(questions)
        self.is_showing_menu = False
        return answer['job_action']
        
    def show_social_menu(self):
        """Sosyalleşme menüsünü gösterir"""
        self.is_showing_menu = True
        
        social_actions = [
            "Arkadaşlarla Buluş",
            "Flört Et",
            "Partiye Git",
            "Geri Dön"
        ]
        
        questions = [
            inquirer.List('social_action',
                         message="Sosyalleşmek için ne yapmak istersiniz?",
                         choices=social_actions),
        ]
        
        answer = inquirer.prompt(questions)
        self.is_showing_menu = False
        return answer['social_action']
        
    def show_multiplayer_lobby(self, is_server=False):
        """Multiplayer lobi ekranını gösterir - geliştirilmiş versiyon"""
        
        # Eğer oyun başlamışsa, lobby UI'ı gösterme (thread-safe)
        if hasattr(self.game, '_game_started_lock') and hasattr(self.game, '_game_started'):
            with self.game._game_started_lock:
                if self.game._game_started:
                    self.console.print("[bright_green]🎮 Oyun başlatılıyor...[/bright_green]")
                    return "Oyun Başladı"  # Özel dönüş değeri
        
        self.console.clear()
        
        lobby_title = "SUNUCU LOBİSİ" if is_server else "OYUNCU LOBİSİ"
        
        title = pyfiglet.figlet_format(lobby_title, font="small")
        self.console.print(Align.center(title, vertical="top"), style="bright_cyan")
        
        # Bağlantı durumu
        if self.game.network:
            status_text = f"[bright_green]Bağlantı Aktif[/bright_green] | "
            status_text += f"Oyuncu Sayısı: {self.game.network.get_player_count()}"
        else:
            status_text = "[bright_red]Bağlantı Yok[/bright_red]"
            
        self.console.print(Panel(
            status_text,
            title="Lobi Durumu",
            border_style="bright_blue",
            box=ROUNDED
        ))
        
        # Kendi karakterini göster
        if self.game.sim:
            self.console.print(Panel(
                f"[bright_green]Karakterin:[/bright_green] {self.game.sim.name}, {self.game.sim.gender}, {self.game.sim.age} yaşında, {self.game.sim.job}",
                title="Kendi Karakterin",
                border_style="bright_green",
                box=ROUNDED
            ))
        
        # Bağlı oyuncuları göster
        if self.game.network and hasattr(self.game.network, 'players'):
            # Oyuncu listesi tablosu
            if self.game.network.players:
                table = Table(title="Lobideki Oyuncular", box=ROUNDED)
                table.add_column("Oyuncu Adı", style="bright_cyan", width=15)
                table.add_column("Cinsiyet", style="bright_white", width=8)
                table.add_column("Yaş", style="bright_white", width=5)
                table.add_column("Meslek", style="bright_white", width=12)
                table.add_column("Ruh Hali", style="bright_green", width=10)
                
                for player_name, player_data in self.game.network.players.items():
                    # Basit dict formatı
                    table.add_row(
                        player_name,
                        player_data.get('gender', 'Bilinmiyor'),
                        str(player_data.get('age', '?')),
                        player_data.get('job', 'İşsiz'),
                        str(player_data.get('mood', 'Nötr'))
                    )
                self.console.print(table)
            else:
                self.console.print(Panel(
                    "[bright_yellow]Henüz başka oyuncu yok.[/bright_yellow]",
                    title="Oyuncu Listesi",
                    border_style="bright_yellow",
                    box=ROUNDED
                ))
        
        # Lobi talimatları
        if is_server:
            self.console.print(Panel(
                "[bright_cyan]Sunucu olarak diğer oyuncuları bekliyorsunuz.[/bright_cyan]\n"
                "[bright_yellow]Diğer oyuncuların bağlanması için IP adresinizi ve port numaranızı (5000) paylaşın.[/bright_yellow]\n"
                "[bright_white]En az 2 oyuncu olduğunda oyunu başlatabilirsiniz.[/bright_white]",
                title="Sunucu Bilgileri",
                border_style="bright_cyan",
                box=ROUNDED
            ))
        else:
            self.console.print(Panel(
                "[bright_cyan]Sunucuya bağlandınız, host'un oyunu başlatmasını bekliyorsunuz.[/bright_cyan]\n"
                "[bright_yellow]Chat yazabilir ve diğer oyuncularla iletişim kurabilirsiniz.[/bright_yellow]",
                title="İstemci Bilgileri",
                border_style="bright_cyan",
                box=ROUNDED
            ))
        
        # Lobi işlemleri
        lobby_actions = [
            "Oyuncu Listesini Yenile",
            "Chat Gönder"
        ]
        
        if is_server:
            lobby_actions.append("Oyunu Başlat")
            
        lobby_actions.append("Lobiden Ayrıl")
        
        questions = [
            inquirer.List('lobby_action',
                         message="Ne yapmak istiyorsunuz?",
                         choices=lobby_actions),
        ]
        
        answer = inquirer.prompt(questions)
        return answer['lobby_action']
    
    def get_chat_input(self) -> str:
        """Chat mesajı girişi alır"""
        try:
            questions = [
                inquirer.Text('message',
                             message="Chat mesajınızı yazın",
                             validate=lambda _, x: len(x.strip()) > 0 or "Boş mesaj gönderilemez!")
            ]
            
            answer = inquirer.prompt(questions)
            return answer['message'].strip() if answer else ""
        except (KeyboardInterrupt, EOFError):
            return ""
    
    def show_multiplayer_action_menu(self):
        """Çok oyunculu mod için aksiyon menüsü"""
        choices = [
            "🔄 Yenile",
            "🍽️  Ye",
            "😴 Uyu", 
            "🚿 Banyo Yap",
            "💼 İş",
            "👥 Sosyalleş",
            "🎲 Bahis Oyunları",
            "💬 Chat Gönder",
            "📊 Oyuncu Listesi",
            "💾 Oyunu Kaydet",
            "🔌 Bağlantıyı Kes"
        ]
        
        return self._get_choice("Multiplayer - Ne yapmak istiyorsun?", choices)
    
    def show_network_diagnostics(self, diagnostics: dict):
        """🚀 YENİ: Network diagnostik bilgilerini gösterir"""
        self.console.clear()
        
        # Ana başlık
        self.console.print(Panel(
            "[bold bright_cyan]📡 Network Diagnostikleri[/bold bright_cyan]",
            style="cyan",
            box=ROUNDED
        ))
        
        # İstatistikler
        stats = diagnostics.get('stats', {})
        self.console.print(Panel(
            f"[green]📦 Gönderilen Paket:[/green] {stats.get('packets_sent', 0):,}\n"
            f"[blue]📥 Alınan Paket:[/blue] {stats.get('packets_received', 0):,}\n"
            f"[yellow]📊 Gönderilen Veri:[/yellow] {self._format_bytes(stats.get('bytes_sent', 0))}\n"
            f"[cyan]📋 Alınan Veri:[/cyan] {self._format_bytes(stats.get('bytes_received', 0))}\n"
            f"[magenta]🗜️  Sıkıştırma Oranı:[/magenta] {stats.get('compression_ratio', 0):.2%}",
            title="Genel İstatistikler",
            border_style="green"
        ))
        
        # Latency bilgileri
        latency_info = diagnostics.get('latency_info', {})
        avg_latency = latency_info.get('average_latency', 0)
        max_latency = latency_info.get('max_latency', 0)
        
        latency_color = "green" if avg_latency < 50 else "yellow" if avg_latency < 100 else "red"
        
        self.console.print(Panel(
            f"[{latency_color}]⚡ Ortalama Latency:[/{latency_color}] {avg_latency:.2f}ms\n"
            f"[red]🔺 Maksimum Latency:[/red] {max_latency:.2f}ms\n"
            f"[green]📉 Packet Loss:[/green] {stats.get('packet_loss', 0):.2%}",
            title="Bağlantı Performansı",
            border_style=latency_color
        ))
        
        # Bağlantı bilgileri
        conn_info = diagnostics.get('connection_info', {})
        role = "🖥️  Sunucu" if conn_info.get('is_server') else "💻 İstemci"
        
        self.console.print(Panel(
            f"[bright_white]🎯 Rol:[/bright_white] {role}\n"
            f"[bright_white]🔗 Bağlı:[/bright_white] {'✅ Evet' if conn_info.get('is_connected') else '❌ Hayır'}\n"
            f"[bright_white]👥 Bağlı Oyuncu:[/bright_white] {conn_info.get('connected_clients', 0)}\n"
            f"[bright_white]🗜️  Sıkıştırma:[/bright_white] {'✅ Aktif' if conn_info.get('compression_enabled') else '❌ Kapalı'}\n"
            f"[bright_white]📦 Batch Boyutu:[/bright_white] {conn_info.get('batch_size', 0)}",
            title="Bağlantı Bilgileri",
            border_style="bright_blue"
        ))
        
        # Queue bilgileri
        queue_info = diagnostics.get('queue_info', {})
        self.console.print(Panel(
            f"[white]📬 Mesaj Kuyruğu:[/white] {queue_info.get('message_queue_size', 0)}\n"
            f"[white]📦 Batch Kuyruğu:[/white] {queue_info.get('batch_queue_size', 0)}\n"
            f"[white]⏳ Bekleyen ACK:[/white] {queue_info.get('pending_acks', 0)}",
            title="Kuyruk Durumu",
            border_style="white"
        ))
        
        # Performans önerileri
        recommendations = self._get_performance_recommendations(diagnostics)
        if recommendations:
            self.console.print(Panel(
                "\n".join(f"• {rec}" for rec in recommendations),
                title="💡 Performans Önerileri",
                border_style="yellow"
            ))
        
        self.console.print("\n[dim]Devam etmek için herhangi bir tuşa basın...[/dim]")
        input()
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Byte'ları okunabilir formata çevirir"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} TB"
    
    def _get_performance_recommendations(self, diagnostics: dict) -> List[str]:
        """Performans önerilerini oluşturur"""
        recommendations = []
        
        latency_info = diagnostics.get('latency_info', {})
        stats = diagnostics.get('stats', {})
        queue_info = diagnostics.get('queue_info', {})
        
        avg_latency = latency_info.get('average_latency', 0)
        packet_loss = stats.get('packet_loss', 0)
        message_queue_size = queue_info.get('message_queue_size', 0)
        
        if avg_latency > 200:
            recommendations.append("🔴 Yüksek latency - İnternet bağlantınızı kontrol edin")
        elif avg_latency > 100:
            recommendations.append("🟡 Orta seviye latency - Network optimizasyonu önerilir")
        
        if packet_loss > 0.05:
            recommendations.append("🟡 Yüksek packet loss - Bağlantı kararsız")
        
        if message_queue_size > 50:
            recommendations.append("🟡 Mesaj kuyruğu dolmuş - Performans etkilenebilir")
        
        if not recommendations:
            recommendations.append("✅ Network performansınız iyi durumda!")
        
        return recommendations
    
    def show_network_optimization_menu(self):
        """🚀 YENİ: Network optimizasyon menüsü"""
        choices = [
            "🚀 Otomatik Optimizasyon",
            "🗜️  Sıkıştırmayı Aç/Kapat",
            "📦 Batch Boyutunu Ayarla",
            "⏱️  Sync Aralığını Ayarla", 
            "🔄 Varsayılan Ayarlara Dön",
            "🔙 Geri Dön"
        ]
        
        return self._get_choice("Network Optimizasyon Ayarları", choices)
    
    def get_batch_size_input(self, current_size: int) -> int:
        """Batch size girişi alır"""
        while True:
            try:
                self.console.print(f"[cyan]Mevcut batch boyutu: {current_size}[/cyan]")
                size_input = input("Yeni batch boyutu (5-50 arası): ").strip()
                size = int(size_input)
                if 5 <= size <= 50:
                    return size
                else:
                    self.console.print("[red]Lütfen 5-50 arası bir değer girin![/red]")
            except ValueError:
                self.console.print("[red]Lütfen geçerli bir sayı girin![/red]")
    
    def get_sync_interval_input(self, current_interval: int) -> int:
        """Sync interval girişi alır"""
        while True:
            try:
                self.console.print(f"[cyan]Mevcut sync aralığı: {current_interval} saniye[/cyan]")
                interval_input = input("Yeni sync aralığı (1-30 arası): ").strip()
                interval = int(interval_input)
                if 1 <= interval <= 30:
                    return interval
                else:
                    self.console.print("[red]Lütfen 1-30 arası bir değer girin![/red]")
            except ValueError:
                self.console.print("[red]Lütfen geçerli bir sayı girin![/red]")
    
    def show_optimization_result(self, message: str, success: bool = True):
        """Optimizasyon sonucunu gösterir"""
        color = "green" if success else "red"
        icon = "✅" if success else "❌"
        
        self.console.print(Panel(
            f"[{color}]{icon} {message}[/{color}]",
            title="Optimizasyon Sonucu",
            border_style=color
        ))
        time.sleep(2)
    
    def show_event(self, event_title, event_description):
        """Olay ekranını gösterir"""
        self.console.clear()
        
        self.console.print(Panel(
            f"[bright_yellow]{event_title}[/bright_yellow]",
            border_style="bright_red",
            box=ROUNDED
        ))
        
        self.console.print(Panel(
            f"[bright_white]{event_description}[/bright_white]",
            border_style="bright_blue",
            box=ROUNDED
        ))
        
        # Devam etmek için bekle
        self.console.print("\n[bright_yellow]Devam etmek için Enter tuşuna basın...[/bright_yellow]")
        input()
    
    def show_death_screen(self, death_info: dict):
        """Ölüm ekranını gösterir"""
        self.console.clear()
        
        # Ölüm başlığı
        death_title = pyfiglet.figlet_format("OLUM", font="slant")
        self.console.print(Align.center(death_title, vertical="top"), style="bright_red")
        
        # Ana ölüm mesajı
        self.console.print(Panel(
            f"[bright_red]💀 {death_info['name']} hayatını kaybetti! 💀[/bright_red]",
            title="OYUN BİTTİ",
            border_style="bright_red",
            box=HEAVY
        ))
        
        # Ölüm detayları
        details = f"[bright_white]Ölüm Sebebi:[/bright_white] [bright_red]{death_info['death_reason']}[/bright_red]\n"
        details += f"[bright_white]Ölüm Zamanı:[/bright_white] {death_info['death_time']}\n"
        details += f"[bright_white]Yaşı:[/bright_white] {death_info['age_at_death']} yaşında\n"
        
        self.console.print(Panel(
            details,
            title="Ölüm Detayları",
            border_style="bright_yellow",
            box=ROUNDED
        ))
        
        # Final istatistikler
        final_stats = death_info['final_stats']
        stats_text = f"[bright_white]Son Para:[/bright_white] [bright_green]${final_stats['money']}[/bright_green]\n"
        stats_text += f"[bright_white]Meslek:[/bright_white] {final_stats['job']}\n"
        stats_text += f"[bright_white]İlişki Sayısı:[/bright_white] {final_stats['relationships']}"
        
        self.console.print(Panel(
            stats_text,
            title="Final İstatistikleri",
            border_style="bright_blue",
            box=ROUNDED
        ))
        
        # Epitaf (mezar taşı yazısı)
        epitaph_quotes = [
            "Hayat kısa, oyun daha da kısa...",
            "Statlarına dikkat etmeliydin...",
            "Bir simülasyonun sonu böyle gelir...",
            "RIP - Rest in Pixels",
            "Game Over - Insert Coin to Continue"
        ]
        
        import random
        epitaph = random.choice(epitaph_quotes)
        
        self.console.print(Panel(
            f"[dim italic]\"{epitaph}\"[/dim italic]",
            title="💭 Epitaf",
            border_style="dim white",
            box=ROUNDED
        ))
        
        # Seçenekler
        choices = [
            "🔄 Yeni Oyun Başlat",
            "📊 Ölüm İstatistiklerini Kaydet", 
            "🚪 Ana Menüye Dön",
            "❌ Oyundan Çık"
        ]
        
        return self._get_choice("Ne yapmak istiyorsunuz?", choices)

    def show_detailed_player_list(self, players_list: List[Dict]):
        """Detaylı oyuncu listesini gösterir"""
        self.console.clear()
        
        self.console.print(Panel(
            "[bold]Detaylı Oyuncu Bilgileri[/bold]",
            title="Multiplayer Oyuncular",
            border_style="bright_blue",
            box=ROUNDED
        ))
        
        if not players_list:
            self.console.print(Panel(
                "[bright_red]Bağlı oyuncu bulunamadı![/bright_red]",
                border_style="bright_red",
                box=ROUNDED
            ))
            time.sleep(2)
            return
            
        # Detaylı oyuncu tablosu
        table = Table(title=f"Aktif Oyuncular ({len(players_list)})", box=ROUNDED)
        table.add_column("Oyuncu", style="bright_cyan", width=12)
        table.add_column("Bilgiler", style="bright_white", width=20)
        table.add_column("Meslek", style="bright_yellow", width=15)
        table.add_column("Stats", style="bright_green", width=25)
        table.add_column("Durum", style="bright_magenta", width=15)
        
        for player_data in players_list:
            # Oyuncu bilgileri
            info = f"{player_data.get('gender', '?')}, {str(player_data.get('age', '?'))} yaş"
            
            # Meslek bilgisi
            job_info = f"{player_data.get('job', 'İşsiz')}"
            if 'job_level' in player_data:
                job_info += f" (Lv.{player_data['job_level']})"
            
            # Stats
            stats = []
            if 'energy' in player_data:
                stats.append(f"Enerji: {player_data['energy']}")
            if 'hunger' in player_data:
                stats.append(f"Açlık: {player_data['hunger']}")
            if 'social' in player_data:
                stats.append(f"Sosyal: {player_data['social']}")
            stats_text = " | ".join(stats) if stats else "Bilinmiyor"
            
            # Durum
            status_parts = []
            if 'mood' in player_data:
                status_parts.append(str(player_data['mood']))
            if 'activity' in player_data:
                status_parts.append(str(player_data['activity']))
            status_text = " - ".join(status_parts) if status_parts else "Aktif"
            
            table.add_row(
                str(player_data.get('name', 'Bilinmeyen')),
                info,
                job_info,
                stats_text,
                status_text
            )
            
        self.console.print(table)
        
        # Ek bilgiler
        total_money = sum(p.get('money', 0) for p in players_list)
        avg_energy = sum(p.get('energy', 0) for p in players_list) / len(players_list) if players_list else 0
        
        self.console.print(Panel(
            f"[bright_green]Toplam Para: ${total_money}[/bright_green] | "
            f"[bright_yellow]Ortalama Enerji: {avg_energy:.2f}[/bright_yellow]",
            title="Toplam İstatistikler",
            border_style="bright_white",
            box=ROUNDED
        ))
        
        # Devam etmek için bekle
        self.console.print("\n[bright_yellow]Devam etmek için Enter tuşuna basın...[/bright_yellow]")
        input()

    def show_multiplayer_social_menu(self, players_list: List[Dict]):
        """Multiplayer sosyalleşme menüsünü gösterir"""
        social_actions = [
            "Arkadaşlarla Buluş",
            "Flört Et", 
            "Partiye Git"
        ]
        
        # Diğer oyuncularla sosyalleşme seçeneklerini ekle
        other_players = [p for p in players_list if p.get('name') != (self.game.sim.name if self.game.sim else '')]
        
        for player in other_players:
            social_actions.append(f"Oyuncuyla Sosyalleş: {player.get('name', 'Bilinmeyen')}")
        
        social_actions.append("Geri Dön")
        
        return self._get_choice("Sosyalleşme - Ne yapmak istiyorsun?", social_actions)
        
    def show_activity_progress(self, activity_name, duration, callback=None):
        """Aktivite ilerleme çubuğunu gösterir"""
        self.console.clear()
        
        self.console.print(Panel(
            f"[bright_cyan]{activity_name}[/bright_cyan]",
            border_style="bright_blue",
            box=ROUNDED
        ))
        
        if self.dev_mode:
            # Dev modda aktiviteleri çok hızlı tamamla
            steps = min(10, duration * 2)  # Dev modda daha az adım
            sleep_time = 0.01  # Çok hızlı
        else:
            steps = duration * 10  # Her saniye için 10 adım
            sleep_time = 0.1   # Normal süre
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"[cyan]{activity_name} yapılıyor...", total=steps)
            
            for i in range(steps):
                time.sleep(sleep_time)
                progress.update(task, completed=i+1)
                
                # Callback fonksiyonu varsa çağır
                if callback:
                    callback(i, steps)
    
    def _get_choice(self, message: str, choices: List[str]) -> str:
        """Seçeneklerden birini seçmek için yardımcı metod"""
        try:
            questions = [
                inquirer.List('choice',
                             message=message,
                             choices=choices),
            ]
            
            answer = inquirer.prompt(questions)
            return answer['choice'] if answer else choices[0]
        except (KeyboardInterrupt, EOFError):
            return choices[-1] if choices else ""
    
    def show_save_confirmation(self, filename: str, success: bool):
        """Oyun kaydetme onay ekranını gösterir"""
        self.console.clear()
        
        if success:
            # Başarılı kaydetme
            save_title = pyfiglet.figlet_format("SAVED", font="slant")
            self.console.print(Align.center(save_title, vertical="top"), style="bright_green")
            
            self.console.print(Panel(
                f"[bright_green]✅ Oyun başarıyla kaydedildi![/bright_green]\n\n"
                f"[bright_white]Dosya adı:[/bright_white] [bright_cyan]{filename}[/bright_cyan]\n"
                f"[bright_white]Kayıt zamanı:[/bright_white] {datetime.now().strftime('%d %B %Y, %H:%M')}\n"
                f"[bright_white]Konum:[/bright_white] Oyun klasörü",
                title="💾 KAYIT BAŞARILI",
                border_style="bright_green",
                box=HEAVY
            ))
            
            # Kayıt detayları
            details = "[bright_green]🎮 Oyun durumunuz güvenle kaydedildi![/bright_green]\n"
            details += "[bright_yellow]📂 Kayıtlı oyun menüsünden yükleyebilirsiniz.[/bright_yellow]\n"
            details += "[bright_blue]💡 Düzenli kayıt yapmayı unutmayın![/bright_blue]"
            
            self.console.print(Panel(
                details,
                title="ℹ️  Bilgi",
                border_style="bright_blue",
                box=ROUNDED
            ))
            
        else:
            # Başarısız kaydetme
            error_title = pyfiglet.figlet_format("ERROR", font="slant")
            self.console.print(Align.center(error_title, vertical="top"), style="bright_red")
            
            self.console.print(Panel(
                f"[bright_red]❌ Oyun kaydedilemedi![/bright_red]\n\n"
                f"[bright_white]Dosya adı:[/bright_white] [bright_cyan]{filename}[/bright_cyan]\n"
                f"[bright_yellow]Lütfen tekrar deneyin veya disk alanını kontrol edin.[/bright_yellow]",
                title="💾 KAYIT HATASI",
                border_style="bright_red",
                box=HEAVY
            ))
        
        self.console.print("\n[bright_yellow]Devam etmek için Enter tuşuna basın...[/bright_yellow]")
        input() 