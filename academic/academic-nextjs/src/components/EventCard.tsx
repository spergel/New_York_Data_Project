import { EventData } from '../types/events';

interface EventCardProps {
  event: EventData;
  onInstitutionClick?: (institution: string) => void;
}

export default function EventCard({ event, onInstitutionClick }: EventCardProps) {
  const handleInstitutionClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onInstitutionClick) {
      onInstitutionClick(event.institution);
    }
  };

  return (
    <div className="event-item">
      <h3 
        className={`event-title ${event.source_url ? 'clickable-event' : ''}`}
        onClick={event.source_url ? () => window.open(event.source_url, '_blank') : undefined}
      >
        {event.title}
      </h3>
      <div className="event-meta">
        <p>
          <strong 
            className="clickable-institution"
            onClick={handleInstitutionClick}
            style={{ cursor: 'pointer', color: '#3b82f6' }}
          >
            {event.institution}
          </strong> • <em>{event.date}</em>
        </p>
        {event.location && event.location !== 'Location TBD' && (
          <p><strong>Location:</strong> {event.location}</p>
        )}
        {event.category && (
          <p><strong>Category:</strong> {event.category}</p>
        )}
      </div>
      <p className="event-description">{event.description}</p>
    </div>
  );
}

