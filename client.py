import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class ModernStudentClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Lab Student Client v4.2")
        self.root.geometry("500x650")
        self.root.configure(bg="#1e1e1e")  # Dark background
        self.sock = None
        
        # Define Professional Color Palette
        self.bg_dark = "#1e1e1e"
        self.bg_light = "#2d2d2d"
        self.accent = "#007acc"  # VS Code Blue
        self.text_color = "#ffffff"
        
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Frame and Label Styles
        style.configure("TFrame", background=self.bg_dark)
        style.configure("TLabel", background=self.bg_dark, foreground=self.text_color, font=("Segoe UI", 10))
        
        # Modern Button Style
        style.configure("Accent.TButton", foreground="white", background=self.accent, font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", background=[('active', '#005a9e')])

    def create_widgets(self):
        # --- Top Header ---
        header = tk.Label(self.root, text="LAB TERMINAL", bg=self.accent, fg="white", font=("Segoe UI", 12, "bold"), pady=10)
        header.pack(fill=tk.X)

        # --- Connection Panel ---
        conn_frame = ttk.Frame(self.root, padding=20)
        conn_frame.pack(fill=tk.X)

        ttk.Label(conn_frame, text="Server IP Address").pack(anchor=tk.W)
        self.ip_entry = tk.Entry(conn_frame, bg=self.bg_light, fg="white", insertbackground="white", borderwidth=0, font=("Consolas", 11))
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)

        ttk.Label(conn_frame, text="Student Name").pack(anchor=tk.W)
        self.name_entry = tk.Entry(conn_frame, bg=self.bg_light, fg="white", insertbackground="white", borderwidth=0, font=("Consolas", 11))
        self.name_entry.pack(fill=tk.X, pady=(5, 15), ipady=8)

        self.btn_connect = ttk.Button(conn_frame, text="JOIN SESSION", style="Accent.TButton", command=self.connect_to_server)
        self.btn_connect.pack(fill=tk.X, pady=10, ipady=5)

        # --- Chat Area ---
        chat_frame = ttk.Frame(self.root, padding=20)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_area = scrolledtext.ScrolledText(
            chat_frame, state='disabled', bg=self.bg_light, fg="#dcdcdc", 
            font=("Consolas", 10), borderwidth=0, highlightthickness=1, 
            highlightbackground="#444", padx=10, pady=10
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        # --- Input Bar (FIXED LINE BELOW) ---
        input_frame = tk.Frame(self.root, bg=self.bg_dark, padx=20, pady=20) 
        input_frame.pack(fill=tk.X)

        self.msg_entry = tk.Entry(input_frame, bg=self.bg_light, fg="white", insertbackground="white", borderwidth=0, font=("Segoe UI", 11))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda x: self.send_message())

        self.btn_send = ttk.Button(input_frame, text="SEND", command=self.send_message)
        self.btn_send.pack(side=tk.RIGHT, ipady=5)

    def log_to_ui(self, message):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, f" {message}\n")
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def connect_to_server(self):
        ip = self.ip_entry.get()
        name = self.name_entry.get()
        if not name:
            messagebox.showwarning("Incomplete", "Please enter your name before joining.")
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, 8080))
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
            # Send name with explicit newline
            self.sock.send(f"{name}\n".encode('ascii'))
            
            self.btn_connect.config(state='disabled')
            self.ip_entry.config(state='disabled')
            self.name_entry.config(state='disabled')
            self.log_to_ui(f"SYSTEM: Successfully connected to {ip}")
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Could not reach server.\n{e}")

    def receive_messages(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if not data: break
                msg = data.decode('utf-8', errors='ignore').strip()
                self.root.after(0, self.log_to_ui, msg)
            except: break
        self.log_to_ui("SYSTEM: Connection lost.")
        self.btn_connect.config(state='normal')

    def send_message(self):
        msg = self.msg_entry.get()
        if msg and self.sock:
            try:
                self.sock.send(f"{msg}\n".encode('ascii'))
                self.log_to_ui(f"YOU: {msg}")
                self.msg_entry.delete(0, tk.END)
            except:
                self.log_to_ui("SYSTEM: Error sending message.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernStudentClient(root)
    root.mainloop()
