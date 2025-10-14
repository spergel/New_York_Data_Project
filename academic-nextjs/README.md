# 📖 NYC Academic Events - Literary Edition

An antique book-themed Next.js application for discovering academic events across New York City's universities. Experience events through the pages of a virtual leather-bound volume with page-flipping animations and classical typography.

## 🎨 Design Philosophy

**Classical restraint over trendy excess.** This application embraces the timeless elegance of antique books with:
- Clean lines and sharp corners (no border-radius)
- Leather and parchment color palette
- Classical serif typography
- Mechanical page-flipping animations
- Ribbon bookmark navigation

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
```bash
cd academic-nextjs
npm install
```

### Development
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000)

### Build for Production
```bash
npm run build
npm start
```

## 📁 Project Structure

```
academic-nextjs/
├── app/                          # Next.js App Router
│   ├── layout.js                # Root layout with book container
│   ├── page.js                  # Home (Table of Contents)
│   ├── globals.css              # Antique book design system
│   ├── events/                  # Events listing page
│   └── institutions/            # Institutions directory
├── components/                   # Reusable components
│   ├── BookContainer.js         # Main book layout
│   ├── RibbonBookmarks.js       # Navigation bookmarks
│   ├── PageContent.js           # Page flipping container
│   ├── EventCard.js             # Event display component
│   └── Pagination.js            # Book-like pagination
├── lib/                         # Utilities
│   └── BookContext.js           # Book state management
└── styles/                      # CSS Modules
```

## 🎭 Key Features

### Antique Book Interface
- **Leather-bound container** with spine decoration
- **Ribbon bookmark navigation** (6 sections)
- **Page-flipping animations** using React Spring
- **Parchment color scheme** with gold accents

### Event Discovery
- **Real-time data** from Cloudflare Worker API
- **Pagination** with book-like page numbers
- **Clickable event titles** linking to original sources
- **Institution filtering** and search capabilities

### Classical Design System
- **Typography**: Times New Roman, serif fonts only
- **Colors**: Leather tones, parchment, ink black
- **Layout**: Grid-based, no flexbox tricks
- **Interactions**: Simple state changes, no animations

## 🔧 API Integration

The application fetches data from the Cloudflare Worker API:
```
https://nyc-academic-events-api.spergel-joshua.workers.dev/api/events
```

### Response Format
```json
{
  "success": true,
  "data": {
    "events": [...],
    "pagination": {
      "total": 400,
      "limit": 10,
      "offset": 0,
      "has_more": true
    }
  }
}
```

## 🚀 Deployment

### Vercel (Recommended)
1. Import the `academic` folder from GitHub
2. Set **Root Directory**: `academic`
3. Deploy automatically

### Manual Deployment
```bash
npm run build
npm start
```

## 🎯 Navigation Structure

- **🏛️ Table of Contents** - Landing page with overview
- **📚 Events** - Paginated event listings
- **🏫 Institutions** - University directory
- **📅 Calendar** - Calendar view (planned)
- **🔍 Search** - Search functionality (planned)
- **ℹ️ About** - Information page (planned)

## 🛠️ Development Guidelines

### CSS Rules (No Modern Trends)
- ❌ No `border-radius`
- ❌ No `box-shadow`
- ❌ No CSS gradients
- ❌ No `backdrop-blur`
- ❌ No `transform: translateZ()`
- ❌ No hover animations
- ❌ No floating elements

### JavaScript Rules
- ✅ React hooks and state
- ✅ CSS Modules for styling
- ✅ React Spring for page flipping (minimal)
- ✅ Zustand for state management
- ✅ No component libraries

### Typography Rules
- ✅ Classical serif fonts only
- ✅ Strict hierarchy (size + weight)
- ✅ No font smoothing tricks
- ✅ Proper line heights

## 📊 Performance

- **Bundle Size**: Minimal dependencies
- **API Caching**: 1-hour cache on Cloudflare
- **Image Optimization**: No images (text-only design)
- **Core Web Vitals**: Optimized for speed

## 🤝 Contributing

This project maintains a strict classical design aesthetic. All contributions must adhere to the antique book design principles and avoid modern UI trends.

## 📄 License

Academic events data courtesy of participating NYC institutions. Interface design inspired by classical book typography and printing traditions.
