from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                               QDialog, QLineEdit, QFileDialog, QListWidget, QDoubleSpinBox, QTextEdit, QSpinBox, QInputDialog)
from PyQt6.QtCore import Qt, QTimer
import settings
import os

class FloatingUI(QWidget):
    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Top bar with status and minimize toggle
        top_layout = QHBoxLayout()
        self.status_label = QLabel("RECORDING")
        self.status_label.setStyleSheet("color: white; background-color: rgba(50, 50, 50, 200); padding: 5px; border-radius: 3px;")
        top_layout.addWidget(self.status_label)
        
        self.toggle_btn = QPushButton("-")
        self.toggle_btn.setFixedSize(24, 24)
        self.toggle_btn.setStyleSheet("background-color: #555555; color: white; border-radius: 12px; font-weight: bold;")
        self.toggle_btn.clicked.connect(self.toggle_minimize)
        top_layout.addWidget(self.toggle_btn)
        
        layout.addLayout(top_layout)

        # Buttons container to easily hide/show
        self.buttons_widget = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.current_app_label = QLabel("App: None")
        self.current_app_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        buttons_layout.addWidget(self.current_app_label)

        self.toggle_target_btn = QPushButton("+ Add Target")
        self.toggle_target_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.toggle_target_btn.clicked.connect(self.on_toggle_target)
        buttons_layout.addWidget(self.toggle_target_btn)

        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.start_btn.clicked.connect(self.on_start)
        buttons_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setStyleSheet("background-color: #ff9800; color: white;")
        self.pause_btn.clicked.connect(self.on_pause)
        buttons_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.stop_btn.clicked.connect(self.on_stop)
        buttons_layout.addWidget(self.stop_btn)

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.settings_btn.clicked.connect(self.on_settings)
        buttons_layout.addWidget(self.settings_btn)

        self.logs_btn = QPushButton("Logs")
        self.logs_btn.setStyleSheet("background-color: #9C27B0; color: white;")
        self.logs_btn.clicked.connect(self.on_logs)
        buttons_layout.addWidget(self.logs_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet("background-color: #555555; color: white;")
        self.close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_btn)

        self.buttons_widget.setLayout(buttons_layout)
        layout.addWidget(self.buttons_widget)

        self.setLayout(layout)
        self.setGeometry(100, 100, 150, 150)
        self.setStyleSheet("background-color: rgba(30, 30, 30, 180); border-radius: 10px;")
        
        self.is_minimized = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(250)

    def toggle_minimize(self):
        self.is_minimized = not self.is_minimized
        if self.is_minimized:
            self.buttons_widget.hide()
            self.toggle_btn.setText("+")
            self.adjustSize() # shrink to fit
        else:
            self.buttons_widget.show()
            self.toggle_btn.setText("-")
            self.adjustSize()

    def update_status(self):
        self.status_label.setText(self.tracker.status)
        current_exe = getattr(self.tracker, 'get_foreground_app', lambda: "")()
        
        if current_exe:
            self.current_app_label.setText(f"App: {current_exe}")
            
            is_target = False
            exe_base = current_exe.replace(".exe", "")
            
            for t in self.tracker.target_apps:
                t_base = t.replace(".exe", "")
                if t == current_exe or (t_base and exe_base and (t_base.startswith(exe_base) or exe_base.startswith(t_base))):
                    is_target = True
                    break
            
            if is_target:
                self.toggle_target_btn.setText("- Remove Target")
                self.toggle_target_btn.setStyleSheet("background-color: #f44336; color: white;")
            else:
                self.toggle_target_btn.setText("+ Add Target")
                self.toggle_target_btn.setStyleSheet("background-color: #4CAF50; color: white;")

    def on_toggle_target(self):
        current_exe = getattr(self.tracker, 'last_foreground_exe', "")
        if not current_exe: return
        
        config = settings.load_settings()
        targets = [app.lower() for app in config.get("target_apps", [])]
        
        is_target = False
        target_to_remove = current_exe
        exe_base = current_exe.replace(".exe", "")
        
        for t in targets:
            t_base = t.replace(".exe", "")
            if t == current_exe or (t_base and exe_base and (t_base.startswith(exe_base) or exe_base.startswith(t_base))):
                is_target = True
                target_to_remove = t
                break
                
        if is_target:
            targets.remove(target_to_remove)
        else:
            targets.append(current_exe)
            
        config["target_apps"] = targets
        settings.save_settings(config)
        self.tracker.reload_settings()

    def on_start(self):
        self.tracker.start()

    def on_pause(self):
        self.tracker.pause()

    def on_stop(self):
        self.tracker.stop()

    def on_logs(self):
        dialog = LogDialog(self)
        dialog.exec()

    def on_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Apply new settings
            self.tracker.reload_settings()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            
            # Keep window on screen
            if self.screen():
                screen_geom = self.screen().availableGeometry()
                new_x = max(screen_geom.left(), min(new_pos.x(), screen_geom.right() - self.width()))
                new_y = max(screen_geom.top(), min(new_pos.y(), screen_geom.bottom() - self.height()))
                self.move(new_x, new_y)
            else:
                self.move(new_pos)
                
            event.accept()

class LogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Application Logs")
        self.setMinimumSize(600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_logs)
        layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        layout.addWidget(clear_btn)

        self.setLayout(layout)
        self.load_logs()

    def load_logs(self):
        if os.path.exists('autolapse.log'):
            with open('autolapse.log', 'r', encoding='utf-8') as f:
                self.log_text.setText(f.read())
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )
        else:
            self.log_text.setText("Log file not found.")

    def clear_logs(self):
        with open('autolapse.log', 'w', encoding='utf-8') as f:
            f.write("")
        self.load_logs()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        self.config = settings.load_settings()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Target Apps
        main_layout.addWidget(QLabel("Target Applications (.exe files):"))
        self.app_list = QListWidget()
        for app in self.config.get("target_apps", []):
            self.app_list.addItem(app)
        main_layout.addWidget(self.app_list)

        app_btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add App Name")
        add_btn.clicked.connect(self.add_app)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_app)
        app_btn_layout.addWidget(add_btn)
        app_btn_layout.addWidget(remove_btn)
        main_layout.addLayout(app_btn_layout)

        # Base Directory
        main_layout.addWidget(QLabel("Save Directory:"))
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit(self.config.get("base_dir", "captures"))
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_dir)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_btn)
        main_layout.addLayout(dir_layout)

        # FPS
        main_layout.addWidget(QLabel("Capture Frame Rate (FPS):"))
        self.fps_spin = QDoubleSpinBox()
        self.fps_spin.setRange(0.1, 30.0)
        self.fps_spin.setValue(self.config.get("fps", 2.0))
        main_layout.addWidget(self.fps_spin)

        # Quality
        main_layout.addWidget(QLabel("JPEG Quality (1-100, lower = smaller file):"))
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(self.config.get("quality", 30))
        main_layout.addWidget(self.quality_spin)

        # Resolution Resize
        main_layout.addWidget(QLabel("Resolution Scale % (1-100, lower = smaller file):"))
        self.resize_spin = QSpinBox()
        self.resize_spin.setRange(1, 100)
        self.resize_spin.setValue(self.config.get("resize_percent", 100))
        main_layout.addWidget(self.resize_spin)

        # Save/Cancel
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def add_app(self):
        text, ok = QInputDialog.getText(self, "Add Application", "Enter executable name (e.g., blender.exe):")
        if ok and text:
            # Add exactly the executable name lowercase to list
            self.app_list.addItem(text.strip().lower())

    def remove_app(self):
        for item in self.app_list.selectedItems():
            self.app_list.takeItem(self.app_list.row(item))

    def browse_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if dir_path:
            self.dir_input.setText(dir_path)

    def save(self):
        apps = []
        for i in range(self.app_list.count()):
            apps.append(self.app_list.item(i).text())
        
        self.config["target_apps"] = apps
        self.config["base_dir"] = self.dir_input.text()
        self.config["fps"] = self.fps_spin.value()
        self.config["quality"] = self.quality_spin.value()
        self.config["resize_percent"] = self.resize_spin.value()
        
        settings.save_settings(self.config)
        self.accept()

