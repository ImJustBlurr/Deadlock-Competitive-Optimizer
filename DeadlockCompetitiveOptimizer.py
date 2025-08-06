import sys
import traceback
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QCheckBox, QComboBox, QPushButton, QMessageBox, QFormLayout, QFileDialog
)
from PyQt6.QtCore import Qt

# helpers
def get_vendor_device_ids(filepath):
    vendor_id = None
    device_id = None

    with open(filepath, "r") as f:
        for line in f:
            if "VendorID" in line:
                vendor_id = re.search(r'\d+', line).group()
            elif "DeviceID" in line:
                device_id = re.search(r'\d+', line).group()
    
    return vendor_id, device_id

class DeadlockCompetitiveOptimizer(QWidget):
    def __init__(self):
        self.settings = {}
        super().__init__()
        self.setWindowTitle("Deadlock Competitive Optimizer")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Settings Path Row
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("e.g. steamapps/common/Deadlock")
        path_browse = QPushButton("Browse...")
        path_browse.clicked.connect(self.browse_path)

        path_layout.addWidget(self.path_input)
        path_layout.addWidget(path_browse)
        form_layout.addRow("Deadlock Path:", path_layout)

        # Resolution Row
        res_row = QHBoxLayout()
        self.resolutionWidth = QLineEdit()
        self.resolutionWidth.setPlaceholderText("Width (1920)")
        self.resolutionHeight = QLineEdit()
        self.resolutionHeight.setPlaceholderText("Height (1080)")
        res_row.addWidget(self.resolutionWidth)
        res_row.addWidget(self.resolutionHeight)
        form_layout.addRow("Resolution:", res_row)

        # Refresh Rate
        self.refreshRate = QLineEdit()
        self.refreshRate.setPlaceholderText("e.g. 144")
        form_layout.addRow("Refresh Rate:", self.refreshRate)

        # FPS
        self.fps = QLineEdit()
        self.fps.setPlaceholderText("e.g. 120")
        form_layout.addRow("Desired FPS:", self.fps)

        # Display Mode
        self.displayMode = QComboBox()
        self.displayMode.addItems(["Fullscreen", "Borderless"])
        form_layout.addRow("Display Mode:", self.displayMode)

        # Texture Quality
        self.textureQuality = QComboBox()
        self.textureQuality.addItems(["Balanced (Recommended)", "Performance", "Quality"])
        form_layout.addRow("Texture Quality:", self.textureQuality)

        main_layout.addLayout(form_layout)

        # Save Button Aligned Bottom Right
        button_row = QHBoxLayout()
        button_row.addStretch()
        save_button = QPushButton("Optimize")
        save_button.clicked.connect(self.optimize)
        button_row.addWidget(save_button)
        main_layout.addLayout(button_row)

        self.setLayout(main_layout)

    def show_error_popup(self, title="Error", message="An error occurred."):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

    def show_success_popup(self, title="Success", message="Operation completed successfully."):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

    def browse_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Deadlock Folder")
        if folder:
            self.path_input.setText(folder)

    def save_settings(self):
        display_mode_map = {
            "Borderless": 0,
            "Fullscreen": 1
        }

        texture_quality_map = {
            "Performance": 4,
            "Balanced (Recommended)": 3,
            "Quality": 0
        }

        self.settings = {
            "resolution_width": int(self.resolutionWidth.text()),
            "resolution_height": int(self.resolutionHeight.text()),
            "refresh_rate": int(self.refreshRate.text()),
            "desired_fps": int(self.fps.text()),
            "display_mode": display_mode_map[self.displayMode.currentText()],
            "texture_quality": texture_quality_map[self.textureQuality.currentText()]
        }
    
    def write_video(self, path):
        video_txt_path = f"{path}/game/citadel/cfg/video.txt"
        self.settings["device_id"], self.settings["vendor_id"] = get_vendor_device_ids(video_txt_path)

        print("Generating new video.txt file...")
        try:
            with open("configs/video.txt", "r") as f:
                template = f.read()
                video_txt_contents = template.format(**self.settings)
        except Exception as e:
            print("Generating failed:", e)
            self.show_error_popup(message=e)
            # return
        print("Successfully generated new video.txt file.")

        print("Writing to video.txt...")
        try:
            with open(video_txt_path, "r+") as f:
                f.seek(0)
                f.write(video_txt_contents)
                f.truncate()
        except Exception as e:
            print("Writing failed:", e)
            self.show_error_popup(message=e)
            # return
        print("Successfully wrote new video.txt file.")

    def write_autoexec(self, path):
        autoexec_cfg_path = f"{path}/game/citadel/cfg/autoexec.cfg"

        print("Reading autoexec.txt file...")
        try:
            with open("configs/autoexec.txt", "r") as f:
                autoexec_cfg_contents = f.read()
        except Exception as e:
            print("Reading failed:", e)
            self.show_error_popup(message=e)
            # return
        print("Successfully read autoexec.txt file.")

        print("Writing to autoexec.cfg...")
        try:
            with open(autoexec_cfg_path, "w") as f:
                f.write(autoexec_cfg_contents)
        except Exception as e:
            print("Writing failed:", e)
            self.show_error_popup(message=e)
            # return
        print("Successfully wrote new autoexec.cfg file.")

    def write_gameinfo(self, path):
        gameinfo_gi_path = f"{path}/game/citadel/gameinfo.gi"

        print("Reading gameinfo.txt file...")
        try:
            with open("configs/gameinfo.txt", "r") as f:
                gameinfo_gi_contents = f.read()
        except Exception as e:
            print("Reading failed:", e)
            self.show_error_popup(message=e)
            # return
        print("Successfully read gameinfo.txt file.")

        with open(gameinfo_gi_path, "r") as f:
            lines = f.readlines()

        if gameinfo_gi_contents.strip() in "".join(lines):
            print("Gameinfo optimization already exists. Skipping insertion.")
            return

        output_lines = []
        inserted = False
        i = 0
        while i < len(lines):
            line = lines[i]
            output_lines.append(line)

            if not inserted and "ConVars" in line:
                i += 1
                if i < len(lines) and "{" in lines[i]:
                    output_lines.append(lines[i])
                    output_lines.append(gameinfo_gi_contents + "\n")
                    inserted = True

            i += 1

        print("Writing to gameinfo.gi...")
        try:
            with open(gameinfo_gi_path, "w") as f:
                f.writelines(output_lines)
        except Exception as e:
            print("Writing failed:", e)
            self.show_error_popup(message=e)
            # return
        print("Successfully wrote new gameinfo.gi file.")

    def optimize(self):
        path = self.path_input.text()
        self.save_settings()
        self.write_video(path)
        self.write_autoexec(path)
        self.write_gameinfo(path)
        self.show_success_popup(message="Successfully optimized your game!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeadlockCompetitiveOptimizer()
    window.show()
    sys.exit(app.exec())