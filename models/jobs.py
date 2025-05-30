from abc import ABC, abstractmethod
import random

class Job(ABC):
    """Ana Job sınıfı - tüm meslekler için temel sınıf"""
    
    def __init__(self, name: str, base_salary: int, energy_cost: int, 
                 experience_gain: int, promotion_threshold: int):
        self.name = name
        self.base_salary = base_salary
        self.energy_cost = energy_cost
        self.experience_gain = experience_gain
        self.promotion_threshold = promotion_threshold
        self.level = 1
        self.experience = 0
        
    @abstractmethod
    def get_description(self) -> str:
        """Her meslek kendi açıklamasını döndürür"""
        pass
    
    @abstractmethod
    def get_skills(self) -> list:
        """Her meslek kendi becerilerini döndürür"""
        pass
    
    def work(self) -> dict:
        """Çalışma sonucu döndürür"""
        salary = self.calculate_salary()
        self.experience += self.experience_gain
        
        return {
            'salary': salary,
            'energy_cost': self.energy_cost,
            'experience_gained': self.experience_gain,
            'can_promote': self.can_promote()
        }
    
    def calculate_salary(self) -> int:
        """Seviyeye göre maaş hesaplar"""
        return int(self.base_salary * (1 + (self.level - 1) * 0.2))
    
    def can_promote(self) -> bool:
        """Terfi edilebilir mi kontrol eder"""
        return self.experience >= self.promotion_threshold * self.level
    
    def promote(self) -> bool:
        """Terfi işlemi"""
        if self.can_promote():
            self.level += 1
            self.experience = 0
            return True
        return False

class UnemployedJob(Job):
    """İşsizlik durumu"""
    
    def __init__(self):
        super().__init__("İşsiz", 0, 0, 0, 0)
    
    def get_description(self) -> str:
        return "Şu an işsizsiniz."
    
    def get_skills(self) -> list:
        return []

class TechJob(Job):
    """Teknoloji sektörü meslekleri"""
    
    def __init__(self, job_type: str):
        if job_type == "Yazılımcı":
            super().__init__("Yazılımcı", 2000, 15, 8, 200)
        elif job_type == "Mühendis":
            super().__init__("Mühendis", 3000, 18, 9, 220)
    
    def get_description(self) -> str:
        if self.name == "Yazılımcı":
            return f"Yazılım geliştirici olarak çalışıyorsunuz. (Seviye {self.level})"
        return f"Mühendis olarak çalışıyorsunuz. (Seviye {self.level})"
    
    def get_skills(self) -> list:
        if self.name == "Yazılımcı":
            return ["Python", "Veritabanı", "Web Geliştirme"]
        return ["Tasarım", "Proje Yönetimi", "Teknik Analiz"]

class HealthcareJob(Job):
    """Sağlık sektörü meslekleri"""
    
    def __init__(self):
        super().__init__("Doktor", 4000, 25, 12, 300)
    
    def get_description(self) -> str:
        return f"Hastanede doktor olarak çalışıyorsunuz. (Seviye {self.level})"
    
    def get_skills(self) -> list:
        return ["Teşhis", "Tedavi", "Hasta Bakımı"]
    
    def work(self) -> dict:
        """Doktorlar için özel çalışma bonusu"""
        result = super().work()
        # Doktorlar bazen acil durum bonusu alabilir
        if random.random() < 0.3:
            result['salary'] *= 1.5
            result['emergency_bonus'] = True
        return result

class EducationJob(Job):
    """Eğitim sektörü meslekleri"""
    
    def __init__(self):
        super().__init__("Öğretmen", 2500, 20, 10, 250)
    
    def get_description(self) -> str:
        return f"Okulda öğretmen olarak çalışıyorsunuz. (Seviye {self.level})"
    
    def get_skills(self) -> list:
        return ["Pedagoji", "Sınıf Yönetimi", "Müfredat Geliştirme"]

class CreativeJob(Job):
    """Yaratıcı sektör meslekleri"""
    
    def __init__(self):
        super().__init__("Sanatçı", 1500, 12, 7, 150)
    
    def get_description(self) -> str:
        return f"Serbest sanatçı olarak çalışıyorsunuz. (Seviye {self.level})"
    
    def get_skills(self) -> list:
        return ["Yaratıcılık", "Tasarım", "Sergi Yönetimi"]
    
    def work(self) -> dict:
        """Sanatçılar için değişken gelir"""
        result = super().work()
        # Sanatçıların geliri daha değişken
        multiplier = random.uniform(0.5, 2.0)
        result['salary'] = int(result['salary'] * multiplier)
        result['variable_income'] = True
        return result

class JobFactory:
    """Job nesneleri oluşturmak için factory sınıfı"""
    
    @staticmethod
    def create_job(job_name: str) -> Job:
        """Job adına göre uygun job nesnesi oluşturur"""
        job_map = {
            "İşsiz": UnemployedJob,
            "Yazılımcı": lambda: TechJob("Yazılımcı"),
            "Mühendis": lambda: TechJob("Mühendis"),
            "Doktor": HealthcareJob,
            "Öğretmen": EducationJob,
            "Sanatçı": CreativeJob
        }
        
        if job_name in job_map:
            job_class = job_map[job_name]
            return job_class() if callable(job_class) else job_class
        else:
            return UnemployedJob() 