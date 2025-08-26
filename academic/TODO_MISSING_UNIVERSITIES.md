# TODO: Missing NYC Universities and Institutions

## Current Status

### ✅ Working Scrapers:
- **Columbia University** (3 academic events)
- **NYU** (40 academic events) - various schools
- **Gallatin School** (2 academic events)
- **ISAW** (1 academic event) - Institute for the Study of the Ancient World
- **JTSA** (3 academic events) - Jewish Theological Seminary
- **New School** (2 academic events)
- **Miller Theatre** (Columbia-affiliated)

### ⚠️ Existing Scrapers with Issues:
- **Barnard College** (0 events) - scraper exists but returns no events
- **Cornell Tech** (1 event) - scraper works but only 1 event (might be filtered out)
- **SOF Heyman** (0 events) - scraper exists but returns no events

## 🚫 Missing Major Universities (Need Scrapers)

### **Large Universities:**
1. **Fordham University** - Jesuit university with multiple campuses
   - Main campus: Bronx
   - Lincoln Center campus: Manhattan
   - Westchester campus
   - Website: https://www.fordham.edu/events/

2. **CUNY System** - City University of New York (multiple colleges)
   - **CUNY Graduate Center** - https://www.gc.cuny.edu/events
   - **Hunter College** - https://hunter.cuny.edu/events/
   - **Brooklyn College** - https://www.brooklyn.cuny.edu/events
   - **Queens College** - https://www.qc.cuny.edu/events/
   - **Baruch College** - https://www.baruch.cuny.edu/events/
   - **City College** - https://www.ccny.cuny.edu/events
   - **Lehman College** - https://www.lehman.edu/events/
   - **John Jay College** - https://www.jjay.cuny.edu/events

3. **St. John's University** - Catholic university
   - Queens campus
   - Manhattan campus
   - Website: https://www.stjohns.edu/events

4. **Pace University** - private university
   - NYC campus
   - Westchester campus
   - Website: https://www.pace.edu/events

### **Art & Design Schools:**
5. **Pratt Institute** - art and design school
   - Website: https://www.pratt.edu/events/

6. **Parsons School of Design** - art and design (part of The New School)
   - Website: https://www.newschool.edu/parsons/events/

7. **School of Visual Arts (SVA)** - art school
   - Website: https://sva.edu/events

8. **Cooper Union** - engineering, art, and architecture
   - Website: https://cooper.edu/events

### **Music & Performing Arts:**
9. **Manhattan School of Music** - music conservatory
   - Website: https://www.msmnyc.edu/events/

10. **Juilliard School** - performing arts (scraper exists but blocked by Cloudflare)

### **Research Institutions:**
11. **Rockefeller University** - biomedical research
     - Website: https://www.rockefeller.edu/events/

12. **Memorial Sloan Kettering** - cancer research
     - Website: https://www.mskcc.org/events

13. **Cold Spring Harbor Laboratory** - biological research
     - Website: https://www.cshl.edu/events/

14. **Brookhaven National Laboratory** - physics research
     - Website: https://www.bnl.gov/events/

### **Specialized Institutions:**
15. **Bank Street College of Education** - education
     - Website: https://www.bankstreet.edu/events/

16. **Union Theological Seminary** - theology
     - Website: https://utsnyc.edu/events/

17. **General Theological Seminary** - Episcopal seminary
     - Website: https://gts.edu/events/

## 📊 **Columbia Department Investigation**

### **Why Columbia Seems Low (Only 3 Events):**
The current Columbia scraper only gets events from the main university calendar. Many departments have their own event pages that aren't included in the main calendar.

### **Columbia Departments - Tested Results:**

#### ✅ **Accessible Departments (No Protection):**
- **Classics**: https://classics.columbia.edu/events (✅ 200 status, Squarespace)
- **Mathematics**: https://math.columbia.edu/events (✅ 200 status, WordPress)
- **Law School**: https://law.columbia.edu/events (✅ 200 status, Drupal)
- **Computer Science**: https://cs.columbia.edu/ (✅ 200 status, no /events page found)
- **History**: https://history.columbia.edu/events (✅ 200 status, WordPress; Note: currently no upcoming events listed on the site)

#### ❌ **Protected Departments (Cloudflare/403):**
- **Philosophy**: https://philosophy.columbia.edu/ (❌ 403)
- **English**: https://english.columbia.edu/events (❌ 403)
- **Anthropology**: https://anthropology.columbia.edu/events (❌ 403)
- **Religion**: https://religion.columbia.edu/ (❌ 403)
- **Art History**: https://arthistory.columbia.edu/ (❌ 403)
- **Music**: https://music.columbia.edu/ (❌ 403)
- **Political Science**: https://polisci.columbia.edu/ (❌ 403)
- **Sociology**: https://sociology.columbia.edu/ (❌ 403)
- **Psychology**: https://psychology.columbia.edu/ (❌ 403)
- **Business School**: https://business.columbia.edu/ (❌ 403)
- **Biology**: https://biology.columbia.edu/ (❌ 403)
- **Physics**: https://physics.columbia.edu/ (❌ 403)
- **Engineering**: https://engineering.columbia.edu/ (❌ 403)
- **Journalism**: https://journalism.columbia.edu/ (❌ 403)
- **SIPA**: https://sipa.columbia.edu/ (❌ 403)

#### ❌ **Non-Existent URLs:**
- economics.columbia.edu
- theatre.columbia.edu
- film.columbia.edu
- architecture.columbia.edu
- publichealth.columbia.edu
- nursing.columbia.edu
- statistics.columbia.edu
- chemistry.columbia.edu
- eesc.columbia.edu
- medicine.columbia.edu
- dental.columbia.edu
- artsinitiative.columbia.edu
- weai.columbia.edu
- mei.columbia.edu
- africanamerican.columbia.edu
- womensstudies.columbia.edu

## Priority Order for New Scrapers:

### **High Priority (Large universities with many events):**
1. **CUNY Graduate Center** - major research institution
2. **Fordham University** - large university with active research
3. **Hunter College** - large CUNY college
4. **Brooklyn College** - large CUNY college

### **Medium Priority (Specialized but active):**
5. **Pratt Institute** - art/design events
6. **Cooper Union** - engineering/architecture events
7. **Rockefeller University** - biomedical research events
8. **Parsons School of Design** - art/design events

### **Lower Priority (Smaller or specialized):**
9. **St. John's University**
10. **Pace University**
11. **School of Visual Arts**
12. **Manhattan School of Music**
13. **Bank Street College**
14. **Union Theological Seminary**

## Notes:
- Some institutions may have events but they might not be academic lectures/series
- Some may require special handling (Cloudflare protection, authentication, etc.)
- Consider checking if events are actually academic before creating scrapers

## 🚀 **IMPLEMENTATION INSTRUCTIONS FOR NEXT MODEL**

### **Phase 1: Easy Wins (No Protection) - START HERE**

#### **Columbia Departments (High Priority - Add to Columbia Total):**
1. **Columbia Classics** - Create `scrapers/columbia_classics_events.py`
   - URL: https://classics.columbia.edu/events
   - Squarespace site
   - Expected: 5-15 academic events (adds to Columbia total)

2. **Columbia Mathematics** - Create `scrapers/columbia_math_events.py`
   - URL: https://math.columbia.edu/events
   - WordPress with custom theme
   - Expected: 5-15 academic events (adds to Columbia total)

3. **Columbia Law** - Create `scrapers/columbia_law_events.py`
   - URL: https://law.columbia.edu/events
   - Drupal site
   - Expected: 10-25 academic events (adds to Columbia total)

4. **Columbia History** - Create `scrapers/columbia_history_events.py`
   - URL: https://history.columbia.edu/events
   - WordPress with Divi theme
   - Expected: currently 0 upcoming events listed; implement scraper template and re-check weekly

#### **Other Universities:**
5. **Fordham University** - Create `scrapers/fordham_events.py`
   - URL: https://www.fordham.edu/events/
   - WordPress site with The Events Calendar plugin
   - Expected: 10-20 academic events

6. **Pratt Institute** - Create `scrapers/pratt_events.py`
   - URL: https://www.pratt.edu/events/
   - Modern website with New Relic tracking
   - Expected: 5-15 academic events

7. **St. John's University** - Create `scrapers/stjohns_events.py`
   - URL: https://www.stjohns.edu/events
   - Standard university website
   - Expected: 5-15 academic events

8. **Cooper Union** - Create `scrapers/cooper_union_events.py`
   - URL: https://cooper.edu/events
   - Drupal-based site
   - Expected: 5-15 academic events

### **Phase 2: Protected Sites (Need Cloudscraper)**
1. **CUNY Graduate Center** - Create `scrapers/cuny_gc_events.py`
   - URL: https://www.gc.cuny.edu/events
   - Use cloudscraper (already installed)
   - Expected: 15-30 academic events

2. **Columbia English** - Create `scrapers/columbia_english_events.py`
   - URL: https://english.columbia.edu/events
   - Use cloudscraper
   - Expected: 5-10 academic events (adds to Columbia total)

3. **Columbia Anthropology** - Create `scrapers/columbia_anthropology_events.py`
   - URL: https://anthropology.columbia.edu/events
   - Use cloudscraper
   - Expected: 5-10 academic events (adds to Columbia total)

### **Phase 3: Test Columbia Departments**
Test accessibility of other Columbia departments from the list above. Many will likely be accessible and could add 20-50+ academic events to Columbia total.

### **Implementation Template:**
Use existing scrapers as templates:
- `scrapers/columbia_events.py` for Columbia departments
- `scrapers/nyu_events.py` for university-wide scrapers
- `scrapers/miller_events.py` for simple WordPress sites

### **Testing Process:**
1. Create scraper file
2. Test with: `python -c "from scrapers.[name]_events import scrape_[name]_events; result = scrape_[name]_events(); print(f'Events found: {len(result.get(\"events\", []))}')"`
3. Run full test: `python main_test.py`
4. Check filtered results: `python filter_academic_events.py`
5. Analyze: `python analyze_filtered.py`

### **Expected Total Addition: 75-180+ academic events**

#### **Columbia Department Impact:**
- **Current Columbia**: 3 academic events
- **Columbia Classics**: 5-15 academic events
- **Columbia Mathematics**: 5-15 academic events
- **Columbia Law**: 10-25 academic events
- **Columbia History**: currently 0 visible; monitor weekly
- **New Columbia Total**: 23-58 academic events (20-55 event increase)

#### **Other Universities Impact:**
- **Fordham**: 10-20 academic events
- **Pratt**: 5-15 academic events
- **St. Johns**: 5-15 academic events
- **Cooper Union**: 5-15 academic events
- **CUNY GC**: 15-30 academic events (with cloudscraper)
- **Protected Columbia Departments**: 25-70 academic events (with cloudscraper)

**Total potential addition: 75-180+ academic events**
