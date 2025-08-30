// Cloudflare Worker for NYC Academic Events API
// This worker serves academic events from the JSON data

// CORS headers for cross-origin requests
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

// Academic events data (converted from scraped data)
const academicEvents = [
  {
    "id": 1,
    "event_id": "evt_columbia_classics_e69dca8f92",
    "name": "Classics Departmental Lecture Series: Stephen Harrison (University of Oxford)",
    "description": "Tuesday, September 9, 2025 4:10 PM 6:00 PM 16:10 18:00 Department of Classics at Columbia University in the City of New York (map) Google Calendar ICS View Event \u2192",
    "start_date": "2025-09-09",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 2,
    "event_id": "evt_columbia_classics_3511b7c2ea",
    "name": "University Seminar in Classical Civilization - Tim Whitmarsh (Oxford)",
    "description": "Thursday, October 16, 2025 7:30 PM 9:00 PM 19:30 21:00 Faculty House (map) Google Calendar ICS View Event \u2192",
    "start_date": "2025-10-16",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 3,
    "event_id": "evt_columbia_classics_16ae6111b0",
    "name": "Classics Departmental Lecture Series: Cat Lambert (Cornell University)",
    "description": "Tuesday, October 21, 2025 12:30 PM 1:30 PM 12:30 13:30 Department of Classics at Columbia University in the City of New York (map) Google Calendar ICS View Event \u2192",
    "start_date": "2025-10-21",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 4,
    "event_id": "evt_columbia_classics_c00710e4f1",
    "name": "Classics Departmental Lecture Series: Nathaniel Jones (Washington University)",
    "description": "Friday, November 14, 2025 4:10 PM 6:00 PM 16:10 18:00 Department of Classics at Columbia University in the City of New York (map) Google Calendar ICS View Event \u2192",
    "start_date": "2025-11-14",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 5,
    "event_id": "evt_columbia_classics_56548327b5",
    "name": "University Seminar in Classical Civilization - Pierre Destr\u00e9e (Louvain)",
    "description": "Thursday, November 20, 2025 7:30 PM 9:00 PM 19:30 21:00 Faculty House (map) Google Calendar ICS View Event \u2192",
    "start_date": "2025-11-20",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 6,
    "event_id": "evt_columbia_classics_e929d96306",
    "name": "Classics Departmental Lecture Series: Jose Antonio Cancino Alfaro (Columbia University)",
    "description": "Friday, December 5, 2025 12:30 PM 1:30 PM 12:30 13:30 Department of Classics at Columbia University in the City of New York (map) Google Calendar ICS View Event \u2192",
    "start_date": "2025-12-05",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 7,
    "event_id": "evt_columbia_classics_4d8bb12b6b",
    "name": "University Seminar in Classical Civilization - Mirjam Kotwick (Princeton)",
    "description": "Thursday, January 22, 2026 7:30 PM 9:00 PM 19:30 21:00 Faculty House (map) Google Calendar ICS View Event \u2192",
    "start_date": "2026-01-22",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 8,
    "event_id": "evt_columbia_classics_25230c685d",
    "name": "Classics Departmental Lecture Series: Jeremiah Coogan (Santa Clara University)",
    "description": "Friday, February 13, 2026 4:10 PM 6:00 PM 16:10 18:00 Department of Classics at Columbia University in the City of New York (map) Google Calendar ICS View Event \u2192",
    "start_date": "2026-02-13",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 9,
    "event_id": "evt_columbia_classics_f9c2270fe8",
    "name": "University Seminar in Classical Civilization - Reviel Netz (Stanford)",
    "description": "Thursday, February 19, 2026 7:30 PM 9:00 PM 19:30 21:00 Faculty House (map) Google Calendar ICS View Event \u2192",
    "start_date": "2026-02-19",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 10,
    "event_id": "evt_columbia_classics_304269407d",
    "name": "Classics Departmental Lecture Series: Tom Keeline (Washington University)",
    "description": "Friday, March 6, 2026 4:10 PM 6:00 PM 16:10 18:00 Department of Classics at Columbia University in the City of New York (map) Google Calendar ICS View Event \u2192",
    "start_date": "2026-03-06",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 11,
    "event_id": "evt_columbia_classics_feb743e3ff",
    "name": "University Seminar in Classical Civilization - Greg Woolf (NYU/ISAW)",
    "description": "Thursday, March 26, 2026 7:30 PM 9:00 PM 19:30 21:00 Faculty House (map) Google Calendar ICS View Event \u2192",
    "start_date": "2026-03-26",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 12,
    "event_id": "evt_columbia_classics_41b0e3adc4",
    "name": "University Seminar in Classical Civilization - Erica Valdivieso (Yale)",
    "description": "Thursday, April 16, 2026 7:30 PM 9:00 PM 19:30 21:00 Faculty House (map) Google Calendar ICS View Event \u2192",
    "start_date": "2026-04-16",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 13,
    "event_id": "evt_columbia_classics_e316fa7d03",
    "name": "Classics Departmental Lecture Series: Ian Moyer (University of Michigan)",
    "description": "Tuesday, April 28, 2026 4:10 PM 6:00 PM 16:10 18:00 Department of Classics at Columbia University in the City of New York (map) Google Calendar ICS View Event \u2192",
    "start_date": "2026-04-28",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 14,
    "event_id": "evt_columbia_classics_4c7ab101e6",
    "name": "Classics Departmental Lecture Series: Melody Wauke (Columbia University)",
    "description": "Friday, May 8, 2026 12:30 PM 1:30 PM 12:30 13:30 Department of Classics at Columbia University in the City of New York (map) Google Calendar ICS View Event \u2192",
    "start_date": "",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 15,
    "event_id": "evt_columbia_classics_02a1e1960f",
    "name": "Classics Lecture Series Presents: Andrew Laird (Brown University)",
    "description": "Friday, March 14, 2025 4:10 PM 6:00 PM 16:10 18:00 Department of Classics at Columbia University in the City of New York (map) Google Calendar ICS View Event \u2192",
    "start_date": "2025-03-14",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 16,
    "event_id": "evt_columbia_classics_64696e0020",
    "name": "Classics Lecture Series Presents: Claire Bubb (NYU)",
    "description": "Tuesday, October 22, 2024 4:10 PM 6:00 PM 16:10 18:00 Department of Classics at Columbia University in the City of New York (map) Google Calendar ICS Title: Vulnerable Bodies: Roman Medical Research and the Enslaved.Abstract: Roman doctors periodically required bodies, both living and dead, for medical demonstration and research. There were many vulnerable bodies in Roman society--animals, the enslaved, the impoverished, the outcast, and the conquered--and this talk will explore which bodies doctors seem to have favored for which purposes. As it turns out, their use of the enslaved appears to have been surprisingly curtailed. The talk will therefore also address Galen's perspectives on slavery and the enslaved and explore the potential boundaries to the exploitation of this particularly vulnerable population. View Event \u2192",
    "start_date": "2024-10-22",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://classics.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 17,
    "event_id": "evt_columbia_b6854b63",
    "name": "Dilemmas of Nat'l Security &amp; Freedom of Religion in Wartime Ukraine",
    "description": "<p><strong>Registration REQUIRED by 4pm on September 17, 2025 to attend this event.</strong></p> <p>Please join the Ukrainian Studies Program at the Harriman Institute for a lecture by&nbsp;<strong>Oxana Shevel</strong>. Moderated by&nbsp;<a href=\"https://harriman.columbia.edu/person/mark-andryczyk/\"><strong>Mark Andryczyk</strong></a>.</p> <p>In the wake of Russia&rsquo;s full-scale invasion, Ukraine has taken steps to limit the influence of the Ukrainian Orthodox Church (UOC), historically aligned with the Russian Orthodox Church (ROC). This talk explores the legal, political, and societal debates in Ukraine surrounding the state's efforts to safeguard Ukraine's &ldquo;spiritual independence&rdquo; while navigating international norms on religious freedom. Why did the Ukrainian state conclude that the UOC pose a threat to Ukraine's spiritual independence? Can a religion ever pose a threat to national security, and when such a threat it believed to exist how should democracies balance national security and religious liberty? Do international legal frameworks on religious freedoms sufficiently account for the use of religion in hybrid warfare and instrumentalization of religion in Russia's war of imperial aggression? The talk will explore these questions with a focus on the post-February 2022 domestic developments and debates in Ukraine while also situating the Ukrainian case in comparative perspective, drawing parallels with how other contemporary democratic states have sought to balance national security concerns and freedom of religion.</p>",
    "start_date": "2025-09-18T19:15:00+00:00",
    "end_date": "2025-09-18T20:30:00+00:00",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://events.columbia.edu/cal/event/eventView.do?b=de&calPath=%2Fpublic%2Fcals%2FMainCal&guid=CAL-00bbdb7c-987e71e0-0198-801db233-000056deevents%40columbia.edu&recurrenceId=",
    "source_name": "columbia Events",
    "venue_name": "International Affairs Building, 420 W. 118 St., New York, NY 10027\tMarshall D. Shulman Seminar Room, 1219",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 18,
    "event_id": "evt_columbia_4e4723c8",
    "name": "Jacques Herzog (Herzog &amp; deMeuron) John Foerster &lsquo;64 Fund Lecture",
    "description": "<p>Response by Dean Andr&eacute;s Jaque</p>",
    "start_date": "2025-09-18T22:30:00+00:00",
    "end_date": "2025-09-19T00:30:00+00:00",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://events.columbia.edu/cal/event/eventView.do?b=de&calPath=%2Fpublic%2Fcals%2FMainCal&guid=CAL-00bbdb70-989828b4-0198-9a97d5d2-0000040aevents%40columbia.edu&recurrenceId=",
    "source_name": "columbia Events",
    "venue_name": "Avery Hall, 1172 Amsterdam Ave., New York, NY 10027\tWood Auditorium",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 19,
    "event_id": "evt_columbia_138c9dd0",
    "name": "Harriman Carnegie Corporation Russia Studies Capstone Conference",
    "description": "<p><strong>Registration REQUIRED by 4pm on September 18, 2025 to attend this event.</strong></p> <p>Please join the Harriman Institute for the Carnegie Corporation Russia Studies Capstone Conference.&nbsp;</p> <h2>Conference Program</h2> <h4>9:00 AM | Welcoming Remarks</h4> <ul> <li><strong>Alexander Cooley </strong>and<strong> Jack Snyder</strong></li> </ul> <h4>9:15 - 10:30 AM | Panel I: Geopolitics and the Fate of Russian and Eurasian Studies</h4> <p>Chair: <strong>Jack Snyder</strong> (Columbia University)</p> <ul> <li><strong>Julie Newton&nbsp;</strong>(Oxford University)</li> <li><strong>Michael Kimmage</strong> (Catholic University)</li> <li><strong>Oxana Shevel</strong> (Tufts University)</li> </ul> <h4>10:45 AM - 12:00 PM | Panel II: Reflections on the Political Economy of Russia</h4> <p>Chair: <strong>Timothy Frye&nbsp;</strong>(Columbia University)</p> <ul> <li><strong>Anton Shirikov</strong> (University of Kansas)</li> <li><strong>Egor Lazarev</strong> (Yale University)</li> <li><strong>Georgiy Syunyaev</strong> (Vanderbilt University)</li> <li><strong>Guzel Garifullina</strong> (University of Richmond)</li> </ul> <h4>12:45 - 1:45 PM | Keynote Remarks</h4> <ul> <li><strong>Robert Legvold</strong></li> </ul> <h4>1:45 - 3:00 PM | Panel III: New Research Agendas and Topics</h4> <p>Chair: <strong>Elise Giuliano </strong>(Columbia University)</p> <ul> <li><strong>Yana Gorokhovskaia</strong> (Freedom House)</li> <li><strong>Paul Goode</strong> (Carleton University, Canada)</li> <li><strong>Valerie Sperling</strong> (Clark University)</li> <li><strong>Yoshiko Herrera</strong> (University of Wisconsin, Madison)</li> </ul> <h4>3:15 - 4:30 PM | Panel IV: Institutional Impacts of the War: Regional Studies and Regional Impacts (Caucasus and Central Asia)</h4> <p>Chair: <strong>Alexander Cooley </strong>(Columbia University)</p> <ul> <li><strong>Julie George</strong> (CUNY)</li> <li><strong>Nargis Kassenova</strong> (Harvard University)</li> <li><strong>Ed Schatz</strong> (University of Toronto)</li> <li><strong>Joshua Tucker</strong> (New York University)</li> </ul> <h4>4:30 PM | Concluding Remarks</h4> <ul> <li><strong>Alexander Cooley</strong></li> </ul>",
    "start_date": "2025-09-19T13:00:00+00:00",
    "end_date": "2025-09-19T20:30:00+00:00",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://events.columbia.edu/cal/event/eventView.do?b=de&calPath=%2Fpublic%2Fcals%2FMainCal&guid=CAL-00bbdb70-98c681f4-0198-c8fe2190-0000711aevents%40columbia.edu&recurrenceId=",
    "source_name": "columbia Events",
    "venue_name": "Pulitzer Hall, 2950 Broadway, New York, NY 10027\tWorld Room",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 20,
    "event_id": "evt_columbia_math_eab81d68fb",
    "name": "2016 SPRING TERM LECTURE SERIES",
    "description": "",
    "start_date": "2016-01-28",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://math.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 21,
    "event_id": "evt_columbia_math_8df0f723ae",
    "name": "Geometric Analysis Seminar",
    "description": "507 Mathematics Hall 507 Math",
    "start_date": "2015-06-12",
    "end_date": "",
    "source": "columbia",
    "source_group": "columbia",
    "source_url": "https://math.columbia.edu/events",
    "source_name": "columbia Events",
    "venue_name": "Columbia University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 22,
    "event_id": "evt_fordham_9a12385662",
    "name": "Scientific Symposium: Community Engagement and Migration",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "fordham",
    "source_group": "fordham",
    "source_url": "https://www.fordham.edu/events/",
    "source_name": "fordham Events",
    "venue_name": "Fordham University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 23,
    "event_id": "evt_fordham_145fb33549",
    "name": "McGinley Chair Lecture\u2014The Ethics of Meritocracy: A Theological Assessment",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "fordham",
    "source_group": "fordham",
    "source_url": "https://www.fordham.edu/events/",
    "source_name": "fordham Events",
    "venue_name": "Fordham University",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 24,
    "event_id": "evt_gallatin_a828a12f",
    "name": "Global Fellowship in Human Rights Symposium",
    "description": "RSVP required",
    "start_date": "2025-10-15T18:30:00",
    "end_date": "2025-10-15T20:30:00",
    "source": "gallatin",
    "source_group": "gallatin",
    "source_url": "https://gallatin.nyu.edu/gallatin/en/utilities/events/2025/10/global-fellowship-in-human-rights-symposium.html",
    "source_name": "gallatin Events",
    "venue_name": "Jerry H. Labowitz Theatre for the Performing Arts",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 25,
    "event_id": "evt_gallatin_9e9a5cb1",
    "name": "A Decade of (De)Tangling the Business of Black Women\u2019s Hair (a conference and homecoming)",
    "description": "RSVP required",
    "start_date": "2025-11-21T12:00:00",
    "end_date": "2025-11-21T20:30:00",
    "source": "gallatin",
    "source_group": "gallatin",
    "source_url": "https://gallatin.nyu.edu/gallatin/en/utilities/events/2025/11/a-decade-of--de-tangling-the-business-of-black-women-s-hair--a-c.html",
    "source_name": "gallatin Events",
    "venue_name": "Jerry H. Labowitz Theatre for the Performing Arts",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 26,
    "event_id": "evt_isaw_78293145",
    "name": "How China\u2019s Early Empires Conquered and Colonized the Yangtze Delta",
    "description": "Speaker: Brian Lander This lecture will take place in person at ISAW. Registration is required; click through for the registration link. This talk will analyze how the Chu, Qin and Han empires conquered and colonized this region, gradually transforming it from a culturally alien frontier into a regular, if remote, part of the Han empire. The paucity of texts on this region\u2019s early history reflects the disdain early China\u2019s literate elites held towards it and makes archaeological evidence particularly important.",
    "start_date": "2025-10-14T17:30:00",
    "end_date": "2025-10-14T19:30:00",
    "source": "isaw",
    "source_group": "isaw",
    "source_url": "https://isaw.nyu.edu/events/china-yangtze-delta",
    "source_name": "isaw Events",
    "venue_name": "ISAW Lecture Hall",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 27,
    "event_id": "evt_jtsa_17ef480e",
    "name": "Biblical Hebrew IV: Advanced Reading Seminar\u2014Ezekiel\u2019s First Prophecies (morning)",
    "description": "In nine, live online sessions, explore this fascinating section of Tanakh that has mystified readers through the ages.",
    "start_date": "2025-10-16T12:00:00",
    "end_date": "2025-10-16T13:00:00",
    "source": "jtsa",
    "source_group": "jtsa",
    "source_url": "https://www.jtsa.edu/event/biblical-hebrew-iv-fall-2025-morning/",
    "source_name": "jtsa Events",
    "venue_name": "Online Event",
    "venue_type": "Online",
    "is_academic": true
  },
  {
    "id": 28,
    "event_id": "evt_jtsa_a16eb3b5",
    "name": "Biblical Hebrew IV: Advanced Reading Seminar\u2014Ezekiel\u2019s First Prophecies (afternoon)",
    "description": "In nine live, online sessions, we will explore this fascinating section of Tanakh that has mystified readers through the ages.",
    "start_date": "2025-10-16T12:00:00",
    "end_date": "2025-10-16T13:00:00",
    "source": "jtsa",
    "source_group": "jtsa",
    "source_url": "https://www.jtsa.edu/event/biblical-hebrew-iv-fall-2025-afternoon/",
    "source_name": "jtsa Events",
    "venue_name": "Online Event",
    "venue_type": "Online",
    "is_academic": true
  },
  {
    "id": 29,
    "event_id": "evt_jtsa_765b5da4",
    "name": "The Decoration of Hebrew Manuscripts After the Invention of Printing",
    "description": "Join Sharon Liberman-Mintz and Emile Schrijver for a special lecture on our Library exhibit, Jewish Worlds Illuminated: A Treasury of Hebrew Manuscripts from The JTS Library.",
    "start_date": "2025-10-20T12:00:00",
    "end_date": "2025-10-20T13:00:00",
    "source": "jtsa",
    "source_group": "jtsa",
    "source_url": "https://www.jtsa.edu/event/decoration-hebrew/",
    "source_name": "jtsa Events",
    "venue_name": "The Grolier Club",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 30,
    "event_id": "evt_newschool_cbcdb57c",
    "name": "Institute for Philosophy and New Humanities 2025",
    "description": "**Attendance is limited to current New School faculty and students. Must have an @newschool.edu email address to register.** Join us for a series of keynote presentations as part of the 2025 Institute for Philosophy and New Humanities: Iconoclasm: Past and Present. The internet (and AI) have made us acutely aware of the power of images, and how it can come to seem reasonable to want to destroy these images as a defense mechanism. The idea of the seminar would be to take up not just explicit bans on images or various forms of censorship, but the philosophical underpinnings of iconoclasm: namely, the view that images are not bearers of truth, are antithetical to human efforts at making the world intelligible, and psychologically deleterious. We hope to invite people with art historical perspectives, alongside philosophers of art with things to say about the fate of iconoclasm beyond its ancient pedigree (Plato, the Bible) into the contemporary world.KEYNOTE LECTURES AND Q&ASTuesday, September 2, 4pm Birgit Mersmann, University of Bonn Thursday, September 4, 4pm Alva No\u00eb, University of California, Berkeley Friday, September 5, 4pm Erin Thompson, CUNY",
    "start_date": "2025-09-02T20:00:00+00:00",
    "end_date": "2025-09-05T22:00:00+00:00",
    "source": "new_school",
    "source_group": "new_school",
    "source_url": "https://event.newschool.edu/ipnh2025",
    "source_name": "new_school Events",
    "venue_name": "University Center, Starr Foundation Hall (UL102)",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 31,
    "event_id": "evt_newschool_ead0a041",
    "name": "Techniques of Music Distinguished Scholars Lecture Series",
    "description": "Techniques of Music Distinguished Scholars Lecture Series presents Prof. Elizabeth H. Margulis (Princeton University)Elizabeth H. Margulis, Professor of Music at Princeton University and Director of the Music Cognition Lab, will deliver a lecture entitled \u201cWhat Can We Learn from Musical Daydreams? Insights from Music Cognition.\u201dA leading scholar in the field, Prof. Margulis is the author of award-winning publications and a former president of the Society for Music Perception and Cognition.This lecture is free and open to both the New School community and the public.",
    "start_date": "2025-10-03T20:00:00+00:00",
    "end_date": "2025-10-03T21:30:00+00:00",
    "source": "new_school",
    "source_group": "new_school",
    "source_url": "https://event.newschool.edu/techniquesofmusicmargulis",
    "source_name": "new_school Events",
    "venue_name": "Ernst C. Stiefel Hall",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 32,
    "event_id": "evt_43bfdb5efe1e2e3b",
    "name": "Simons Seminar - Kade Head-Marsden, UM Twin Cities",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 33,
    "event_id": "evt_f19d3c19cf42e3af",
    "name": "Seminar: Molly Schumer (Stanford)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 34,
    "event_id": "evt_2cebf5208e3cf304",
    "name": "Applied Microeconomics Seminar: \"TBA\" - John Eric Humphries (Yale)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 35,
    "event_id": "evt_1e5eaa19320650ba",
    "name": "Opening Lecture: C. Riley Snorton",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 36,
    "event_id": "evt_ccecec538b712b9a",
    "name": "Colloquium: Christopher Cummins, MIT",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 37,
    "event_id": "evt_47d18397642100d6",
    "name": "Seminar: Duncan Smith (NYU Biology)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 38,
    "event_id": "evt_d9a975836d780106",
    "name": "McNelis Lecture: Phil Baran, Scripps",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 39,
    "event_id": "evt_7a612a6164e8a492",
    "name": "Seminar: Martin Picard (Columbia University)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 40,
    "event_id": "evt_ef5ff6ac7aca9373",
    "name": "Colloquium: Tobin Sosnick, U Chicago",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 41,
    "event_id": "evt_4bc04d8e58e7b01e",
    "name": "Department Colloquium: Rachel Fraser (MIT)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 42,
    "event_id": "evt_cfb0a22b762c002b",
    "name": "Seminar: J. Brooks Crickard (Cornell)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 43,
    "event_id": "evt_0ee5e133c7448319",
    "name": "Applied Microeconomics Seminar: \"TBA\" - Eric Chyn (Uni. of Texas - Austin)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 44,
    "event_id": "evt_c2c3625221884f7d",
    "name": "Seminar: Sebastien Thibaudeau, U Poitiers",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 45,
    "event_id": "evt_a9b82430b04e3252",
    "name": "Mala Kamm Memorial Lecture: Elizabeth Anderson (University of Michigan)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 46,
    "event_id": "evt_de101f77ca498d92",
    "name": "Simons Seminar - Jiankun Lyu, Rockefeller Univ.",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 47,
    "event_id": "evt_d4c49110cc8a0df9",
    "name": "Seminar: Floria Mora-Kepfer Uy (University of Rochester)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 48,
    "event_id": "evt_8a0ffb1f4e1bf0e0",
    "name": "Seminar: George Burslem, UPenn",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 49,
    "event_id": "evt_bcbb324ea4b2c070",
    "name": "CQP Seminar by Dr. Tomohiro Soejima ",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 50,
    "event_id": "evt_846b437e793681f6",
    "name": "Colloquium: Thomas Maimone, Berkeley",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 51,
    "event_id": "evt_a5fd94fd4cb13fa3",
    "name": "CGEB - David K. Backus Memorial Lecture: \"How Good is International Risk Sharing?\" - Mark Aguiar (Princeton University)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 52,
    "event_id": "evt_856340a8551020b3",
    "name": "Seminar: Caleb Lareau (MSKCC)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 53,
    "event_id": "evt_8d2dc85628f71bfc",
    "name": "Seminar, Makoto Fujita, U Tokyo",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 54,
    "event_id": "evt_cfa6be9bb43c2de4",
    "name": "Colloquium: Paul Wiseman, McGill",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 55,
    "event_id": "evt_b18a0c0eaffeadbe",
    "name": "Applied Microeconomics Seminar: \"TBA\" - Camille Landais (LSE)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 56,
    "event_id": "evt_8ef5e2cf1f1c7392",
    "name": "Seminar: Lukas Muechler, Penn State",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 57,
    "event_id": "evt_9fd1616084480eca",
    "name": "Colloquium: David Nagib, OSU",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 58,
    "event_id": "evt_91474e6d03b197c4",
    "name": "Colloquium: Yi Tang, UCLA",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 59,
    "event_id": "evt_a40ba59cfd194916",
    "name": "Department Colloquium: Gordon Belot (University of Michigan)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 60,
    "event_id": "evt_5b406059f4c2db05",
    "name": "Applied Microeconomics Seminar: \"TBA\" - Heather Sarsons (Uni. of Chicago)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 61,
    "event_id": "evt_f7a2f998fc9873b4",
    "name": "Seminar: Danna Freedman, MIT",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 62,
    "event_id": "evt_54859ebb9ec28cb1",
    "name": "2025 Issues in Modern Philosophy Conference",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 63,
    "event_id": "evt_0a4cbb33b7408bce",
    "name": "Colloquium: Christina White, UIUC",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 64,
    "event_id": "evt_54859ebb9ec28cb1",
    "name": "2025 Issues in Modern Philosophy Conference",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 65,
    "event_id": "evt_ddc6d192a4be6d19",
    "name": "Seminar: Leah Dodson, UMD",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 66,
    "event_id": "evt_ca36a861dca2d3ca",
    "name": "Department Colloquium: Michael Rescorla (UCLA)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 67,
    "event_id": "evt_ce3183535cecce8f",
    "name": "Molecular Frontiers Symposium",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 68,
    "event_id": "evt_ce3183535cecce8f",
    "name": "Molecular Frontiers Symposium",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 69,
    "event_id": "evt_5fe53a83f604d079",
    "name": "Applied Microeconomics Seminar: \"TBA\" - Patrick Bayer (Duke University)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 70,
    "event_id": "evt_62580de0d3b853e6",
    "name": "Final Conference of the William Burt's Italian Papers Project",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 71,
    "event_id": "evt_c90063cefa7294c1",
    "name": "Applied Microeconomics Seminar: \"TBA\" - Zoe Cullen (Harvard University)",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "",
    "source_name": "nyu Events",
    "venue_name": "",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 72,
    "event_id": "evt_nyu_law_eed9d16077",
    "name": "LLM Inaugural Lecture",
    "description": "",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "https://law.nyu.edu/events",
    "source_name": "nyu Events",
    "venue_name": "NYU Law",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 73,
    "event_id": "evt_nyu_medicine_16e7cf32de",
    "name": "Additional Education and Research Calendars",
    "description": "Applied Bioinformatics Laboratories Biochemistry and Molecular Biophysics Seminar Series Emergency Medicine Prevention and Education Partnership Genes, Systems, and Computation Seminar Series Health Sciences Library HiBRID Lab Immunology Club Integrative Health Office of Diversity Affairs Office of Science and Research Section for Global Health Technology Opportunities and Ventures Translational Research in Progress Seminars Working Group on Compassionate Use and Preapproval Access How to Submit an Event or Request a New Calendar If you are part of NYU Grossman School of Medicine and would like to submit an event, choose a specific calendar and click the \u201cSubmit an Event\u201d button, and then log in with your Kerberos ID and password to complete the event submission form. Your request will be reviewed by the calendar\u2019s manager. To request a new calendar, please fill out a public website content request form. For the Request Type field, select med.nyu.edu and then provide the details about your new calendar request. Please also use this content request form if you already have a calendar and would like to have your events pull into your med.nyu.edu site. For general information, browse our frequently asked questions. (Kerberos ID and password required).",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "https://med.nyu.edu/events",
    "source_name": "nyu Events",
    "venue_name": "NYU Medical Center",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 74,
    "event_id": "evt_nyu_stern_0951151a35",
    "name": "Crypto and Blockchain Economics Research Forum",
    "description": "\u2014 June 12, 2025 On Thursday, June 12, NYU Stern's Finance Department will co-host the 5th annual Crypto and Blockchain Economics Research Forum conference. Read More",
    "start_date": "2025-06-12",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "https://stern.nyu.edu/events",
    "source_name": "nyu Events",
    "venue_name": "NYU Stern",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 75,
    "event_id": "evt_nyu_stern_dc347402c5",
    "name": "NYU Stern Summer Climate Finance Conference",
    "description": "\u2014 May 23, 2025 On Thursday, May 23, 2025, the NYU Stern Climate Finance Initiative and the Volatility and Risk Institute will co-host the NYU Stern Summer Climate Finance Conference. Read More",
    "start_date": "",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "https://stern.nyu.edu/events",
    "source_name": "nyu Events",
    "venue_name": "NYU Stern",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 76,
    "event_id": "evt_nyu_stern_03b0321d04",
    "name": "Four-School Accounting Research Conference",
    "description": "\u2014 April 4, 2025 The Department of Accounting at NYU Stern School of Business will host the Four-School Accounting Research Conference on Friday, April 4, 2025.This annual conference brings together accounting researchers from four leading northeastern business schools, Columbia Business School, NYU Stern, Wharton School at the University of Pennsylvania, and Yale School of Management. Read More",
    "start_date": "2025-04-04",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "https://stern.nyu.edu/events",
    "source_name": "nyu Events",
    "venue_name": "NYU Stern",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 77,
    "event_id": "evt_nyu_stern_4c826e7fef",
    "name": "Haitkin Lecture Series featuring Jonathan Haidt",
    "description": "\u2014 March 18, 2025 NYU-Stern's own Jonathan Haidt will begin with the case he made in his global bestseller The Anxious Generation, about how the rapid transition from a \"play-based childhood\" to a \"phone-based childhood\" in the years between 2010 and 2015 changed the course of human development around the world. Haidt will then go far beyond the mental health impacts to discuss the damage done by phone-based life to education, attention, creativity, the economy, families, and democracy. Read More",
    "start_date": "2025-03-18",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "https://stern.nyu.edu/events",
    "source_name": "nyu Events",
    "venue_name": "NYU Stern",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 78,
    "event_id": "evt_nyu_stern_cb11c6e6ae",
    "name": "2025 NYU Stern Fintech Conference: Fintech and the Future 2025",
    "description": "\u2014 February 28, 2025 On February 28, 2025, the Fubon Center for Technology, Business and Innovation will host the 2025 NYU Stern Fintech Conference titled \"Fintech and the Future 2025.\" Read More",
    "start_date": "2025-02-28",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "https://stern.nyu.edu/events",
    "source_name": "nyu Events",
    "venue_name": "NYU Stern",
    "venue_type": "Offline",
    "is_academic": true
  },
  {
    "id": 79,
    "event_id": "evt_nyu_stern_9a3b3852f9",
    "name": "3rd Annual Symposium on Innovation and Sustainable Real Estate",
    "description": "\u2014 February 18, 2025 On Tuesday, February 18, 2025, the Chen Institute for Global Real Estate Finance hosted its 3rd Annual Symposium on Innovation and Sustainable Real Estate, in partnership with the NYU Office of Sustainability and the NYU Stern Center for Sustainable Business. Read More",
    "start_date": "2025-02-18",
    "end_date": "",
    "source": "nyu",
    "source_group": "nyu",
    "source_url": "https://stern.nyu.edu/events",
    "source_name": "nyu Events",
    "venue_name": "NYU Stern",
    "venue_type": "Offline",
    "is_academic": true
  }
];

// Helper function to filter events
function filterEvents(events, filters) {
  let filtered = events;
  
  if (filters.institution) {
    filtered = filtered.filter(event => event.source === filters.institution);
  }
  
  if (filters.source_group) {
    filtered = filtered.filter(event => event.source_group === filters.source_group);
  }
  
  if (filters.date_from) {
    filtered = filtered.filter(event => event.start_date >= filters.date_from);
  }
  
  if (filters.date_to) {
    filtered = filtered.filter(event => event.start_date <= filters.date_to);
  }
  
  if (filters.academic_only !== false) {
    filtered = filtered.filter(event => event.is_academic === true);
  }
  
  return filtered;
}

// Helper function to paginate results
function paginateEvents(events, skip = 0, limit = 50) {
  const total = events.length;
  const paginated = events.slice(skip, skip + limit);
  
  return {
    events: paginated,
    total: total,
    page: Math.floor(skip / limit) + 1,
    per_page: limit
  };
}

// Helper function to get institutions with event counts
function getInstitutions(events) {
  const institutionMap = new Map();
  
  events.forEach(event => {
    if (event.is_academic) {
      const key = event.source_group;
      if (!institutionMap.has(key)) {
        institutionMap.set(key, {
          name: event.source_name || event.source_group,
          source_group: event.source_group,
          event_count: 0
        });
      }
      institutionMap.get(key).event_count++;
    }
  });
  
  return Array.from(institutionMap.values()).sort((a, b) => b.event_count - a.event_count);
}

// Main request handler
async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  
  // Handle CORS preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }
  
  try {
    // Root endpoint
    if (path === '/' || path === '/api') {
      return new Response(JSON.stringify({
        message: "NYC Academic Events API",
        version: "1.0.0",
        endpoints: {
          events: "/api/events",
          event_by_id: "/api/events/{event_id}",
          institutions: "/api/institutions",
          stats: "/api/stats"
        }
      }), { headers: corsHeaders });
    }
    
    // Health check
    if (path === '/health') {
      return new Response(JSON.stringify({
        status: "healthy",
        service: "nyc-academic-events-api",
        timestamp: new Date().toISOString()
      }), { headers: corsHeaders });
    }
    
    // Get all events
    if (path === '/api/events') {
      const skip = parseInt(url.searchParams.get('skip') || '0');
      const limit = Math.min(parseInt(url.searchParams.get('limit') || '50'), 100);
      const institution = url.searchParams.get('institution');
      const source_group = url.searchParams.get('source_group');
      const date_from = url.searchParams.get('date_from');
      const date_to = url.searchParams.get('date_to');
      const academic_only = url.searchParams.get('academic_only') !== 'false';
      
      const filters = { institution, source_group, date_from, date_to, academic_only };
      const filtered = filterEvents(academicEvents, filters);
      const result = paginateEvents(filtered, skip, limit);
      
      return new Response(JSON.stringify(result), { headers: corsHeaders });
    }
    
    // Get specific event by ID
    if (path.startsWith('/api/events/')) {
      const eventId = path.split('/').pop();
      const event = academicEvents.find(e => e.event_id === eventId);
      
      if (!event) {
        return new Response(JSON.stringify({ error: "Event not found" }), {
          status: 404,
          headers: corsHeaders
        });
      }
      
      return new Response(JSON.stringify(event), { headers: corsHeaders });
    }
    
    // Get institutions
    if (path === '/api/institutions') {
      const institutions = getInstitutions(academicEvents);
      const result = {
        institutions: institutions,
        total: institutions.length
      };
      
      return new Response(JSON.stringify(result), { headers: corsHeaders });
    }
    
    // Get statistics
    if (path === '/api/stats') {
      const academicEventsOnly = academicEvents.filter(e => e.is_academic);
      const institutions = getInstitutions(academicEvents);
      
      // Group events by month
      const monthlyStats = {};
      academicEventsOnly.forEach(event => {
        if (event.start_date) {
          const month = event.start_date.substring(0, 7); // YYYY-MM
          monthlyStats[month] = (monthlyStats[month] || 0) + 1;
        }
      });
      
      const result = {
        total_academic_events: academicEventsOnly.length,
        total_institutions: institutions.length,
        monthly_events: Object.entries(monthlyStats).map(([month, count]) => ({
          month,
          count
        })),
        last_updated: new Date().toISOString()
      };
      
      return new Response(JSON.stringify(result), { headers: corsHeaders });
    }
    
    // 404 for unknown endpoints
    return new Response(JSON.stringify({ error: "Endpoint not found" }), {
      status: 404,
      headers: corsHeaders
    });
    
  } catch (error) {
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: corsHeaders
    });
  }
}

// Export the fetch event handler
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});
