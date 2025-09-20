# Overview

Moroccan Journey is a premium cultural tourism platform built with Flask that connects travelers with authentic Moroccan experiences. The platform serves as a bridge between cultural enthusiasts, heritage experiences, and traditional Moroccan communities, focusing on premium cultural adventures, traditional workshops, and heritage tourism. It features role-based access control, payment processing through Stripe, and a complete cultural experience lifecycle management system from discovery to booking and participation.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
- **Flask-based MVC architecture** with server-side rendering using Jinja2 templates
- **SQLAlchemy ORM** for database abstraction and relationship management
- **Flask-Login** for session management and user authentication
- **Flask-WTF** with WTForms for form handling and validation
- **Bootstrap 5** for responsive frontend styling with custom CSS enhancements

## Authentication & Authorization
- **Role-based access control** with three user roles: admin, club_manager, and member
- **Secure password hashing** using Werkzeug's security utilities
- **Decorator-based route protection** for role-specific functionality
- **Session-based authentication** with Flask-Login integration

## Database Design
- **Relational database structure** using SQLAlchemy with the following core entities:
  - **Users** with role-based permissions and profile information
  - **Events** with pricing, location, and capacity management
  - **Clubs** for community organization and categorization
  - **Event Registrations** linking users to events with payment status
  - **Club Memberships** for managing club participation
- **Foreign key relationships** ensuring data integrity across entities
- **Decimal precision** for monetary values to avoid floating-point errors

## Payment Processing
- **Stripe integration** for secure payment handling
- **Environment-based API key management** for development and production separation
- **Payment status tracking** within event registrations

## Security Measures
- **Environment variable configuration** for sensitive data like database URLs and API keys
- **CSRF protection** through Flask-WTF
- **Production environment validation** to prevent insecure deployments
- **Password complexity requirements** and secure storage

## Template Architecture
- **Base template inheritance** for consistent UI/UX across all pages
- **Modular template structure** organized by feature areas (auth, events, clubs)
- **Bootstrap component integration** with custom styling for brand identity
- **Responsive design patterns** for mobile and desktop compatibility

# External Dependencies

## Core Framework Dependencies
- **Flask** - Web application framework
- **Flask-SQLAlchemy** - Database ORM and management
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and CSRF protection
- **WTForms** - Form validation and rendering

## Payment Processing
- **Stripe API** - Payment processing and subscription management
- Requires STRIPE_SECRET_KEY environment variable

## Database
- **PostgreSQL** (via DATABASE_URL environment variable)
- SQLAlchemy supports multiple database backends through connection string configuration

## Frontend Libraries
- **Bootstrap 5** - CSS framework for responsive design
- **Bootstrap Icons** - Icon library for UI elements

## Environment Management
- **python-dotenv** - Environment variable loading from .env files
- Requires SESSION_SECRET for production deployments

## Demo Data Management
- **Custom population script** (populate_demo_data.py) for generating realistic sample data
- Supports creating demo users, clubs, events, and relationships for testing and demonstration