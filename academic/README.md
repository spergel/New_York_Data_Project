# NYC Academic Events API

A FastAPI-based REST API for accessing academic events from NYC universities and institutions. The system automatically scrapes events from 22+ institutions weekly and provides a clean API for accessing the data.

## 🚀 Features

- **79+ Academic Events** from NYC institutions
- **22 Active Scrapers** covering major universities
- **RESTful API** with filtering and pagination
- **Auto-generated Documentation** at `/docs`
- **Weekly Automated Updates** via GitHub Actions
- **Database Storage** with SQLite/PostgreSQL support

## 📊 Coverage

### Universities & Institutions:
- **Columbia University** (Classics, Math, Law, History, Religion, Social Difference)
- **NYU** (General, Stern, Law, Medicine, Education, Engineering, CIMS)
- **CUNY** (Hunter, Brooklyn)
- **Other Institutions**: Fordham, Pratt, St. John's, Cooper Union, Gallatin, ISAW, JTSA, New School, Miller Theatre, Simons Foundation

## 🛠️ API Endpoints

### Get All Events
```
GET /api/events
```

**Query Parameters:**
- `skip` (int): Number of events to skip (pagination)
- `limit` (int): Number of events to return (max 100)
- `institution` (string): Filter by institution (e.g., 'columbia', 'nyu')
- `source_group` (string): Filter by source group (e.g., 'columbia_classics')
- `date_from` (string): Filter events from date (YYYY-MM-DD)
- `date_to` (string): Filter events to date (YYYY-MM-DD)
- `academic_only` (bool): Return only academic events (default: true)

### Get Specific Event
```
GET /api/events/{event_id}
```

### Get Institutions
```
GET /api/institutions
```

### Get Statistics
```
GET /api/stats
```

### Health Check
```
GET /health
```

## 🚀 Deployment on Railway

### Prerequisites
- Railway account
- GitHub repository connected to Railway

### Setup Steps:

1. **Fork/Clone this repository**

2. **Connect to Railway:**
   - Go to [Railway](https://railway.app)
   - Create new project
   - Connect your GitHub repository
   - Railway will auto-detect the Python app

3. **Configure Environment Variables:**
   - `DATABASE_URL`: Railway will provide this automatically
   - `PORT`: Railway will set this automatically

4. **Deploy:**
   - Railway will automatically deploy when you push to main
   - The app will be available at your Railway URL

5. **Set up GitHub Actions:**
   - Add `DATABASE_URL` as a GitHub secret
   - The weekly scraping will run automatically

## 🔧 Local Development

### Install Dependencies
```bash
cd academic
pip install -r requirements.txt
```

### Run the API
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Run Scraping Service
```bash
python scraper_service.py
```

### View API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📁 Project Structure

```
academic/
├── main.py                 # FastAPI application
├── database.py             # Database models and setup
├── models.py               # Pydantic models
├── routes.py               # API routes
├── scraper_service.py      # Scraping service
├── requirements.txt        # Python dependencies
├── railway.json           # Railway configuration
├── scrapers/              # Individual scraper modules
├── utils/                 # Utility functions
└── .github/workflows/     # GitHub Actions
```

## 🔄 Weekly Updates

The system automatically updates every Sunday at 2 AM UTC via GitHub Actions:

1. Runs all scrapers
2. Filters for academic events
3. Updates the database
4. Commits changes to git

## 📈 API Response Format

### Events Response
```json
{
  "events": [
    {
      "id": 1,
      "event_id": "evt_columbia_classics_abc123",
      "name": "Classics Departmental Lecture Series",
      "description": "Lecture description...",
      "start_date": "2025-09-09",
      "source": "columbia",
      "source_group": "columbia_classics",
      "venue_name": "Columbia University",
      "is_academic": true
    }
  ],
  "total": 79,
  "page": 1,
  "per_page": 50
}
```

## 🤝 Contributing

1. Fork the repository
2. Add new scrapers in the `scrapers/` directory
3. Test locally with `python main.py`
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues or questions:
- Check the API documentation at `/docs`
- Review the scraper logs
- Open an issue on GitHub
