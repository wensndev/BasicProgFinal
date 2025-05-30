import random
from datetime import datetime, time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class Events:
    def __init__(self, game):
        self.game = game
        self.console = game.ui.console
        self.last_event_time = None
        self.event_cooldown = 300  # 5 dakika
        self.is_action_in_progress = False
        
        # Günün saatlerine göre event olasılıkları
        self.time_based_probabilities = {
            'morning': 0.1,    # %10
            'afternoon': 0.15, # %15
            'evening': 0.2,    # %20
            'night': 0.05     # %5
        }
        
        # Event kategorileri ve olasılıkları
        self.event_categories = {
            'work': {
                'probability': 0.2,  # %20
                'events': [
                    {
                        'name': 'İşten Zam',
                        'description': 'Patronunuz performansınızdan memnun ve size zam teklif ediyor!',
                        'condition': lambda sim: sim.job != "İşsiz" and sim.job_satisfaction > 70,
                        'effect': lambda sim: {'money': random.randint(500, 1000)}
                    },
                    {
                        'name': 'İşten Kovulma Riski',
                        'description': 'Performansınız düşük, işinizden olabilirsiniz!',
                        'condition': lambda sim: sim.job != "İşsiz" and sim.job_satisfaction < 30,
                        'effect': lambda sim: {'job_satisfaction': -20}
                    }
                ]
            },
            'social': {
                'probability': 0.15,  # %15
                'events': [
                    {
                        'name': 'Eski Arkadaş',
                        'description': 'Eski bir arkadaşınızla karşılaştınız!',
                        'condition': lambda sim: sim.social < 70,
                        'effect': lambda sim: {'social': 15, 'mood': 10}
                    },
                    {
                        'name': 'Yeni Arkadaş',
                        'description': 'Yeni bir arkadaş edindiniz!',
                        'condition': lambda sim: sim.social < 50,
                        'effect': lambda sim: {'social': 10, 'mood': 5}
                    }
                ]
            },
            'luck': {
                'probability': 0.1,  # %10
                'events': [
                    {
                        'name': 'Şanslı Gün',
                        'description': 'Bugün şanslısınız! Cebinizde para buldunuz.',
                        'condition': lambda sim: True,
                        'effect': lambda sim: {'money': random.randint(100, 500), 'mood': 15}
                    },
                    {
                        'name': 'Şanssız Gün',
                        'description': 'Bugün şanssızsınız! Cüzdanınızı kaybettiniz.',
                        'condition': lambda sim: sim.money > 100,
                        'effect': lambda sim: {'money': -random.randint(50, 200), 'mood': -10}
                    }
                ]
            },
            'health': {
                'probability': 0.1,  # %10
                'events': [
                    {
                        'name': 'Hasta Olma',
                        'description': 'Hasta oldunuz! Dinlenmeniz gerekiyor.',
                        'condition': lambda sim: sim.energy < 30,
                        'effect': lambda sim: {'energy': -20, 'mood': -10, 'hygiene': -15}
                    },
                    {
                        'name': 'Sağlıklı Gün',
                        'description': 'Kendinizi çok iyi hissediyorsunuz!',
                        'condition': lambda sim: sim.energy > 70,
                        'effect': lambda sim: {'energy': 10, 'mood': 5}
                    }
                ]
            }
        }

    def get_time_of_day(self):
        """Günün saatine göre zaman dilimini döndürür"""
        hour = self.game.game_time.hour
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 24:
            return 'evening'
        else:
            return 'night'

    def check_for_events(self, sim):
        """Event kontrolü yapar"""
        if self.is_action_in_progress:
            return
            
        current_time = datetime.now()
        if self.last_event_time and (current_time - self.last_event_time).total_seconds() < self.event_cooldown:
            return
            
        # Günün saatine göre event olasılığını belirle
        time_of_day = self.get_time_of_day()
        time_prob = self.time_based_probabilities[time_of_day]
        
        # Event olasılığını kontrol et
        if random.random() < time_prob:
            # Kategori seç
            category = random.choices(
                list(self.event_categories.keys()),
                weights=[cat['probability'] for cat in self.event_categories.values()]
            )[0]
            
            # Event seç
            available_events = [
                event for event in self.event_categories[category]['events']
                if event['condition'](sim)
            ]
            
            if available_events:
                event = random.choice(available_events)
                self.show_event(event, sim)
                self.last_event_time = current_time

    def show_event(self, event, sim):
        """Olayı gösterir ve etkilerini uygular"""
        # UI ile event göster
        self.game.ui.show_event(event['name'], event['description'])
        
        # Etkileri uygula
        effects = event['effect'](sim)
        
        # Sim'in durumunu güncelle
        for attr, value in effects.items():
            if hasattr(sim, attr):
                if attr == 'money':
                    sim.money += value
                else:
                    current_value = getattr(sim, attr)
                    new_value = max(0, min(100, current_value + value))
                    setattr(sim, attr, new_value)
        
        # Bildirim göster
        effect_text = []
        for attr, value in effects.items():
            if value > 0:
                effect_text.append(f"{attr.capitalize()}: +{value}")
            else:
                effect_text.append(f"{attr.capitalize()}: {value}")
                
        if effect_text:
            self.game.ui.show_notification(f"Olay etkileri: {', '.join(effect_text)}", "info", 5)

    def start_action(self):
        """Eylem başladığında çağrılır"""
        self.is_action_in_progress = True

    def end_action(self):
        """Eylem bittiğinde çağrılır"""
        self.is_action_in_progress = False 