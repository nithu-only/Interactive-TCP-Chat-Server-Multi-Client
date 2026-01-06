#!/usr/bin/env python3
# Ubuntu Networking Lab Server v2.0 - Module 5.2
import socket, threading, os
from datetime import datetime
from colorama import init, Fore, Style
init()

class UbuntuLabServer:
    def __init__(self):
        self.clients = []
        self.stats = {'connections': 0, 'messages': 0}
    
    def log(self, msg, color=Fore.WHITE):
        ts = datetime.now().strftime('%H:%M:%S')
        print(f'[{ts}]{color} UbuntuLab |{Style.RESET_ALL} {msg}')
    
    def banner(self):
        os.system('clear')
        ip = socket.gethostbyname(socket.gethostname())
        print(Fore.GREEN + f'''
╔══════════════════════════════════════════════════════╗
║  🐍 PYTHON MODULE 5.2 NETWORKING LAB SERVER v2.0    ║
║  Ubuntu Server • Multi-Client • Real-time Chat      ║
╠══════════════════════════════════════════════════════╣
║  📶 SERVER IP: {ip:<15} PORT: 8080                 ║
║  👥 MAX CLIENTS: 50  📊 STATS: {self.stats}         ║
╚══════════════════════════════════════════════════════╝
        ''' + Style.RESET_ALL)
    
    def start(self):
        self.banner()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 8080))
        s.listen(50)
        
        self.log('🚀 LIVE! 0.0.0.0:8080 - Waiting for students...', Fore.GREEN)
        self.log(f'🌐 Connect: telnet {socket.gethostbyname(socket.gethostname())} 8080', Fore.YELLOW)
        
        while True:
            c, addr = s.accept()
            self.clients.append(c)
            self.stats['connections'] += 1
            self.log(f'🔗 C#{len(self.clients)}: {addr[0]}:{addr[1]} ✅', Fore.BLUE)
            t = threading.Thread(target=self.handle_client, args=(c, addr))
            t.daemon = True
            t.start()
    
    def handle_client(self, c, addr):
        cid = len(self.clients)
        while True:
            try:
                data = c.recv(1024).decode(errors='ignore')
                if not data: break
                self.stats['messages'] += 1
                self.log(f'📨 C#{cid}({addr[0]}): {data[:40]}{"..."if len(data)>40 else""}', Fore.YELLOW)
                reply = input(f'💬 C#{cid}: ')
                if reply.lower() in ['quit','shutdown']:
                    return os._exit(0)
                if reply.startswith('/all '):
                    for x in self.clients:
                        if x!=c: x.send(f'BROADCAST: {reply[4:]}\n'.encode())
                else:
                    c.send(reply.encode())
            except: break
        c.close()
        if c in self.clients: self.clients.remove(c)
        self.log(f'🔌 C#{cid} DISCONNECTED', Fore.RED)

if __name__=='__main__': UbuntuLabServer().start()
