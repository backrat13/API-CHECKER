# API Checker Tool

A simple command-line tool to detect and manage running APIs on your local machine and in your browser.

## Features

- 🚀 Detect locally running APIs on various ports
- 🌐 Identify APIs being used in browser tabs
- ⚡ View detailed information about each API
- ❌ Terminate unwanted API processes
- 🎨 Clean, interactive command-line interface

## Installation

1. Make sure you have Python 3.6+ installed
2. Clone this repository or download the files
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the tool with:

```bash
python api_checker.py
```

### On Linux/macOS

For best results (especially for detecting all processes), run with sudo:

```bash
sudo python api_checker.py
```

### Navigation

- Use arrow keys to navigate the menu
- Press Enter to select an option
- Press Ctrl+C to exit the program at any time

## How It Works

The tool scans for:
1. **Local APIs**: Identifies processes listening on various ports
2. **Browser APIs**: Detects active API connections in web browsers

## Requirements

- Python 3.6+
- psutil
- inquirer
- prettytable

## License

MIT

## Contributing

Feel free to submit issues and enhancement requests!
