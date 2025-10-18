export interface EventData {
  title: string;
  institution: string;
  date: string;
  description: string;
  location?: string;
  category?: string;
  source_url?: string;
}

export interface NavigationState {
  currentPage: number;
  history: number[];
  currentSection: 'all' | 'institution';
  currentInstitution?: string;
}

export interface BookmarkData {
  institution: string;
  count: number;
  firstPageIndex: number;
}

