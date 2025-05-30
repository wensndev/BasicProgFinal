import time
from datetime import datetime
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.align import Align
from rich.style import Style
from rich.box import ROUNDED, HEAVY

class StatsDisplay:
    """Oyuncu statlarını gösteren sınıf"""
    
    def __init__(self, game):
        self.game = game
        self.console = Console()
        self.last_update = None
        self.update_interval = 2  # Saniye cinsinden güncelleme aralığı
        
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
    
    def create_stat_bar(self, value, attribute, label, bar_length=20):
        """Stat çubuğu oluşturur"""
        style = "bright_green"
        
        # Kritik durum kontrolü
        if hasattr(self.game.sim, 'critical_thresholds') and attribute in self.game.sim.critical_thresholds:
            thresholds = self.game.sim.critical_thresholds[attribute]
            if value <= thresholds['critical']:
                style = "bright_red"
            elif value <= thresholds['warning']:
                style = "bright_yellow"
        
        # Çubuğu oluştur
        filled = int((value / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Etiket genişliği sabit (etiketleri aynı hizaya getirmek için)
        # Etiket ve değer ile birlikte döndür - sağa hizalı değer
        return f"[bright_cyan]{label + ':':<10}[/bright_cyan] [{style}]{bar}[/{style}] {value:.2f}/100"
    
    def get_compact_stats_panel(self):
        """Kompakt stat paneli oluşturur"""
        if not self.game.sim:
            return Panel("Karakter yok", title="Durum", border_style="bright_yellow")
        
        status = self.game.sim.get_status()
        
        # Tek sütunlu kompakt tablo oluştur - satırlar arası boşluk için padding'i artır
        stats_table = Table(box=None, show_header=False, expand=True, padding=(0,2))
        stats_table.add_column("", ratio=1)
        
        # Tüm statları alt alta diz
        stats_table.add_row(self.create_stat_bar(status['mood'], 'mood', "Ruh", 30))
        stats_table.add_row(self.create_stat_bar(status['energy'], 'energy', "Enerji", 30))
        stats_table.add_row(self.create_stat_bar(status['hunger'], 'hunger', "Açlık", 30))
        stats_table.add_row(self.create_stat_bar(status['hygiene'], 'hygiene', "Temiz", 30))
        stats_table.add_row(self.create_stat_bar(status['social'], 'social', "Sosyal", 30))
        
        # Para bilgisini ekle - etiket genişliği sabit
        stats_table.add_row(f"[bright_green]{'Para:':<10}[/bright_green] {status['money']:.2f}₺")
        
        # Tarih bilgisi - etiket genişliği sabit
        stats_table.add_row(f"[bright_cyan]{'Tarih:':<10}[/bright_cyan] {self.game.format_time()}")
        
        # Panel oluştur - kompakt ve tek sütun, genişliği içeriğe göre ayarla
        return Panel(
            stats_table,
            title=f"[bright_yellow]{status['name']} - {status['job'] or 'İşsiz'}[/bright_yellow]",
            border_style="bright_yellow",
            box=ROUNDED,
            padding=(0,1)
        )
    
    def get_detailed_stats_panel(self):
        """Detaylı stat paneli oluşturur"""
        if not self.game.sim:
            return Panel("Karakter yok", title="Durum", border_style="bright_cyan")
        
        status = self.game.sim.get_status()
        
        # Sol taraf - Temel bilgiler
        left_panel = Table(box=ROUNDED, show_header=False, expand=True)
        left_panel.add_column("Özellik", style="bright_cyan", width=15)
        left_panel.add_column("Değer", style="bright_yellow")
        
        left_panel.add_row("Karakter", f"[bright_white]{status['name']}[/bright_white]")
        left_panel.add_row("Cinsiyet", f"{status['gender']}")
        left_panel.add_row("Yaş", f"{status['age']}")
        left_panel.add_row("Meslek", f"{status['job'] or 'İşsiz'}")
        left_panel.add_row("Para", f"[bright_green]{status['money']:.2f}₺[/bright_green]")
        
        # Sağ taraf - Stat çubukları
        right_panel = Table(box=ROUNDED, show_header=False, expand=True)
        right_panel.add_column("Özellik", style="bright_cyan", width=15)
        right_panel.add_column("Değer", style="bright_yellow")
        
        # Stat çubukları
        bar_length = 20
        right_panel.add_row("Ruh Hali", self.create_stat_bar(status['mood'], 'mood', "", bar_length))
        right_panel.add_row("Enerji", self.create_stat_bar(status['energy'], 'energy', "", bar_length))
        right_panel.add_row("Açlık", self.create_stat_bar(status['hunger'], 'hunger', "", bar_length))
        right_panel.add_row("Temizlik", self.create_stat_bar(status['hygiene'], 'hygiene', "", bar_length))
        right_panel.add_row("Sosyallik", self.create_stat_bar(status['social'], 'social', "", bar_length))
        
        # İki paneli birleştir
        content = Layout()
        content.split(
            Layout(Panel(
                left_panel,
                title="Karakter Bilgileri",
                border_style="bright_blue",
                box=ROUNDED
            )),
            Layout(Panel(
                right_panel,
                title="Durum Çubukları",
                border_style="bright_green",
                box=ROUNDED
            ))
        )
        
        return Panel(
            content,
            title=f"[bright_cyan]{status['name']} - Detaylı Durum Bilgileri[/bright_cyan]",
            border_style="bright_cyan",
            box=ROUNDED
        )
    
    def get_warnings_panel(self):
        """Kritik durumlar ve uyarılar için panel oluşturur"""
        if not self.game.sim:
            return None
            
        # is_critical veya has_warnings kontrolü
        if not (self.game.sim.is_critical or self.game.sim.has_warnings):
            return None
            
        status = self.game.sim.get_status()
        
        if 'warnings' not in status or not status['warnings']:
            return None
            
        warnings_text = "\n".join([f"⚠️ {warning.upper()}" for warning in status['warnings']])
        
        # Uyarı durumunun ciddiyetine göre başlık ve stil belirleme
        has_critical = any("kritik seviyede" in warning for warning in status['warnings'])
        
        title = "KRİTİK DURUMLAR" if has_critical else "UYARILAR"
        border_style = "bright_red" if has_critical else "bright_yellow"
        
        return Panel(
            warnings_text,
            title=title,
            border_style=border_style,
            box=HEAVY,
            padding=(1, 2),
            width=50
        )
    
    def display_stats(self, compact=True):
        """Statları konsola yazdırır"""
        if not self.game.sim:
            return
            
        # Güncelleme aralığını kontrol et
        now = datetime.now()
        if self.last_update and (now - self.last_update).total_seconds() < self.update_interval:
            return
            
        self.last_update = now
        
        # Önce sim durumunu güncelle
        status = self.game.sim.get_status()
        
        # Uyarı paneli
        warnings_panel = self.get_warnings_panel()
        if warnings_panel:
            self.console.print(warnings_panel)
            
        # Stat paneli
        if compact:
            self.console.print(self.get_compact_stats_panel())
        else:
            self.console.print(self.get_detailed_stats_panel())
            
        # Zaman bilgisi - kompakt modda panel içine taşındı
        if not compact:
            time_text = f"[bright_cyan]Tarih:[/bright_cyan] {self.game.format_time()}"
            self.console.print(Align.center(time_text))
    
    def display_multiplayer_stats(self, players: Dict[str, Any]):
        """Multiplayer oyuncuların statlarını görüntüler"""
        if not self.game.sim:
            return
            
        # Kendi statlarını üstte göster (kompakt)
        self.console.print(self.get_compact_stats_panel())
        
        # Diğer oyuncuların statlarını göster
        if not players or len(players) <= 1:
            return
            
        # Multiplayer oyuncu tablosu
        table = Table(title="Diğer Oyuncular", box=ROUNDED, expand=False)
        table.add_column("Oyuncu", style="bright_cyan", width=12)
        table.add_column("Meslek", style="bright_yellow", width=12)
        table.add_column("Enerji", style="bright_green", width=8)
        table.add_column("Açlık", style="bright_red", width=8)
        table.add_column("Sosyal", style="bright_blue", width=8)
        table.add_column("Para", style="bright_green", width=10)
        table.add_column("Aktivite", style="bright_magenta", width=12)
        
        for player_name, player_data in players.items():
            # Kendi karakterini atla
            if player_name == self.game.sim.name:
                continue
                
            # PlayerState objesi olup olmadığını kontrol et
            if hasattr(player_data, 'name'):
                # PlayerState objesi
                energy = getattr(player_data, 'energy', 0)
                hunger = getattr(player_data, 'hunger', 0)
                social = getattr(player_data, 'social', 0)
                money = getattr(player_data, 'money', 0)
                job = getattr(player_data, 'job', 'İşsiz')
                activity = getattr(player_data, 'activity', 'Boşta')
            else:
                # Dict objesi (eski format)
                energy = player_data.get('energy', 0)
                hunger = player_data.get('hunger', 0)
                social = player_data.get('social', 0)
                money = player_data.get('money', 0)
                job = player_data.get('job', 'İşsiz')
                activity = player_data.get('activity', 'Boşta')
            
            # Renk kodlaması
            energy_color = self._get_stat_color(energy)
            hunger_color = self._get_stat_color(100 - hunger)  # Açlık ters mantık
            social_color = self._get_stat_color(social)
            
            table.add_row(
                str(player_name),
                str(job[:10] + "..." if len(job) > 10 else job),
                f"[{energy_color}]{energy:.2f}[/{energy_color}]",
                f"[{hunger_color}]{hunger:.2f}[/{hunger_color}]",
                f"[{social_color}]{social:.2f}[/{social_color}]",
                f"${money:.2f}",
                str(activity[:10] + "..." if len(activity) > 10 else activity)
            )
        
        if table.row_count > 0:
            self.console.print(table)
        
        # Multiplayer bilgi paneli
        network_info = self.game.get_network_status()
        if network_info['connected']:
            info_text = f"[bright_green]Bağlantı: Aktif[/bright_green] | "
            info_text += f"Oyuncu Sayısı: {network_info['player_count']} | "
            info_text += f"Rol: {network_info['server_info']}"
            
            self.console.print(Panel(
                info_text,
                title="Multiplayer Durumu",
                border_style="bright_green",
                box=ROUNDED
            ))
    
    def _get_stat_color(self, value: int) -> str:
        """Stat değerine göre renk kodu döndürür"""
        if value >= 80:
            return "bright_green"
        elif value >= 50:
            return "bright_yellow"
        elif value >= 30:
            return "yellow"
        else:
            return "bright_red"
    
    def display_multiplayer_summary(self, players: Dict[str, Any]):
        """Multiplayer oyuncuların özet bilgilerini gösterir"""
        if not players:
            return
            
        # Özet istatistikler
        total_players = len(players)
        total_money = 0
        avg_energy = 0
        avg_social = 0
        jobs = {}
        
        for player_name, player_data in players.items():
            if hasattr(player_data, 'money'):
                # PlayerState objesi
                total_money += getattr(player_data, 'money', 0)
                avg_energy += getattr(player_data, 'energy', 0)
                avg_social += getattr(player_data, 'social', 0)
                job = getattr(player_data, 'job', 'İşsiz')
            else:
                # Dict objesi
                total_money += player_data.get('money', 0)
                avg_energy += player_data.get('energy', 0)
                avg_social += player_data.get('social', 0)
                job = player_data.get('job', 'İşsiz')
            
            jobs[job] = jobs.get(job, 0) + 1
        
        if total_players > 0:
            avg_energy = avg_energy / total_players
            avg_social = avg_social / total_players
        
        # En yaygın meslek
        most_common_job = max(jobs.items(), key=lambda x: x[1])[0] if jobs else "Bilinmiyor"
        
        # Özet tablosu
        summary_table = Table(title="Multiplayer Özet", box=ROUNDED)
        summary_table.add_column("İstatistik", style="bright_cyan")
        summary_table.add_column("Değer", style="bright_yellow")
        
        summary_table.add_row("Toplam Oyuncu", str(total_players))
        summary_table.add_row("Toplam Para", f"${total_money:.2f}")
        summary_table.add_row("Ortalama Enerji", f"{avg_energy:.2f}")
        summary_table.add_row("Ortalama Sosyal", f"{avg_social:.2f}")
        summary_table.add_row("En Yaygın Meslek", most_common_job)
        
        self.console.print(summary_table) 