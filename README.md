# NYC Academic Events - 90s Global Village Coffeehouse Edition ☕

A cozy, nostalgic academic events platform with the warm vibes of a 90s coffeehouse and the intellectual energy of NYC's academic community.

## 🎨 Design Philosophy

**90s Global Village Coffeehouse + NYC Academic Vibes**

- **Warm, earthy tones** - Deep browns, warm creams, coffee colors
- **Vintage typography** - Playfair Display serifs with Source Sans Pro accents
- **Paper textures** and subtle grain effects
- **Hand-drawn elements** - Coffee stains, organic shapes
- **NYC academic character** - Institution neighborhoods, borough-based exploration

## 🚀 Features

### Multiple View Modes
1. **Dashboard** - Coffeehouse bulletin board with event cards
2. **Calendar View** - Vintage calendar layout (coming soon)
3. **List View** - Traditional list with coffeehouse styling (coming soon)
4. **NYC Map** - Explore events by neighborhood (coming soon)
5. **Institutions** - Browse by academic institution (coming soon)

### Coffeehouse Aesthetics
- **Glassmorphism cards** with subtle shadows and backdrop blur
- **Hover animations** that lift cards and reveal details
- **Organic layouts** with flowing, comfortable spacing
- **Warm color palette** - Easy on the eyes for long reading sessions
- **Vintage form elements** with modern functionality

### Academic Event Features
- **Smart filtering** by institution, event type, date, and search
- **Event categorization** - Lectures, seminars, conferences, workshops
- **Institution branding** - Each university gets its own visual identity
- **NYC neighborhood integration** - Events organized by borough
- **Responsive design** - Works beautifully on all devices

## 🛠 Technical Implementation

### Frontend Architecture
- **Component-based design** for easy maintenance and updates
- **View switching system** with smooth transitions
- **Responsive grid layouts** that adapt to different screen sizes
- **CSS custom properties** for consistent theming
- **Modern animations** with CSS transitions and transforms

### Styling Approach
- **90s nostalgia** meets modern web standards
- **Coffeehouse color scheme** - Browns, creams, warm tones
- **Typography hierarchy** - Clear, readable, scholarly
- **Interactive elements** - Hover effects, focus states, animations
- **Accessibility first** - High contrast, readable fonts, clear navigation

## 🎯 User Experience Goals

1. **Cozy and Welcoming** - Feels like your favorite local coffee shop
2. **Intellectual Discovery** - Easy to find and explore academic events
3. **NYC Authenticity** - Reflects the city's academic and cultural diversity
4. **Nostalgic Comfort** - Familiar 90s aesthetic with modern functionality
5. **Community Focus** - Brings together NYC's academic community

## 🚧 Development Status

### ✅ Completed
- Main dashboard with coffeehouse styling
- Navigation system with multiple views
- Event filtering and search
- Responsive design framework
- 90s coffeehouse aesthetic

### 🚧 In Progress
- Calendar view implementation
- List view with enhanced styling
- NYC map integration
- Institution-specific pages

### 📋 Planned
- Event detail modals
- Calendar integration (Google, Outlook)
- Social sharing features
- User accounts and favorites
- Mobile app version

## 🎨 Color Palette

- **Primary Brown**: `#8b4513` (Saddle Brown)
- **Secondary Brown**: `#a0522d` (Sienna)
- **Dark Brown**: `#654321` (Dark Brown)
- **Cream**: `#f5f1e8` (Light Cream)
- **Warm Beige**: `#e8dcc0` (Warm Beige)
- **Light Beige**: `#d4c4a8` (Light Beige)

## 🔧 Getting Started

1. **Clone the repository**
2. **Navigate to the frontend directory**
3. **Open `index.html` in your browser**
4. **Or run a local server**: `python -m http.server 8000`

## 🧪 Testing Scrapers

We have comprehensive testing tools for all event scrapers:

### Quick Test
```bash
# Test all scrapers with existing output
python test_scrapers.py

# Test with detailed output
python test_scrapers.py -v

# Test specific category
python test_scrapers.py -c academic
```

### Windows Users
Double-click these batch files:
- `test_all_scrapers.bat` - Quick test of all scrapers
- `test_all_verbose.bat` - Detailed test with JSON report
- `test_academic_only.bat` - Test only academic scrapers

### Documentation
- See **[TESTING.md](TESTING.md)** for comprehensive testing guide
- See **[TEST_EXAMPLES.md](TEST_EXAMPLES.md)** for practical examples

### Category-Specific Runners
- **Academic**: `cd academic && python weekly_scraper.py`
- **Tech**: `cd tech && python run_all_scrapers.py`
- **Exercise**: `cd exercise && python run_all_scrapers.py`

## 🌟 Inspiration

This design draws inspiration from:
- **90s Global Village Coffeehouse** aesthetic
- **NYC academic institutions** and their character
- **Vintage coffee shop** atmospheres
- **Academic discovery** and intellectual exploration
- **Community gathering** spaces

## 🤝 Contributing

We welcome contributions to enhance the coffeehouse experience! Areas for improvement:
- Additional view modes
- Enhanced animations
- More NYC-specific features
- Accessibility improvements
- Performance optimizations

---

*Built with ☕ and 📚 for the NYC academic community*
