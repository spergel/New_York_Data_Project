import { EventData } from '../types/events';
import EventCard from './EventCard';

interface PageContentProps {
  title: string;
  events: EventData[];
  pageNumber: number;
  onInstitutionClick?: (institution: string) => void;
}

export default function PageContent({ title, events, pageNumber, onInstitutionClick }: PageContentProps) {
  return (
    <div className="page">
      <div className="page-content">
        <div className="page-main-content">
          <h2 className="page-header">{title}</h2>
          <div className="paint-thing-graphic">
            <svg viewBox="0 0 100 60" className="paint-flame">
              <path d="M20 50 Q30 20 40 45 Q50 10 60 40 Q70 15 80 35 L85 50 Z" fill="#dc2626" opacity="0.8"/>
              <path d="M25 50 Q35 25 45 50 Q55 20 65 45 Q75 25 80 50 L85 50 Z" fill="#f59e0b" opacity="0.7"/>
            </svg>
          </div>
          <div className="page-text">
            {events.map((event, eventIndex) => (
              <EventCard
                key={`${event.title}-${eventIndex}`}
                event={event}
                onInstitutionClick={onInstitutionClick}
              />
            ))}
          </div>
          <div className="page-footer">{pageNumber}</div>
        </div>
      </div>
    </div>
  );
}

