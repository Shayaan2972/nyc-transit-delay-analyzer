# NYC Transit Delay Analyzer

Real-time ETL pipeline that ingests MTA subway alerts, processes delay data, and provides analytics through a RESTful API and interactive dashboard.

## Project Overview

This project demonstrates a complete data engineering workflow: extracting real-time transit data from the MTA API, transforming it into structured records, loading it into PostgreSQL, and serving insights through a Flask API with a responsive frontend.

## Features

- **Real-time Data Ingestion**: Fetches live subway alerts from MTA's public API every 30 seconds
- **Data Cleaning & Transformation**: Parses JSON responses, extracts relevant fields, and handles missing data
- **PostgreSQL Storage**: Implements schema with unique constraints to prevent duplicate entries
- **Analytics API**: RESTful endpoints serving delay statistics and trends
- **Interactive Dashboard**: Web interface displaying current delays and 7-day analytics
- **Auto-refresh**: Frontend updates every 30 seconds without manual refresh

## Tech Stack

**Backend:**
- Python 3.13
- Flask (API server)
- psycopg2 (PostgreSQL driver)
- requests (HTTP client)
- python-dotenv (environment management)

**Database:**
- PostgreSQL 16
- Time-series queries with interval filtering
- Composite unique constraints for deduplication

**Frontend:**
- Vanilla JavaScript (async/await, fetch API)
- HTML5/CSS3
- Responsive design with gradient styling

## Architecture
```
MTA API → Python ETL (app.py) → PostgreSQL → Flask API (server.py) → Dashboard (app.html)
```

### Data Flow:
1. **Extract**: Fetch real-time alerts from MTA GTFS feed
2. **Transform**: Parse JSON, extract route IDs, filter valid delays
3. **Load**: Insert into PostgreSQL with conflict handling
4. **Serve**: Flask API endpoints for delays and statistics
5. **Visualize**: Dashboard displays current delays and trends

## Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 16+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/Shayaan2972/nyc-transit-delay-analyzer.git
cd nyc-transit-delay-analyzer
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Database
```bash
# Create database
createdb nyc_subway_delays

# Run schema
psql -d nyc_subway_delays -f database/nyc_subway_delays.sql
```

### 4. Environment Variables
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Run ETL Pipeline
```bash
python application/app.py
```

Expected output (example):
```
Found 245 entities in API response
Successfully parsed 12 delays
Inserted 8 records
Transfer complete
```

### 6. Start Web Server
```bash
python application/server.py
```

Visit: `http://localhost:5000`

## Project Structure
```
nyc-transit-delay-analyzer/
├── application/
│   ├── app.py              # ETL pipeline (fetch, parse, insert)
│   ├── server.py           # Flask API with 3 endpoints
│   └── templates/
│       └── app.html        # Dashboard frontend
├── database/
│   └── nyc_subway_delays.sql  # PostgreSQL schema
├── .env.example            # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

## API Endpoints

### `GET /`
Returns dashboard HTML page

### `GET /api/delays`
Returns last 50 delay records ordered by update time

**Response:**
```json
[
  {
    "train_line": "4",
    "alert_message": "Delays due to signal problems",
    "alert_type": "Delays",
    "created": "2024-11-27 18:30:00",
    "updated": "2024-11-27 18:35:00"
  }
]
```

### `GET /api/stats/worst-lines`
Returns delay count per line (last 7 days)

**Response:**
```json
[
  {"train_line": "4", "delay_type": 25},
  {"train_line": "A", "delay_type": 18}
]
```

### `GET /api/stats/delay-types`
Returns breakdown by alert type (last 7 days)

**Response:**
```json
[
  {"alerts": "Delays", "count": 45},
  {"alerts": "Suspended", "count": 12}
]
```

## Database Schema
```sql
CREATE TABLE subway_delays (
    id SERIAL PRIMARY KEY,
    train_line VARCHAR(30),
    alert_message VARCHAR(5000),
    alert_type VARCHAR(300),
    created TIMESTAMP,
    updated TIMESTAMP,
    CONSTRAINT unique_alert UNIQUE(train_line, alert_message, created)
);
```

**Key Design Decisions:**
- Composite unique constraint prevents duplicate alerts
- Timestamps enable time-series analysis

## Key SQL Queries

**Worst performing lines (7-day window):**
```sql
SELECT train_line, COUNT(*) as delay_count
FROM subway_delays
WHERE created > NOW() - INTERVAL '7 days'
GROUP BY train_line
ORDER BY delay_count DESC;
```

## Future Enhancements

- [ ] Add delay frequency heatmap by hour of day
- [ ] Create predictive model for delay patterns
- [ ] Add email/SMS alerts for specific lines
- [ ] Historical trend analysis (30/90 day views)

## 📝 Development Notes

### Data Quality Challenges
- Not all MTA alerts have `route_id` (station-specific alerts)
- Alert text varies significantly (requires careful parsing)
- Duplicate alerts during active incidents (handled with UNIQUE constraint)

## Sample Output
```
6 Train
Delays due to signal problems at 51 St

A Train  
Service changes due to track maintenance

Delay Statistics (Last 7 Days)
4 Train: 25
A Train: 18
L Train: 12
```

## Contributing

This is a portfolio project, but suggestions are welcome! 

##  License

MIT License - feel free to use 


