# 🎓 NYC Academic Events Website

A clean, simple website displaying academic events from universities and institutions across New York City in classic early 2000s academic style.

## 🚀 Quick Start

### Option 1: Python Server (Recommended)
```bash
cd academic
python serve.py
```
Then visit http://localhost:8000 in your browser.

### Option 2: Simple HTTP Server
```bash
cd academic
python -m http.server 8000
```

### Option 3: Direct File Access
Simply open `index.html` in your web browser.

## 📊 Features

### ✅ Current Features
- **403+ Events** including those with missing data (for debugging scrapers)
- **Real-time Filtering** by institution, category, and date
- **Clickable Sorting** - click column headers to sort by date, event, institution, or location
- **Source Detection** - Automatically detects institutions from event names/URLs
- **Visual Indicators** - Shows "inferred" sources and missing data in orange/red

*Note: Currently showing all events (including unknown sources) to help fix scrapers*

### 🎯 Event Information Displayed
- **Event Title** (clickable link to event page)
- **Date & Time** (verified, future events only)
- **Institution** (verified or inferred from event data)
- **Location** (venue name and address)
- **Categories** (Education, Science, etc.)

*Note: Currently showing all events to help identify and fix scraper issues*

### 🔍 Filtering & Sorting Options
- **Institution Filter** - Show events from specific universities (including inferred sources)
- **Category Filter** - Filter by event type (Education, Science, etc.)
- **Date Filter** - Show today, this week, this month, or all future events
- **Clickable Column Headers** - Sort by date, event title, institution, or location

*Note: Currently showing all events (including unknown sources) to help fix scrapers*

## 📁 File Structure

```
academic/
├── index.html          # Main HTML page
├── styles.css          # CSS styling
├── script.js           # JavaScript functionality
├── serve.py           # Local development server
├── scraped_events.json # Events data (auto-generated)
└── README.md          # This file
```

## 🔧 Data Source

Events are automatically scraped from:
- Columbia University (various departments)
- NYU (Courant, Engineering, Medicine, etc.)
- The New School
- Cooper Union
- Cornell Tech
- Fordham University
- Pratt Institute
- Juilliard School
- And 17+ more institutions

## 🎨 Design Philosophy

**Classic Early 2000s Academic Style**
- Simple, clean table layout
- Traditional academic website aesthetic
- Fast loading and reliable
- No unnecessary complexity

**Functional & Accessible**
- Clear, readable event listings
- Easy navigation and filtering
- Works on all devices
- Focus on content over style

## 🚧 Future Enhancements

### Phase 2 (Style & Polish)
- Enhanced animations and transitions
- Better typography and spacing
- Institution-specific color schemes
- Advanced filtering options

### Phase 3 (Advanced Features)
- Event calendar view
- Map integration showing locations
- User favorites and bookmarks
- Email notifications
- Social sharing

### Phase 4 (Mobile App)
- React Native mobile application
- Push notifications for new events
- Offline event caching

## 🛠 Technical Details

### Frontend Stack
- **HTML** - Simple table structure
- **CSS** - Traditional styling, no modern frameworks
- **Vanilla JavaScript** - Lightweight and fast
- **Table Layout** - Classic academic website approach

### Data Handling
- **JSON API** - Loads events from `scraped_events.json`
- **Client-side Filtering** - Fast, no server required
- **Error Handling** - Graceful fallbacks

### Performance
- **Static Files** - No server processing required
- **Efficient Filtering** - Fast search and sort
- **Lazy Loading** - Ready for pagination

## 📈 Data Statistics

- **Total Events**: 403+
- **Institutions**: 24
- **Categories**: Education, Science, Arts, Technology, etc.
- **Date Range**: Current month + upcoming events
- **Update Frequency**: Weekly (automated)

## 🐛 Troubleshooting

### "Failed to load events data"
- Ensure `scraped_events.json` exists in the academic folder
- Check that the file is valid JSON
- Verify file permissions

### Website not loading
- Make sure you're serving from the `academic/` directory
- Check that all files (HTML, CSS, JS) are present
- Try hard refresh (Ctrl+F5)

### Filters not working
- Check browser console for JavaScript errors
- Ensure events data loaded correctly
- Verify filter values in HTML

## 🤝 Contributing

### Adding New Features
1. Edit `script.js` for functionality
2. Update `styles.css` for styling
3. Modify `index.html` for structure

### Data Sources
- New institution scrapers go in `scrapers/` folder
- Update `scraped_events.json` after adding scrapers
- Test with `python test_scrapers.py`

## 📝 License

This project is part of the NYC Academic Events scraper system. See main project README for details.

---

**Ready to use!** 🚀 Visit http://localhost:8000 after running the server.