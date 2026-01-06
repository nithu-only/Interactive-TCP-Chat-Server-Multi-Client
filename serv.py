#!/usr/bin/env python3
# Teacher Panel v4.0 - HISTORY + No Clear Screen
import socket, threading, os
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
        print('\\n' + '='*70)
        print('🎯 TEACHER v4.0 | Students:', len([c for c in self.clients if self.clients[c]['alive']]))
        if self.clients:
            for sid in sorted(self.clients):
                if self.clients[sid]['alive']:
                    info = self.clients[sid]
                    print(f'  #{sid}: {info["name"]} ({info["ip"]}) 🟢')
        print('='*70)
        print('r5=reply#5, a=all, h=history, q=quit')
    
    def safe_recv(self, sock):
        try:
            data = sock.recv(1024)
            if not data: return ''
            return ''.join([c for c in data.decode('utf-8', errors='ignore') if 32<=ord(c)<=126]).strip()
        except: return ''
    
    def send(self, sock, msg):
        try: sock.send(f'{msg}\\n'.encode('ascii', errors='ignore'))
        except: pass
    
    def handle_student(self, sock, addr):
        sid = self.next_id; self.next_id += 1
        name = f'Student{sid}'
        self.clients[sid] = {'sock': sock, 'addr': addr, 'name': name, 'alive': True}
        self.send(sock, f'✅ Welcome {name}!')
        self.log(f'🔗 #{sid} {name} ({addr[0]})')
        
        while sid in self.clients and self.clients[sid]['alive']:
            msg = self.safe_recv(sock)
            if msg:
                self.log(f'📨 #{sid}({name}): {msg}')
            else: break
        
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
        for sid in self.clients:
            if self.clients[sid]['alive']:
                self.send(self.clients[sid]['sock'], f'📢 ALL: {msg}')
                count += 1
        self.log(f'📢 Broadcast {count} students')
    
    def show_history(self):
        print('\\n📜 LAST MESSAGES:')
        print('-'*40)
        for line in self.history[-8:]:
            print(line)
    
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 8080))
        s.listen(50)
        ip = socket.gethostbyname(socket.gethostname())
        
        self.log(f'🚀 v4.0 LIVE {ip}:8080')
        
        threading.Thread(target=lambda: [self.handle_student(*s.accept()) or time.sleep(0.1) for _ in iter(int,1)], daemon=True).start()
        
        while True:
            self.dashboard()
            cmd = input('\\n🎯 ').lower()
            if cmd=='q': self.broadcast('Lab end!'); break
            elif cmd=='h': self.show_history()
            elif cmd=='a': self.broadcast(input('📢 '))
            elif cmd.startswith('r') and cmd[1:].isdigit():
                sid=int(cmd[1:])
                self.reply(sid, input(f'#{sid}: '))
    
TeacherPanelV4().run()
