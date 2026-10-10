import socket
import threading
from datetime import datetime
from Modules.logger import logger

# Global list acting as the server's mail spool
SERVER_MAILBOX = [
    "Subject: Welcome Message\r\n"
    f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\r\n"
    "From: server@example.edu\r\n\r\n"
    "This is the default message in the test mailbox.\r\n"
]


def run_smtp():
    global SERVER_MAILBOX
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 8025))
        server.listen(1)
        logger.info("[SMTP SERVER] Listening on port 8025...")

        while True:
            conn, addr = server.accept()
            try:
                conn.sendall(b"220 test.example.edu SMTP ready\r\n")
                while True:
                    data = conn.recv(1024).decode('utf-8')
                    if not data: break

                    if data.upper().startswith("EHLO") or data.upper().startswith("HELO"):
                        conn.sendall(b"250 OK\r\n")
                    elif data.upper().startswith("MAIL FROM") or data.upper().startswith("RCPT TO"):
                        conn.sendall(b"250 OK\r\n")
                    elif data.upper().startswith("DATA"):
                        conn.sendall(b"354 End data with <CRLF>.<CRLF>\r\n")

                        email_data = ""
                        while "\r\n.\r\n" not in email_data:
                            email_data += conn.recv(1024).decode('utf-8')

                        # Append the received email to the mailbox
                        SERVER_MAILBOX.append(email_data.replace("\r\n.\r\n", ""))

                        conn.sendall(b"250 Message accepted\r\n")
                    elif data.upper().startswith("QUIT"):
                        conn.sendall(b"221 Bye\r\n")
                        break
            except Exception:
                pass
            finally:
                conn.close()
    except Exception as e:
        logger.error(f"SMTP Server Error: {e}")


def run_pop():
    global SERVER_MAILBOX
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 8110))
        server.listen(1)
        logger.info("[POP3 SERVER] Listening on port 8110...")

        while True:
            conn, addr = server.accept()
            try:
                conn.sendall(b"+OK POP3 server ready\r\n")
                while True:
                    data = conn.recv(1024).decode('utf-8')
                    if not data: break

                    if data.upper().startswith("USER") or data.upper().startswith("PASS"):
                        conn.sendall(b"+OK\r\n")
                    elif data.upper().startswith("LIST"):
                        response = f"+OK {len(SERVER_MAILBOX)} messages\r\n"
                        for idx, msg in enumerate(SERVER_MAILBOX):
                            response += f"{idx + 1} {len(msg)}\r\n"
                        response += ".\r\n"
                        conn.sendall(response.encode('utf-8'))
                    elif data.upper().startswith("RETR"):
                        try:
                            msg_idx = int(data.split()[1]) - 1
                            if 0 <= msg_idx < len(SERVER_MAILBOX):
                                email_response = f"+OK message follows\r\n{SERVER_MAILBOX[msg_idx]}\r\n.\r\n"
                                conn.sendall(email_response.encode('utf-8'))
                            else:
                                conn.sendall(b"-ERR no such message\r\n")
                        except:
                            conn.sendall(b"-ERR invalid command\r\n")
                    elif data.upper().startswith("QUIT"):
                        conn.sendall(b"+OK Bye\r\n")
                        break
            except Exception:
                pass
            finally:
                conn.close()
    except Exception as e:
        logger.error(f"POP3 Server Error: {e}")


def start_back_servers():
    threading.Thread(target=run_smtp, daemon=True).start()
    threading.Thread(target=run_pop, daemon=True).start()