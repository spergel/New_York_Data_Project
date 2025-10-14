import styles from './page.module.css'

export default function HomePage() {
  return (
    <main className={styles.main}>
      <div className={styles.titlePage}>
        <h1 className={styles.title}>
          NYC Academic Events
        </h1>

        <div className={styles.subtitle}>
          Literary Edition
        </div>

        <div className={styles.description}>
          <p className={styles.bodyText}>
            Discover academic events across New York City's universities
            through the pages of this antique volume.
          </p>

          <p className={styles.bodyText}>
            Use the ribbon bookmarks above to navigate through different sections,
            or turn the pages to explore events chronologically.
          </p>
        </div>

        <div className={styles.contents}>
          <h2 className={styles.heading2}>Table of Contents</h2>

          <div className={styles.contentsList}>
            <div className={styles.contentsItem}>
              <span className={styles.pageNumber}>1-50</span>
              <span className={styles.chapterTitle}>Current Events</span>
            </div>

            <div className={styles.contentsItem}>
              <span className={styles.pageNumber}>51-100</span>
              <span className={styles.chapterTitle}>Upcoming Events</span>
            </div>

            <div className={styles.contentsItem}>
              <span className={styles.pageNumber}>101-150</span>
              <span className={styles.chapterTitle}>By Institution</span>
            </div>

            <div className={styles.contentsItem}>
              <span className={styles.pageNumber}>151-200</span>
              <span className={styles.chapterTitle}>Calendar View</span>
            </div>

            <div className={styles.contentsItem}>
              <span className={styles.pageNumber}>201-250</span>
              <span className={styles.chapterTitle}>Search & Discovery</span>
            </div>
          </div>
        </div>

        <div className={styles.published}>
          <p className={styles.caption}>
            Published 2025 • New York City
          </p>
        </div>
      </div>
    </main>
  )
}
