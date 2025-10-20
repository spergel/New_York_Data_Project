"""
Centralized category utilities for academic event scrapers.
Provides standardized categorization logic and category definitions.
"""

# Standard category definitions
STANDARD_CATEGORIES = {
    'EDUCATION': {
        'name': 'Education',
        'keywords': [
            'education', 'academic', 'university', 'college', 'school', 'learning',
            'teaching', 'course', 'seminar', 'lecture', 'workshop', 'conference',
            'symposium', 'colloquium', 'presentation', 'talk', 'discussion'
        ]
    },
    'SCIENCE': {
        'name': 'Science',
        'keywords': [
            'science', 'research', 'physics', 'chemistry', 'biology', 'mathematics',
            'math', 'statistics', 'data', 'computation', 'computational', 'neuroscience',
            'engineering', 'technology', 'quantum', 'mechanics', 'theorem', 'proof',
            'algorithm', 'model', 'theory', 'experiment', 'laboratory', 'analysis'
        ]
    },
    'ARTS': {
        'name': 'Arts',
        'keywords': [
            'art', 'arts', 'music', 'theater', 'theatre', 'dance', 'performance',
            'exhibition', 'gallery', 'museum', 'concert', 'recital', 'opera',
            'ballet', 'choreography', 'film', 'cinema', 'visual', 'creative',
            'design', 'architecture', 'photography', 'sculpture', 'painting'
        ]
    },
    'HEALTH': {
        'name': 'Health & Medicine',
        'keywords': [
            'health', 'medical', 'medicine', 'clinical', 'patient', 'treatment',
            'therapy', 'diagnosis', 'disease', 'wellness', 'public health',
            'biomedical', 'pharmaceutical', 'nursing', 'doctor', 'hospital',
            'clinic', 'mental health', 'psychology', 'neuroscience'
        ]
    },
    'TECH': {
        'name': 'Technology',
        'keywords': [
            'technology', 'computer', 'software', 'programming', 'coding',
            'development', 'engineering', 'ai', 'artificial intelligence',
            'machine learning', 'data science', 'cybersecurity', 'blockchain',
            'internet', 'digital', 'automation', 'robotics', 'hardware'
        ]
    },
    'SOCIAL': {
        'name': 'Social & Community',
        'keywords': [
            'social', 'community', 'networking', 'meetup', 'club', 'society',
            'organization', 'volunteer', 'activism', 'diversity', 'inclusion',
            'equity', 'justice', 'policy', 'governance', 'sustainability'
        ]
    },
    'BUSINESS': {
        'name': 'Business & Finance',
        'keywords': [
            'business', 'finance', 'economics', 'marketing', 'management',
            'entrepreneurship', 'startup', 'venture', 'investment', 'corporate',
            'industry', 'commerce', 'trade', 'leadership', 'strategy'
        ]
    },
    'CULTURE': {
        'name': 'Culture & Society',
        'keywords': [
            'culture', 'cultural', 'society', 'history', 'heritage', 'tradition',
            'language', 'literature', 'philosophy', 'ethics', 'religion',
            'anthropology', 'sociology', 'politics', 'international'
        ]
    }
}

def categorize_by_keywords(text, confidence_threshold=0.1):
    """
    Categorize text based on keyword matching.

    Args:
        text: Text to analyze (title + description)
        confidence_threshold: Minimum confidence score to include category

    Returns:
        List of category strings
    """
    if not text:
        return []

    text_lower = text.lower()
    categories = set()
    scores = {}

    # Calculate scores for each category
    for category, data in STANDARD_CATEGORIES.items():
        score = 0
        keywords = data['keywords']

        for keyword in keywords:
            if keyword in text_lower:
                # Give higher weight to longer, more specific keywords
                weight = len(keyword) / 10  # Normalize by approximate word length
                score += weight

        # Normalize by text length to avoid bias toward longer texts
        normalized_score = score / max(len(text.split()), 1)
        scores[category] = normalized_score

        if normalized_score >= confidence_threshold:
            categories.add(category)

    # Always include EDUCATION for academic events unless explicitly categorized
    if not categories and any(term in text_lower for term in ['university', 'college', 'academic', 'education']):
        categories.add('EDUCATION')

    return sorted(list(categories))

def get_category_mapping():
    """
    Get a simple mapping from common terms to standard categories.
    Useful for scrapers that have predefined tags/categories.
    """
    return {
        # Science & Tech
        'science': 'SCIENCE',
        'physics': 'SCIENCE',
        'chemistry': 'SCIENCE',
        'biology': 'SCIENCE',
        'mathematics': 'SCIENCE',
        'math': 'SCIENCE',
        'statistics': 'SCIENCE',
        'computer science': 'TECH',
        'engineering': 'TECH',
        'technology': 'TECH',
        'ai': 'TECH',
        'artificial intelligence': 'TECH',
        'machine learning': 'TECH',
        'data science': 'TECH',

        # Arts & Culture
        'art': 'ARTS',
        'arts': 'ARTS',
        'music': 'ARTS',
        'theater': 'ARTS',
        'theatre': 'ARTS',
        'dance': 'ARTS',
        'performance': 'ARTS',
        'film': 'ARTS',
        'visual arts': 'ARTS',

        # Health & Medicine
        'health': 'HEALTH',
        'medical': 'HEALTH',
        'medicine': 'HEALTH',
        'clinical': 'HEALTH',
        'biomedical': 'HEALTH',
        'neuroscience': 'HEALTH',
        'psychology': 'HEALTH',

        # Business & Social
        'business': 'BUSINESS',
        'economics': 'BUSINESS',
        'finance': 'BUSINESS',
        'management': 'BUSINESS',
        'social': 'SOCIAL',
        'community': 'SOCIAL',
        'policy': 'SOCIAL',
        'politics': 'SOCIAL',

        # Education (fallback)
        'education': 'EDUCATION',
        'academic': 'EDUCATION',
        'teaching': 'EDUCATION',
        'learning': 'EDUCATION'
    }

def map_tags_to_categories(tags):
    """
    Map a list of tags to standard categories.

    Args:
        tags: List of tag strings

    Returns:
        List of standard category strings
    """
    if not tags:
        return []

    categories = set()
    mapping = get_category_mapping()

    for tag in tags:
        tag_lower = tag.lower()
        for key, category in mapping.items():
            if key in tag_lower:
                categories.add(category)

    return sorted(list(categories))

def determine_categories(event_data, method='auto'):
    """
    Main categorization function that can use different methods.

    Args:
        event_data: Dictionary with event information (title, description, tags, etc.)
        method: 'auto' (keyword-based), 'tags' (tag mapping), or 'hybrid'

    Returns:
        List of category strings
    """
    categories = set()

    # Get text content for analysis
    title = event_data.get('title', '')
    description = event_data.get('description', '')
    tags = event_data.get('tags', []) or event_data.get('categories', [])

    text_content = f"{title} {description}".strip()

    if method == 'tags' and tags:
        # Use tag mapping
        categories.update(map_tags_to_categories(tags))
    elif method == 'hybrid':
        # Use both keyword analysis and tag mapping
        categories.update(categorize_by_keywords(text_content))
        if tags:
            categories.update(map_tags_to_categories(tags))
    else:
        # Default: keyword-based analysis
        categories.update(categorize_by_keywords(text_content))

    # Ensure we have at least EDUCATION for academic events
    if not categories and any(term in text_content.lower() for term in ['university', 'college', 'academic']):
        categories.add('EDUCATION')

    # If still no categories, default to EDUCATION
    if not categories:
        categories.add('EDUCATION')

    return sorted(list(categories))

