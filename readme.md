# Data Usage Tracker

This Python application monitors data usage and notifies the user at specified intervals. It includes features to track network connectivity and provide notifications through a graphical interface using Tkinter.

## Features

- **Network Monitoring**: Tracks data usage by monitoring bytes sent and received over the network.
- **Interval Notification**: Notifies the user periodically about data usage, adjustable by the user.
- **Network Connectivity**: Detects and displays the current Wi-Fi SSID when connected to a network.
- **Graphical User Interface**: Provides a simple interface to start and stop tracking and configure notification intervals.

## Setup

### Prerequisites

- Python 3.7+
- `psutil` library (`pip install psutil`)
- Tkinter library (usually included with Python installations)
- Windows OS (for full functionality due to platform-specific commands)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/legeRise/Data-Usage-Tracker-in-python.git
   cd Data-Usage-Tracker-in-python
   python guiUsage.py

.exe is also there if don't plan to run python program. You can simply double-click guiUsage.exe and it will start running.
 
