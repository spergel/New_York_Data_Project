import { NavigationState } from '../types/events';

interface NavigationControlsProps {
  navigationState: NavigationState;
  onGoToPage: (pageNumber: number) => void;
}

export default function NavigationControls({
  navigationState,
  onGoToPage
}: NavigationControlsProps) {
  return (
    <div className="flex flex-col items-center space-y-4 p-4">
      {/* Empty navigation - bookmark handles TOC navigation */}
    </div>
  );
}
