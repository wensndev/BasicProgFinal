from abc import ABC, abstractmethod
from models.sim import Sim
import random

class CharacterType(ABC):
    """Karakter tipi için ana sınıf"""
    
    @abstractmethod
    def get_personality_traits(self) -> dict:
        """Kişilik özelliklerini döndürür"""
        pass
    
    @abstractmethod
    def get_starting_bonuses(self) -> dict:
        """Başlangıç bonuslarını döndürür"""
        pass
    
    @abstractmethod
    def get_special_abilities(self) -> list:
        """Özel yetenekleri döndürür"""
        pass

class AmbitiousSim(Sim):
    """Hırslı karakter tipi"""
    
    def __init__(self, name, gender, age=25):
        super().__init__(name, gender, age)
        # Hırslı karakterler işe odaklı
        self.job_satisfaction = 70  # Yüksek iş memnuniyeti
        self.money += 500  # Ekstra başlangıç parası
        self.character_type = "Hırslı"
    
    def work_at_job(self):
        """Hırslı karakterler çalışırken bonus alır"""
        result = super().work_at_job()
        if result['success']:
            # %20 bonus deneyim
            if 'experience_gained' in result:
                result['experience_gained'] = int(result['experience_gained'] * 1.2)
                result['message'] += " (Hırslı bonus: +%20 deneyim)"
        return result

class SocialSim(Sim):
    """Sosyal karakter tipi"""
    
    def __init__(self, name, gender, age=25):
        super().__init__(name, gender, age)
        # Sosyal karakterler ilişkiler konusunda başarılı
        self.social = 80  # Yüksek sosyal seviye
        self.job_satisfaction = 50  # Orta seviye iş memnuniyeti
        self.character_type = "Sosyal"
    
    def update_relationship(self, other_sim, change, event=None):
        """Sosyal karakterler ilişkilerde bonus alır"""
        # %50 bonus ilişki gelişimi
        bonus_change = int(change * 1.5) if change > 0 else change
        super().update_relationship(other_sim, bonus_change, event)

class CreativeSim(Sim):
    """Yaratıcı karakter tipi"""
    
    def __init__(self, name, gender, age=25):
        super().__init__(name, gender, age)
        # Yaratıcı karakterler sanat işlerinde başarılı
        self.mood = 80  # Yüksek ruh hali
        self.job_satisfaction = 60  # Yaratıcı işlerde daha mutlu
        self.character_type = "Yaratıcı"
    
    def work_at_job(self):
        """Yaratıcı karakterler sanat işlerinde bonus alır"""
        result = super().work_at_job()
        if result['success'] and self.job_instance.name == "Sanatçı":
            # Sanatçı işinde %30 daha fazla para
            result['salary'] = int(result['salary'] * 1.3)
            result['message'] += " (Yaratıcı bonus: +%30 gelir)"
        return result

class BalancedSim(Sim):
    """Dengeli karakter tipi"""
    
    def __init__(self, name, gender, age=25):
        super().__init__(name, gender, age)
        # Dengeli karakterler her alanda orta seviyede
        self.character_type = "Dengeli"
        self.job_satisfaction = 55  # Biraz daha yüksek iş memnuniyeti
        # Tüm istatistikleri biraz artır
        self.energy = min(100, self.energy + 10)
        self.mood = min(100, self.mood + 10)
        self.social = min(100, self.social + 10)
    
    def update_needs(self, energy=0, hunger=0, hygiene=0, mood=0, social=0):
        """Dengeli karakterler daha yavaş yorulur"""
        # Negatif etkileri %20 azalt
        adjusted_energy = energy * 0.8 if energy < 0 else energy
        adjusted_hunger = hunger * 0.8 if hunger < 0 else hunger
        adjusted_hygiene = hygiene * 0.8 if hygiene < 0 else hygiene
        
        super().update_needs(adjusted_energy, adjusted_hunger, adjusted_hygiene, mood, social)

class CharacterFactory:
    """Karakter tipi factory'si"""
    
    @staticmethod
    def create_character(character_type: str, name: str, gender: str, age: int) -> Sim:
        """Karakter tipine göre uygun Sim oluşturur"""
        type_map = {
            "Hırslı": AmbitiousSim,
            "Sosyal": SocialSim,
            "Yaratıcı": CreativeSim,
            "Dengeli": BalancedSim
        }
        
        character_class = type_map.get(character_type, BalancedSim)
        return character_class(name, gender, age)
    
    @staticmethod
    def get_available_types() -> list:
        """Mevcut karakter tiplerini döndürür"""
        return ["Hırslı", "Sosyal", "Yaratıcı", "Dengeli"]
    
    @staticmethod
    def get_type_description(character_type: str) -> str:
        """Karakter tipi açıklaması"""
        descriptions = {
            "Hırslı": "İş hayatında başarılı, hızlı deneyim kazanır",
            "Sosyal": "İlişkilerde yetenekli, sosyal bonuslar alır", 
            "Yaratıcı": "Sanat işlerinde başarılı, yüksek ruh hali",
            "Dengeli": "Her alanda dengeli, yavaş yorulur"
        }
        return descriptions.get(character_type, "Standart karakter tipi") 