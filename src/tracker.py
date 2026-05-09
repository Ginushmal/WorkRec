import time
import os
from datetime import datetime
import threading
import win32gui
import win32process
import psutil
from mss import mss
from pynput import mouse, keyboard
from PIL import Image
import settings
import logging

# Setup logging
logger = logging.getLogger('AutoLapse')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('autolapse.log', mode='a', encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(fh)

class WorkTracker:
    def __init__(self):
        self.status = "STARTING..."
        self.reload_settings()
        
        self.running = False
        self.paused = False
        self.activity_detected = False
        
        self.mouse_listener = mouse.Listener(
            on_move=self._on_activity,
            on_click=self._on_activity,
            on_scroll=self._on_activity
        )
        self.mouse_listener.start()
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_activity
        )
        self.keyboard_listener.start()

        self.last_capture_time = 0

    def reload_settings(self):
        config = settings.load_settings()
        self.target_apps = [app.lower() for app in config.get("target_apps", [])]
        base_dir = config.get("base_dir", "captures")
        self.base_dir = os.path.abspath(base_dir)
        fps = config.get("fps", 2.0)
        self.quality = config.get("quality", 30)
        self.resize_percent = config.get("resize_percent", 100)
        self.interval = 1.0 / fps if fps > 0 else 0.5
        logger.info(f"Settings loaded. Target apps: {self.target_apps}, FPS: {fps}, Quality: {self.quality}, Scale: {self.resize_percent}%, Dir: {self.base_dir}")

    def _on_activity(self, *args, **kwargs):
        self.activity_detected = True

    def start(self):
        self.running = True
        self.paused = False

    def pause(self):
        self.paused = True

    def stop(self):
        self.running = False

    def is_target_active(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return False, ""
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid <= 0:
                return False, ""
                
            try:
                process = psutil.Process(pid)
                exe_name = process.name().lower()
            except psutil.Error as e:
                exe_name = ""
                logger.debug(f"psutil error for pid {pid}: {e}")
            
            window_title = win32gui.GetWindowText(hwnd).lower()
            
            # Log the current active window to debug matching issues
            logger.debug(f"Active window -> exe: '{exe_name}', title: '{window_title}'")
            
            for app in self.target_apps:
                app_base = app.replace(".exe", "")
                exe_base = exe_name.replace(".exe", "") if exe_name else ""
                
                # Check for direct match, or if one name starts with the other (to handle 'blender-launcher' vs 'blender')
                # Or check if the user's defined app base is directly in the window title
                if (app == exe_name or 
                    (app_base and exe_base and (app_base.startswith(exe_base) or exe_base.startswith(app_base))) or 
                    (app_base and app_base in window_title)):
                    
                    app_label = exe_base if exe_base else app_base
                    logger.debug(f"Matched target list item '{app}' with '{app_label}'")
                    return True, app_label
        except Exception as e:
            logger.error(f"Error in is_target_active: {e}")
            pass
            
        return False, ""

    def get_foreground_app(self):
        if not hasattr(self, 'last_foreground_exe'):
            self.last_foreground_exe = ""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return self.last_foreground_exe
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid <= 0:
                return self.last_foreground_exe
                
            try:
                process = psutil.Process(pid)
                exe_name = process.name().lower()
            except psutil.Error:
                return self.last_foreground_exe
            
            # Prevent "UI" from overwriting the last actual target app
            if "python" in exe_name or "autolapse" in exe_name or "explorer" in exe_name:
                return self.last_foreground_exe
                
            self.last_foreground_exe = exe_name
            return exe_name
        except Exception:
            return getattr(self, 'last_foreground_exe', "")
        
    def capture_screen(self, app_name):
        date_str = datetime.now().strftime("%Y-%m-%d")
        dir_path = os.path.join(self.base_dir, app_name, date_str)
        os.makedirs(dir_path, exist_ok=True)
        
        filename = f"frame_{int(time.time()*1000)}.jpg"
        filepath = os.path.join(dir_path, filename)

        with mss() as sct:
            sct_img = sct.grab(sct.monitors[1]) # Primary monitor
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            
            if hasattr(self, 'resize_percent') and self.resize_percent < 100:
                new_w = int(img.width * (self.resize_percent / 100.0))
                new_h = int(img.height * (self.resize_percent / 100.0))
                img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)

            # Aggressive compression to save disk space
            img.save(filepath, "JPEG", quality=self.quality, optimize=True)
            
    def run(self):
        self.running = True
        logger.info("Tracker started.")
        while True:
            is_active, app_name = self.is_target_active()
            
            # --- Auto-trigger recording behavior requested ---
            # If the app is active, automatically wake from Stop/Pause
            if is_active and (not self.running or self.paused):
                self.running = True
                self.paused = False

            if not self.running:
                self.status = "STOPPED"
                time.sleep(1)
                continue
                
            if self.paused:
                self.status = "PAUSED"
                time.sleep(1)
                continue
                
            current_time = time.time()
            if is_active:
                if self.activity_detected:
                    self.status = f"RECORDING ({app_name})"
                    if current_time - self.last_capture_time >= self.interval:
                        try:
                            self.capture_screen(app_name)
                        except Exception as e:
                            self.status = f"ERROR: {e}"
                        self.activity_detected = False # Reset for next frame
                        self.last_capture_time = current_time
                else:
                    self.status = f"IDLE ({app_name})"
                    self.last_capture_time = current_time
            else:
                self.status = "WAITING FOR TARGET APP"
                self.last_capture_time = current_time
                self.activity_detected = False
                    
            time.sleep(0.1)
