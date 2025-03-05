"""Calendar configurations for various sources"""

#TODO: Cozy Sundays nbqghatsg76q5hvuncn0eidonebg6pmj@import.calendar.google.com, https://lu.ma/cozy-sundays
# ICS Calendar configurations 
ICS_CALENDARS = {
   
    "walk_club": {
        "id": "http://api.lu.ma/ics/get?entity=calendar&id=cal-nIXe5Toh3KsgZWg",
        "community_id": "com_walk_club"
    },
    
    
}

# Google Calendar configurations
GOOGLE_CALENDARS = {
   
    "empire_skate": {
        "id": "i446n1u4c38ptol8a1v96foqug@group.calendar.google.com",
        "community_id": "com_empire_skate"
    },
    # "pptc": {
    #     "id": "",
    #     "community_id": "com_pptc"
    # },
    # "NYC Running Events": {
    #     "id": "6rmf6flvneht3ccnv0tjk2bi9r40tq86@import.calendar.google.com",
    #     "community_id": "com_nyc_running_events"
    # },

    
   
}

# List of available scrapers
SCRAPERS = [
    
    'google_calendar_scraper',
    'ics_calendar_scraper'
] 