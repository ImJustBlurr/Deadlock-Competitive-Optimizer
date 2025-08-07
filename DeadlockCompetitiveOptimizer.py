import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QCheckBox, QComboBox, QPushButton, QMessageBox, QFormLayout, QFileDialog
)
from PyQt6.QtCore import Qt
from utils import log_error, set_file_readonly, is_file_readonly

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

        # Read Only
        self.readOnly = QCheckBox("Make video.txt read-only to fully save these settings")
        form_layout.addRow(self.readOnly)

        main_layout.addLayout(form_layout)

        # Optimize
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
        msg.setText(f"{message} See console for more information.")
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

    def save_settings(self) -> bool:
        """Saves all user entered information to the optimizer"""
        display_mode_map = {
            "Borderless": 0,
            "Fullscreen": 1
        }

        texture_quality_map = {
            "Performance": 4,
            "Balanced (Recommended)": 3,
            "Quality": 0
        }

        try:
            self.settings = {
                "resolution_width": int(self.resolutionWidth.text()),
                "resolution_height": int(self.resolutionHeight.text()),
                "refresh_rate": int(self.refreshRate.text()),
                "desired_fps": int(self.fps.text()),
                "display_mode": display_mode_map[self.displayMode.currentText()],
                "texture_quality": texture_quality_map[self.textureQuality.currentText()]
            }
        except Exception as e:
            log_error(e)
            self.show_error_popup(message="Cannot save settings. Ensure you have entered the correct information.")
            return False

        return True

    def get_vendor_device_ids(self, video_txt):
        """Returns vendor_id, device_id grabbed from video.txt file"""
        vendor_id = None
        device_id = None

        with open(video_txt, "r") as f:
            for line in f:
                if "VendorID" in line:
                    vendor_id = re.search(r'\d+', line).group() # grab the numeric characters in that line
                elif "DeviceID" in line:
                    device_id = re.search(r'\d+', line).group() # grab the numeric characters in that line
        
        return vendor_id, device_id
    
    def write_video(self, path) -> bool:
        video_txt_path = f"{path}/game/citadel/cfg/video.txt"

        # get id's
        try:
            self.settings["device_id"], self.settings["vendor_id"] = self.get_vendor_device_ids(video_txt_path)
        except Exception as e:
            log_error(e)
            self.show_error_popup(message=f"Failed to get your Vendor/Device ID's from {video_txt_path}. Ensure you have the correct path and have launched Deadlock prior to optimizing.")
            return False
        else:
            print(f"Retrieved Vendor/Device ID's from {video_txt_path}")

        # generate modified video.txt file
        try:
            with open("configs/video.txt", "r") as f:
                template = f.read()
                video_txt_contents = template.format(**self.settings)
        except Exception as e:
            log_error(e)
            self.show_error_popup(message=f"Failed to generate new video.txt file. Ensure you have entered the correct information.")
            return False
        else:
            print("Successfully generated new video.txt file.")

        # write the new video.txt file
        try:
            if is_file_readonly(video_txt_path):
                response = QMessageBox.question(
                    self,
                    "File is Read-Only",
                    f"{video_txt_path} is currently read-only. Do you want to make it writable to overwrite it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if response == QMessageBox.StandardButton.No:
                    return False
                else:
                    set_file_readonly(video_txt_path, readonly=False)

            with open(video_txt_path, "r+") as f:
                f.seek(0)
                f.write(video_txt_contents)
                f.truncate()
        except Exception as e:
            log_error(e)
            self.show_error_popup(message=f"Failed to write to {video_txt_path}. Ensure you have the correct path and have launched Deadlock prior to optimizing.")
            return False
        else:
            print(f"Successfully optimized {video_txt_path}")

        # handle bak file
        try:
            set_file_readonly(f"{video_txt_path}.bak", readonly=False)
            with open(f"{video_txt_path}.bak", "w") as f:
                f.seek(0)
                f.write(video_txt_contents)
                f.truncate()
            set_file_readonly(f"{video_txt_path}.bak")
        except Exception as e:
            log_error(e)

        # set file to readonly
        try:
            if self.readOnly.isChecked():
                set_file_readonly(video_txt_path, True)
        except Exception as e:
            log_error(e)
            self.show_error_popup(message=f"Failed to set {video_txt_path} to read-only. Ensure you have the correct path, the correct permissions, and have launched Deadlock prior to optimizing.")

        return True

    def write_autoexec(self, path) -> bool:
        autoexec_cfg_path = f"{path}/game/citadel/cfg/autoexec.cfg"

        # get autoexec content
        try:
            with open("configs/autoexec.txt", "r") as f:
                temp_autoexec_cfg_contents = f.read()
                autoexec_cfg_contents = temp_autoexec_cfg_contents.format(desired_fps=self.settings["desired_fps"])
        except Exception as e:
            log_error(e)
            self.show_error_popup(message=f"Failed to get autoexec config from configs/autoexec.txt. Ensure your exe/.py file is in the same directory as the configs folder.")
            return False
        else:
            print("Successfully retrieved autoexec config data.")

        # write to autoexec.cfg; create it if it does not exist
        try:
            with open(autoexec_cfg_path, "w") as f:
                f.write(autoexec_cfg_contents)
        except Exception as e:
            log_error(e)
            self.show_error_popup(message=f"Failed to write to {autoexec_cfg_path}. Ensure you have the correct path and have launched Deadlock prior to optimizing.")
            return False
        else:
            print(f"Successfully optimized {autoexec_cfg_path}")

        return True

    def write_gameinfo(self, path):
        gameinfo_gi_path = f"{path}/game/citadel/gameinfo.gi"

        # get gameinfo modification content
        try:
            with open("configs/gameinfo.txt", "r") as f:
                gameinfo_gi_contents = f.read()
        except Exception as e:
            log_error
            self.show_error_popup(message=f"Failed to get gameinfo config from configs/gameinfo.txt. Ensure your exe/.py file is in the same directory as the configs folder.")
            return False
        else:
            print("Successfully retrieved gameinfo config data.")

        # get gameinfo existing content
        try:
            with open(gameinfo_gi_path, "r") as f:
                lines = f.readlines()
        except Exception as e:
            log_error(e)
            self.show_error_popup(message=f"Failed to write to {gameinfo_gi_path}. Ensure you have the correct path and have launched Deadlock prior to optimizing.")
            return False

        # see if gameinfo is modified already
        if gameinfo_gi_contents.strip() in "".join(lines):
            print("Gameinfo optimization already exists. Skipping insertion.")
            return True

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

        # writing to gameinfo
        try:
            with open(gameinfo_gi_path, "w") as f:
                f.writelines(output_lines)
        except Exception as e:
            log_error(e)
            self.show_error_popup(message=f"Failed to write to {gameinfo_gi_path}. Ensure you have the correct path and have launched Deadlock prior to optimizing.")
            return False
        else:
            print(f"Successfully optimized {gameinfo_gi_path}")

        return True

    def optimize(self):
        path = self.path_input.text()

        if not self.save_settings(): return
        if not self.write_video(path): return
        if not self.write_autoexec(path): return
        if not self.write_gameinfo(path): return
        self.show_success_popup(message="Successfully optimized your game!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeadlockCompetitiveOptimizer()
    window.show()
    sys.exit(app.exec())