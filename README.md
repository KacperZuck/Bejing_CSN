# Lightweight Email Client

## Project Description
A lightweight email client implemented in Python using raw socket programming. The project demonstrates how application-layer network protocols work in practice by utilizing a basic subset of SMTP for sending and POP3 for receiving plain-text messages.

## Features
* **Low-level Communication:** Sending and receiving emails is implemented exclusively using raw TCP sockets (`socket` module), without utilizing high-level libraries that hide protocol implementations.
* **Secure Logging:** Records connection events, operations, and errors to log files with unique timestamps, while strictly preventing login passwords from being logged.
* **Local Mailbox (Bonus):** Persistently saves downloaded messages in a lightweight SQLite relational database so they can be viewed after restarting the program.
* **Graphical User Interface (Bonus):** A desktop GUI application built with the `tkinter` library.
* **Improved Concurrency (Bonus):** Separates network operations from the user interface using the `threading` module, preventing the application from freezing while waiting for server responses.
* **Built-in Test Servers:** The application automatically runs simulated, socket-based SMTP and POP3 test servers in the background for easy testing.

## Setup and Execution
1. Ensure you have Python 3.8 or newer installed on your system.
2. No external dependencies are required (the project relies entirely on Python's standard library).
3. Run the main file using the command: `python main.py`
4. The built-in test servers will automatically start and listen on local ports `8025` (SMTP) and `8110` (POP3).
