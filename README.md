# Deadlock Competitive Optimizer

A desktop application to help players optimize settings of the Valve game **Deadlock** for a more competitive experience. This tool provides a simple GUI to adjust video, performance, and configuration settings, and applies them directly to your Deadlock installation.

## Features

- Easy-to-use graphical interface (PyQt6)
- Set resolution, refresh rate, FPS, display mode, and texture quality
- Automatically updates `video.txt`, `autoexec.cfg`, and `gameinfo.gi`
- Optionally makes `video.txt` read-only to prevent unwanted changes
- Backup of original configuration files

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/ImJustBlurr/Deadlock-Competitive-Optimizer.git
   cd Deadlock-Competitive-Optimizer
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   *Dependencies: `PyQt6`*

3. **Ensure the `configs` folder is present in the project directory.**

## Usage

1. **Run the application:**
   ```sh
   python DeadlockCompetitiveOptimizer.py
   ```

2. **Select your Deadlock installation folder.**

3. **Adjust your desired settings and click "Optimize".**

4. **The tool will update your configuration files and notify you of success.**

## Notes

- The project is currently a WIP. Once it is ready I will release an executable!
- Make sure you have launched Deadlock at least once before using this tool.
- The tool is not affiliated with Valve.
- Always backup your configuration files before making changes.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## License

This project is not affiliated with Valve.
