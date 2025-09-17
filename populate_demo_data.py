#!/usr/bin/env python3
"""
Demo data population script for The Journey platform
Run this script to populate the database with realistic sample data
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add the current directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Club, Event, EventRegistration, ClubMembership
from werkzeug.security import generate_password_hash

def create_demo_users():
    """Create demo users with different roles"""
    demo_users = [
        {
            'email': 'sarah.chen@demo.com',
            'first_name': 'Sarah',
            'last_name': 'Chen',
            'city': 'San Francisco',
            'role': 'admin',
            'bio': 'Community builder passionate about sustainable living and bringing people together through meaningful experiences.'
        },
        {
            'email': 'marcus.rivera@demo.com',
            'first_name': 'Marcus',
            'last_name': 'Rivera',
            'city': 'San Francisco',
            'role': 'club_manager',
            'bio': 'Cultural arts enthusiast and community organizer. Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        },
        {
            'email': 'emily.rodriguez@demo.com',
            'first_name': 'Emily',
            'last_name': 'Rodriguez',
            'city': 'San Francisco',
            'role': 'club_manager',
            'bio': 'Event coordinator specializing in sustainable events and eco-friendly workshops.'
        },
        {
            'email': 'david.kim@demo.com',
            'first_name': 'David',
            'last_name': 'Kim',
            'city': 'Oakland',
            'role': 'club_manager',
            'bio': 'Professional networker and startup founder. Passionate about building connections in the tech community.'
        },
        {
            'email': 'jessica.martinez@demo.com',
            'first_name': 'Jessica',
            'last_name': 'Martinez',
            'city': 'San Jose',
            'role': 'user',
            'bio': 'Environmental advocate and green living enthusiast. Always looking for new ways to reduce my carbon footprint.'
        },
        {
            'email': 'maya.patel@demo.com',
            'first_name': 'Maya',
            'last_name': 'Patel',
            'city': 'Berkeley',
            'role': 'user',
            'bio': 'Art lover and cultural explorer. Sed ut perspiciatis unde omnis iste natus error sit voluptatem.'
        },
        {
            'email': 'alex.johnson@demo.com',
            'first_name': 'Alex',
            'last_name': 'Johnson',
            'city': 'San Francisco',
            'role': 'user',
            'bio': 'Tech professional interested in work-life balance and community engagement.'
        },
        {
            'email': 'lisa.wang@demo.com',
            'first_name': 'Lisa',
            'last_name': 'Wang',
            'city': 'Palo Alto',
            'role': 'user',
            'bio': 'Wellness coach and mindfulness practitioner. At vero eos et accusamus et iusto odio dignissimos.'
        }
    ]
    
    created_users = []
    for user_data in demo_users:
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = User()
            user.email = user_data['email']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.city = user_data['city']
            user.role = user_data['role']
            user.bio = user_data['bio']
            user.password_hash = generate_password_hash('password123')
            user.interests = f"[\"{user_data['role']}\", \"community\", \"networking\"]"
            
            db.session.add(user)
            created_users.append(user)
    
    db.session.commit()
    return created_users

def create_demo_clubs(users):
    """Create demo clubs"""
    demo_clubs = [
        {
            'name': 'Green Living Club',
            'description': 'Join us for workshops on sustainable living, zero-waste practices, organic gardening, and eco-friendly lifestyle tips. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
            'category': 'sustainable',
            'city': 'San Francisco',
            'manager_email': 'emily.rodriguez@demo.com'
        },
        {
            'name': 'Cultural Arts Collective',
            'description': 'A vibrant community celebrating local arts, hosting gallery walks, artist showcases, and cultural exchange events. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam.',
            'category': 'cultural',
            'city': 'San Francisco',
            'manager_email': 'marcus.rivera@demo.com'
        },
        {
            'name': 'Tech Professionals Network',
            'description': 'Monthly meetups for tech professionals featuring guest speakers, industry insights, career development workshops, and networking opportunities. Sed ut perspiciatis unde omnis iste natus error.',
            'category': 'entertainment',
            'city': 'San Francisco',
            'manager_email': 'david.kim@demo.com'
        },
        {
            'name': 'Mindful Living Circle',
            'description': 'Weekly meditation sessions, mindfulness workshops, wellness talks, and community support for holistic living. At vero eos et accusamus et iusto odio dignissimos ducimus.',
            'category': 'sustainable',
            'city': 'Berkeley',
            'manager_email': 'lisa.wang@demo.com'
        },
        {
            'name': 'Urban Gardeners Society',
            'description': 'Community garden maintenance, seasonal planting workshops, seed swaps, and sustainable agriculture education. Nemo enim ipsam voluptatem quia voluptas sit aspernatur.',
            'category': 'sustainable',
            'city': 'Oakland',
            'manager_email': 'jessica.martinez@demo.com'
        },
        {
            'name': 'Photography & Film Club',
            'description': 'Monthly photo walks, film screenings, equipment workshops, and collaborative projects celebrating visual storytelling. Temporibus autem quibusdam et aut officiis debitis.',
            'category': 'cultural',
            'city': 'San Jose',
            'manager_email': 'maya.patel@demo.com'
        }
    ]
    
    created_clubs = []
    for club_data in demo_clubs:
        # Find the manager
        manager = User.query.filter_by(email=club_data['manager_email']).first()
        if manager:
            # Check if club already exists
            existing_club = Club.query.filter_by(name=club_data['name']).first()
            if not existing_club:
                club = Club()
                club.name = club_data['name']
                club.description = club_data['description']
                club.category = club_data['category']
                club.city = club_data['city']
                club.manager_id = manager.id
                
                db.session.add(club)
                created_clubs.append(club)
    
    db.session.commit()
    return created_clubs

def create_demo_events(users, clubs):
    """Create demo events"""
    base_date = datetime.now() + timedelta(days=1)
    
    demo_events = [
        {
            'title': 'Zero Waste Workshop: Kitchen Edition',
            'description': 'Learn practical tips for reducing waste in your kitchen, making natural cleaning products, and sustainable food storage. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minima veniam.',
            'category': 'sustainable',
            'date_offset': 3,
            'location': 'Community Center Room A',
            'city': 'San Francisco',
            'price': Decimal('25.00'),
            'capacity': 30,
            'creator_email': 'emily.rodriguez@demo.com',
            'club_name': 'Green Living Club'
        },
        {
            'title': 'Local Artists Showcase',
            'description': 'An evening celebrating emerging local artists with live demonstrations, art sales, and community networking. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam.',
            'category': 'cultural',
            'date_offset': 5,
            'location': 'Downtown Art Gallery',
            'city': 'San Francisco',
            'price': Decimal('0.00'),
            'capacity': 80,
            'creator_email': 'marcus.rivera@demo.com',
            'club_name': 'Cultural Arts Collective'
        },
        {
            'title': 'Professional Networking Mixer',
            'description': 'Monthly networking event for tech professionals featuring guest speaker presentations, industry insights, and structured networking activities. At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis.',
            'category': 'entertainment',
            'date_offset': 7,
            'location': 'Tech Hub Downtown',
            'city': 'San Francisco',
            'price': Decimal('15.00'),
            'capacity': 50,
            'creator_email': 'david.kim@demo.com',
            'club_name': 'Tech Professionals Network'
        },
        {
            'title': 'Composting 101: Home Setup',
            'description': 'Hands-on workshop teaching the basics of home composting, worm bins, and turning kitchen scraps into garden gold. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit.',
            'category': 'sustainable',
            'date_offset': 10,
            'location': 'Urban Farm Co-op',
            'city': 'Oakland',
            'price': Decimal('20.00'),
            'capacity': 25,
            'creator_email': 'jessica.martinez@demo.com',
            'club_name': 'Urban Gardeners Society'
        },
        {
            'title': 'Mindfulness & Meditation Circle',
            'description': 'Weekly guided meditation session followed by group discussion on mindful living practices. Suitable for all experience levels. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus.',
            'category': 'sustainable',
            'date_offset': 2,
            'location': 'Wellness Center Berkeley',
            'city': 'Berkeley',
            'price': Decimal('0.00'),
            'capacity': 20,
            'creator_email': 'lisa.wang@demo.com',
            'club_name': 'Mindful Living Circle'
        },
        {
            'title': 'Photography Walk: Golden Hour',
            'description': 'Join fellow photographers for a guided walk through the city during golden hour. Tips on composition, lighting, and post-processing included. Et harum quidem rerum facilis est et expedita distinctio.',
            'category': 'cultural',
            'date_offset': 8,
            'location': 'Meetup at City Park Entrance',
            'city': 'San Jose',
            'price': Decimal('10.00'),
            'capacity': 15,
            'creator_email': 'maya.patel@demo.com',
            'club_name': 'Photography & Film Club'
        },
        {
            'title': 'Sustainable Fashion Swap',
            'description': 'Bring clothes you no longer wear and swap them for new-to-you items. Learn about sustainable fashion and textile recycling. Nam libero tempore, cum soluta nobis est eligendi optio cumque.',
            'category': 'sustainable',
            'date_offset': 12,
            'location': 'Community Hall',
            'city': 'San Francisco',
            'price': Decimal('5.00'),
            'capacity': 40,
            'creator_email': 'emily.rodriguez@demo.com',
            'club_name': 'Green Living Club'
        },
        {
            'title': 'Open Mic Night',
            'description': 'Monthly open mic featuring local musicians, poets, comedians, and storytellers. All skill levels welcome. Sign-up starts at 7 PM. Itaque earum rerum hic tenetur a sapiente delectus.',
            'category': 'cultural',
            'date_offset': 15,
            'location': 'The Corner Cafe',
            'city': 'San Francisco',
            'price': Decimal('0.00'),
            'capacity': 60,
            'creator_email': 'marcus.rivera@demo.com',
            'club_name': 'Cultural Arts Collective'
        },
        {
            'title': 'Startup Pitch Practice',
            'description': 'Practice your startup pitch in a supportive environment with feedback from experienced entrepreneurs and investors. Ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis.',
            'category': 'entertainment',
            'date_offset': 18,
            'location': 'Innovation Hub',
            'city': 'Palo Alto',
            'price': Decimal('30.00'),
            'capacity': 35,
            'creator_email': 'david.kim@demo.com',
            'club_name': 'Tech Professionals Network'
        },
        {
            'title': 'Community Garden Workday',
            'description': 'Join us for our monthly community garden maintenance day. Tools provided, but bring gloves and water. Pizza lunch included! Similique sunt in culpa qui officia deserunt mollitia animi.',
            'category': 'sustainable',
            'date_offset': 20,
            'location': 'Sunshine Community Garden',
            'city': 'Oakland',
            'price': Decimal('0.00'),
            'capacity': 25,
            'creator_email': 'jessica.martinez@demo.com',
            'club_name': 'Urban Gardeners Society'
        }
    ]
    
    created_events = []
    for event_data in demo_events:
        # Find the creator
        creator = User.query.filter_by(email=event_data['creator_email']).first()
        # Find the club
        club = Club.query.filter_by(name=event_data['club_name']).first()
        
        if creator:
            # Check if event already exists
            existing_event = Event.query.filter_by(title=event_data['title']).first()
            if not existing_event:
                event = Event()
                event.title = event_data['title']
                event.description = event_data['description']
                event.category = event_data['category']
                event.date_time = base_date + timedelta(days=event_data['date_offset'])
                event.location = event_data['location']
                event.city = event_data['city']
                event.price = event_data['price']
                event.capacity = event_data['capacity']
                event.creator_id = creator.id
                if club:
                    event.club_id = club.id
                
                db.session.add(event)
                created_events.append(event)
    
    db.session.commit()
    return created_events

def create_demo_memberships(users, clubs):
    """Create demo club memberships"""
    memberships_created = 0
    
    # Give each user membership to 1-3 random clubs
    for user in users:
        num_clubs = random.randint(1, min(3, len(clubs)))
        user_clubs = random.sample(clubs, num_clubs)
        
        for club in user_clubs:
            # Check if membership already exists
            existing = ClubMembership.query.filter_by(user_id=user.id, club_id=club.id).first()
            if not existing:
                membership = ClubMembership()
                membership.user_id = user.id
                membership.club_id = club.id
                db.session.add(membership)
                memberships_created += 1
    
    db.session.commit()
    return memberships_created

def create_demo_registrations(users, events):
    """Create demo event registrations"""
    registrations_created = 0
    
    # Register users for some events (but not over capacity)
    for event in events:
        # Register 50-80% of capacity
        num_registrations = random.randint(int(event.capacity * 0.5), int(event.capacity * 0.8))
        registered_users = random.sample(users, min(num_registrations, len(users)))
        
        for user in registered_users:
            # Check if registration already exists
            existing = EventRegistration.query.filter_by(user_id=user.id, event_id=event.id).first()
            if not existing:
                registration = EventRegistration()
                registration.user_id = user.id
                registration.event_id = event.id
                registration.payment_status = 'paid'
                db.session.add(registration)
                registrations_created += 1
    
    db.session.commit()
    return registrations_created

def main():
    """Main function to populate demo data"""
    with app.app_context():
        print("🌟 Populating The Journey with demo data...")
        
        # Create all tables
        db.create_all()
        
        # Create demo users
        print("👥 Creating demo users...")
        users = create_demo_users()
        print(f"   Created {len(users)} users")
        
        # Create demo clubs
        print("🏢 Creating demo clubs...")
        clubs = create_demo_clubs(users)
        print(f"   Created {len(clubs)} clubs")
        
        # Create demo events
        print("📅 Creating demo events...")
        events = create_demo_events(users, clubs)
        print(f"   Created {len(events)} events")
        
        # Create demo memberships
        print("🤝 Creating club memberships...")
        all_users = User.query.all()
        all_clubs = Club.query.all()
        memberships = create_demo_memberships(all_users, all_clubs)
        print(f"   Created {memberships} memberships")
        
        # Create demo registrations
        print("📝 Creating event registrations...")
        all_events = Event.query.all()
        registrations = create_demo_registrations(all_users, all_events)
        print(f"   Created {registrations} registrations")
        
        print("\n🎉 Demo data population complete!")
        print("\nDemo accounts you can use:")
        print("📧 sarah.chen@demo.com (Admin)")
        print("📧 marcus.rivera@demo.com (Club Manager)")
        print("📧 emily.rodriguez@demo.com (Club Manager)")
        print("📧 jessica.martinez@demo.com (User)")
        print("🔐 Password for all demo accounts: password123")

if __name__ == '__main__':
    main()