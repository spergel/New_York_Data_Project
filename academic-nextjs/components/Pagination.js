import styles from './Pagination.module.css'

export default function Pagination({ currentPage, totalPages, onPageChange }) {
  const getVisiblePages = () => {
    const delta = 2
    const range = []
    const rangeWithDots = []

    for (let i = Math.max(2, currentPage - delta); i <= Math.min(totalPages - 1, currentPage + delta); i++) {
      range.push(i)
    }

    if (currentPage - delta > 2) {
      rangeWithDots.push(1, '...')
    } else {
      rangeWithDots.push(1)
    }

    rangeWithDots.push(...range)

    if (currentPage + delta < totalPages - 1) {
      rangeWithDots.push('...', totalPages)
    } else if (totalPages > 1) {
      rangeWithDots.push(totalPages)
    }

    return rangeWithDots
  }

  if (totalPages <= 1) return null

  return (
    <nav className={styles.pagination} aria-label="Event pages">
      <button
        className={styles.pageButton}
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        aria-label="Previous page"
      >
        ◀ PREVIOUS
      </button>

      <div className={styles.pageNumbers}>
        {getVisiblePages().map((page, index) => (
          <span key={index}>
            {page === '...' ? (
              <span className={styles.ellipsis}>...</span>
            ) : (
              <button
                className={`${styles.pageButton} ${styles.pageNumber} ${
                  page === currentPage ? styles.active : styles.inactive
                }`}
                onClick={() => onPageChange(page)}
                disabled={page === currentPage}
                aria-label={`Page ${page}`}
                aria-current={page === currentPage ? 'page' : undefined}
              >
                {page}
              </button>
            )}
          </span>
        ))}
      </div>

      <button
        className={styles.pageButton}
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        aria-label="Next page"
      >
        NEXT ▶
      </button>

      <div className={styles.pageInfo}>
        <span className={styles.caption}>
          Page {currentPage} of {totalPages}
        </span>
      </div>
    </nav>
  )
}
