
# ACCTrainer

## Introduction

ACCTrainer is a Python-based utility designed to read shared memory from Assetto Corsa Competizione (ACC) for real-time data logging and monitoring. The tool leverages multithreading to perform logging and monitoring tasks in parallel, aiming to improve efficiency and responsiveness.

## Features

- **Real-time Data Logging**: Logs data such as pad life, strategy tire set, max RPM, and more at millisecond intervals.
- **Monitoring and Alerts**: Monitors specific conditions, such as pad life dropping below a certain level, and triggers graphical alerts.
- **Multithreading**: Utilizes a multi-threaded architecture for concurrent logging and monitoring.

## Requirements

- Python 3.x
- Assetto Corsa Competizione installed and running

## Installation

Clone the repository and navigate into the project directory.

\```bash
git clone https://github.com/lOXBetter/ACCTrainer.git
cd ACCTrainer
\```

## Usage

Run the `ACCTrainer.py` script to start the data logging and monitoring.

\```bash
python ACCTrainer.py
\```

## How It Works

### Logging Thread

This thread is responsible for logging real-time data from ACC into a log file. The data includes but is not limited to:

- Pad life for all wheels
- Current strategy tire set
- Max RPM

### Monitoring Thread

This thread continuously monitors the log data and triggers alerts based on certain conditions. For example, a graphical alert is triggered when the front left pad life drops below 10.

## Troubleshooting

If you encounter any issues or have questions, please check the FAQ section or open an issue on GitHub.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT
