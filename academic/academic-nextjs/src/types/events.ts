export interface EventData {
  title: string;
  institution: string;
  date: string;
  description: string;
  location?: string;
  category?: string[];
  source_url?: string;
}

export interface NavigationState {
  currentPage: number;
  history: number[];
  currentSection: 'all' | 'institution' | 'category';
  currentInstitution?: string;
  currentCategory?: string;
}

export interface BookmarkData {
  institution: string;
  count: number;
  firstPageIndex: number;
}

