import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

class StudentClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lab Student Client v1.0")
        self.sock = None
        
        # --- UI Layout ---
        # Connection Frame (IP and Name)
        self.conn_frame = tk.Frame(root)
        self.conn_frame.pack(pady=10)
        
        tk.Label(self.conn_frame, text="Server IP:").grid(row=0, column=0)
        self.ip_entry = tk.Entry(self.conn_frame)
        self.ip_entry.insert(0, "127.0.0.1") # Default local
        self.ip_entry.grid(row=0, column=1)
        
        tk.Label(self.conn_frame, text="Your Name:").grid(row=1, column=0)
        self.name_entry = tk.Entry(self.conn_frame)
        self.name_entry.grid(row=1, column=1)
        
        self.btn_connect = tk.Button(self.conn_frame, text="Connect", command=self.connect_to_server)
        self.btn_connect.grid(row=2, columnspan=2, pady=5)
        
        # Chat Display
        self.chat_area = scrolledtext.ScrolledText(root, state='disabled', width=50, height=15)
        self.chat_area.pack(padx=10, pady=5)
        
        # Message Input
        self.msg_entry = tk.Entry(root, width=40)
        self.msg_entry.pack(side=tk.LEFT, padx=10, pady=10)
        self.msg_entry.bind("<Return>", lambda x: self.send_message())
        
        self.btn_send = tk.Button(root, text="Send", command=self.send_message)
        self.btn_send.pack(side=tk.LEFT, pady=10)

    def log_to_ui(self, message):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def connect_to_server(self):
        ip = self.ip_entry.get()
        name = self.name_entry.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter your name!")
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, 8080))
            
            # Start background thread to listen for messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
            # Send name immediately (matching the server handshake)
            self.sock.send(f"{name}\n".encode('ascii'))
            self.btn_connect.config(state='disabled')
            self.log_to_ui(f"📡 Connected to {ip}")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if not data: break
                msg = data.decode('utf-8', errors='ignore').strip()
                self.root.after(0, self.log_to_ui, msg)
            except:
                break
        self.log_to_ui("❌ Disconnected from server.")
        self.btn_connect.config(state='normal')

    def send_message(self):
        msg = self.msg_entry.get()
        if msg and self.sock:
            try:
                self.sock.send(f"{msg}\n".encode('ascii'))
                self.log_to_ui(f"You: {msg}")
                self.msg_entry.delete(0, tk.END)
            except:
                self.log_to_ui("⚠️ Failed to send message.")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentClientGUI(root)
    root.mainloop()
