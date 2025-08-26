# Website Accessibility Analysis

## 🔍 **Website Access Test Results**

### ✅ **Accessible Websites (No Protection):**

#### **Missing Universities:**
1. **Fordham University** - ✅ Accessible (200 status, 245KB content)
   - URL: https://www.fordham.edu/events/
   - Notes: WordPress site with The Events Calendar plugin

2. **Pratt Institute** - ✅ Accessible (200 status, 164KB content)
   - URL: https://www.pratt.edu/events/
   - Notes: Modern website with New Relic tracking

3. **St. John's University** - ✅ Accessible (200 status, 36KB content)
   - URL: https://www.stjohns.edu/events
   - Notes: Standard university website

4. **Cooper Union** - ✅ Accessible (200 status, 59KB content)
   - URL: https://cooper.edu/events
   - Notes: Drupal-based site

#### **Columbia Departments:**
1. **Columbia History** - ✅ Accessible (200 status, 61KB content)
   - URL: https://history.columbia.edu/events
   - Notes: WordPress with Divi theme

### ❌ **Protected Websites (Cloudflare/403):**

#### **Missing Universities:**
1. **CUNY Graduate Center** - ❌ Cloudflare Protected (403 status)
   - URL: https://www.gc.cuny.edu/events
   - Notes: Will need cloudscraper

#### **Columbia Departments:**
1. **Columbia English** - ❌ Cloudflare Protected (403 status)
   - URL: https://english.columbia.edu/events
   - Notes: Will need cloudscraper

2. **Columbia Anthropology** - ❌ Cloudflare Protected (403 status)
   - URL: https://anthropology.columbia.edu/events
   - Notes: Will need cloudscraper

## 🎯 **Priority Recommendations**

### **Immediate Opportunities (No Protection):**
1. **Fordham University** - Large university, likely many academic events
2. **Pratt Institute** - Art/design events, might have academic lectures
3. **St. John's University** - Catholic university, potential academic events
4. **Cooper Union** - Engineering/architecture events
5. **Columbia History** - Departmental events (could add to Columbia total)

### **Medium Priority (Need Cloudscraper):**
1. **CUNY Graduate Center** - Major research institution
2. **Columbia English** - Departmental events
3. **Columbia Anthropology** - Departmental events

## 📊 **Columbia Department Investigation**

### **Why Columbia Seems Low (Only 3 Events):**
The current Columbia scraper only gets events from the main university calendar. Many departments have their own event pages that aren't included in the main calendar.

### **Columbia Departments to Check:**
- ✅ **History** - Accessible
- ❌ **English** - Cloudflare protected
- ❌ **Anthropology** - Cloudflare protected
- **Philosophy** - Need to test
- **Political Science** - Need to test
- **Sociology** - Need to test
- **Economics** - Need to test
- **Psychology** - Need to test
- **Biology** - Need to test
- **Physics** - Need to test
- **Mathematics** - Need to test
- **Computer Science** - Need to test
- **Engineering** - Need to test
- **Law School** - Need to test
- **Business School** - Need to test
- **Medical School** - Need to test

## 🚀 **Next Steps**

### **Phase 1: Easy Wins (No Protection)**
1. Create scraper for **Fordham University**
2. Create scraper for **Columbia History** (add to Columbia total)
3. Create scraper for **Pratt Institute**
4. Create scraper for **St. John's University**
5. Create scraper for **Cooper Union**

### **Phase 2: Protected Sites (Need Cloudscraper)**
1. Create scraper for **CUNY Graduate Center**
2. Create scraper for **Columbia English**
3. Create scraper for **Columbia Anthropology**

### **Phase 3: Test More Columbia Departments**
Test accessibility of other Columbia departments to potentially add many more events to the Columbia total.

## 📈 **Expected Impact**
- **Fordham**: Could add 10-20 academic events
- **Columbia Departments**: Could add 20-50 academic events (if we can access them)
- **CUNY GC**: Could add 15-30 academic events
- **Others**: Could add 5-15 academic events each

**Total potential addition: 50-130+ academic events**
