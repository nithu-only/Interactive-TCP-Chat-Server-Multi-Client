# 📡 Interactive TCP Chat Server – Multi-Client

An **interactive TCP-based chat application** built using Python that allows **multiple students (clients)** to connect to a **teacher (server)** and communicate in real time.
The client application provides a **GUI interface** for easy connection and messaging.

---

## 🧠 Project Overview

This project demonstrates **TCP socket programming** with a **multi-client architecture**.
A central server listens on a fixed port and manages all incoming client connections, while clients connect through a GUI by providing the server IP and their name.

This project is suitable for:

* Networking fundamentals
* Client–server architecture
* Socket programming
* Academic labs & demonstrations

---

## 🚀 Features

* 🖥️ **TCP Server (`serv.py`)**

  * Listens on **default port 8080**
  * Handles multiple client connections
  * Relays messages between teacher and students

* 💬 **GUI Client (`client.py`)**

  * Opens a graphical interface on execution
  * Prompts user for **Server IP address** and **Name**
  * Enables real-time chat with the teacher

* 🔄 **Multi-Client Support**

  * Multiple students can connect simultaneously
  * Messages are exchanged through the server

---

## 🛠️ Tech Stack

* **Python 3**
* **Socket programming**
* **GUI (Tkinter or similar Python GUI library)**

---

## 📁 Project Structure

```
Interactive-TCP-Chat-Server-Multi-Client/
├── serv.py        # TCP chat server (Teacher side)
├── client.py      # GUI-based chat client (Student side)
├── README.md      # Project documentation
└── .gitignore
```

---

## ▶️ How to Run

### 🧑‍🏫 Start the Server (Teacher)

1. Open a terminal
2. Navigate to the project directory
3. Run:

```bash
python3 serv.py
```

📌 The server will start listening on **port 8080** by default.

---

### 🎓 Start the Client (Student)

1. Open a new terminal
2. Run:

```bash
python3 client.py
```

3. A **GUI window** will open:

   * Enter **Server IP address**
   * Enter your **Name**
   * Click **Connect**
4. Start chatting with the teacher!

> You can open multiple client instances on the same or different machines within the same network.

---

## 💡 Notes

* Ensure the **server is running before clients connect**
* Server and clients must be on the **same network** or reachable IP
* Port **8080** must not be blocked by firewall
* Ideal for **classroom chat systems**, **lab exams**, and **networking demonstrations**

---

## 🔮 Future Enhancements

* Private messaging
* User authentication
* Chat history logging
* File sharing
* Secure communication (TLS/Encryption)

---

## 🧾 License

This project is open for educational and learning purposes.
