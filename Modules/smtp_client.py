import socket
from datetime import datetime
from Modules.logger import logger


class SMTPClient:
    """Module for sending emails using pure TCP sockets."""

    def __init__(self, server, port):
        self.server = server
        self.port = port

    def send_email(self, from_address, to_address, subject, body):
        logger.info(f"Connecting to SMTP server: {self.server}:{self.port}")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10.0)
                s.connect((self.server, self.port))

                recv = s.recv(1024).decode('utf-8')
                logger.debug(f"S: {recv.strip()}")

                def send_command(cmd):
                    logger.debug(f"C: {cmd}")
                    s.sendall((cmd + "\r\n").encode('utf-8'))
                    response = s.recv(1024).decode('utf-8')
                    logger.debug(f"S: {response.strip()}")
                    return response

                send_command("EHLO student-client")
                send_command(f"MAIL FROM: <{from_address}>")
                send_command(f"RCPT TO: <{to_address}>")

                resp_data = send_command("DATA")
                if not resp_data.startswith('354'):
                    raise Exception(f"Server rejected DATA command: {resp_data}")

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

                message = f"Subject: {subject}\r\n"
                message += f"Date: {current_time}\r\n"
                message += f"From: <{from_address}>\r\n"
                message += f"To: <{to_address}>\r\n"
                message += "\r\n"
                message += body
                message += "\r\n.\r\n"

                logger.debug("C: [Sending message body and terminating dot...]")
                s.sendall(message.encode('utf-8'))

                resp_msg = s.recv(1024).decode('utf-8')
                logger.debug(f"S: {resp_msg.strip()}")

                send_command("QUIT")

            logger.info(f"Message to {to_address} sent successfully.")
            return True

        except socket.timeout:
            logger.error("Error: Server response timeout.")
            return False
        except Exception as e:
            logger.error(f"SMTP sending error: {e}")
            return False