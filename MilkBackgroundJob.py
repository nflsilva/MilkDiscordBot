import threading
import time
import asyncio


class MilkBackgroundJob:

    def background_process(self):
        while self.is_running:
            now = time.time()
            self.elapsed_time = now - self.last_run
            self.last_run = now
            self.method()
            time.sleep(10)

    def __init__(self, method):
        self.is_running = False
        self.elapsed_time = time.time()
        self.last_run = time.time()
        self.method = method
        self.thread = threading.Thread(target=self.background_process)

    def start(self):
        self.is_running = True
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.thread.join()
