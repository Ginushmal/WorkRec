# AutoLapse Work Tracker

AutoLapse Work Tracker automates hyperlapse-style screen captures of your active work sessions.

## Features

- **Context-Aware:** Captures only when target apps (e.g., Blender, After Effects) are focused.
- **Active Detection:** Pauses capturing when the mouse/keyboard is idle to save space.
- **Efficient Capture:** Captures highly-compressed JPEGs at a low frame rate (2 FPS by default). You can customize the image quality and resolution scale to further optimize and aggressively reduce disk space used.
- **Auto Route:** Saves captures to `captures/AppName/YYYY-MM-DD/` folder structure.
- **Floating UI:** "Always-on-top" minimal UI with a minimize [-] toggle, dynamic target bounding, and manual control (Start, Pause, Stop).
- **Persistent Settings & Logging:** UI configuration persists dynamically (including target apps, FPS, quality, and resolution), with built-in real-time tracking logs.

## Installation

1. Clone or download the repository.
2. Create a virtual environment and install the required dependencies:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate
   pip install -r requirements.txt
   ```

## Running the Application (Development)

Run the main script from your virtual environment:

```bash
python src/main.py
```

## Compiling to a Standalone Executable (.exe)

If you modify the Python files, you can recompile the tool into a single standalone executable by running `build.bat` or by typing the following command inside your activated virtual environment:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "AutoLapse" "src/main.py"
```

The new `AutoLapse.exe` file will be generated and placed inside the `dist/` folder.

## Running on Boot

To make the application run automatically on computer boot:

1. Compile the `.exe` using the steps above.
2. Press `Win + R`, type `shell:startup`, and press Enter.
3. Open the `dist/` folder inside your WorkRec directory.
4. Right-click on `AutoLapse.exe` and select **Create shortcut**.
5. Drag and drop the created shortcut into the `Startup` folder you opened in step 2.
