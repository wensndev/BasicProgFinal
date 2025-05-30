import socket
import json
import threading
import time
import os
from typing import Dict, List, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

# Sunucu kilit dosyası
SERVER_LOCK_FILE = "server.lock"

class SimpleNetwork:
    def __init__(self, game, is_server: bool = False, host: str = "localhost", port: int = 5000):
        self.game = game
        self.console = Console()
        self.is_server = is_server
        self.host = host
        self.port = port
        
        # Server/Client objects
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.connected_clients: Dict[str, socket.socket] = {}  # connection_id -> socket
        self.running = False
        
        # Player data - BASİT!
        self.players: Dict[str, Dict] = {}  # player_name -> player_data
        self.my_player_name = ""
        
        # Threading
        self.lock = threading.Lock()
    
    @classmethod
    def is_server_active(cls) -> bool:
        """Aktif bir sunucu var mı kontrol eder"""
        return os.path.exists(SERVER_LOCK_FILE)
    
    def _create_server_lock(self):
        """Sunucu kilit dosyası oluşturur"""
        try:
            with open(SERVER_LOCK_FILE, "w") as f:
                f.write(f"{self.host}:{self.port}")
            return True
        except Exception:
            return False
    
    def _remove_server_lock(self):
        """Sunucu kilit dosyasını kaldırır"""
        try:
            if os.path.exists(SERVER_LOCK_FILE):
                os.remove(SERVER_LOCK_FILE)
        except Exception:
            pass
    
    def start_server(self) -> bool:
        """Sunucuyu başlatır - BASİT!"""
        if self.is_server_active():
            self.console.print("[red]Zaten aktif bir sunucu çalışıyor![/red]")
            return False
            
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(4)
            
            self._create_server_lock()
            self.running = True
            
            # Server thread başlat
            server_thread = threading.Thread(target=self._run_server)
            server_thread.daemon = True
            server_thread.start()
            
            self.console.print(f"[green]✅ Sunucu başlatıldı: {self.host}:{self.port}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Sunucu başlatılamadı: {e}[/red]")
            return False
    
    def connect_to_server(self) -> bool:
        """Sunucuya bağlanır - BASİT!"""
        try:
            self.console.print(f"[cyan]Sunucuya bağlanılıyor: {self.host}:{self.port}[/cyan]")
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10.0)
            self.client_socket.connect((self.host, self.port))
            
            self.running = True
            
            # Client thread başlat
            client_thread = threading.Thread(target=self._run_client)
            client_thread.daemon = True
            client_thread.start()
            
            self.console.print("[green]✅ Sunucuya bağlanıldı![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Bağlantı hatası: {e}[/red]")
            return False
    
    def _run_server(self):
        """Server ana döngüsü"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                connection_id = f"client_{len(self.connected_clients)}"
                
                with self.lock:
                    self.connected_clients[connection_id] = client_socket
                
                # Client handler thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, connection_id)
                )
                client_thread.daemon = True
                client_thread.start()
                
                self.console.print(f"[green]Yeni bağlantı: {address} (ID: {connection_id})[/green]")
                
            except Exception as e:
                if self.running:
                    self.console.print(f"[red]Server hatası: {e}[/red]")
                break
    
    def _handle_client(self, client_socket: socket.socket, connection_id: str):
        """Client mesajlarını işler"""
        try:
            while self.running:
                try:
                    # Mesaj al
                    data = client_socket.recv(4096)
                    if not data:
                        break
                        
                    message = json.loads(data.decode())
                    message['connection_id'] = connection_id
                    
                    # Mesajı işle
                    self._process_server_message(message, client_socket)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    self.console.print(f"[red]Client işleme hatası: {e}[/red]")
                    break
                    
        except Exception as e:
            self.console.print(f"[red]Client handler hatası: {e}[/red]")
        finally:
            self._disconnect_client(connection_id, client_socket)
    
    def _run_client(self):
        """Client ana döngüsü"""
        try:
            while self.running:
                try:
                    data = self.client_socket.recv(4096)
                    if not data:
                        break
                        
                    message = json.loads(data.decode())
                    self._process_client_message(message)
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    self.console.print(f"[red]Client mesaj hatası: {e}[/red]")
                    break
    
        except Exception as e:
            self.console.print(f"[red]Client döngü hatası: {e}[/red]")
        finally:
            self.running = False
    
    def _process_server_message(self, message: dict, sender_socket: socket.socket):
        """Server tarafında mesaj işleme"""
        msg_type = message.get('type')
        
        if msg_type == 'player_join':
            player_name = message['player_name']
            player_data = message['player_data']
            
            with self.lock:
                self.players[player_name] = player_data
            
            # Tüm oyunculara yeni oyuncuyu bildir
            broadcast_msg = {
                'type': 'player_joined',
                'player_name': player_name,
                'player_data': player_data
            }
            self._broadcast(broadcast_msg, exclude=sender_socket)
            
            # Yeni oyuncuya mevcut oyuncu listesini gönder
            welcome_msg = {
                'type': 'player_list',
                'players': dict(self.players)
            }
            self._send_to_socket(sender_socket, welcome_msg)
            
            self.console.print(f"[green]✅ Oyuncu katıldı: {player_name}[/green]")
            
        elif msg_type == 'chat_message':
            # Chat mesajını broadcast et
            self._broadcast(message)
            
        elif msg_type == 'player_update':
            # Oyuncu durumu güncelleme
            player_name = message['player_name']
            update_data = message['player_data']
            
            with self.lock:
                if player_name in self.players:
                    self.players[player_name].update(update_data)
                
            # Diğer oyunculara ilet
            self._broadcast(message, exclude=sender_socket)
    
        elif msg_type == 'game_start':
            # Server tarafında oyun başlatma (normalde server bu mesajı gönderir ama kendisi de işlemeli)
            self._broadcast(message)  # Tüm client'lara ilet
        
        elif msg_type == 'player_disconnected':
            # Oyuncu ayrılma
            player_name = message.get('player_name', '')
            if player_name:
                with self.lock:
                    if player_name in self.players:
                        del self.players[player_name]
                self.console.print(f"[yellow]Oyuncu ayrıldı: {player_name}[/yellow]")
        
        elif msg_type == 'player_death':
            # Oyuncu ölümü
            player_name = message.get('player_name', 'Bilinmeyen')
            death_reason = message.get('death_reason', 'Bilinmeyen sebep')
            death_time = message.get('death_time', 'Bilinmeyen zaman')
            
            self.console.print(f"[bright_red]💀 {player_name} hayatını kaybetti![/bright_red]")
            self.console.print(f"[bright_red]Sebep: {death_reason}[/bright_red]")
            self.console.print(f"[dim]Zaman: {death_time}[/dim]")
            
            # Oyuncuyu listeden kaldır
            with self.lock:
                if player_name in self.players:
                    del self.players[player_name]
    
    def _process_client_message(self, message: dict):
        """Client tarafında mesaj işleme"""
        msg_type = message.get('type')
        
        if msg_type == 'player_joined':
            player_name = message['player_name']
            player_data = message['player_data']
            
            with self.lock:
                self.players[player_name] = player_data
            
            self.console.print(f"[green]🎮 Yeni oyuncu: {player_name}[/green]")
            
        elif msg_type == 'player_list':
            # Tam oyuncu listesi
            with self.lock:
                self.players = message['players']
            
            self.console.print(f"[cyan]📊 Oyuncu listesi güncellendi: {len(self.players)} oyuncu[/cyan]")
            
        elif msg_type == 'player_update':
            # Oyuncu durumu güncelleme
            player_name = message['player_name']
            update_data = message['player_data']
            
            with self.lock:
                if player_name in self.players:
                    self.players[player_name].update(update_data)
            
        elif msg_type == 'chat_message':
            player_name = message.get('player_name', 'Bilinmeyen')
            chat_text = message.get('message', '')
            self.console.print(f"[cyan][{player_name}]: {chat_text}[/cyan]")
        
        elif msg_type == 'game_start':
            # Oyun başlatma mesajı
            host_name = message.get('host', 'Host')
            start_message = message.get('message', 'Oyun başlıyor!')
            
            self.console.print(f"[bright_green]🎮 {start_message} (Host: {host_name})[/bright_green]")
            
            # Game nesnesine oyun başlatma sinyali gönder
            if hasattr(self.game, '_handle_game_start'):
                self.game._handle_game_start()
            
        elif msg_type == 'player_disconnected':
            # Oyuncu ayrılma
            player_name = message.get('player_name', '')
            if player_name:
                with self.lock:
                    if player_name in self.players:
                        del self.players[player_name]
                self.console.print(f"[yellow]Oyuncu ayrıldı: {player_name}[/yellow]")
        
        elif msg_type == 'player_death':
            # Oyuncu ölümü
            player_name = message.get('player_name', 'Bilinmeyen')
            death_reason = message.get('death_reason', 'Bilinmeyen sebep')
            death_time = message.get('death_time', 'Bilinmeyen zaman')
            
            self.console.print(f"[bright_red]💀 {player_name} hayatını kaybetti![/bright_red]")
            self.console.print(f"[bright_red]Sebep: {death_reason}[/bright_red]")
            self.console.print(f"[dim]Zaman: {death_time}[/dim]")
            
            # Oyuncuyu listeden kaldır
            with self.lock:
                if player_name in self.players:
                    del self.players[player_name]
    
    def _broadcast(self, message: dict, exclude: Optional[socket.socket] = None):
        """Tüm client'lara mesaj gönder"""
        if not self.is_server:
            return
            
        failed_clients = []
        
        with self.lock:
            for conn_id, client_socket in self.connected_clients.items():
                if client_socket != exclude:
                    try:
                        self._send_to_socket(client_socket, message)
                    except Exception:
                        failed_clients.append(conn_id)
        
        # Başarısız client'ları temizle
        for conn_id in failed_clients:
            with self.lock:
                if conn_id in self.connected_clients:
                    del self.connected_clients[conn_id]
    
    def _send_to_socket(self, sock: socket.socket, message: dict):
        """Socket'e mesaj gönder"""
        data = json.dumps(message).encode()
        sock.send(data)
    
    def _disconnect_client(self, connection_id: str, client_socket: socket.socket):
        """Client bağlantısını kes"""
        # Client'ı listeden kaldır
        with self.lock:
            if connection_id in self.connected_clients:
                del self.connected_clients[connection_id]
        
        # Oyuncuyu bul ve kaldır
        player_to_remove = None
        with self.lock:
            for player_name, player_data in list(self.players.items()):
                if player_data.get('connection_id') == connection_id:
                    player_to_remove = player_name
                    del self.players[player_name]
                    break
        
        # Diğer oyunculara bildir
        if player_to_remove:
            disconnect_msg = {
                'type': 'player_disconnected',
                'player_name': player_to_remove
            }
            self._broadcast(disconnect_msg)
            self.console.print(f"[yellow]Oyuncu ayrıldı: {player_to_remove}[/yellow]")
        
        # Socket'i kapat
        try:
            client_socket.close()
        except Exception:
            pass
    
    # PUBLIC API - Basit ve temiz!
    
    def join_game(self, player_name: str, player_data: dict):
        """Oyuna katıl"""
        self.my_player_name = player_name
        
        if self.is_server:
            # Server kendi oyuncusunu ekler
            with self.lock:
                self.players[player_name] = player_data
            self.console.print(f"[green]Host olarak katıldı: {player_name}[/green]")
            return True
        else:
            # Client sunucuya mesaj gönder
            message = {
                'type': 'player_join',
                'player_name': player_name,
                'player_data': player_data
            }
            try:
                self._send_to_socket(self.client_socket, message)
                return True
            except Exception as e:
                self.console.print(f"[red]Katılım hatası: {e}[/red]")
                return False
    
    def send_chat_message(self, player_name: str, message: str):
        """Chat mesajı gönder"""
        chat_msg = {
            'type': 'chat_message',
            'player_name': player_name,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.is_server:
            # Server broadcast eder
            self._broadcast(chat_msg)
            # Local echo
            self.console.print(f"[cyan][{player_name}]: {message}[/cyan]")
        else:
            # Client sunucuya gönder
            try:
                self._send_to_socket(self.client_socket, chat_msg)
            except Exception as e:
                self.console.print(f"[red]Chat hatası: {e}[/red]")
    
    def send_player_update(self, player_name: str, player_data: dict):
        """Oyuncu durumu güncelle"""
        # Local güncelleme
        with self.lock:
            if player_name in self.players:
                self.players[player_name].update(player_data)
        
        # Network güncelleme
        update_msg = {
            'type': 'player_update',
            'player_name': player_name,
            'player_data': player_data
        }
        
        if self.is_server:
            self._broadcast(update_msg)
        else:
            try:
                self._send_to_socket(self.client_socket, update_msg)
            except Exception:
                pass
    
    def get_player_count(self) -> int:
        """Oyuncu sayısı"""
        with self.lock:
            return len(self.players)
    
    def get_players_list(self) -> List[Dict]:
        """Oyuncu listesi"""
        with self.lock:
            return [
                {'name': name, **data} 
                for name, data in self.players.items()
            ]
    
    def is_connected(self) -> bool:
        """Bağlantı durumu"""
        return self.running
    
    def disconnect(self):
        """Bağlantıyı kes"""
        self.running = False
        
        if self.is_server:
            # Server kapatma
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception:
                    pass
                    
            # Tüm client'ları kapat
            with self.lock:
                for client_socket in self.connected_clients.values():
                    try:
                        client_socket.close()
                    except Exception:
                        pass
            self.connected_clients.clear()
            
            self._remove_server_lock()
            
        else:
            # Client kapatma
            if self.client_socket:
                try:
                    self.client_socket.close()
                except Exception:
                    pass
        
        with self.lock:
            self.players.clear()
            
        self.console.print("[yellow]Bağlantı kapatıldı![/yellow]")
    
    def __del__(self):
        if self.is_server:
            self._remove_server_lock() 

# Backward compatibility - eski Network sınıfını SimpleNetwork'e yönlendir
Network = SimpleNetwork 