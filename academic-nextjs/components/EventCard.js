import styles from './EventCard.module.css'

export default function EventCard({ event }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const formatTime = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  const eventUrl = event.source_url || event.metadata?.source_url || event.url
  const location = event.venue?.name || event.metadata?.venue?.name || event.location || 'Location TBD'
  const institution = event.source_group || event.source_name || event.metadata?.source_name || 'Unknown Institution'

  return (
    <div className={styles.eventCard}>
      <div className={styles.eventHeader}>
        <h3 className={styles.eventTitle}>
          {eventUrl ? (
            <a
              href={eventUrl}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.eventLink}
            >
              {event.name || event.title || 'Untitled Event'}
            </a>
          ) : (
            event.name || event.title || 'Untitled Event'
          )}
        </h3>
      </div>

      <div className={styles.eventMeta}>
        <div className={styles.eventDateTime}>
          <span className={styles.date}>{formatDate(event.start_date)}</span>
          <span className={styles.time}>{formatTime(event.start_date)}</span>
        </div>

        <div className={styles.eventInstitution}>
          {institution}
        </div>

        <div className={styles.eventLocation}>
          {location}
        </div>
      </div>

      {event.description && (
        <div className={styles.eventDescription}>
          <p className={styles.descriptionText}>
            {event.description.length > 150
              ? `${event.description.substring(0, 150)}...`
              : event.description
            }
          </p>
        </div>
      )}

      {eventUrl && (
        <div className={styles.eventActions}>
          <a
            href={eventUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.readMoreButton}
          >
            VIEW EVENT
          </a>
        </div>
      )}
    </div>
  )
}
