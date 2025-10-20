import { BookmarkData } from '../types/events';

interface BookmarkRibbonProps {
  bookmarks: BookmarkData[];
  onBookmarkClick: (institution: string) => void;
}

export default function BookmarkRibbon({ bookmarks, onBookmarkClick }: BookmarkRibbonProps) {
  const sortedBookmarks = [...bookmarks].sort((a, b) => a.institution.localeCompare(b.institution));

  return (
    <div className="book-bookmarks-container">
      {sortedBookmarks.map((bookmark) => (
        <div 
          key={bookmark.institution}
          className="book-bookmark" 
          onClick={() => onBookmarkClick(bookmark.institution)}
          title={`${bookmark.institution} (${bookmark.count} events)`}
        >
          <span className="bookmark-label">
            {bookmark.institution.length > 12 
              ? `${bookmark.institution.substring(0, 10)}...` 
              : bookmark.institution
            }
          </span>
          <span className="bookmark-number">({bookmark.count})</span>
        </div>
      ))}
    </div>
  );
}

