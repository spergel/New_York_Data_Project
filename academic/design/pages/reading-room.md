# 📖 Reading Room Page Design Specification

## Overview
The Reading Room serves as the grand entrance to the literary library, featuring a classic scholarly space with oak floors, brass fixtures, and a central card catalog. This is where users first arrive and choose their destination.

## Layout Concept
- **Grand Entrance Hall**: Wide oak staircase leading to stack entrances
- **Central Catalog**: Massive brass card catalog listing all sections and functions
- **Reference Desk**: Literary information kiosk with librarian-style assistance
- **Period Details**: Vintage telephones, brass lamps, ornate lighting fixtures

## Visual Elements to Draw

### 1. **Oak Floor Pattern**
- **Style**: Classic hardwood patterns with brass inlays
- **Colors**: Warm oak with gold vein accents
- **Details**: Library seal inlay at center, radiating book patterns
- **Size**: Full viewport width, perspective-correct for depth

### 2. **Brass Card Catalog**
- **Dimensions**: 8ft tall x 6ft wide, mounted on mahogany pedestal
- **Structure**: Brass frame with glass panels, internal lighting
- **Content**: Section numbers, subject names, illuminated indicators
- **Typography**: Literary font for section names, illuminated letters
- **Interactive**: Backlit drawers that glow when hovered

### 3. **Stack Entrance**
- **Quantity**: 3 stack doors in mahogany frames
- **Style**: Literary grillwork, circular section indicators
- **Doors**: Sliding oak panels with frosted glass inserts
- **Call Buttons**: Large circular brass buttons with LED indicators
- **Details**: Brass handrails, ornate molding around openings

### 4. **Reference Desk**
- **Shape**: Curved mahogany counter with brass trim
- **Features**: Vintage telephone, brass bell, librarian lamp
- **Signage**: "Information" plaque in literary script
- **Accessories**: Leather-bound reference book, brass pen holder

### 5. **Architectural Details**
- **Columns**: Fluted mahogany columns with brass capitals
- **Ceiling**: Ornate plasterwork with brass light fixtures
- **Walls**: Mahogany wainscoting, wallpaper above chair rail
- **Doors**: Heavy brass-framed doors to other areas
- **Lighting**: Crystal chandeliers, wall sconces, warm lamp accents

### 6. **Decorative Elements**
- **Rug**: Large oriental rug with literary border
- **Plants**: Large potted palms in brass planters
- **Artwork**: Literary paintings, bronze sculptures
- **Clock**: Large brass clock face on rear wall
- **Mail Slots**: Individual brass slots for each section

## Interactive Features

### Navigation Elements
- **Card Catalog**: Clickable section listings that trigger stack calls
- **Stack Doors**: Open/close animations when called
- **Call Buttons**: Press animations with sound effects
- **Reference Desk**: Modal popup with library information

### Animations Required
- **Door Openings**: Smooth sliding oak doors with mechanical sounds
- **Light Fades**: Lamp lights that glow to life when activated
- **Button Presses**: Satisfying click animations with audio feedback
- **Stack Arrival**: Bell dings, section indicator lights up

## Content Areas

### Card Catalog Content
```
GROUND FLOOR - Main Reading Room & Information
1ST FLOOR - Today's Events
2ND FLOOR - Tomorrow's Events
3RD FLOOR - This Week's Events
5TH FLOOR - Columbia University Events
8TH FLOOR - NYU Events
10TH FLOOR - CUNY Events
15TH FLOOR - Special Events & Conferences
20TH FLOOR - Card Catalog
25TH FLOOR - Study Carrel
30TH FLOOR - Reference Desk
BASEMENT - Rare Books Room & Archives
```

### Welcome Message
- **Location**: Large brass plaque above reference desk
- **Text**: "Welcome to the NYC Academic Events Library"
- **Style**: Illuminated literary lettering
- **Animation**: Subtle glow effect, letters appear sequentially

## Technical Specifications

### Responsive Behavior
- **Desktop**: Full grand reading room view with all details visible
- **Tablet**: Simplified layout, focus on central catalog
- **Mobile**: Vertical stack, stack controls at bottom

### Performance Considerations
- **Background**: High-resolution oak texture (tiled for performance)
- **Animations**: CSS transforms for smooth 60fps performance
- **Loading**: Progressive loading of decorative elements

### Accessibility Features
- **Keyboard Navigation**: Tab through catalog items
- **Screen Reader**: Descriptive alt text for all architectural elements
- **High Contrast**: Enhanced visibility for card catalog
- **Reduced Motion**: Simplified animations for motion-sensitive users

## Sound Design
- **Ambient**: Subtle library ambiance (page turning, quiet conversations)
- **Interactive**: Button press sounds, stack dings
- **Atmospheric**: Period-appropriate classical music (optional)

## Color Palette
- **Primary Oak**: #D2691E (Warm brown)
- **Brass Elements**: #FFD700 (Gold)
- **Catalog Glass**: #E8E8E8 (Frosted glass)
- **Lamp Accents**: #FFFF99 (Warm yellow)
- **Shadow Details**: #36454F (Charcoal)

## Typography
- **Catalog**: Custom literary display font
- **Section Numbers**: Bold serif numerals
- **Signage**: Literary script for decorative text
- **Body Text**: Clean serif for information panels
