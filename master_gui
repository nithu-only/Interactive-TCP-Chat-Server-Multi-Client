import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

class TeacherServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("👨‍🏫 Instructor Control Panel v5.0")
        self.root.geometry("800x600")
        self.root.configure(bg="#252526")

        # Backend Data
        self.clients = {}
        self.next_id = 1
        self.server_sock = None

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", background="#2d2d2d", foreground="white", fieldbackground="#2d2d2d", font=("Segoe UI", 10))
        self.style.map("Treeview", background=[('selected', '#007acc')])

    def create_widgets(self):
        # --- Sidebar (Student List) ---
        sidebar = tk.Frame(self.root, bg="#333333", width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(sidebar, text="ONLINE STUDENTS", bg="#333333", fg="#aaaaaa", font=("Segoe UI", 9, "bold")).pack(pady=10)

        self.student_tree = ttk.Treeview(sidebar, columns=("ID", "Name"), show='headings', height=20)
        self.student_tree.heading("ID", text="ID")
        self.student_tree.heading("Name", text="Name")
        self.student_tree.column("ID", width=40, anchor=tk.CENTER)
        self.student_tree.column("Name", width=180)
        self.student_tree.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # --- Main Chat Area ---
        main_area = tk.Frame(self.root, bg="#252526")
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.log_area = scrolledtext.ScrolledText(main_area, state='disabled', bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10), borderwidth=0)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # --- Control Bar ---
        control_bar = tk.Frame(main_area, bg="#252526", pady=10)
        control_bar.pack(fill=tk.X)

        self.msg_entry = tk.Entry(control_bar, bg="#3c3c3c", fg="white", borderwidth=0, font=("Segoe UI", 11))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5), ipady=8)
        self.msg_entry.bind("<Return>", lambda x: self.send_to_selected())

        btn_send = tk.Button(control_bar, text="REPLY", bg="#007acc", fg="white", command=self.send_to_selected, font=("Segoe UI", 9, "bold"), padx=15)
        btn_send.pack(side=tk.LEFT, padx=5)

        btn_all = tk.Button(control_bar, text="BROADCAST", bg="#6a9955", fg="white", command=self.broadcast_all, font=("Segoe UI", 9, "bold"), padx=15)
        btn_all.pack(side=tk.LEFT, padx=10)

    def log(self, message):
        ts = datetime.now().strftime('%H:%M:%S')
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"[{ts}] {message}\n")
        self.log_area.configure(state='disabled')
        self.log_area.yview(tk.END)

    def update_student_list(self):
        # Clear current list
        for i in self.student_tree.get_children():
            self.student_tree.delete(i)
        # Add active clients
        for sid, info in self.clients.items():
            if info['alive']:
                self.student_tree.insert("", tk.END, values=(sid, info['name']))

    def start_server(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('0.0.0.0', 8080))
        self.server_sock.listen(50)
        self.log("🚀 Server started on port 8080. Waiting for students...")

        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while True:
            conn, addr = self.server_sock.accept()
            threading.Thread(target=self.handle_student, args=(conn, addr), daemon=True).start()

    def handle_student(self, conn, addr):
        sid = self.next_id
        self.next_id += 1

        try:
            # Simple Name Handshake
            name_data = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            name = name_data if name_data else f"Student_{sid}"

            self.clients[sid] = {'sock': conn, 'addr': addr, 'name': name, 'alive': True}
            self.root.after(0, self.update_student_list)
            self.log(f"🔗 {name} joined from {addr[0]}")

            while True:
                data = conn.recv(1024)
                if not data: break
                msg = data.decode('utf-8', errors='ignore').strip()
                self.log(f"📩 {name}: {msg}")

        except: pass
        finally:
            if sid in self.clients:
                self.clients[sid]['alive'] = False
                self.log(f"👋 {self.clients[sid]['name']} disconnected.")
                self.clients.pop(sid)
                self.root.after(0, self.update_student_list)
            conn.close()

    def send_to_selected(self):
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please click a student in the sidebar first!")
            return

        # Get the ID from the selected row
        item = self.student_tree.item(selected[0])
        sid = item['values'][0]
        msg = self.msg_entry.get().strip()

        if msg and sid in self.clients:
            target = self.clients[sid]
            try:
                # Add \r\n to ensure it shows up correctly on the student side
                target['sock'].send(f"💬 Teacher: {msg}\r\n".encode('ascii', errors='ignore'))
                self.log(f"📤 Sent to {target['name']}: {msg}")
                self.msg_entry.delete(0, tk.END)
            except (ConnectionResetError, BrokenPipeError, OSError):
                self.log(f"❌ Failed: {target['name']} has disconnected.")
                self.clients[sid]['alive'] = False
                self.root.after(0, self.update_student_list)
        elif not msg:
            messagebox.showwarning("Empty Message", "You cannot send an empty message.")


    def broadcast_all(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            messagebox.showwarning("Empty Message", "Please enter a message to broadcast.")
            return

        count = 0
        # We use list(self.clients.keys()) to avoid 'dictionary changed size' errors
        for sid in list(self.clients.keys()):
            if self.clients[sid]['alive']:
                try:
                    # Added \n at the end - THIS IS THE CRITICAL FIX
                    self.clients[sid]['sock'].send(f"📢 ALL: {msg}\n".encode('ascii', errors='ignore'))
                    count += 1
                except:
                    self.clients[sid]['alive'] = False

        self.log(f"📢 Broadcasted to {count} students: {msg}")
        self.msg_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = TeacherServerGUI(root)
    app.start_server()
    root.mainloop()
