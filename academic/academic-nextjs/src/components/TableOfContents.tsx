import { EventData } from '../types/events';

interface TableOfContentsProps {
  events: EventData[];
  onPageClick: (pageNumber: number) => void;
}

export default function TableOfContents({ events, onPageClick }: TableOfContentsProps) {
  // Clean up organizations - group departments under parent institutions
  const cleanInstitutions = (institution: string) => {
    const name = institution.toLowerCase();
    if (name.includes('nyu') || name.includes('new york university') || name.includes('isaw')) return 'New York University';
    if (name.includes('columbia')) return 'Columbia University';
    if (name.includes('cornell')) return 'Cornell University';
    if (name.includes('cooper union')) return 'Cooper Union';
    if (name.includes('pratt')) return 'Pratt Institute';
    if (name.includes('juilliard')) return 'Juilliard School';
    if (name.includes('new school')) return 'The New School';
    if (name.includes('simons')) return 'Simons Foundation';
    if (name.includes('jtsa') || name.includes('jewish theological')) return 'Jewish Theological Seminary';
    return institution; // Keep original if no match
  };

  const getUniversityColor = (institution: string) => {
    const name = institution.toLowerCase();
    if (name.includes('columbia')) return '#1f4e79'; // Columbia Blue
    if (name.includes('nyu') || name.includes('new york university')) return '#57068c'; // NYU Purple
    if (name.includes('cornell')) return '#b31b1b'; // Cornell Red
    if (name.includes('cooper union')) return '#006400'; // Cooper Green
    if (name.includes('pratt')) return '#ff6b35'; // Pratt Orange
    if (name.includes('juilliard')) return '#8b0000'; // Juilliard Dark Red
    if (name.includes('new school')) return '#e31837'; // New School Red
    if (name.includes('simons')) return '#2e8b57'; // Simons Green
    return '#6b7280'; // Default Gray
  };

  // Get unique institutions
  const institutions = [...new Set(events.map(e => cleanInstitutions(e.institution)))].sort();

  // Create table of contents items
  const tocItems = [
    { type: 'all', name: 'All Events', count: events.length, color: '#3b82f6', page: 1 },
    ...institutions.map((inst, index) => ({ 
      type: 'institution', 
      name: inst, 
      count: events.filter(e => cleanInstitutions(e.institution) === inst).length, 
      color: getUniversityColor(inst),
      page: 2 + index // Each institution gets its own section starting from page 2
    }))
  ];

  const tocItemsPerPage = 8;
  const totalTocPages = Math.ceil(tocItems.length / tocItemsPerPage);

  return (
    <>
      {Array.from({ length: totalTocPages }, (_, tocPageIndex) => {
        const tocPageItems = tocItems.slice(tocPageIndex * tocItemsPerPage, (tocPageIndex + 1) * tocItemsPerPage);
        const tocPageNumber = tocPageIndex + 1;

        return (
          <div key={tocPageIndex} className="page">
            <div className="page-content">
              <div className="page-main-content">
                <h2 className="page-header">TABLE OF CONTENTS</h2>
                <div className="paint-thing-graphic">
                  <svg viewBox="0 0 100 60" className="paint-flame">
                    <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#dc2626" opacity="0.8"/>
                    <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#f59e0b" opacity="0.7"/>
                  </svg>
                </div>
                <div className="page-text">
                  <div className="book-toc">
                    {tocPageItems.map((item, index) => (
                      <div 
                        key={index}
                        className="toc-entry" 
                        onClick={() => onPageClick(item.page - 1)}
                        style={{ cursor: 'pointer' }}
                      >
                        <span className="toc-title">{item.name}</span>
                        <span className="toc-dots"></span>
                        <span className="toc-page">{item.page}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="page-footer">{tocPageNumber}</div>
              </div>
            </div>
          </div>
        );
      })}
    </>
  );
}

