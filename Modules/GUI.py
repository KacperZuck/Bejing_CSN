import tkinter as tk
from tkinter import messagebox
import threading

from Modules.mailbox_db import MailboxDB
from Modules.smtp_client import SMTPClient
from Modules.pop_client import POP3Client

class ClientGUI:
    """Graphical User Interface implementation."""
    def __init__(self, root):
        self.root = root
        self.root.title("Lightweight Email Client")
        self.root.geometry("700x550")

        self.db = MailboxDB()
        self.smtp = SMTPClient("127.0.0.1", 8025)
        self.pop3 = POP3Client("127.0.0.1", 8110)

        self._build_ui()

    def _build_ui(self):
        input_frame = tk.Frame(self.root)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        tk.Label(input_frame, text="Email Subject:").pack(anchor=tk.W)
        self.subject_entry = tk.Entry(input_frame)
        self.subject_entry.pack(fill=tk.X, pady=(0, 5))

        tk.Label(input_frame, text="Email Body:").pack(anchor=tk.W)
        self.body_text = tk.Text(input_frame, height=5)
        self.body_text.pack(fill=tk.X)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Send Email (SMTP)", command=self.send_mail_thread, bg="lightblue").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Check Mail (POP3)", command=self.check_mail_thread, bg="lightgreen").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Show Local Messages", command=self.show_local_messages).pack(side=tk.LEFT, padx=10)

        self.text_area = tk.Text(self.root, wrap=tk.WORD, state=tk.DISABLED)
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def clear_ui(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.config(state=tk.DISABLED)

    def write_to_ui(self, message):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

    def check_mail_thread(self):
        self.clear_ui()
        self.write_to_ui("Checking mail on POP3 server...")
        threading.Thread(target=self._check_mail_task, daemon=True).start()

    def _check_mail_task(self):
        messages = self.pop3.fetch_emails("student", "secret")
        if messages:
            for msg in messages:
                self.db.save_message(
                    msg["msg_number"], msg["sender"], msg["subject"], msg["date"], msg["body"]
                )
            self.root.after(0, lambda: self._show_just_downloaded(messages))
        else:
            self.root.after(0, lambda: self.write_to_ui("\nThe mailbox is empty or an error occurred (check logs)."))

    def _show_just_downloaded(self, messages):
        self.write_to_ui(f"\nSuccess! Downloaded {len(messages)} messages from the server.\n")
        self.write_to_ui("--- NEWLY DOWNLOADED MESSAGES ---")
        for msg in messages:
            self.write_to_ui(f"From: {msg['sender']} | Subject: {msg['subject']} | Date: {msg['date']}")
            self.write_to_ui(f"Body: {msg['body']}")
            self.write_to_ui("-" * 40)

    def send_mail_thread(self):
        threading.Thread(target=self._send_mail_task, daemon=True).start()

    def _send_mail_task(self):
        subject = self.subject_entry.get()
        body = self.body_text.get("1.0", tk.END).strip()

        if not subject or not body:
            self.root.after(0, lambda: messagebox.showwarning("Missing Info", "Please enter a subject and body."))
            return

        success = self.smtp.send_email(
            from_address="me@myclient.edu",
            to_address="test@recipient.edu",
            subject=subject,
            body=body
        )
        if success:
            self.root.after(0, lambda: messagebox.showinfo("Success", "Message sent to the SMTP server!\n\nClick 'Check Mail (POP3)' to view it."))
            self.root.after(0, lambda: self.subject_entry.delete(0, tk.END))
            self.root.after(0, lambda: self.body_text.delete("1.0", tk.END))
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", "Failed to send the message."))

    def show_local_messages(self):
        self.clear_ui()
        messages = self.db.get_all_messages()
        if not messages:
            self.write_to_ui("No messages in the local SQLite database.")
            return

        self.write_to_ui(f"--- ALL LOCAL MESSAGES (Total: {len(messages)}) ---")
        for msg in messages:
            self.write_to_ui(f"From: {msg[2]} | Date: {msg[4]}")
            self.write_to_ui(f"Subject: {msg[3]}")
            self.write_to_ui(f"Body: {msg[5]}")
            self.write_to_ui("-" * 40)