# Internship Watcher 2.0 🚨

A Python script that monitors the [Summer 2026 Internships repository](https://github.com/SimplifyJobs/Summer2026-Internships) and automatically sends email notifications when new internship listings are added.

## Features

- 🔍 **Automatic Monitoring**: Checks for new internships every 30 minutes
- 📧 **Email Notifications**: Sends beautifully formatted HTML emails when new listings are found
- 🏢 **Multi-Category Support**: Tracks Software Engineering, Quantitative Finance, Hardware Engineering, and Data Science internships
- 💾 **Smart Persistence**: Remembers previously seen listings to avoid duplicate notifications
- 📊 **Detailed Logging**: Comprehensive logging to file and console
- 🧪 **Testing Mode**: Test script to verify functionality before running

## Environment Variables

The following environment variables are required (already configured in `.env`):

```
SMTP_PASS=dfrrqsrdpaytntfk
SMTP_USER=pranithravella@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
EMAIL_FROM=pranithravella@gmail.com
EMAIL_TO=pranithravella@gmail.com
```

## Setup and Usage

1. **Quick setup** (recommended):
   ```bash
   python3 setup.py
   ```

2. **Manual setup**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Test the watcher** (recommended first step):
   ```bash
   source venv/bin/activate && python test_watcher.py
   ```

4. **Start monitoring**:
   ```bash
   source venv/bin/activate && python internship_watcher.py
   ```

5. **Stop monitoring**: Press `Ctrl+C`

## How It Works

1. **Fetches** the latest README from the Summer 2026 internships repository
2. **Parses** markdown tables to extract internship data (company, role, location, category)
3. **Compares** with previously seen listings stored in `previous_internships.json`
4. **Sends email** notifications for any new internships found
5. **Repeats** every 30 minutes

## Files Generated

- `previous_internships.json` - Stores internship data to track new additions
- `internship_watcher.log` - Detailed logs of the watcher's activity

## Email Format

When new internships are found, you'll receive an email with:
- Subject: "🚨 X New Summer 2026 Internship(s) Found!"
- HTML table with company, role, location, and category
- Link to the full repository for application details

## Monitoring Repository

This script monitors: https://github.com/SimplifyJobs/Summer2026-Internships

## Current Status

✅ **Working** - Successfully monitoring 15+ internship listings across multiple categories
- ✅ **Smart Parsing** - Now captures ALL company positions, including additional roles marked with arrows (↳)
- ✅ **Complete Coverage** - Tracks multiple positions per company (e.g., 5 Optiver roles, 4 Palantir roles)