#!/usr/bin/env python3
# Teacher Panel v3.1 - TELNET UTF8 FIXED
import socket, threading, os
from datetime import datetime

class TeacherPanel:
    def __init__(self):
        self.clients = {}
        self.next_id = 1
    
    def log(self, msg):
        ts = datetime.now().strftime('%H:%M:%S')
        print(f'[{ts}] 🎓 TEACHER | {msg}')
    
    def safe_recv(self, sock):
        """Safe receive - ignores telnet garbage"""
        try:
            data = sock.recv(1024)
            if not data: return None
            # Ignore non-text bytes, extract printable text
            text = ''.join(c for c in data.decode('utf-8', errors='ignore') if ord(c) > 31 and ord(c) < 127)
            return text.strip() if text else None
        except:
            return None
    
    def dashboard(self):
        os.system('clear')
        print('🎯 TEACHER PANEL v3.1 - 50 Student Capacity')
        print('=' * 60)
        if not self.clients:
            print('👥 No students connected')
        else:
            print(f'📊 {len(self.clients)} students online')
            for sid in sorted(self.clients):
                info = self.clients[sid]
                status = '🟢' if info['alive'] else '🔴'
                print(f'{sid:2d}: {info["name"][:10]:<10} | {info["ip"]:<15} | {status}')
        print('=' * 60)
        print('Commands: r5=reply #5, a=all broadcast, q=quit')
    
    def send_msg(self, sock, msg):
        try:
            sock.send((msg + '\n').encode('ascii', errors='ignore'))
        except: pass
    
    def handle_student(self, sock, addr):
        sid = self.next_id
        self.next_id += 1
        ip = addr[0]
        name = f'Student{sid}'  # Auto-name, NO input = NO UTF8 error
        
        self.clients[sid] = {
            'sock': sock, 'ip': ip, 'name': name, 'alive': True, 'count': 0
        }
        self.send_msg(sock, f'✅ Connected as {name}! Send messages to teacher.')
        self.log(f'🔗 #{sid} "{name}" ({ip}) ✅')
        
        while sid in self.clients and self.clients[sid]['alive']:
            msg = self.safe_recv(sock)
            if msg:
                self.clients[sid]['count'] += 1
                self.log(f'📨 #{sid}({name}): {msg[:50]}')
            else:
                break
        
        self.clients[sid]['alive'] = False
        try: sock.close()
        except: pass
        self.log(f'👋 #{sid}({name}) disconnected')
        self.clients.pop(sid, None)
    
    def reply_student(self, sid, msg):
        if sid in self.clients and self.clients[sid]['alive']:
            self.send_msg(self.clients[sid]['sock'], f'💬 Teacher: {msg}')
            self.log(f'✅ Replied #{sid}')
            return True
        self.log(f'❌ #{sid} offline')
        return False
    
    def broadcast_all(self, msg):
        count = 0
        for sid in list(self.clients):
            if self.clients[sid]['alive']:
                self.send_msg(self.clients[sid]['sock'], f'📢 Teacher Broadcast: {msg}')
                count += 1
        self.log(f'📢 Broadcast to {count} students')
    
    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 8080))
        s.listen(50)
        
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = '0.0.0.0'
            
        self.log(f'🚀 LIVE: {ip}:8080')
        self.log('📡 Students connect: telnet YOUR_IP 8080')
        
        # Background client acceptor
        def accept_loop():
            while True:
                c, a = s.accept()
                t = threading.Thread(target=self.handle_student, args=(c, a))
                t.daemon = True
                t.start()
        
        threading.Thread(target=accept_loop, daemon=True).start()
        
        # Teacher commands
        while True:
            self.dashboard()
            cmd = input('\n🎯 Command: ').strip().lower()
            
            if cmd == 'q':
                self.broadcast_all('🛑 Lab complete - Goodbye everyone!')
                break
            elif cmd == 'a':
                self.broadcast_all(input('📢 Message to ALL: '))
            elif cmd.startswith('r') and cmd[1:].isdigit():
                sid = int(cmd[1:])
                self.reply_student(sid, input(f'💬 To Student #{sid}: '))
            else:
                print('❓ Type: r5 (reply student 5), a (all), q (quit)')
    
if __name__ == '__main__':
    TeacherPanel().run()
