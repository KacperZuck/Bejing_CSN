import tkinter as tk
import time

from Modules.logger import logger
from Modules.servers import start_servers
from Modules.GUI import ClientGUI

if __name__ == "__main__":
    logger.info("Starting application.")

    start_servers()
    time.sleep(0.5)

    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()

    logger.info("Application closed.")