import json
import logging
import numpy as np
import os
from typing import Dict, List, Tuple, Set
import torch
from transformers import BertTokenizer, BertModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Define categories for academic events
CATEGORIES = {
    "lectures_seminars": {
        "name": "Lectures & Seminars",
        "subcategories": [
            "lectures",
            "seminars",
            "guest_lectures",
            "distinguished_lectures",
            "research_seminars",
            "colloquia"
        ],
        "keywords": [
            "lecture", "seminar", "talk", "speaker", "guest lecturer", 
            "distinguished speaker", "academic talk", "faculty presentation"
        ]
    },
    "conferences_symposia": {
        "name": "Conferences & Symposia",
        "subcategories": [
            "conferences",
            "symposia",
            "congresses",
            "forums",
            "summits",
            "conventions"
        ],
        "keywords": [
            "conference", "symposium", "congress", "forum", "summit", 
            "convention", "academic meeting", "scholarly gathering"
        ]
    },
    "workshops_trainings": {
        "name": "Workshops & Trainings",
        "subcategories": [
            "workshops",
            "trainings",
            "masterclasses",
            "tutorials",
            "hands_on_sessions",
            "skill_development"
        ],
        "keywords": [
            "workshop", "training", "masterclass", "tutorial", "hands-on", 
            "skill development", "practical session", "interactive learning"
        ]
    },
    "panel_discussions": {
        "name": "Panel Discussions & Debates",
        "subcategories": [
            "panel_discussions",
            "debates",
            "roundtables",
            "forums",
            "town_halls",
            "dialogues"
        ],
        "keywords": [
            "panel", "discussion", "debate", "roundtable", "forum", "town hall", 
            "dialogue", "expert panel", "academic debate"
        ]
    },
    "research_presentations": {
        "name": "Research Presentations",
        "subcategories": [
            "research_presentations",
            "paper_presentations",
            "poster_sessions",
            "research_showcases",
            "dissertation_defenses",
            "thesis_presentations"
        ],
        "keywords": [
            "research", "presentation", "paper", "poster", "showcase", 
            "dissertation", "thesis", "defense", "academic research"
        ]
    },
    "performances_exhibitions": {
        "name": "Performances & Exhibitions",
        "subcategories": [
            "concerts",
            "recitals",
            "plays",
            "dance_performances",
            "art_exhibitions",
            "film_screenings",
            "literary_readings"
        ],
        "keywords": [
            "concert", "recital", "play", "dance", "exhibition", "art", 
            "film", "screening", "literary", "reading", "performance"
        ]
    },
    "student_activities": {
        "name": "Student Activities & Organizations",
        "subcategories": [
            "club_meetings",
            "student_government",
            "social_events",
            "cultural_celebrations",
            "student_competitions",
            "volunteer_activities"
        ],
        "keywords": [
            "student", "club", "organization", "meeting", "social", "cultural", 
            "celebration", "competition", "volunteer", "student-led"
        ]
    },
    "academic_ceremonies": {
        "name": "Academic Ceremonies & Events",
        "subcategories": [
            "commencement",
            "convocation",
            "graduation",
            "awards_ceremonies",
            "honor_society_inductions",
            "academic_celebrations"
        ],
        "keywords": [
            "ceremony", "commencement", "convocation", "graduation", "awards", 
            "honors", "induction", "academic celebration", "recognition"
        ]
    }
}

def load_auxiliary_data():
    """Load university community and location data for enhanced categorization"""
    communities = {}
    locations = {}
    
    try:
        with open('academic/data/university_communities.json', 'r', encoding='utf-8') as f:
            communities_data = json.load(f)
            communities = {com['id']: com for com in communities_data.get('communities', [])}
            
        with open('academic/data/university_locations.json', 'r', encoding='utf-8') as f:
            locations_data = json.load(f)
            locations = {loc['id']: loc for loc in locations_data.get('locations', [])}
    except Exception as e:
        logging.warning(f"Could not load auxiliary data: {str(e)}")
    
    return communities, locations

class EventCategorizer:
    # Define category mappings as a class variable
    CATEGORY_MAP = {
        # Lectures & Seminars
        "Lecture": "lectures_seminars",
        "Seminar": "lectures_seminars",
        "Guest Lecture": "lectures_seminars",
        "Distinguished Lecture": "lectures_seminars",
        "Research Seminar": "lectures_seminars",
        "Colloquium": "lectures_seminars",
        
        # Conferences & Symposia
        "Conference": "conferences_symposia",
        "Symposium": "conferences_symposia",
        "Congress": "conferences_symposia",
        "Forum": "conferences_symposia",
        "Summit": "conferences_symposia",
        "Convention": "conferences_symposia",
        
        # Workshops & Trainings
        "Workshop": "workshops_trainings",
        "Training": "workshops_trainings",
        "Masterclass": "workshops_trainings",
        "Tutorial": "workshops_trainings",
        "Hands-on Session": "workshops_trainings",
        "Skill Development": "workshops_trainings",
        
        # Panel Discussions & Debates
        "Panel Discussion": "panel_discussions",
        "Debate": "panel_discussions",
        "Roundtable": "panel_discussions",
        "Forum": "panel_discussions",
        "Town Hall": "panel_discussions",
        "Dialogue": "panel_discussions",
        
        # Research Presentations
        "Research Presentation": "research_presentations",
        "Paper Presentation": "research_presentations",
        "Poster Session": "research_presentations",
        "Research Showcase": "research_presentations",
        "Dissertation Defense": "research_presentations",
        "Thesis Presentation": "research_presentations",
        
        # Performances & Exhibitions
        "Concert": "performances_exhibitions",
        "Recital": "performances_exhibitions",
        "Play": "performances_exhibitions",
        "Dance Performance": "performances_exhibitions",
        "Art Exhibition": "performances_exhibitions",
        "Film Screening": "performances_exhibitions",
        "Literary Reading": "performances_exhibitions",
        
        # Student Activities
        "Club Meeting": "student_activities",
        "Student Government": "student_activities",
        "Social Event": "student_activities",
        "Cultural Celebration": "student_activities",
        "Student Competition": "student_activities",
        "Volunteer Activity": "student_activities",
        
        # Academic Ceremonies
        "Commencement": "academic_ceremonies",
        "Convocation": "academic_ceremonies",
        "Graduation": "academic_ceremonies",
        "Awards Ceremony": "academic_ceremonies",
        "Honor Society Induction": "academic_ceremonies",
        "Academic Celebration": "academic_ceremonies"
    }
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased').to(self.device)
        self.model.eval()
        
        # Load community and location data
        self.communities, self.locations = load_auxiliary_data()
        
        # Pre-compute category embeddings
        self.category_embeddings = {}
        for category, data in CATEGORIES.items():
            # Combine keywords and subcategories for better embeddings
            all_terms = data['keywords'] + [sub.replace('_', ' ') for sub in data['subcategories']]
            self.category_embeddings[category] = self._get_text_embedding(
                ' '.join(all_terms)
            )
            
        # Build community category mappings
        self.community_category_mappings = self._build_community_category_mappings()
    
    def _build_community_category_mappings(self):
        """Build mappings between university community categories/tags and our event categories"""
        mappings = {}
        
        for community_id, community in self.communities.items():
            community_mappings = set()
            
            # Map based on community type
            community_type = community.get('type', '')
            if 'Academic' in community_type:
                community_mappings.add('lectures_seminars')
                community_mappings.add('research_presentations')
            
            # Map based on community category
            categories = community.get('category', [])
            for category in categories:
                if category == 'Education' or category == 'Research' or category == 'Academic':
                    community_mappings.add('lectures_seminars')
                    community_mappings.add('research_presentations')
                if category == 'Law':
                    community_mappings.add('panel_discussions')
                if category == 'Engineering' or category == 'Technology':
                    community_mappings.add('workshops_trainings')
                if category == 'Public Policy' or category == 'International Affairs':
                    community_mappings.add('conferences_symposia')
                    community_mappings.add('panel_discussions')
                if category == 'Liberal Arts' or category == 'Sciences' or category == 'Humanities':
                    community_mappings.add('lectures_seminars')
                    community_mappings.add('performances_exhibitions')
                if category == 'Mathematics' or category == 'Computer Science':
                    community_mappings.add('research_presentations')
                    community_mappings.add('workshops_trainings')
            
            # Map based on community tags
            tags = community.get('tags', [])
            for tag in tags:
                if tag in ['education', 'research', 'academic', 'ivy league']:
                    community_mappings.add('lectures_seminars')
                    community_mappings.add('research_presentations')
                if tag in ['law', 'legal education']:
                    community_mappings.add('panel_discussions')
                if tag in ['engineering', 'technology', 'innovation']:
                    community_mappings.add('workshops_trainings')
                if tag in ['public policy', 'international affairs', 'global policy']:
                    community_mappings.add('conferences_symposia')
                    community_mappings.add('panel_discussions')
                if tag in ['liberal arts', 'sciences', 'humanities']:
                    community_mappings.add('lectures_seminars')
                    community_mappings.add('performances_exhibitions')
                if tag in ['mathematics', 'computer science']:
                    community_mappings.add('research_presentations')
                    community_mappings.add('workshops_trainings')
            
            mappings[community_id] = list(community_mappings)
            
        return mappings
    
    def _get_community_categories(self, event: Dict) -> List[str]:
        """Get relevant categories based on community information"""
        community_id = event.get('community_id')
        if not community_id or community_id not in self.communities:
            return []
            
        # Get pre-mapped categories for this community
        base_categories = self.community_category_mappings.get(community_id, [])
        
        # Get community data
        community = self.communities[community_id]
        
        # Add categories based on community type
        if community.get('type') == 'Academic Community':
            base_categories.append('lectures_seminars')
        
        return list(set(base_categories))  # Remove duplicates
    
    def _get_text_embedding(self, text: str) -> np.ndarray:
        """Get BERT embedding for a text string"""
        with torch.no_grad():
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            outputs = self.model(**inputs)
            # Use CLS token embedding as text representation
            embedding = outputs.last_hidden_state[0][0].cpu().numpy()
            
        return embedding
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        # Convert to native Python float and round to 2 decimal places
        return round(float(similarity), 2)
    
    def _get_community_boost(self, event: Dict, category: str, similarity: float) -> float:
        """Calculate confidence boost based on community data"""
        boost = 0.0
        
        # Updated to use community_id instead of communityId
        community_id = event.get('community_id')
        if not community_id or community_id not in self.communities:
            return boost
            
        community = self.communities[community_id]
        
        # Boost based on community type
        if community.get('type') == 'Academic Community':
            if category in ['lectures_seminars', 'research_presentations']:
                boost += 0.1
        
        # Boost based on specific community
        if 'Law' in community.get('name', '') and category == 'panel_discussions':
            boost += 0.15
        if 'Engineering' in community.get('name', '') and category == 'workshops_trainings':
            boost += 0.15
        if 'SIPA' in community.get('name', '') and category in ['conferences_symposia', 'panel_discussions']:
            boost += 0.15
        if 'Arts' in community.get('name', '') and category == 'performances_exhibitions':
            boost += 0.15
        
        return boost
    
    def _get_location_boost(self, event: Dict, category: str, similarity: float) -> float:
        """Calculate confidence boost based on location data"""
        boost = 0.0
        
        # Updated to use location_id instead of locationId
        location_id = event.get('location_id')
        if not location_id or location_id not in self.locations:
            return boost
            
        location = self.locations[location_id]
        
        # Boost based on location type
        if location.get('type') == 'University Building':
            if 'Law' in location.get('name', '') and category == 'panel_discussions':
                boost += 0.1
            if 'Engineering' in location.get('name', '') and category == 'workshops_trainings':
                boost += 0.1
            if 'SIPA' in location.get('name', '') and category in ['conferences_symposia', 'panel_discussions']:
                boost += 0.1
            if 'Kimmel' in location.get('name', '') and category in ['student_activities', 'performances_exhibitions']:
                boost += 0.1
            if 'Library' in location.get('name', '') and category in ['lectures_seminars', 'research_presentations']:
                boost += 0.05
        
        # Check venue information in metadata if available
        metadata = event.get('metadata', {})
        venue = metadata.get('venue', {})
        venue_name = venue.get('name', '')
        
        if 'Library' in venue_name and category in ['lectures_seminars', 'research_presentations']:
            boost += 0.05
        if 'Auditorium' in venue_name and category in ['lectures_seminars', 'performances_exhibitions']:
            boost += 0.05
        if 'Lab' in venue_name and category in ['workshops_trainings', 'research_presentations']:
            boost += 0.05
        
        return boost
    
    def categorize_event(self, event: Dict) -> List[Tuple[str, float]]:
        """Categorize an event using both community info and content analysis"""
        # Get community-based categories first
        community_categories = self._get_community_categories(event)
        
        # Combine relevant text fields with different weights
        event_text = (
            f"{event.get('name', '')} " 
            f"{' '.join(event.get('tags', []) or [])} " 
            f"{event.get('type', '')} " * 2  # Weight event type
        )
        
        # Add category information if available
        if isinstance(event.get('category'), list):
            event_text += f"{' '.join(str(cat) for cat in event.get('category', []))} "
        
        # Add description
        event_text += f"{event.get('description', '')} "
        
        # Add metadata tags if available
        metadata = event.get('metadata', {})
        if isinstance(metadata, dict) and 'additional_info' in metadata and 'tags' in metadata['additional_info']:
            event_text += f"{' '.join(metadata['additional_info'].get('tags', []))} "
        
        # Add organizer information if available
        if isinstance(metadata, dict) and 'organizer' in metadata and 'name' in metadata['organizer']:
            event_text += f"{metadata['organizer'].get('name', '')} "
        
        # Add venue information if available
        if isinstance(metadata, dict) and 'venue' in metadata and 'name' in metadata['venue']:
            event_text += f"{metadata['venue'].get('name', '')} "
        
        # Get event embedding
        event_embedding = self._get_text_embedding(event_text)
        
        # Calculate similarity with each category
        similarities = []
        for category, embedding in self.category_embeddings.items():
            # Get base similarity
            similarity = self._cosine_similarity(event_embedding, embedding)
            
            # Boost score if category was suggested by community info
            if category in community_categories:
                similarity = min(round(similarity * 1.5, 2), 1.0)  # 50% boost, capped at 1.0
            
            # Apply community-based boost
            community_boost = self._get_community_boost(event, category, similarity)
            
            # Apply location-based boost
            location_boost = self._get_location_boost(event, category, similarity)
            
            # Combine base similarity with boosts
            final_similarity = min(round(similarity + community_boost + location_boost, 2), 1.0)
            
            similarities.append((category, final_similarity))
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Filter out low confidence matches
        return [(cat, conf) for cat, conf in similarities if conf > 0.6]  # Lowered threshold for better coverage

def load_events(file_path: str) -> List[Dict]:
    """Load events from a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Check if the data is directly a list of events or has an 'events' key
            if isinstance(data, list):
                return data
            elif 'events' in data:
                return data.get('events', [])
            else:
                # Try to find events in the structure
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        if any(k in value[0] for k in ['name', 'title', 'event_name']):
                            return value
                logging.warning(f"Could not find events in {file_path}")
                return []
    except Exception as e:
        logging.error(f"Error loading events: {str(e)}")
        return []

def save_categorized_events(events: List[Dict], output_path: str):
    """Save categorized events to a JSON file"""
    try:
        # Convert any numpy values to Python native types
        for event in events:
            if 'categoryConfidence' in event:
                # Ensure all values are native Python types and round to 2 decimal places
                event['categoryConfidence'] = {
                    str(cat): round(float(conf), 2) 
                    for cat, conf in event['categoryConfidence'].items()
                }
                
            # Clean up categories to ensure they're just the category IDs
            if 'categories' in event:
                # Ensure categories are strings and remove any that are malformed
                cleaned_categories = []
                for cat in event['categories']:
                    # If it's a string and in our CATEGORIES dict, keep it
                    if isinstance(cat, str) and cat in CATEGORIES:
                        cleaned_categories.append(cat)
                    # If it's a dict or malformed string, try to extract the ID
                    elif isinstance(cat, (dict, str)):
                        try:
                            if isinstance(cat, dict) and 'id' in cat:
                                if cat['id'] in CATEGORIES:
                                    cleaned_categories.append(cat['id'])
                            elif isinstance(cat, str):
                                # Try to find a matching category ID
                                for category_id in CATEGORIES:
                                    if category_id in cat or CATEGORIES[category_id]['name'] in cat:
                                        cleaned_categories.append(category_id)
                                        break
                        except:
                            continue
                
                # Remove duplicates while preserving order
                event['categories'] = list(dict.fromkeys(cleaned_categories))
                
                # Map academic categories to standard model categories
                mapped_categories = set()
                for cat in event['categories']:
                    if cat == 'lectures_seminars' or cat == 'conferences_symposia':
                        mapped_categories.add('education')
                    elif cat == 'research_presentations':
                        mapped_categories.add('science')
                    elif cat == 'performances_exhibitions':
                        mapped_categories.add('arts')
                    elif cat == 'student_activities':
                        mapped_categories.add('social')
                    elif cat == 'workshops_trainings':
                        mapped_categories.add('education')
                    elif cat == 'panel_discussions':
                        mapped_categories.add('education')
                    elif cat == 'academic_ceremonies':
                        mapped_categories.add('education')
                    else:
                        mapped_categories.add('other')
                
                # Add mapped categories to the event
                event['mappedCategories'] = list(mapped_categories)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({'events': events}, f, indent=2)
        logging.info(f"Saved categorized events to {output_path}")
    except Exception as e:
        logging.error(f"Error saving categorized events: {str(e)}")
        raise

def create_sample_event_file():
    """Create a sample event file for testing if all_events_combined.json doesn't exist"""
    sample_events = [
        {
            "id": "evt_sample_001",
            "name": "Machine Learning in Healthcare: Current Applications and Future Directions",
            "type": "Lecture",
            "location_id": "loc_columbia_main",
            "community_id": "com_columbia_general",
            "description": "This lecture explores the current applications of machine learning in healthcare and discusses future directions for research and implementation.",
            "start_date": "2025-04-15T14:00:00+00:00",
            "end_date": "2025-04-15T16:00:00+00:00",
            "category": ["TECHNOLOGY", "HEALTH"],
            "price": {
                "amount": 0.0,
                "type": "free"
            },
            "status": "scheduled",
            "registration_required": False,
            "tags": ["AI", "Machine Learning", "Healthcare", "Lecture"],
            "metadata": {
                "source_url": "https://events.columbia.edu/sample",
                "source_name": "Columbia University",
                "venue": {
                    "name": "Pupin Hall Auditorium",
                    "type": "venue"
                },
                "organizer": {
                    "name": "Department of Computer Science",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": "Computer Science",
                    "tags": ["AI", "Machine Learning", "Healthcare", "Lecture"]
                }
            }
        },
        {
            "id": "evt_sample_002",
            "name": "Constitutional Law Symposium: First Amendment in the Digital Age",
            "type": "Symposium",
            "location_id": "loc_columbia_law",
            "community_id": "com_columbia_law",
            "description": "A symposium discussing the challenges and interpretations of First Amendment rights in the context of digital communication and social media platforms.",
            "start_date": "2025-05-10T09:00:00+00:00",
            "end_date": "2025-05-11T17:00:00+00:00",
            "category": ["LAW", "TECHNOLOGY"],
            "price": {
                "amount": 25.0,
                "type": "paid",
                "details": "Free for students with ID"
            },
            "status": "scheduled",
            "registration_required": True,
            "tags": ["Law", "First Amendment", "Digital Rights"],
            "metadata": {
                "source_url": "https://law.columbia.edu/sample",
                "source_name": "Columbia Law School",
                "venue": {
                    "name": "Columbia Law School, Jerome Greene Hall",
                    "type": "venue"
                },
                "organizer": {
                    "name": "Columbia Law School",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": "Law",
                    "tags": ["Constitutional Law", "First Amendment", "Digital Rights", "Symposium"]
                }
            }
        },
        {
            "id": "evt_sample_003",
            "name": "Global Policy Workshop: Climate Change Adaptation Strategies",
            "type": "Workshop",
            "location_id": "loc_columbia_sipa",
            "community_id": "com_columbia_sipa",
            "description": "A hands-on workshop focused on developing climate change adaptation strategies for vulnerable communities around the world.",
            "start_date": "2025-06-05T10:00:00+00:00",
            "end_date": "2025-06-05T16:00:00+00:00",
            "category": ["POLICY", "ENVIRONMENT"],
            "price": {
                "amount": 0.0,
                "type": "free"
            },
            "status": "scheduled",
            "registration_required": True,
            "tags": ["Climate Change", "Policy", "Workshop"],
            "metadata": {
                "source_url": "https://sipa.columbia.edu/sample",
                "source_name": "Columbia SIPA",
                "venue": {
                    "name": "SIPA Building, Room 1501",
                    "type": "venue"
                },
                "organizer": {
                    "name": "School of International and Public Affairs",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": "International and Public Affairs",
                    "tags": ["Climate Change", "Policy", "Global Affairs", "Workshop"]
                }
            }
        },
        {
            "id": "evt_sample_004",
            "name": "Student Jazz Ensemble Spring Concert",
            "type": "Concert",
            "location_id": "loc_nyu_kimmel",
            "community_id": "com_nyu_general",
            "description": "The NYU Student Jazz Ensemble presents their annual spring concert featuring original compositions and jazz standards.",
            "start_date": "2025-04-20T19:00:00+00:00",
            "end_date": "2025-04-20T21:00:00+00:00",
            "category": ["ARTS", "MUSIC"],
            "price": {
                "amount": 10.0,
                "type": "paid",
                "details": "Free for NYU students"
            },
            "status": "scheduled",
            "registration_required": False,
            "tags": ["Jazz", "Concert", "Music"],
            "metadata": {
                "source_url": "https://events.nyu.edu/sample",
                "source_name": "NYU Events",
                "venue": {
                    "name": "Kimmel Center, Eisner & Lubin Auditorium",
                    "type": "venue"
                },
                "organizer": {
                    "name": "NYU Steinhardt School of Culture, Education, and Human Development",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": "Music",
                    "tags": ["Jazz", "Concert", "Student Performance", "Music"]
                }
            }
        },
        {
            "id": "evt_sample_005",
            "name": "Quantum Computing Research Presentation",
            "type": "Research Presentation",
            "location_id": "loc_nyu_courant",
            "community_id": "com_nyu_courant",
            "description": "Presentation of recent breakthroughs in quantum computing algorithms and their potential applications in cryptography and optimization problems.",
            "start_date": "2025-05-15T15:00:00+00:00",
            "end_date": "2025-05-15T17:00:00+00:00",
            "category": ["TECHNOLOGY", "RESEARCH"],
            "price": {
                "amount": 0.0,
                "type": "free"
            },
            "status": "scheduled",
            "registration_required": True,
            "tags": ["Quantum Computing", "Research", "Computer Science"],
            "metadata": {
                "source_url": "https://cims.nyu.edu/sample",
                "source_name": "NYU Courant",
                "venue": {
                    "name": "Warren Weaver Hall, Room 109",
                    "type": "venue"
                },
                "organizer": {
                    "name": "Courant Institute of Mathematical Sciences",
                    "type": "organizer"
                },
                "additional_info": {
                    "department": "Computer Science",
                    "tags": ["Quantum Computing", "Research", "Computer Science", "Mathematics"]
                }
            }
        }
    ]
    
    try:
        os.makedirs('academic/events', exist_ok=True)
        with open('academic/events/all_events_combined.json', 'w', encoding='utf-8') as f:
            json.dump(sample_events, f, indent=2)
        logging.info("Created sample events file at academic/events/all_events_combined.json")
        return sample_events
    except Exception as e:
        logging.error(f"Error creating sample events file: {str(e)}")
        return []

def filter_and_separate_events(events: List[Dict]) -> Dict[str, List[Dict]]:
    """Filter events and separate them into categories"""
    result = {
        "combined": [],  # All filtered events combined
        "lectures": [],  # Lecture/seminar events
        "performances": [],  # Free performance events
        "other": []  # Events that didn't match our filter criteria
    }
    
    filtered_count = 0
    lecture_count = 0
    performance_count = 0
    other_count = 0
    
    # Non-academic keywords - events with these in the title or description should not be considered academic lectures
    non_academic_keywords = [
        "information session", "info session", "advocate", "well-being", "wellness", 
        "orientation", "recruitment", "recruiting", "information meeting", "office hours",
        "group meeting", "club meeting", "committee meeting", "social", "networking", 
        "meetup", "meet-up", "meet up", "mixer", "tea", "coffee", "lunch", "dinner", 
        "breakfast", "reception", "celebration", "party", "graduation", "ceremony", 
        "career fair", "job fair", "employment", "volunteer", "grand rounds",
        "mental health", "emotional health", "well-being resource", "wellness resource",
        "student organization", "student club", "student group", "safe zone", 
        "training session", "support", "solidarity", "ally", "advocacy training",
        "awareness training", "identity", "resource sharing", "diversity training"
    ]
    
    # Positive academic indicators - events with these in title/description are more likely to be academic
    academic_indicators = [
        "lecture", "seminar", "colloquium", "symposium", "conference", "talk", 
        "book event", "book talk", "research", "professor", "faculty", "scholar",
        "physics", "mathematics", "computer science", "biology", "chemistry",
        "literature", "history", "philosophy", "economics", "sociology",
        "anthropology", "psychology", "political science", "linguistics",
        "astronomy", "earth science", "engineering", "archaeology", 
        "classics", "humanities", "neuroscience", "justice", "rights",
        "policy", "discussion", "panel", "author", "debate", "institute"
    ]
    
    # Exclusive performance keywords - MUST have one of these in the title to be considered a performance
    exclusive_performance_keywords = [
        "concert", "recital", "music", "musical", "theatre", "theater", 
        "performance", "dance", "symphony", "orchestra", "choir", 
        "opera", "exhibit", "exhibition", "gallery", "screening", "film",
        "play", "jazz", "band"
    ]
    
    for event in events:
        # Get event name, type, and description for analysis
        name = event.get('name', '').lower()
        event_type = event.get('type', '').lower()
        description = event.get('description', '').lower()
        text = f"{name} {description}"
        tags = event.get('tags', [])
        if isinstance(tags, list):
            tags = [tag.lower() if isinstance(tag, str) else '' for tag in tags]
        else:
            tags = []
        
        # Check for non-academic indicators
        is_non_academic = any(keyword in text for keyword in non_academic_keywords)
        is_student_related = any(term in text for term in ["student group", "student club", "student org", "student association", "well-being advocate"])
        
        # Check for academic indicators
        has_academic_indicator = any(indicator in text for indicator in academic_indicators)
        
        # Check for academic speakers - professors, researchers, etc.
        academic_speaker_indicators = ["professor", "faculty", "researcher", "scientist", "dr.", "phd", "scholar", "author"]
        has_academic_speaker = any(indicator in text for indicator in academic_speaker_indicators)
        
        # Check if this is explicitly a lecture/talk/seminar/colloquium/book event
        lecture_indicators = ["lecture", "seminar", "talk", "colloquium", "symposium", "conference", "book event", "book talk", "discussion", "panel"]
        is_explicit_lecture = any(indicator in name.lower() for indicator in lecture_indicators)
        
        # Determine if this is a genuine academic lecture - be more lenient
        is_lecture = (
            (is_explicit_lecture or has_academic_speaker or 
             (has_academic_indicator and not is_student_related)) and 
            not is_non_academic
        )
        
        # Type indicates it's an academic event
        if event_type == "seminar" or event_type == "colloquium" or event_type == "lecture":
            # Still check if it contains non-academic keywords to exclude training sessions
            if not any(keyword in text for keyword in ["safe zone", "training session", "identity", "ally", "advocacy training"]):
                is_lecture = True
        
        # STRICT performance check - must have a performance keyword in the title
        is_performance = any(keyword in name.lower() for keyword in exclusive_performance_keywords)
        
        # Double check with venue for additional confirmation
        if is_performance:
            metadata = event.get('metadata', {})
            venue_name = metadata.get('venue', {}).get('name', '').lower() if metadata else ''
            organizer_name = metadata.get('organizer', {}).get('name', '').lower() if metadata else ''
            
            # Look for artistic venues
            artistic_venues = ['theatre', 'theater', 'gallery', 'museum', 'concert hall', 'auditorium', 'recital hall'] 
            venue_confirms = any(venue in venue_name for venue in artistic_venues)
            
            # If it's not a clear performance from title + venue, require more confirmation
            if not venue_confirms:
                # Count performance terms in description
                performance_terms_in_desc = sum(1 for term in exclusive_performance_keywords if term in description.lower())
                # Only keep it as a performance if there are multiple mentions in description 
                if performance_terms_in_desc < 2:
                    is_performance = False
        
        # Check if event is free
        is_free = False
        
        # Check price dictionary
        price_info = event.get('price', {})
        if isinstance(price_info, dict):
            price_type = price_info.get('type', '').lower()
            price_amount = price_info.get('amount', 0)
            price_details = price_info.get('details', '').lower()
            
            is_free = (price_type == 'free' or 
                      price_amount == 0 or 
                      'free' in price_type or 
                      'free' in price_details)
        
        # Check metadata for price information
        if not is_free:
            metadata = event.get('metadata', {})
            if isinstance(metadata, dict):
                # Check if there's price info in metadata
                if 'price' in metadata:
                    meta_price = metadata.get('price', '')
                    if isinstance(meta_price, dict):
                        is_free = meta_price.get('type', '').lower() == 'free' or meta_price.get('amount', 0) == 0
                    elif isinstance(meta_price, str):
                        is_free = 'free' in meta_price.lower()
                
                # Check additional info
                additional_info = metadata.get('additional_info', {})
                if isinstance(additional_info, dict) and 'price' in additional_info:
                    add_price = additional_info.get('price', '')
                    if isinstance(add_price, str):
                        is_free = 'free' in add_price.lower()
                    elif isinstance(add_price, dict):
                        is_free = add_price.get('type', '').lower() == 'free' or add_price.get('amount', 0) == 0
        
        # If price info still not found, check for free keywords in description
        if not is_free:
            is_free = ('free' in description or 
                      'no charge' in description or 
                      'complimentary' in description or
                      'no admission' in description)
        
        # Add events to appropriate categories
        if is_lecture:
            event['filter_reason'] = 'lecture_seminar'
            result["lectures"].append(event)
            result["combined"].append(event)
            lecture_count += 1
            filtered_count += 1
        elif is_performance and is_free:
            event['filter_reason'] = 'free_performance'
            result["performances"].append(event)
            result["combined"].append(event)
            performance_count += 1
            filtered_count += 1
        else:
            # Keep track of other events too
            event['filter_reason'] = 'other'
            result["other"].append(event)
            other_count += 1
    
    logging.info(f"Processed {len(events)} events:")
    logging.info(f"- Lectures & Seminars: {lecture_count}")
    logging.info(f"- Free Performances: {performance_count}")
    logging.info(f"- Other (not matching filters): {other_count}")
    logging.info(f"- Total filtered events: {filtered_count}")
    
    return result

def generate_filter_report(events: List[Dict]):
    """Generate a report of filtered events by source and category"""
    sources = {}
    categories = {
        'lectures_seminars': 0,
        'performances_exhibitions': 0,
        'other': 0
    }
    
    for event in events:
        # Count by source
        source = event.get('source', 'unknown')
        if source not in sources:
            sources[source] = {
                'total': 0,
                'lectures': 0,
                'performances': 0
            }
        
        sources[source]['total'] += 1
        
        # Count by filter reason
        filter_reason = event.get('filter_reason', '')
        
        if filter_reason == 'lecture_seminar':
            categories['lectures_seminars'] += 1
            sources[source]['lectures'] += 1
        elif filter_reason == 'free_performance':
            categories['performances_exhibitions'] += 1
            sources[source]['performances'] += 1
        else:
            categories['other'] += 1
    
    # Print report
    logging.info("\n=== FILTERED EVENTS REPORT ===")
    logging.info(f"Total events: {len(events)}")
    logging.info(f"Lectures & Seminars: {categories['lectures_seminars']}")
    logging.info(f"Free Performances & Exhibitions: {categories['performances_exhibitions']}")
    logging.info(f"Other: {categories['other']}")
    
    logging.info("\nEvents by source:")
    for source, counts in sorted(sources.items(), key=lambda x: x[1]['total'], reverse=True):
        logging.info(f"  {source}: {counts['total']} total ({counts['lectures']} lectures, {counts['performances']} performances)")

def main():
    # Create necessary directories
    os.makedirs('academic/data', exist_ok=True)
    os.makedirs('academic/events', exist_ok=True)
    
    # Check if all_events_combined.json exists
    events_file_path = 'academic/events/all_events_combined.json'
    if not os.path.exists(events_file_path):
        logging.warning(f"{events_file_path} not found. Creating sample events file.")
        events = create_sample_event_file()
    else:
        # Load events from all_events_combined.json
        events = load_events(events_file_path)
        if not events:
            logging.warning("No events found in all_events_combined.json. Creating sample events file.")
            events = create_sample_event_file()
    
    if not events:
        logging.error("Failed to load or create events. Exiting.")
        return
    
    # Initialize categorizer
    categorizer = EventCategorizer()
    
    # Categorize events
    categorized_count = 0
    for event in events:
        try:
            # Get categories with confidence scores
            categories_with_scores = categorizer.categorize_event(event)
            
            # Add categories to event
            event['categories'] = [cat for cat, _ in categories_with_scores]
            event['categoryConfidence'] = {cat: score for cat, score in categories_with_scores}
            categorized_count += 1
        except Exception as e:
            logging.error(f"Error categorizing event {event.get('id', 'unknown')}: {str(e)}")
    
    # Filter and separate events into categories
    categorized_events = filter_and_separate_events(events)
    
    # Generate report for filtered events
    generate_filter_report(categorized_events['combined'])
    
    # Save each category to a separate file
    save_categorized_events(categorized_events['combined'], 'academic/data/events.json')
    save_categorized_events(categorized_events['lectures'], 'academic/data/lecture_events.json')
    save_categorized_events(categorized_events['performances'], 'academic/data/performance_events.json')
    save_categorized_events(categorized_events['other'], 'academic/data/other_events.json')
    
    logging.info(f"Categorized {categorized_count} out of {len(events)} events")
    logging.info(f"Saved {len(categorized_events['combined'])} filtered events (combined)")
    logging.info(f"Saved {len(categorized_events['lectures'])} lecture events")
    logging.info(f"Saved {len(categorized_events['performances'])} performance events")
    logging.info(f"Saved {len(categorized_events['other'])} other events")

if __name__ == "__main__":
    main()