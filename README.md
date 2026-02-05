## Usagi Scary Snake

A horror-flavored Snake game with achievements, Beast Mode obstacles, and a secret ending.

### Features
- Menu, credits, achievements, and difficulty selection
- Beast Mode with moving obstacles
- Achievement popups and secret unlocks
- Golden food, whisper messages, and background tinting
- Final narrative sequence at score 100

### Requirements
- Python 3.10+
- Windows/macOS/Linux

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the game:
```bash
python main.py
```

### Controls
- Arrow keys: Move
- P: Pause
- M: Mute
- F11: Fullscreen
- H: Secret (menu only)

### Notes
- Audio and image files are required for the full experience.
- The score 100 achievement is hidden until unlocked.

### Build a Windows .exe (PyInstaller)
```bash
pip install pyinstaller
pyinstaller usagi_scary_snake.spec
```

The executable will be in:
```
dist/UsagiScarySnake/UsagiScarySnake.exe
```

Zip the **dist/UsagiScarySnake** folder and upload it to GitHub Releases.
