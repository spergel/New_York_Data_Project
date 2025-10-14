'use client'

import { useState, useEffect } from 'react'
import EventCard from '../../components/EventCard'
import Pagination from '../../components/Pagination'
import styles from './page.module.css'

const EVENTS_PER_PAGE = 10

export default function EventsPage() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalEvents, setTotalEvents] = useState(0)

  useEffect(() => {
    loadEvents()
  }, [currentPage])

  const loadEvents = async () => {
    try {
      setLoading(true)
      const offset = (currentPage - 1) * EVENTS_PER_PAGE
      const response = await fetch(
        `https://nyc-academic-events-api.spergel-joshua.workers.dev/api/events?limit=${EVENTS_PER_PAGE}&offset=${offset}`
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setEvents(data.data.events || [])
      setTotalEvents(data.data.pagination?.total || 0)
    } catch (error) {
      console.error('Error loading events:', error)
      setEvents([])
    } finally {
      setLoading(false)
    }
  }

  const totalPages = Math.ceil(totalEvents / EVENTS_PER_PAGE)

  if (loading) {
    return (
      <div className={styles.container}>
        <h1 className={styles.heading1}>Academic Events</h1>
        <div className={styles.loading}>Loading events...</div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.heading1}>Academic Events</h1>

      <div className={styles.stats}>
        <span className={styles.caption}>
          Page {currentPage} of {totalPages} • {totalEvents} total events
        </span>
      </div>

      <div className={styles.eventsGrid}>
        {events.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>

      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
        />
      )}
    </div>
  )
}
