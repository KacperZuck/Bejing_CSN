import socket
from datetime import datetime
from Modules.logger import logger


class POP3Client:
    """Module for receiving emails using pure TCP sockets."""

    def __init__(self, server, port):
        self.server = server
        self.port = port

    def fetch_emails(self, username, password):
        logger.info(f"Authenticating user {username} on POP3 server {self.server}:{self.port}")
        messages = []

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10.0)
                s.connect((self.server, self.port))

                if not s.recv(1024).decode('utf-8').startswith('+OK'): return None

                def send_command(cmd, log_cmd=True):
                    if log_cmd: logger.debug(f"C: {cmd}")
                    s.sendall((cmd + "\r\n").encode('utf-8'))

                send_command(f"USER {username}")
                s.recv(1024)

                send_command(f"PASS {password}", log_cmd=False)
                if not s.recv(1024).decode('utf-8').startswith('+OK'):
                    logger.error("POP3 Error: Authentication failed.")
                    return None

                send_command("LIST")
                list_resp = ""
                while True:
                    list_resp += s.recv(1024).decode('utf-8')
                    if "\r\n.\r\n" in list_resp: break

                try:
                    num_messages = int(list_resp.split()[1])
                except (IndexError, ValueError):
                    num_messages = 0

                logger.info(f"Found {num_messages} messages on the server. Starting download...")

                for i in range(1, num_messages + 1):
                    send_command(f"RETR {i}")
                    retr_resp = ""
                    while True:
                        retr_resp += s.recv(4096).decode('utf-8', errors='ignore')
                        if "\r\n.\r\n" in retr_resp: break

                    if retr_resp.startswith('+OK'):
                        parts = retr_resp.split("\r\n\r\n", 1)
                        if len(parts) > 1:
                            headers_raw = parts[0]
                            body_content = parts[1].split("\r\n.\r\n")[0]
                        else:
                            headers_raw = ""
                            body_content = retr_resp.split("\r\n.\r\n")[0]

                        subject = "No subject"
                        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                        for line in headers_raw.split("\r\n"):
                            if line.lower().startswith("subject:"):
                                subject = line[8:].strip()
                            elif line.lower().startswith("date:"):
                                date_str = line[5:].strip()

                        messages.append({
                            "msg_number": i,
                            "sender": "server@example.com",
                            "subject": subject,
                            "date": date_str,
                            "body": body_content.strip()
                        })

                send_command("QUIT")
                s.recv(1024)

            logger.info("POP3 connection closed.")
            return messages

        except Exception as e:
            logger.error(f"POP3 communication error: {e}")
            return None