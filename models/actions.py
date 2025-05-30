from rich.console import Console
from rich.progress import Progress
import time
import random
import inquirer
from datetime import datetime, timedelta
from rich.panel import Panel
import math

class Actions:
    def __init__(self, game):
        self.game = game
        self.console = game.ui.console
        self._last_progress_time = None
        self._progress_step = 0.05  # İlerleme çubuğu adım süresi
        
    def _show_progress(self, message, duration=2.5):
        """Optimize edilmiş ilerleme çubuğu gösterimi"""
        self.game.ui.show_activity_progress(message, duration)
    
    def eat(self, sim):
        """Yemek yeme eylemi"""
        if self.game.events.is_action_in_progress:
            return {}
        
        self.game.events.start_action()
        try:
            # Yemek yeme etkileri
            cost = random.randint(20, 50)
            sim.money -= cost
            
            # Tüm değişiklikleri tek seferde uygula
            sim.update_needs(hunger=40, energy=10, mood=5)
            
            # Aktivite bilgisini döndür
            return {
                'name': 'Yemek yeme',
                'duration': 3,
                'cost': cost,
                'effects': {
                    'hunger': 40,
                    'energy': 10,
                    'mood': 5
                }
            }
        finally:
            self.game.events.end_action()
    
    def go_to_work(self, sim):
        """İşe gitme aksiyonu - yeni job sistemi ile"""
        self.game.events.start_action()
        try:
            # Yeni job sistemi ile çalışma
            work_result = sim.work_at_job()
            
            if not work_result['success']:
                self.game.ui.show_notification(work_result['message'], "warning")
                return {}
            
            # Çalışma saatleri
            work_hours = random.randint(4, 8)
            
            # Başarı mesajını göster
            message = work_result['message']
            if work_result.get('emergency_bonus'):
                message += " Acil durum bonusu aldınız!"
            if work_result.get('variable_income'):
                message += f" Sanat geliriniz bugün {'yüksek' if work_result['salary'] > sim.job_instance.base_salary else 'düşük'}!"
            
            self.game.ui.show_notification(message, "success")
            
            # Aktivite bilgisini döndür
            return {
                'name': f'{sim.job_instance.name} olarak çalışma',
                'duration': work_hours,
                'salary': work_result['salary'],
                'effects': {
                    'energy': -work_result['energy_cost'],
                    'hunger': -20,
                    'mood': -10,
                    'social': -15
                }
            }
        finally:
            self.game.events.end_action()
    
    def find_job(self, sim):
        """İş arama aksiyonu - yeni job sistemi ile"""
        self.game.events.start_action()
        try:
            # Uygun işleri filtrele
            available_jobs = ["Yazılımcı", "Öğretmen", "Doktor", "Sanatçı", "Mühendis"]
            
            # Mevcut işi listeden çıkar
            if sim.job_instance.name in available_jobs:
                available_jobs.remove(sim.job_instance.name)
            
            if not available_jobs:
                self.game.ui.show_notification("Şu an için uygun iş ilanı bulunmuyor.", "warning")
                return {}
            
            # İş seçimi
            questions = [
                inquirer.List('job',
                            message="Başvurmak istediğiniz işi seçin:",
                            choices=available_jobs + ["İptal"]),
            ]
            
            answer = inquirer.prompt(questions)
            
            if answer['job'] == "İptal":
                return {}
                
            # İş başvurusu - yeni job sistemi ile
            sim.change_job(answer['job'])
            
            self.game.ui.show_notification(f"{answer['job']} işine başvurdunuz!", "success")
            
            return {
                'name': 'İş arama',
                'duration': 2,
                'new_job': answer['job']
            }
        finally:
            self.game.events.end_action()
    
    def quit_job(self, sim):
        """İşten istifa etme aksiyonu - yeni job sistemi ile"""
        if sim.job_instance.name == "İşsiz":
            self.game.ui.show_notification("Zaten işsizsiniz!", "warning")
            return {}
            
        self.game.events.start_action()
        try:
            old_job = sim.job_instance.name
            sim.change_job("İşsiz")
            
            self.game.ui.show_notification(f"{old_job} işinden istifa ettiniz!", "info")
            
            return {
                'name': 'İşten istifa etme',
                'duration': 1,
                'old_job': old_job
            }
        finally:
            self.game.events.end_action()
    
    def sleep(self, sim):
        """Uyuma aksiyonu"""
        if self.game.events.is_action_in_progress:
            return {}
        
        self.game.events.start_action()
        try:
            # Uyuma süresi
            hours = random.randint(6, 8)
            
            # İhtiyaçları güncelle
            sim.update_needs(energy=50, mood=20, hunger=-10)
            
            # Aktivite bilgisini döndür
            return {
                'name': 'Uyuma',
                'duration': hours,  # Gerçek uyuma süresini kullan
                'effects': {
                    'energy': 50,
                    'mood': 20,
                    'hunger': -10
                }
            }
        finally:
            self.game.events.end_action()
    
    def take_bath(self, sim):
        """Banyo yapma aksiyonu"""
        if self.game.events.is_action_in_progress:
            return {}
        
        self.game.events.start_action()
        try:
            # İhtiyaçları güncelle
            sim.update_needs(hygiene=60, mood=15, energy=-5)
            
            # Aktivite bilgisini döndür
            return {
                'name': 'Banyo yapma',
                'duration': 2,
                'effects': {
                    'hygiene': 60,
                    'mood': 15,
                    'energy': -5
                }
            }
        finally:
            self.game.events.end_action()
    
    def socialize(self, sim):
        """Sosyalleşme aksiyonu"""
        if self.game.events.is_action_in_progress:
            return {}
            
        self.game.events.start_action()
        try:
            # Sosyalleşme seçenekleri
            social_action = self.game.ui.show_social_menu()
            
            if social_action == "Geri Dön":
                return {}
                
            # Aktivite bilgisi
            activity_info = {
                'name': social_action,
                'duration': random.randint(2, 4),
                'effects': {
                    'social': random.randint(20, 40),
                    'mood': random.randint(10, 30),
                    'energy': -random.randint(10, 20)
                }
            }
            
            # İhtiyaçları güncelle
            sim.update_needs(
                social=activity_info['effects']['social'],
                mood=activity_info['effects']['mood'],
                energy=activity_info['effects']['energy']
            )
            
            # İlişki oluşturma veya geliştirme
            if social_action == "Flört Et" and random.random() > 0.3:
                # Rastgele bir isim seç
                names = ["Ayşe", "Mehmet", "Zeynep", "Ali", "Fatma", "Ahmet"]
                name = random.choice(names)
                
                # İlişki oluştur veya güncelle
                if name not in sim.relationships:
                    sim.relationships[name] = {
                        'level': random.randint(20, 40),
                        'type': 'Flört'
                    }
                else:
                    sim.relationships[name]['level'] += random.randint(5, 15)
                    if sim.relationships[name]['level'] > 70:
                        sim.relationships[name]['type'] = 'Sevgili'
                
                self.game.ui.show_notification(f"{name} ile ilişkiniz gelişti!", "success")
                
            return activity_info
        finally:
            self.game.events.end_action()
    
    def meet_friends(self, sim):
        """Arkadaşlarla buluşma aksiyonu"""
        if self.game.events.is_action_in_progress:
            return {}
            
        self.game.events.start_action()
        try:
            # İhtiyaçları güncelle
            sim.update_needs(social=40, mood=20, energy=-15, hunger=-10)
            
            # Aktivite bilgisini döndür
            return {
                'name': 'Arkadaşlarla buluşma',
                'duration': 3,
                'effects': {
                    'social': 40,
                    'mood': 20,
                    'energy': -15,
                    'hunger': -10
                }
            }
        finally:
            self.game.events.end_action()
    
    def flirt(self, sim):
        """Flört etme aksiyonu"""
        if self.game.events.is_action_in_progress:
            return {}
            
        self.game.events.start_action()
        try:
            # İhtiyaçları güncelle
            sim.update_needs(social=30, mood=25, energy=-10)
            
            # Rastgele bir isim seç
            names = ["Ayşe", "Mehmet", "Zeynep", "Ali", "Fatma", "Ahmet"]
            name = random.choice(names)
            
            # İlişki oluştur veya güncelle
            if name not in sim.relationships:
                sim.relationships[name] = {
                    'level': random.randint(20, 40),
                    'type': 'Flört'
                }
            else:
                sim.relationships[name]['level'] += random.randint(5, 15)
                if sim.relationships[name]['level'] > 70:
                    sim.relationships[name]['type'] = 'Sevgili'
            
            # Aktivite bilgisini döndür
            return {
                'name': 'Flört etme',
                'duration': 2,
                'effects': {
                    'social': 30,
                    'mood': 25,
                    'energy': -10
                },
                'relationship': {
                    'name': name,
                    'level': sim.relationships[name]['level'],
                    'type': sim.relationships[name]['type']
                }
            }
        finally:
            self.game.events.end_action()
    
    def go_to_party(self, sim):
        """Partiye gitme aksiyonu"""
        if self.game.events.is_action_in_progress:
            return {}
            
        self.game.events.start_action()
        try:
            # Parti maliyeti
            cost = random.randint(50, 100)
            sim.money -= cost
            
            # İhtiyaçları güncelle
            sim.update_needs(social=50, mood=30, energy=-30, hygiene=-20)
            
            # Aktivite bilgisini döndür
            return {
                'name': 'Partiye gitme',
                'duration': 4,
                'cost': cost,
                'effects': {
                    'social': 50,
                    'mood': 30,
                    'energy': -30,
                    'hygiene': -20
                }
            }
        finally:
            self.game.events.end_action()
    
    def save_game(self, sim):
        """Oyunu kaydetme aksiyonu"""
        self.game.save_game() 