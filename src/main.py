import sys
import os
import threading
from PyQt6.QtWidgets import QApplication
from ui import FloatingUI
from tracker import WorkTracker

def main():
    app = QApplication(sys.argv)
    
    # Run tracker in background thread
    tracker = WorkTracker()
    tracker_thread = threading.Thread(target=tracker.run, daemon=True)
    tracker_thread.start()

    window = FloatingUI(tracker)
    window.show()

    # When UI is closed, PyQt will exit the main loop. 
    # Since background thread is a daemon, it will terminate as well.
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
