import './globals.css'
import { BookProvider } from '../lib/BookContext'
import BookContainer from '../components/BookContainer'

export const metadata = {
  title: 'NYC Academic Events - Literary Edition',
  description: 'Discover academic events across New York City universities through an antique book interface',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <BookProvider>
          <BookContainer>
            {children}
          </BookContainer>
        </BookProvider>
      </body>
    </html>
  )
}
