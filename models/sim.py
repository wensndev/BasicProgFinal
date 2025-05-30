import json
import os
import random
from datetime import datetime, timedelta
from models.jobs import Job, JobFactory
import time

class Sim:
    def __init__(self, name, gender, age=25):
        self.name = name
        self.gender = gender
        self.age = age
        self.mood = 70.00
        self.energy = 100.00
        self.hunger = 70.00
        self.hygiene = 100.00
        self.social = 50.00
        self.money = 1000.00
        
        # Job sistemi - yeni yaklaşım
        self.job_instance = JobFactory.create_job("İşsiz")
        self.job = self.job_instance.name  # Geriye uyumluluk için
        self.job_level = 1  # İş seviyesi
        self.job_experience = 0  # İş deneyimi
        self.job_satisfaction = 50  # İş memnuniyeti (0-100)
        
        self.relationships = {}
        self.relationship_levels = {
            "Yabancı": 0,
            "Tanıdık": 20,
            "Arkadaş": 40,
            "İyi Arkadaş": 60,
            "En İyi Arkadaş": 80,
            "Sevgili": 90
        }
        self.relationship_events = []  # İlişki olaylarını tutacak liste
        self.last_interaction = {}  # Son etkileşim zamanlarını tutacak sözlük
        self.relationship_memory = {}  # İlişki anılarını tutacak sözlük
        self.compatibility = {}  # Karakter uyumluluklarını tutacak sözlük
        self.social_traits = []  # Sosyal özellikleri tutacak liste
        self.relationship_goals = {}  # İlişki hedeflerini tutacak sözlük
        self.current_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        self.state = "normal"  # normal, depressed, flirty, etc.
        self.game_time = None  # Game sınıfından alınacak
        self.last_warning_time = None
        self.critical_states = set()  # Aktif kritik durumları tutar
        self.is_critical = False  # Kritik durum kontrolü için
        self.has_warnings = False  # Uyarı durumu kontrolü için
        self._critical_attributes = set()  # Kritik durumda olan özellikler
        
        # Ölüm mekanizması
        self.is_alive = True  # Canlı mı?
        self.death_reason = None  # Ölüm sebebi
        self.critical_time_counters = {}  # Her kritik durum için süre sayacı
        self.death_thresholds = {
            'energy': 15,     # 15 saniye kritik seviyede kalırsa ölür
            'hunger': 30,     # 30 saniye kritik seviyede kalırsa ölür
            'hygiene': 90,    # 1.5 dakika kritik seviyede kalırsa ölür
            'mood': 45,       # 45 saniye kritik seviyede kalırsa ölür
            'social': 120     # 2 dakika kritik seviyede kalırsa ölür
        }
        
        # Kritik durum eşikleri ve etkileri
        self.critical_thresholds = {
            'energy': {
                'warning': 20,  # 20'den düşükse uyarı
                'critical': 10,  # 10'dan düşükse kritik
                'effects': {
                    'warning': lambda: self._handle_critical_state('energy', 'warning', 
                        "Yorgunsunuz! Dinlenmeniz gerekiyor.", -5, 0, 0),
                    'critical': lambda: self._handle_critical_state('energy', 'critical',
                        "AŞIRI YORGUNLUK! Hemen dinlenmelisiniz!", -10, -5, -100)
                }
            },
            'hunger': {
                'warning': 20,  # 20'den düşükse uyarı (açlık)
                'critical': 10,  # 10'dan düşükse kritik
                'effects': {
                    'warning': lambda: self._handle_critical_state('hunger', 'warning',
                        "Açsınız! Yemek yemelisiniz.", -5, -5, 0),
                    'critical': lambda: self._handle_critical_state('hunger', 'critical',
                        "AÇLIKTAN BAYILMAK ÜZERESİNİZ! Hemen yemek yemelisiniz!", -15, -10, -200)
                }
            },
            'hygiene': {
                'warning': 20,  # 20'den düşükse uyarı
                'critical': 10,  # 10'dan düşükse kritik
                'effects': {
                    'warning': lambda: self._handle_critical_state('hygiene', 'warning',
                        "Kirli hissediyorsunuz! Banyo yapmalısınız.", -5, -5, 0),
                    'critical': lambda: self._handle_critical_state('hygiene', 'critical',
                        "DAYANILMAZ KİRLİLİK! Hemen banyo yapmalısınız!", -20, -10, -150)
                }
            },
            'mood': {
                'warning': 20,  # 20'den düşükse uyarı
                'critical': 10,  # 10'dan düşükse kritik
                'effects': {
                    'warning': lambda: self._handle_critical_state('mood', 'warning',
                        "Kendinizi kötü hissediyorsunuz.", -5, -5, 0),
                    'critical': lambda: self._handle_critical_state('mood', 'critical',
                        "DEPRESYONA GİRİYORSUNUZ! Bir şeyler yapmalısınız!", -10, -15, -300)
                }
            },
            'social': {
                'warning': 20,  # 20'den düşükse uyarı
                'critical': 10,  # 10'dan düşükse kritik
                'effects': {
                    'warning': lambda: self._handle_critical_state('social', 'warning',
                        "Yalnızlık hissetmeye başladınız.", -5, -5, 0),
                    'critical': lambda: self._handle_critical_state('social', 'critical',
                        "SOSYAL İZOLASYON! İnsanlarla görüşmelisiniz!", -15, -10, -250)
                }
            }
        }
    
    def _check_critical_state(self, attribute):
        """Bir özelliğin kritik durumda olup olmadığını kontrol eder"""
        if attribute not in self.critical_thresholds:
            return False
            
        value = getattr(self, attribute)
        thresholds = self.critical_thresholds[attribute]
        
        if value <= thresholds['critical']:
            return True
        return False
    
    def _update_critical_state(self):
        """Kritik durumları günceller"""
        old_critical = self.is_critical
        self._critical_attributes.clear()
        
        # Tüm özellikleri kontrol et
        for attr in self.critical_thresholds.keys():
            if self._check_critical_state(attr):
                self._critical_attributes.add(attr)
        
        # Kritik durum değiştiyse güncelle
        self.is_critical = len(self._critical_attributes) > 0
        
        # Ölüm kontrolü yap
        self._check_death_conditions()
    
    def _check_death_conditions(self):
        """Ölüm koşullarını kontrol eder ve gerekirse ölümü gerçekleştirir"""
        if not self.is_alive:
            return
            
        current_time = time.time()
        
        # Her kritik özellik için süre sayacını güncelle
        for attr in self.critical_thresholds.keys():
            if self._check_critical_state(attr):
                # Eğer bu özellik için sayaç yoksa başlat
                if attr not in self.critical_time_counters:
                    self.critical_time_counters[attr] = current_time
                    
                # Ne kadar süredir kritik seviyede?
                critical_duration = current_time - self.critical_time_counters[attr]
                
                # Ölüm eşiğini aştı mı?
                if critical_duration >= self.death_thresholds[attr]:
                    self._die(attr)
                    return
            else:
                # Kritik seviyede değilse sayacı sıfırla
                if attr in self.critical_time_counters:
                    del self.critical_time_counters[attr]
    
    def _die(self, cause_attribute):
        """Karakterin ölümünü gerçekleştirir"""
        self.is_alive = False
        
        # Ölüm sebeplerini belirle
        death_reasons = {
            'energy': "Aşırı yorgunluk nedeniyle kalp krizi",
            'hunger': "Açlıktan ölme",
            'hygiene': "Hastalık ve enfeksiyon",
            'mood': "Depresyon ve intihar",
            'social': "Sosyal izolasyon ve zihinsel çöküş"
        }
        
        self.death_reason = death_reasons.get(cause_attribute, "Bilinmeyen sebep")
        
        # Ölüm zamanını kaydet
        if self.game_time:
            self.death_time = self.game_time
        else:
            self.death_time = datetime.now()
    
    def get_death_info(self):
        """Ölüm bilgilerini döndürür"""
        if self.is_alive:
            return None
            
        return {
            'name': self.name,
            'death_reason': self.death_reason,
            'death_time': self.death_time.strftime("%d %B %Y, %H:%M") if hasattr(self, 'death_time') else "Bilinmiyor",
            'age_at_death': self.age,
            'final_stats': {
                'money': self.money,
                'job': self.job,
                'relationships': len(self.relationships)
            }
        }
    
    def can_perform_action(self):
        """Aksiyon yapabilir mi kontrol eder"""
        return self.is_alive
    
    def _check_warning_state(self, attribute):
        """Bir özelliğin uyarı durumunda olup olmadığını kontrol eder"""
        if attribute not in self.critical_thresholds:
            return False
            
        value = getattr(self, attribute)
        thresholds = self.critical_thresholds[attribute]
        
        # Sadece warning seviyesinde olup critical seviyesinde olmayanları kontrol et
        if value <= thresholds['warning'] and value > thresholds['critical']:
            return True
        return False
    
    def get_warning_attributes(self):
        """Uyarı durumunda olan özellikleri döndürür"""
        warning_attributes = []
        
        # Tüm özellikleri kontrol et
        for attr in self.critical_thresholds.keys():
            if self._check_warning_state(attr):
                warning_attributes.append(attr)
        
        # Uyarı durumu güncelle
        self.has_warnings = len(warning_attributes) > 0
        
        return warning_attributes
    
    def update_needs(self, energy=0, hunger=0, hygiene=0, mood=0, social=0):
        """İhtiyaçları günceller ve kritik durumları kontrol eder"""
        # Önce mevcut değerleri al
        current_energy = self.energy
        current_hunger = self.hunger
        current_hygiene = self.hygiene
        current_mood = self.mood
        current_social = self.social
        
        # Değişimleri uygula ve sınırla - round ile 2 ondalık haneye yuvarla
        self.energy = round(max(0, min(100, current_energy + energy)), 2)
        self.hunger = round(max(0, min(100, current_hunger + hunger)), 2)
        self.hygiene = round(max(0, min(100, current_hygiene + hygiene)), 2)
        self.mood = round(max(0, min(100, current_mood + mood)), 2)
        self.social = round(max(0, min(100, current_social + social)), 2)
        
        # Kritik durumları güncelle
        self._update_critical_state()
        
        # Uyarı durumlarını kontrol et
        self.get_warning_attributes()
    
    def _handle_critical_state(self, attribute, level, message, mood_effect, energy_effect, money_effect):
        """Kritik durum etkilerini uygular"""
        # Son uyarıdan bu yana en az 5 dakika geçmiş olmalı
        if self.last_warning_time and self.game_time:
            time_diff = (self.game_time - self.last_warning_time).total_seconds()
            if time_diff < 300:  # 5 dakika
                return
            
        self.last_warning_time = self.game_time
        
        # Etkileri uygula
        self.mood += mood_effect
        self.energy += energy_effect
        self.money += money_effect
        
        # Değerleri sınırla
        self.mood = max(0, min(100, self.mood))
        self.energy = max(0, min(100, self.energy))
    
    def get_status(self):
        """Sim'in durumunu döndürür"""
        # Kritik ve uyarı durumlarını güncelle
        self._update_critical_state()
        self.get_warning_attributes()
        
        # Kritik durumları kontrol et
        warnings = []
        for attr in self._critical_attributes:
            thresholds = self.critical_thresholds[attr]
            value = getattr(self, attr)
            if value <= thresholds['critical']:
                warnings.append(f"{attr} kritik seviyede")
        
        # Uyarı durumlarını kontrol et
        warning_attributes = self.get_warning_attributes()
        for attr in warning_attributes:
            warnings.append(f"{attr} düşük seviyede")
        
        # Durum bilgisini oluştur
        status = {
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'mood': self.mood,
            'energy': self.energy,
            'hunger': self.hunger,
            'hygiene': self.hygiene,
            'social': self.social,
            'money': self.money,
            'job': self.job,
            'state': self.state,
            'game_time': self.game_time.strftime("%d %B %Y, %H:%M") if self.game_time else "Bilinmiyor",
            'relationships': self.relationships
        }
        
        # Kritik durumlar veya uyarılar varsa ekle
        if warnings:
            status['warnings'] = warnings
            
        return status
    
    def update_stats_during_activity(self, activity_info, step, total_steps):
        """Aktivite sırasında istatistikleri günceller"""
        if 'effects' not in activity_info:
            return
            
        # Her adımda etkilerin bir kısmını uygula
        effects = activity_info['effects']
        progress_ratio = (step + 1) / total_steps
        
        # Etkileri hesapla ve uygula
        for attr, value in effects.items():
            if hasattr(self, attr):
                # Toplam etkinin progress_ratio kadarını uygula
                step_effect = value * progress_ratio / total_steps
                current = getattr(self, attr)
                
                if attr == 'money':
                    # Para için doğrudan ekle/çıkar - round ile 2 ondalık haneye yuvarla
                    if step == total_steps - 1:  # Son adımda kalan tüm parayı ekle
                        setattr(self, attr, round(current + (value - (step * step_effect)), 2))
                    else:
                        setattr(self, attr, round(current + step_effect, 2))
                else:
                    # Diğer özellikler için sınırla (0-100 arası) ve round et
                    new_value = round(max(0, min(100, current + step_effect)), 2)
                    setattr(self, attr, new_value)
    
    def advance_time(self, hours=1):
        """Zamanı ilerletir ve ihtiyaçları günceller"""
        if not self.game_time:
            return
            
        # İhtiyaçları güncelle (zaman ilerlemeden)
        energy_change = -2 * hours
        hunger_change = -3 * hours
        hygiene_change = -1 * hours
        social_change = -1 * hours
        
        self.update_needs(
            energy=energy_change,
            hunger=hunger_change,
            hygiene=hygiene_change,
            social=social_change
        )
    
    def calculate_mood(self):
        """Ruh halini diğer faktörlere göre hesaplar"""
        base_mood = 50  # Temel ruh hali
        
        # Diğer faktörlerin etkisi
        energy_factor = self.energy * 0.2
        hunger_factor = self.hunger * 0.2
        hygiene_factor = self.hygiene * 0.1
        social_factor = self.social * 0.1
        
        # İş memnuniyeti etkisi
        job_factor = 0
        if self.job and self.job != "İşsiz":
            job_factor = self.job_satisfaction * 0.1
        
        # Toplam ruh hali
        total_mood = base_mood + energy_factor + hunger_factor + hygiene_factor + social_factor + job_factor
        
        # Sınırla ve güncelle - round ile 2 ondalık haneye yuvarla
        self.mood = round(max(0, min(100, total_mood)), 2)
        
        return self.mood
    
    def save(self):
        """Sim'i kaydeder - yeni job sistemi ile"""
        try:
            data = {
                'name': self.name,
                'gender': self.gender,
                'age': self.age,
                'mood': self.mood,
                'energy': self.energy,
                'hunger': self.hunger,
                'hygiene': self.hygiene,
                'social': self.social,
                'money': self.money,
                'job': self.job,
                'job_level': self.job_level,
                'job_experience': self.job_experience,
                'job_satisfaction': self.job_satisfaction,
                # Yeni job sistemi verileri
                'job_instance_name': self.job_instance.name,
                'job_instance_level': self.job_instance.level,
                'job_instance_experience': self.job_instance.experience,
                'relationships': self.relationships,
                'state': self.state,
                'game_time': self.game_time.strftime("%Y-%m-%d %H:%M:%S") if self.game_time else None
            }
            
            with open(f"save_{self.name}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Kaydetme hatası: {e}")
            return False
    
    @classmethod
    def load(cls, name):
        """Kaydedilmiş Sim'i yükler - yeni job sistemi ile"""
        try:
            with open(f"save_{name}.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sim = cls(data['name'], data['gender'], data['age'])
            sim.mood = round(data['mood'], 2)
            sim.energy = round(data['energy'], 2)
            sim.hunger = round(data['hunger'], 2)
            sim.hygiene = round(data['hygiene'], 2)
            sim.social = round(data['social'], 2)
            sim.money = round(data['money'], 2)
            sim.job = data['job']
            sim.job_level = data['job_level']
            sim.job_experience = data['job_experience']
            sim.job_satisfaction = data['job_satisfaction']
            sim.relationships = data['relationships']
            sim.state = data['state']
            
            # Yeni job sistemi verilerini yükle
            if 'job_instance_name' in data:
                sim.job_instance = JobFactory.create_job(data['job_instance_name'])
                sim.job_instance.level = data.get('job_instance_level', 1)
                sim.job_instance.experience = data.get('job_instance_experience', 0)
                sim.job = sim.job_instance.name  # Senkronize et
            else:
                # Eski kayıt dosyaları için geriye uyumluluk
                sim.job_instance = JobFactory.create_job(data['job'])
            
            # Zamanı yükle
            if data['game_time']:
                sim.game_time = datetime.strptime(data['game_time'], "%Y-%m-%d %H:%M:%S")
            
            return sim
        except Exception as e:
            print(f"Yükleme hatası: {e}")
            return None
    
    def _get_state(self):
        """Sim'in durumunu belirler"""
        if self.mood < 20:
            return "depressed"
        elif self.energy < 20:
            return "exhausted"
        elif self.hunger < 20:
            return "hungry"
        elif self.hygiene < 20:
            return "dirty"
        elif self.social < 20:
            return "lonely"
        elif self.mood > 80:
            return "happy"
        else:
            return "normal"
    
    def get_job_info(self):
        """İş bilgilerini döndürür - yeni job sistemi ile"""
        return {
            'title': self.job_instance.name,
            'level': self.job_instance.level,
            'base_salary': self.job_instance.base_salary,
            'salary': self.job_instance.calculate_salary(),
            'experience': self.job_instance.experience,
            'next_level': self.job_instance.promotion_threshold * self.job_instance.level,
            'satisfaction': self.job_satisfaction,
            'description': self.job_instance.get_description(),
            'skills': self.job_instance.get_skills()
        }
    
    def change_job(self, new_job_name: str):
        """Mesleği değiştirir"""
        self.job_instance = JobFactory.create_job(new_job_name)
        self.job = self.job_instance.name  # Geriye uyumluluk için
    
    def work_at_job(self):
        """İş yapar ve sonuçları döndürür"""
        if self.job_instance.name == "İşsiz":
            return {
                'success': False,
                'message': "İşsizsiniz! Önce bir iş bulmanız gerekiyor.",
                'salary': 0,
                'energy_cost': 0
            }
        
        # Yeterli enerji kontrolü
        if self.energy < self.job_instance.energy_cost:
            return {
                'success': False,
                'message': "Çalışmak için yeterli enerjiniz yok!",
                'salary': 0,
                'energy_cost': 0
            }
        
        # İş sonuçlarını al
        work_result = self.job_instance.work()
        
        # Sim'in değerlerini güncelle
        self.energy -= work_result['energy_cost']
        self.money += work_result['salary']
        
        # Terfi kontrolü
        promotion_message = ""
        if work_result['can_promote'] and self.job_instance.promote():
            promotion_message = f" Tebrikler! {self.job_instance.level}. seviyeye terfi ettiniz!"
        
        return {
            'success': True,
            'message': f"İş gününüz tamamlandı!{promotion_message}",
            'salary': work_result['salary'],
            'energy_cost': work_result['energy_cost'],
            'experience_gained': work_result['experience_gained'],
            'emergency_bonus': work_result.get('emergency_bonus', False),
            'variable_income': work_result.get('variable_income', False)
        }
    
    def add_relationship(self, other_sim, initial_level=0):
        """Yeni bir ilişki ekler"""
        if other_sim.name not in self.relationships:
            # Uyumluluk hesapla
            compatibility = random.randint(30, 90)
            
            # İlişki türünü belirle
            relationship_type = "Tanıdık"
            for level_name, level_value in self.relationship_levels.items():
                if initial_level >= level_value:
                    relationship_type = level_name
            
            # İlişkiyi ekle
            self.relationships[other_sim.name] = {
                'level': initial_level,
                'type': relationship_type,
                'compatibility': compatibility,
                'goals': [],
                'memory': [],
                'interactions': 0
            }
            
            # Karşılıklı ilişki
            if self.name not in other_sim.relationships:
                other_sim.add_relationship(self, initial_level)
    
    def update_relationship(self, other_sim, change, event=None):
        """İlişkiyi günceller"""
        if other_sim.name not in self.relationships:
            self.add_relationship(other_sim, max(0, change))
            return
        
        # İlişki seviyesini güncelle
        self.relationships[other_sim.name]['level'] += change
        self.relationships[other_sim.name]['level'] = max(0, min(100, self.relationships[other_sim.name]['level']))
        
        # İlişki türünü güncelle
        current_level = self.relationships[other_sim.name]['level']
        for level_name, level_value in sorted(self.relationship_levels.items(), key=lambda x: x[1], reverse=True):
            if current_level >= level_value:
                self.relationships[other_sim.name]['type'] = level_name
                break
        
        # Etkileşim sayısını artır
        self.relationships[other_sim.name]['interactions'] += 1
        
        # Olay varsa kaydet
        if event:
            self.relationships[other_sim.name]['memory'].append({
                'event': event,
                'time': self.game_time.strftime("%Y-%m-%d %H:%M") if self.game_time else "Bilinmiyor",
                'level_change': change
            })
        
        # Hedefleri kontrol et
        self.check_relationship_goals(other_sim)
        
        # Karşılıklı ilişkiyi güncelle
        if self.name in other_sim.relationships:
            other_sim.update_relationship(self, change * 0.8, event)
    
    def get_relationship_info(self, other_sim):
        """İlişki bilgilerini döndürür"""
        if other_sim.name not in self.relationships:
            return None
        
        rel = self.relationships[other_sim.name]
        
        return {
            'name': other_sim.name,
            'level': rel['level'],
            'type': rel['type'],
            'compatibility': rel['compatibility'],
            'interactions': rel['interactions'],
            'recent_events': rel['memory'][-5:] if rel['memory'] else [],
            'goals': rel['goals']
        }
    
    def add_relationship_goal(self, other_sim, goal):
        """İlişki hedefi ekler"""
        if other_sim.name not in self.relationships:
            self.add_relationship(other_sim)
        
        if goal not in self.relationships[other_sim.name]['goals']:
            self.relationships[other_sim.name]['goals'].append(goal)
    
    def check_relationship_goals(self, other_sim):
        """İlişki hedeflerini kontrol eder"""
        if other_sim.name not in self.relationships or not self.relationships[other_sim.name]['goals']:
            return
        
        rel = self.relationships[other_sim.name]
        completed_goals = []
        
        for goal in rel['goals']:
            # Hedef kontrolü
            if goal == "Arkadaş Ol" and rel['level'] >= self.relationship_levels["Arkadaş"]:
                completed_goals.append(goal)
            elif goal == "İyi Arkadaş Ol" and rel['level'] >= self.relationship_levels["İyi Arkadaş"]:
                completed_goals.append(goal)
            elif goal == "En İyi Arkadaş Ol" and rel['level'] >= self.relationship_levels["En İyi Arkadaş"]:
                completed_goals.append(goal)
            elif goal == "Flört Et" and rel['type'] == "Flört":
                completed_goals.append(goal)
            elif goal == "Sevgili Ol" and rel['level'] >= self.relationship_levels["Sevgili"]:
                completed_goals.append(goal)
        
        # Tamamlanan hedefleri kaldır
        for goal in completed_goals:
            rel['goals'].remove(goal)
            
            # Hedef tamamlandığında anı ekle
            rel['memory'].append({
                'event': f"Hedef tamamlandı: {goal}",
                'time': self.game_time.strftime("%Y-%m-%d %H:%M") if self.game_time else "Bilinmiyor",
                'level_change': 0
            }) 