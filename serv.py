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

    def save_logs(self):
        filename = f"lab_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write("\n".join(self.history))
        print(f"\n📂 Logs saved to {filename}")

    def dashboard(self):
        print('\n' + '='*70)
        active_clients = [c for c in self.clients if self.clients[c]['alive']]
        print(f'🎯 TEACHER v4.1 | Students Online: {len(active_clients)}')

        if active_clients:
            for sid in sorted(self.clients):
                if self.clients[sid]['alive']:
                    info = self.clients[sid]
                    print(f'  #{sid}: {info["name"]} ({info["addr"][0]}) 🟢')
        print('='*70)
        print('r5=reply#5, k5=kick#5, a=all, h=history, q=quit')

    def safe_recv(self, sock):
        try:
            data = sock.recv(1024)
            if not data: return None
            msg = data.decode('utf-8', errors='ignore').strip()
            return ''.join([c for c in msg if 32<=ord(c)<=126])
        except: return None

    def send(self, sock, msg):
        try: sock.send(f'{msg}\r\n'.encode('ascii', errors='ignore'))
        except: pass

    def handle_student(self, sock, addr):
        sid = self.next_id
        self.next_id += 1

        # --- NAME REGISTRATION STEP ---
        self.send(sock, "📝 Enter your Full Name to join:")
        student_name = self.safe_recv(sock)
        if not student_name: student_name = f"Unknown_{sid}"

        self.clients[sid] = {'sock': sock, 'addr': addr, 'name': student_name, 'alive': True}
        self.send(sock, f'✅ Welcome {student_name}! You are Student #{sid}')
        self.log(f'🔗 #{sid} {student_name} joined from {addr[0]}')

        while sid in self.clients and self.clients[sid]['alive']:
            msg = self.safe_recv(sock)
            if msg is not None and msg != '':
                self.log(f'📨 #{sid}({student_name}): {msg}')
            elif msg is None: # Connection lost
                break

        if sid in self.clients:
            self.clients[sid]['alive'] = False
            sock.close()
            self.log(f'👋 #{sid} ({student_name}) left')
            self.clients.pop(sid, None)

    def kick(self, sid):
        if sid in self.clients:
            self.send(self.clients[sid]['sock'], "🚫 You have been removed from the session.")
            self.clients[sid]['alive'] = False
            self.clients[sid]['sock'].close()
            self.log(f'⚠️ Kicked #{sid}')

    def reply(self, sid, msg):
        if sid in self.clients and self.clients[sid]['alive']:
            self.send(self.clients[sid]['sock'], f'💬 Teacher: {msg}')
            self.log(f'✅ →#{sid}({self.clients[sid]["name"]}): {msg}')

    def broadcast(self, msg):
        for sid in list(self.clients.keys()):
            if self.clients[sid]['alive']:
                self.send(self.clients[sid]['sock'], f'📢 ALL: {msg}')
        self.log(f'📢 Broadcast: {msg}')

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # Specific for Linux
        except AttributeError:
            pass # Some OS versions don't support SO_REUSEPORT

        s.bind(('0.0.0.0', 8080))
        s.listen(50)
        self.log(f'🚀 v4.1 LIVE on port 8080')

        def accept_loop():
            while True:
                try:
                    c, a = s.accept()
                    threading.Thread(target=self.handle_student, args=(c, a), daemon=True).start()
                except: break

        threading.Thread(target=accept_loop, daemon=True).start()

        while True:
            self.dashboard()
            cmd = input('\n🎯 ').lower().strip()
            if cmd == 'q':
                self.broadcast('Lab session ended.')
                self.save_logs()
                break
            elif cmd == 'h':
                print('\n'.join(self.history[-10:]))
            elif cmd == 'a':
                self.broadcast(input('📢 Message: '))
            elif cmd.startswith('r') and cmd[1:].isdigit():
                sid = int(cmd[1:])
                self.reply(sid, input(f'Reply to {self.clients[sid]["name"]}: '))
            elif cmd.startswith('k') and cmd[1:].isdigit():
                self.kick(int(cmd[1:]))

if __name__ == "__main__":
    server = TeacherPanelV4()
    try:
        server.run()
    except Exception as e:
        print(f"Server crashed: {e}")
    finally:
        # Clean up would happen here if you stored 's' as self.socket
        print("Cleaning up resources...")
