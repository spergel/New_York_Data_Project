import styles from './RibbonBookmarks.module.css'

const BOOKMARKS = [
  { id: 'home', label: 'TOC', title: 'Table of Contents' },
  { id: 'events', label: 'EVT', title: 'Events' },
  { id: 'institutions', label: 'INS', title: 'Institutions' },
  { id: 'calendar', label: 'CAL', title: 'Calendar' },
  { id: 'search', label: 'SRCH', title: 'Search' },
  { id: 'about', label: 'ABT', title: 'About' },
]

export default function RibbonBookmarks({ currentPage, onPageChange, disabled }) {
  return (
    <nav className={styles.ribbonBookmarks}>
      <div className={styles.bookmarkContainer}>
        {BOOKMARKS.map((bookmark) => (
          <button
            key={bookmark.id}
            className={`${styles.bookmark} ${
              currentPage === bookmark.id ? styles.active : styles.inactive
            }`}
            onClick={() => !disabled && onPageChange(bookmark.id)}
            disabled={disabled}
            title={bookmark.title}
            aria-label={`Navigate to ${bookmark.title}`}
          >
            <span className={styles.bookmarkLabel}>
              {bookmark.label}
            </span>
          </button>
        ))}
      </div>
    </nav>
  )
}
