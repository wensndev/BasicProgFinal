import random
import time
from typing import Dict, Tuple

class GamblingGames:
    """Bahis oyunları sınıfı"""
    
    def __init__(self, ui):
        self.ui = ui
        
        # Bahis oyunu kazanma oranları (olasılık, çarpan)
        self.bet_odds = [
            (50, 0),     # %50 şans - para kaybı (x0)
            (25, 1.5),   # %25 şans - x1.5 kazanç
            (15, 2),     # %15 şans - x2 kazanç
            (8, 5),      # %8 şans - x5 kazanç
            (2, 10)      # %2 şans - x10 kazanç
        ]
        
        # Slot makinesi sembolleri ve oranları
        self.slot_symbols = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎', '7️⃣']
        self.slot_payouts = {
            ('🍒', '🍒', '🍒'): 2,      # x2
            ('🍋', '🍋', '🍋'): 3,      # x3
            ('🍊', '🍊', '🍊'): 4,      # x4
            ('🍇', '🍇', '🍇'): 5,      # x5
            ('⭐', '⭐', '⭐'): 10,     # x10
            ('💎', '💎', '💎'): 25,     # x25
            ('7️⃣', '7️⃣', '7️⃣'): 50,   # x50 JACKPOT!
            # İkili eşleşmeler
            ('🍒', '🍒'): 1.2,
            ('🍋', '🍋'): 1.3,
            ('🍊', '🍊'): 1.4,
            ('🍇', '🍇'): 1.5,
            ('⭐', '⭐'): 2,
            ('💎', '💎'): 5,
            ('7️⃣', '7️⃣'): 10
        }
    
    def play_bet_game(self, bet_amount: float) -> Dict:
        """Basit bahis oyunu - şansına güven!"""
        if bet_amount <= 0:
            return {
                'success': False,
                'message': "Geçerli bir bahis miktarı girin!",
                'winnings': 0
            }
        
        # Animasyon göster
        self.ui.console.clear()
        self.ui.console.print("🎲 [bright_yellow]Şansınızı deniyorsunuz...[/bright_yellow] 🎲")
        self.ui.console.print(f"[bright_white]Bahis: {bet_amount}₺[/bright_white]\n")
        
        # Geliştirilmiş zar atma animasyonu
        dice_faces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
        for i in range(15):
            dice1 = random.choice(dice_faces)
            dice2 = random.choice(dice_faces)
            
            # Animasyon çerçevesi
            frame = f"""
┌─────────────────────┐
│    🎲 {dice1}  {dice2} 🎲    │
│                     │
│   {'● ' * (i % 5 + 1)}{'○ ' * (5 - i % 5)}  │
└─────────────────────┘
            """
            
            self.ui.console.print(frame)
            time.sleep(0.15)
            
            # Ekranı temizle (son tur hariç)
            if i < 14:
                self.ui.console.clear()
                self.ui.console.print("🎲 [bright_yellow]Şansınızı deniyorsunuz...[/bright_yellow] 🎲")
                self.ui.console.print(f"[bright_white]Bahis: {bet_amount}₺[/bright_white]\n")
        
        self.ui.console.print("\n[bright_cyan]Sonuç hesaplanıyor...[/bright_cyan]")
        time.sleep(1)
        
        # Sonucu belirle
        rand = random.randint(1, 100)
        cumulative = 0
        
        for chance, multiplier in self.bet_odds:
            cumulative += chance
            if rand <= cumulative:
                if multiplier == 0:
                    # Kaybetti
                    winnings = -bet_amount
                    result_message = f"💔 [bright_red]Kaybettiniz! -{bet_amount}₺[/bright_red]"
                    self.ui.console.print(result_message)
                else:
                    # Kazandı
                    profit = bet_amount * (multiplier - 1)
                    winnings = profit
                    result_message = f"🎉 [bright_green]Kazandınız! x{multiplier} = +{profit}₺[/bright_green]"
                    self.ui.console.print(result_message)
                
                return {
                    'success': True,
                    'message': result_message,
                    'winnings': winnings,
                    'multiplier': multiplier,
                    'duration': 1  # 1 saat zaman geçişi
                }
        
        # Bu noktaya hiç gelmemeli ama güvenlik için
        return {
            'success': False,
            'message': "Bir hata oluştu!",
            'winnings': 0
        }
    
    def play_slots(self, bet_amount: float) -> Dict:
        """Slot makinesi oyunu"""
        if bet_amount <= 0:
            return {
                'success': False,
                'message': "Geçerli bir bahis miktarı girin!",
                'winnings': 0
            }
        
        self.ui.console.clear()
        self.ui.console.print("🎰 [bright_cyan]SLOT MAKİNESİ[/bright_cyan] 🎰")
        self.ui.console.print(f"Bahis: {bet_amount}₺")
        self.ui.console.print("\n🎰 Çeviriyor... 🎰")
        
        # Slot animasyonu
        for round_num in range(8):
            # Her tur için rastgele semboller göster
            slot1 = random.choice(self.slot_symbols)
            slot2 = random.choice(self.slot_symbols)
            slot3 = random.choice(self.slot_symbols)
            
            self.ui.console.print(f"\r┌─────────────┐")
            self.ui.console.print(f"│  {slot1}  │  {slot2}  │  {slot3}  │")
            self.ui.console.print(f"└─────────────┘")
            
            time.sleep(0.3)
            if round_num < 7:  # Son turda silme
                self.ui.console.clear()
                self.ui.console.print("🎰 [bright_cyan]SLOT MAKİNESİ[/bright_cyan] 🎰")
                self.ui.console.print(f"Bahis: {bet_amount}₺")
                self.ui.console.print("\n🎰 Çeviriyor... 🎰")
        
        # Final sonuç
        final_slot1 = random.choice(self.slot_symbols)
        final_slot2 = random.choice(self.slot_symbols)
        final_slot3 = random.choice(self.slot_symbols)
        
        slots = (final_slot1, final_slot2, final_slot3)
        
        self.ui.console.print("\n🎰 [bright_yellow]SONUÇ:[/bright_yellow] 🎰")
        self.ui.console.print(f"┌─────────────┐")
        self.ui.console.print(f"│  {final_slot1}  │  {final_slot2}  │  {final_slot3}  │")
        self.ui.console.print(f"└─────────────┘")
        
        # Kazancı hesapla
        winnings = self._calculate_slot_winnings(slots, bet_amount)
        
        if winnings > bet_amount:
            profit = winnings - bet_amount
            multiplier = winnings / bet_amount
            result_message = f"🎉 [bright_green]KAZANDINIZ! x{multiplier:.1f} = +{profit}₺[/bright_green]"
            
            # Özel kazanç mesajları
            if slots == ('7️⃣', '7️⃣', '7️⃣'):
                result_message += "\n🔥 [bright_yellow]JACKPOT! 7-7-7![/bright_yellow] 🔥"
            elif slots == ('💎', '💎', '💎'):
                result_message += "\n💎 [bright_cyan]ELMAS ÜÇLÜ![/bright_cyan] 💎"
            elif slots == ('⭐', '⭐', '⭐'):
                result_message += "\n⭐ [bright_magenta]YILDIZ ÜÇLÜ![/bright_magenta] ⭐"
                
        elif winnings == bet_amount:
            profit = 0
            result_message = f"😐 [bright_yellow]Berabere! Paranız geri döndü.[/bright_yellow]"
        else:
            profit = -bet_amount
            result_message = f"💔 [bright_red]Kaybettiniz! -{bet_amount}₺[/bright_red]"
        
        self.ui.console.print(f"\n{result_message}")
        
        return {
            'success': True,
            'message': result_message,
            'winnings': profit,
            'slots': slots,
            'duration': 1  # 1 saat zaman geçişi
        }
    
    def _calculate_slot_winnings(self, slots: Tuple, bet_amount: float) -> float:
        """Slot sonuçlarına göre kazancı hesaplar"""
        # Tam üçlü kontrol et
        if slots in self.slot_payouts:
            return bet_amount * self.slot_payouts[slots]
        
        # İkili eşleşme kontrol et
        if slots[0] == slots[1] and (slots[0], slots[1]) in self.slot_payouts:
            return bet_amount * self.slot_payouts[(slots[0], slots[1])]
        elif slots[1] == slots[2] and (slots[1], slots[2]) in self.slot_payouts:
            return bet_amount * self.slot_payouts[(slots[1], slots[2])]
        elif slots[0] == slots[2] and (slots[0], slots[2]) in self.slot_payouts:
            return bet_amount * self.slot_payouts[(slots[0], slots[2])]
        
        # Hiç eşleşme yok - kayıp
        return 0
    
    def get_gambling_stats(self) -> str:
        """Bahis istatistiklerini gösterir"""
        stats = "🎲 [bright_cyan]BAHİS OYUNU ORANLARI[/bright_cyan] 🎲\n\n"
        stats += "💰 Şansınızı deneyin:\n"
        stats += "• %50 şans - Para kaybı 💔\n"
        stats += "• %25 şans - x1.5 kazanç 💰\n"
        stats += "• %15 şans - x2 kazanç 🎉\n"
        stats += "• %8 şans - x5 kazanç 🔥\n"
        stats += "• %2 şans - x10 kazanç 💎\n\n"
        
        stats += "🎰 [bright_magenta]SLOT MAKİNESİ ÖDEMELER[/bright_magenta] 🎰\n\n"
        stats += "🔥 JACKPOT:\n"
        stats += "• 7️⃣-7️⃣-7️⃣ = x50 💥\n"
        stats += "• 💎-💎-💎 = x25 💎\n"
        stats += "• ⭐-⭐-⭐ = x10 ⭐\n\n"
        stats += "🎯 ÜÇLÜ EŞLEŞMELERİ:\n"
        stats += "• 🍇-🍇-🍇 = x5\n"
        stats += "• 🍊-🍊-🍊 = x4\n"
        stats += "• 🍋-🍋-🍋 = x3\n"
        stats += "• 🍒-🍒-🍒 = x2\n\n"
        stats += "💡 İkili eşleşmeler de küçük ödüller verir!"
        
        return stats 