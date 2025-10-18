import { NavigationState } from '../types/events';

interface NavigationControlsProps {
  navigationState: NavigationState;
  onGoToPage: (pageNumber: number) => void;
  onGoToFirstPage: () => void;
  onGoToTableOfContents: () => void;
}

export default function NavigationControls({ 
  navigationState, 
  onGoToPage, 
  onGoToFirstPage, 
  onGoToTableOfContents
}: NavigationControlsProps) {
  return (
    <div className="flex flex-col items-center space-y-4 p-4">
      {/* Main Navigation Controls */}
      <div className="flex space-x-4">
        <button
          onClick={onGoToTableOfContents}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          Table of Contents
        </button>
        <button
          onClick={onGoToFirstPage}
          className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
        >
          First Page
        </button>
      </div>

      {/* Instructions */}
      <div className="text-center text-sm text-gray-600 dark:text-gray-400 max-w-2xl">
        <p>
          {navigationState.currentSection === 'all' 
            ? "Click the left/right edges of pages to flip, use arrow keys (←/→), or click the red bookmark ribbons to jump to institutions."
            : "Click institution names in events to navigate to their sections, or use the Table of Contents to return to all events."
          }
        </p>
        <p className="mt-2 text-xs">
          💡 Tip: Click the blue edges of pages to flip, or use arrow keys for navigation
        </p>
      </div>
    </div>
  );
}
