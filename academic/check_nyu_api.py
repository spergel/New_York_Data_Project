import requests
import json

NYU_API_URL = "https://events.nyu.edu/live/calendar/view/all/categories/Open%20to%20the%20Public?user_tz=America%2FDetroit&template_vars=id,href,title,image_src,date_title,time,title_link,location,latitude,longitude,summary,is_canceled,repeats,is_multi_day,is_first_multi_day,multi_day_span,tag_classes,category_classes,is_online,has_map&syntax=%3Cwidget%20type%3D%22events_calendar%22%3E%3Carg%20id%3D%22modular_true%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22mini_cal_heat_map%22%3Efalse%3C%2Farg%3E%3Carg%20id%3D%22search_all_events_only%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22search_all_events_only%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22include_featured_content%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22thumb_width%22%3E430%3C%2Farg%3E%3Carg%20id%3D%22thumb_height%22%3E300%3C%2Farg%3E%3Carg%20id%3D%22hide_repeats%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22show_groups%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22show_locations%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22show_tags%22%3Etrue%3C%2Farg%3E%3Carg%20id%3D%22feed_base_path%22%3Ehttp%3A%2F%2Fwww.nyu.edu%2Ffeeds%2Fevents%3C%2Farg%3E%3C%2Fwidget%3E"

resp = requests.get(NYU_API_URL)
data = resp.json()

print(f"Total events: {data.get('event_count', 0)}")
print(f"Pages: {data.get('page', 1)}")
print(f"Per page: {data.get('per_page', 50)}")
print(f"Date keys: {list(data.get('events', {}).keys())[:5]}")

total_events = 0
for date_key, day_events in data.get('events', {}).items():
    if isinstance(day_events, list):
        total_events += len(day_events)
        print(f"Date {date_key}: {len(day_events)} events")

print(f"Total events in response: {total_events}")

# Show some event titles
count = 0
for date_key, day_events in data.get('events', {}).items():
    if isinstance(day_events, list):
        for event in day_events:
            if count < 10:
                print(f"Event {count+1}: {event.get('title', 'No title')}")
                count += 1
            else:
                break
    if count >= 10:
        break
