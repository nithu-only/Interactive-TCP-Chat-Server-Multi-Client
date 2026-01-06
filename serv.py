#!/usr/bin/env python3
import socket, threading, os, time
from datetime import datetime

class TeacherPanelV4:
    def __init__(self):
        self.clients = {}
        self.next_id = 1
        self.history = []
    
    def log(self, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        line = f'[{ts}] {msg}'
        self.history.append(line)
        print(line)
    
    def dashboard(self):
        # Use a real newline \n instead of \\n
        print('\n' + '='*70)
        active_count = len([c for c in self.clients if self.clients[c]['alive']])
        print(f'🎯 TEACHER v4.0 | Students: {active_count}')
        
        if self.clients:
            for sid in sorted(self.clients):
                if self.clients[sid]['alive']:
                    info = self.clients[sid]
                    # FIXED: Changed ["ip"] to ["addr"][0]
                    print(f'  #{sid}: {info["name"]} ({info["addr"][0]}) 🟢')
        print('='*70)
        print('r5=reply#5, a=all, h=history, q=quit')
    
    def safe_recv(self, sock):
        try:
            data = sock.recv(1024)
            if not data: return ''
            # Decode and strip unwanted whitespace/null bytes
            msg = data.decode('utf-8', errors='ignore').strip()
            return ''.join([c for c in msg if 32<=ord(c)<=126])
        except: return ''
    
    def send(self, sock, msg):
        try: 
            # Added \r\n for better compatibility with different terminals
            sock.send(f'{msg}\r\n'.encode('ascii', errors='ignore'))
        except: pass
    
    def handle_student(self, sock, addr):
        sid = self.next_id
        self.next_id += 1
        name = f'Student{sid}'
        self.clients[sid] = {'sock': sock, 'addr': addr, 'name': name, 'alive': True}
        
        self.send(sock, f'✅ Welcome {name}!')
        self.log(f'🔗 #{sid} {name} ({addr[0]})')
        
        while sid in self.clients and self.clients[sid]['alive']:
            msg = self.safe_recv(sock)
            if msg:
                self.log(f'📨 #{sid}({name}): {msg}')
            elif msg == '': # This helps detect clean disconnects
                break
        
        self.clients[sid]['alive'] = False
        sock.close()
        self.log(f'👋 #{sid} left')
        self.clients.pop(sid, None)
    
    def reply(self, sid, msg):
        if sid in self.clients and self.clients[sid]['alive']:
            self.send(self.clients[sid]['sock'], f'💬 Teacher: {msg}')
            self.log(f'✅ →#{sid}: {msg}')
    
    def broadcast(self, msg):
        count = 0
        for sid in list(self.clients.keys()):
            if self.clients[sid]['alive']:
                self.send(self.clients[sid]['sock'], f'📢 ALL: {msg}')
                count += 1
        self.log(f'📢 Broadcast to {count} students')
    
    def show_history(self):
        print('\n📜 LAST MESSAGES:')
        print('-'*40)
        for line in self.history[-8:]:
            print(line)
    
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('0.0.0.0', 8080))
        except OSError as e:
            print(f"❌ Could not bind to port 8080: {e}")
            return
            
        s.listen(50)
        # Getting local IP more reliably
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        self.log(f'🚀 v4.0 LIVE on {local_ip}:8080')
        
        # Cleaner thread management
        def accept_loop():
            while True:
                try:
                    client_sock, client_addr = s.accept()
                    threading.Thread(target=self.handle_student, args=(client_sock, client_addr), daemon=True).start()
                except:
                    break

        threading.Thread(target=accept_loop, daemon=True).start()
        
        while True:
            self.dashboard()
            try:
                cmd = input('\n🎯 ').lower().strip()
                if cmd == 'q': 
                    self.broadcast('Lab end!')
                    break
                elif cmd == 'h': 
                    self.show_history()
                elif cmd == 'a': 
                    msg = input('📢 Message to all: ')
                    self.broadcast(msg)
                elif cmd.startswith('r') and cmd[1:].isdigit():
                    sid = int(cmd[1:])
                    msg = input(f'Reply to #{sid}: ')
                    self.reply(sid, msg)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    TeacherPanelV4().run()
