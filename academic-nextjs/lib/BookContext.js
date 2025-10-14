import { createContext, useContext, useState } from 'react'

const BookContext = createContext()

export function BookProvider({ children }) {
  const [currentPage, setCurrentPage] = useState('home')
  const [isFlipping, setIsFlipping] = useState(false)

  const navigateToPage = (pageId) => {
    if (pageId !== currentPage) {
      setIsFlipping(true)
      setTimeout(() => {
        setCurrentPage(pageId)
        setIsFlipping(false)
      }, 300)
    }
  }

  return (
    <BookContext.Provider value={{
      currentPage,
      isFlipping,
      navigateToPage
    }}>
      {children}
    </BookContext.Provider>
  )
}

export function useBook() {
  const context = useContext(BookContext)
  if (!context) {
    throw new Error('useBook must be used within a BookProvider')
  }
  return context
}
