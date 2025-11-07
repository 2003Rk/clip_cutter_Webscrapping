# ClipScutter Automation Tool

A powerful Python automation tool that streamlines the process of creating and downloading video clips from YouTube videos using the ClipScutter web service. This tool automates the entire workflow from reading clip specifications to downloading the final video clips.

## 🚀 Features

- **📋 CSV-Driven Automation**: Read clip ranges from CSV files for bulk processing
- **🎯 Intelligent URL Handling**: Efficiently groups clips by YouTube URL to minimize repetitive operations
- **🔐 Automated Login**: Supports both regular login and premium trial account setup
- **📥 Bulk Download**: Automatically downloads all created clips (premium $20 feature)
- **⚡ Performance Optimized**: Ultra-fast processing with configurable timing settings
- **📊 Comprehensive Logging**: Detailed logging with error tracking and screenshots
- **🛡️ Error Recovery**: Robust error handling with retry mechanisms
- **🎥 Quality Control**: Supports 1080p and multiple fallback quality options

## 📁 Project Structure

```
clip_cutter_Webscrapping-main/
├── README.md                    # This file
├── requirements.txt            # Python dependencies
├── config.py                  # Configuration settings
├── main.py                    # Legacy main script
├── run_automation.py          # Primary execution script
├── csv_reader.py             # CSV parsing utilities
├── web_automation.py         # ClipScutter web interface automation
├── download_clips.py         # Clip downloading functionality
├── clip_ranges.csv          # Sample clip specifications
├── downloads/               # Downloaded clips storage
├── logs/                   # Application logs
└── __pycache__/           # Python cache files
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- Stable internet connection

### Setup

1. **Clone or download the project**
   ```bash
   cd /path/to/project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure settings**
   Edit `config.py` to update:
   - File paths
   - Login credentials
   - Download preferences
   - Performance settings

## 📝 Usage

### Basic Usage

```bash
python run_automation.py
```

### Command Line Options

```bash
# Run in headless mode
python run_automation.py --headless

# Use custom CSV file
python run_automation.py --csv-file /path/to/your/clips.csv

# Download only (skip clip creation)
python run_automation.py --download-only

# Get help
python run_automation.py --help
```

### CSV Format

Create a CSV file with clip specifications in the following format:

```csv
start_time,end_time,youtube_url
00:05:34,00:06:18,https://youtu.be/USOQid7YJ2s
00:07:12,00:08:08,https://youtu.be/USOQid7YJ2s
00:11:29,00:11:51,https://youtu.be/skVd7mI6MQU
```

**Format Details:**
- `start_time`: Clip start time (HH:MM:SS format)
- `end_time`: Clip end time (HH:MM:SS format)  
- `youtube_url`: Full YouTube video URL

## ⚙️ Configuration

### Key Settings in `config.py`

```python
# Authentication
LOGIN_EMAIL = "your_email@example.com"
LOGIN_PASSWORD = "your_password"

# Performance Settings
HEADLESS_MODE = False          # Set True for background operation
DELAY_BETWEEN_CLIPS = 1.0     # Processing speed control
MAX_DOWNLOAD_RETRIES = 3      # Download retry attempts

# Quality Preferences
PREFERRED_QUALITY = "1080p"
FALLBACK_QUALITIES = ["1080", "Full HD", "720p", "720", "HD"]
```

### Directory Structure

The tool expects the following directory structure:
```
your_base_directory/
├── clip_ranges.csv
├── downloads/          # Auto-created
├── logs/              # Auto-created  
└── error_screenshots/ # Auto-created
```

## 🔧 Core Components

### 1. CSV Reader (`csv_reader.py`)
- Parses clip specification files
- Groups clips by YouTube URL for efficient processing
- Validates time formats and URLs

### 2. Web Automation (`web_automation.py`)
- Selenium-based ClipScutter interface automation
- Handles login, premium trial setup, and clip creation
- Smart element detection and interaction

### 3. Clip Downloader (`download_clips.py`)
- Automated clip downloading from ClipScutter clips page
- Supports direct downloads and streaming
- Progress tracking and error recovery

### 4. Main Controller (`run_automation.py`)
- Orchestrates the entire automation workflow
- Command-line interface and argument parsing
- Comprehensive error handling and reporting

## 🎯 Workflow

1. **Initialize**: Load configuration and setup browser
2. **Authenticate**: Login to ClipScutter account
3. **Parse CSV**: Read and group clip specifications
4. **Create Clips**: 
   - Navigate to clip creation page
   - Input YouTube URL (once per video)
   - Create multiple clips for same video efficiently
   - Set quality preferences
5. **Download**: 
   - Navigate to clips page
   - Download all created clips automatically
   - Organize files in download directory

## 📊 Logging and Monitoring

### Log Levels
- **INFO**: General operation status
- **DEBUG**: Detailed automation steps
- **WARNING**: Recoverable issues
- **ERROR**: Failed operations with retry info
- **CRITICAL**: System failures

### Log Locations
- Console output for real-time monitoring
- `logs/clipscutter_automation.log` for persistent logging
- `error_screenshots/` for visual debugging

## 🛡️ Error Handling

### Automatic Recovery
- Element detection timeouts with retries
- Network error recovery
- Browser crash detection and restart
- Download failure retry with exponential backoff

### Error Screenshots
- Automatic screenshot capture on failures
- Timestamped files for debugging
- Browser state preservation

## ⚡ Performance Optimization

### Speed Features
- Ultra-fast URL input processing (0.5s delays)
- Efficient clip creation (1.0s between clips)
- Parallel processing capabilities (experimental)
- Smart element waiting strategies

### Resource Management
- Configurable browser options
- Memory-efficient CSV processing  
- Optimized download chunk sizes
- Automatic cleanup procedures

## 🔒 Security Notes

- Store credentials securely in `config.py`
- Use environment variables for production deployments
- Regular credential rotation recommended
- Browser data isolation for privacy

## 🐛 Troubleshooting

### Common Issues

1. **Browser crashes**: Update ChromeDriver, check Chrome version
2. **Element not found**: Adjust wait timeouts in config
3. **Download failures**: Check network connection, verify download directory permissions
4. **Login issues**: Verify credentials, check for CAPTCHA requirements

### Debug Mode

Enable debug logging:
```python
LOG_LEVEL = "DEBUG"  # in config.py
```

## 📈 Future Enhancements

- [ ] Multi-browser support (Firefox, Edge)
- [ ] Parallel clip creation
- [ ] Advanced video quality selection
- [ ] Batch processing for multiple CSV files
- [ ] Web dashboard for monitoring
- [ ] API integration for external systems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is for educational and automation purposes. Please respect ClipScutter's terms of service and rate limits.

## ⚠️ Disclaimer

This tool automates interactions with the ClipScutter website. Users are responsible for:
- Complying with ClipScutter's terms of service
- Respecting rate limits and fair usage
- Ensuring appropriate YouTube content permissions
- Following applicable copyright laws

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Verify configuration settings
4. Test with minimal CSV data first

---

**Author**: Automated ClipScutter Bot  
**Version**: 1.0  
**Last Updated**: November 2025
