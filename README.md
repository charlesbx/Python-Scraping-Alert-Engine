# 🕵️‍♂️ Python Scraping Alert Engine

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" />
  <img src="https://img.shields.io/badge/scraping-beautifulsoup4-green" />
  <img src="https://img.shields.io/badge/docker-ready-0db7ed" />
  <img src="https://img.shields.io/badge/automation-engine-orange" />
  <img src="https://img.shields.io/badge/alerts-telegram%20%2F%20discord-7289da" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" />
  <br/>
  <img src="https://github.com/charlesbx/Python-Scraping-Alert-Engine/workflows/CI/badge.svg" />
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" />
  <img src="https://img.shields.io/badge/tests-20%20passed-success" />
</p>

A production-ready Python automation tool to monitor websites, detect new items, and send real-time alerts on Telegram/Discord.

Built as a **freelance-grade automation template**: config-driven, modular architecture, type-hinted, fully tested, Docker-ready, and with comprehensive logging.

**🎯 Perfect for demonstrating:**
- Clean, modular Python architecture
- Type hints and comprehensive docstrings
- Unit testing with pytest (20+ tests, 100% coverage on core modules)
- CI/CD with GitHub Actions
- Professional documentation and code quality standards

## ✨ Features

| Feature | Status |
|---|---|
Config-based scraping targets (`config.yaml`) | ✅
Multi-site scraping | ✅
Duplicate-safe storage (CSV) | ✅
Automatic new item detection | ✅
Telegram & Discord alerts | ✅ (via `.env`)
Retry/backoff HTTP calls | ✅
Logging to file + console | ✅ (`logs/app.log`)
Interactive CLI menu | ✅
Docker & Compose support | ✅
Offline local run | ✅

## 📂 Project Structure

```
.
├── src/autoscrape/       # modular source code
│   ├── scraper.py        # web scraping logic
│   ├── storage.py        # CSV persistence
│   ├── alerts.py         # Telegram/Discord alerts
│   ├── cli.py            # interactive CLI
│   └── main.py           # application entry point
├── tests/                # unit tests (20+ tests)
│   ├── test_scraper.py
│   ├── test_storage.py
│   └── test_alerts.py
├── monitor.py            # main entry point
├── config.yaml           # scraping rules
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/    # CI/CD configuration
├── data/                 # CSV output (auto-created)
├── logs/                 # logs/app.log (auto-created)
└── requirements-dev.txt  # development dependencies
```

## ⚙️ Configuration

### Targets (`config.yaml`)

```yaml
storage:
  csv_path: "data/output.csv"
  unique_key: "link"

alerts:
  enabled: false

targets:
  - name: "hn_new"
    url: "https://news.ycombinator.com/newest"
    item: ".athing"
    fields:
      title: ".titleline a::text"
      link: ".titleline a::attr(href)"
    csv_path: "data/hn_new.csv"
```

### 🔐 Environment variables (`.env`)

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
DISCORD_WEBHOOK_URL=...
```

Do not leave them empty if alerts is enabled in config.

> Alert toggling in the app currently only affects runtime — config is not edited (Docker mounts it read-only).  

## ▶️ Usage

![Demo AutoScrape Alerts](./assets/demo.gif)

### Run normally
```
python monitor.py
```

### CLI features
- Scrape all sites
- Select target
- Dry-run (no CSV write / no alerts)
- Limit number of scraped items
- Toggle alerts (runtime only)

## 🐳 Docker

### Build
```
docker compose build
```

### Interactive mode (menu)
```
docker compose run autoscrape
```

## 📦 What this project demonstrates

### Technical Skills
✅ **Clean Architecture**: Modular design with separated concerns (scraping, storage, alerts, CLI)  
✅ **Type Safety**: Full type hints throughout the codebase  
✅ **Testing**: 20+ unit tests with pytest, mocking, and high coverage  
✅ **CI/CD**: GitHub Actions workflow for automated testing, linting, and security checks  
✅ **Code Quality**: Black formatting, isort imports, flake8 linting  
✅ **Documentation**: Comprehensive docstrings, README, and contributing guide  
✅ **Error Handling**: Robust retry logic with exponential backoff  
✅ **Logging**: Structured logging to file and console  
✅ **Security**: Bandit scans, safe credential handling via environment variables  
✅ **Docker**: Production-ready containerization  

### Freelance-Ready Features
A **production-grade automation engine**, ideal for:

- 📊 Job monitoring and aggregation
- 💼 Lead generation systems
- 🛍️ Product drop alerts
- 📈 Market intelligence bots
- ⚙️ Internal automation scripts for clients
- 🔔 Real-time notification systems

## 🧪 Development

### Run Tests
```bash
pytest tests/ -v
pytest tests/ --cov=src/autoscrape --cov-report=term
```

### Code Formatting
```bash
black src/ tests/
isort src/ tests/
```

### Linting
```bash
flake8 src/ tests/
```

### Security Scan
```bash
bandit -r src/
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚧 Roadmap

| Feature | Status |
|---|---|
| ✅ Modular architecture | **Done** |
| ✅ Type hints | **Done** |
| ✅ Unit tests | **Done** |
| ✅ CI/CD | **Done** |
| 🔜 Persist alert settings | Planned |
| 🔜 Add FastAPI dashboard | Planned |
| 🔜 SQLite history | Planned |
| 🔜 Webhook trigger mode | Planned |

## 👤 Author

Made by **Charles Baux**  
- GitHub: https://github.com/charlesbx  
- Focus: automation, scraping, bots & internal tools

⭐ Star the project if you like it!

---

**This project showcases professional Python development practices suitable for freelance portfolio and client work.**
