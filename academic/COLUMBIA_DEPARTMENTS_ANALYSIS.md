# Columbia Department Events Analysis

## 🔍 **Accessibility Test Results**

### ✅ **Accessible Columbia Departments (No Protection):**

#### **Arts & Humanities:**
1. **Classics** - ✅ Accessible (200 status, 413KB content)
   - URL: https://classics.columbia.edu/events
   - Platform: Squarespace
   - Expected: 5-15 academic events

#### **Sciences:**
2. **Mathematics** - ✅ Accessible (200 status, 72KB content)
   - URL: https://math.columbia.edu/events
   - Platform: WordPress with custom theme
   - Expected: 5-15 academic events

#### **Professional Schools:**
3. **Law School** - ✅ Accessible (200 status, 76KB content)
   - URL: https://law.columbia.edu/events
   - Platform: Drupal
   - Expected: 10-25 academic events

#### **Computer Science:**
4. **Computer Science** - ✅ Accessible (200 status, base site)
   - URL: https://cs.columbia.edu/ (no /events page found)
   - Platform: Custom
   - Note: Need to find events page or calendar

### ❌ **Protected Columbia Departments (Cloudflare/403):**

#### **Arts & Humanities:**
- Philosophy: https://philosophy.columbia.edu/ (❌ 403)
- Religion: https://religion.columbia.edu/ (❌ 403)
- Art History: https://arthistory.columbia.edu/ (❌ 403)
- Music: https://music.columbia.edu/ (❌ 403)

#### **Social Sciences:**
- Political Science: https://polisci.columbia.edu/ (❌ 403)
- Sociology: https://sociology.columbia.edu/ (❌ 403)
- Psychology: https://psychology.columbia.edu/ (❌ 403)
- Business School: https://business.columbia.edu/ (❌ 403)

#### **Sciences:**
- Biology: https://biology.columbia.edu/ (❌ 403)
- Physics: https://physics.columbia.edu/ (❌ 403)

#### **Professional Schools:**
- Engineering: https://engineering.columbia.edu/ (❌ 403)
- Journalism: https://journalism.columbia.edu/ (❌ 403)
- SIPA: https://sipa.columbia.edu/ (❌ 403)

### ❌ **Non-Existent URLs:**
- economics.columbia.edu
- theatre.columbia.edu
- film.columbia.edu
- architecture.columbia.edu
- publichealth.columbia.edu
- nursing.columbia.edu

## 🎯 **Immediate Opportunities**

### **Phase 1: Easy Wins (No Protection)**
1. **Columbia Classics** - Create `scrapers/columbia_classics_events.py`
   - Squarespace site, likely structured events
   - Expected: 5-15 academic events

2. **Columbia Mathematics** - Create `scrapers/columbia_math_events.py`
   - WordPress site with custom theme
   - Expected: 5-15 academic events

3. **Columbia Law** - Create `scrapers/columbia_law_events.py`
   - Drupal site
   - Expected: 10-25 academic events

4. **Columbia Computer Science** - Investigate events page
   - Base site accessible, need to find events location
   - Could be under different URL pattern

### **Phase 2: Protected Sites (Need Cloudscraper)**
1. **Columbia Philosophy** - Create `scrapers/columbia_philosophy_events.py`
2. **Columbia Political Science** - Create `scrapers/columbia_polisci_events.py`
3. **Columbia Psychology** - Create `scrapers/columbia_psychology_events.py`
4. **Columbia Business** - Create `scrapers/columbia_business_events.py`

## 📊 **Expected Impact**

### **Immediate Addition (No Protection):**
- **Columbia Classics**: 5-15 academic events
- **Columbia Mathematics**: 5-15 academic events  
- **Columbia Law**: 10-25 academic events
- **Columbia CS**: 5-15 academic events (if events page found)

**Total Phase 1: 25-70 academic events**

### **Protected Sites (With Cloudscraper):**
- **Columbia Philosophy**: 5-15 academic events
- **Columbia Political Science**: 5-15 academic events
- **Columbia Psychology**: 5-15 academic events
- **Columbia Business**: 10-25 academic events

**Total Phase 2: 25-70 academic events**

### **Overall Columbia Impact:**
- **Current Columbia**: 3 academic events
- **Potential Addition**: 50-140 academic events
- **New Columbia Total**: 53-143 academic events

## 🚀 **Implementation Priority**

### **Start with these 3 (Easy Wins):**
1. **Columbia Classics** (Squarespace - structured)
2. **Columbia Mathematics** (WordPress - familiar)
3. **Columbia Law** (Drupal - professional events)

### **Then investigate:**
4. **Columbia Computer Science** - Find events page
5. **Protected departments** - Use cloudscraper

## 📝 **Notes**
- Many Columbia departments use Cloudflare protection
- Some departments may not have separate event pages
- Professional schools (Law, Business) likely have more events
- Arts departments may have more performance events than academic lectures
