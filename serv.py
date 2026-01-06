#!/usr/bin/env python3
import socket, threading, os
from datetime import datetime

class TeacherPanel:
    def __init__(self):
        self.clients = {}  # {id: (socket, addr, name)}
        self.next_id = 1
    
    def log(self, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        print(f'[{ts}] 🎓 TEACHER | {msg}')
    
    def dashboard(self):
        os.system('clear')
        print('🎯 TEACHER CONTROL PANEL v3.0')
        print('='*60)
        if not self.clients:
            print('👥 No students connected')
        else:
            print(f'📊 {len(self.clients)} students online')
            for sid, (sock, addr, name) in self.clients.items():
                status = '🟢' if sock else '🔴'
                print(f'{sid:2}: {name:<12} | {addr[0]:15} | {status}')
        print('='*60)
        print('Commands: r5=reply#5, a=all, q=quit')
    
    def reply_private(self, sid, msg):
        if sid in self.clients:
            sock = self.clients[sid][0]
            try:
                sock.send(f'💬 PRIVATE Teacher: {msg}'.encode())
                self.log(f'✅ Replied to #{sid} "{self.clients[sid][2]}"')
            except: self.log(f'❌ #{sid} offline')
    
    def broadcast(self, msg):
        for sid, (sock, _, _) in list(self.clients.items()):
            try:
                sock.send(f'📢 ALL: {msg}'.encode())
            except: pass
        self.log(f'📢 Sent to {len(self.clients)} students')
    
    def handle_student(self, sock, addr):
        sid = self.next_id; self.next_id += 1
        sock.send(b'Name: ')
        name = sock.recv(50).decode().strip() or f'Student{sid}'
        self.clients[sid] = (sock, addr, name)
        self.log(f'🔗 #{sid} "{name}" from {addr[0]}')
        
        while sid in self.clients:
            try:
                msg = sock.recv(1024).decode(errors='ignore')
                if msg: 
                    self.log(f'📨 #{sid} "{name}": {msg.strip()}')
            except: break
        sock.close()
        self.clients.pop(sid, None)
    
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 8080))
        s.listen(50)
        ip = socket.gethostbyname(socket.gethostname())
        
        self.log(f'SERVER LIVE: {ip}:8080')
        self.log('Students: telnet IP 8080')
        
        def accept_loop():
            while True:
                c, a = s.accept()
                t = threading.Thread(target=self.handle_student, args=(c, a))
                t.daemon = True; t.start()
        
        import threading
        threading.Thread(target=accept_loop, daemon=True).start()
        
        while True:
            self.dashboard()
            cmd = input('🎯 ').strip().lower()
            if cmd == 'q': 
                self.broadcast('🛑 Lab complete!'); break
            elif cmd == 'a':
                self.broadcast(input('📢 Message: '))
            elif cmd.startswith('r') and cmd[1:].isdigit():
                sid = int(cmd[1:])
                self.reply_private(sid, input(f'💬 To #{sid}: '))
    
TeacherPanel().run()
