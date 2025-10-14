import { useState } from 'react'
import RibbonBookmarks from './RibbonBookmarks'
import PageContent from './PageContent'
import styles from './BookContainer.module.css'

export default function BookContainer({ children }) {
  const [currentPage, setCurrentPage] = useState('home')
  const [isPageFlipping, setIsPageFlipping] = useState(false)

  const handlePageChange = (pageId) => {
    if (pageId !== currentPage) {
      setIsPageFlipping(true)
      // Simulate page flip timing
      setTimeout(() => {
        setCurrentPage(pageId)
        setIsPageFlipping(false)
      }, 300)
    }
  }

  return (
    <div className={styles.book}>
      {/* Book spine decoration */}
      <div className={styles.spine}></div>

      {/* Main book content */}
      <div className={styles.content}>
        {/* Ribbon bookmarks navigation */}
        <RibbonBookmarks
          currentPage={currentPage}
          onPageChange={handlePageChange}
          disabled={isPageFlipping}
        />

        {/* Page content area */}
        <PageContent isFlipping={isPageFlipping}>
          {children}
        </PageContent>
      </div>
    </div>
  )
}
