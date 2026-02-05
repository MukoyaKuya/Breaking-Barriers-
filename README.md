# GraceCommunity Church Web Application

A responsive, modern web application for a church built with Django, Tailwind CSS, and HTMX.

## Features

- **Home Page**: Hero section, mission/vision cards, daily verses, news section, and testimonials
- **News & Events**: Dynamic news listing with HTMX "Load More" functionality
- **Gallery**: Photo gallery with category filtering and lightbox modal
- **About Page**: Church history, mission, vision, and leadership information
- **Donations Page**: Information about giving and ways to contribute
- **Admin Interface**: Full Django admin for managing verses, news, testimonials, and gallery images

## Technology Stack

- **Backend**: Django 5.0+
- **Frontend Styling**: Tailwind CSS (via CDN)
- **Interactivity**: HTMX, Alpine.js
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Rich Text Editor**: django-ckeditor
- **Static Files**: WhiteNoise

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Website: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Project Structure

```
BBInternational/
├── manage.py
├── requirements.txt
├── church_app/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── church/               # Main application
│   ├── models.py        # Verse, NewsItem, Testimonial, GalleryImage
│   ├── views.py         # All view functions
│   ├── urls.py          # URL routing
│   ├── admin.py         # Admin configuration
│   └── templates/       # HTML templates
│       └── church/
│           ├── base.html
│           ├── home.html
│           └── partials/
├── static/              # Static files (CSS, JS, images)
├── media/               # User-uploaded files
└── db.sqlite3          # SQLite database (development)
```

## Models

- **Verse**: Daily/weekly Bible verses with featured status
- **NewsItem**: News articles and events with rich text content
- **Testimonial**: Member testimonials with approval workflow
- **GalleryImage**: Photo gallery images with categories

## Design System

- **Primary Brand Color**: `rgb(153, 0, 48)` (Deep Burgundy/Crimson)
- **Typography**: Sans-serif headings, serif/sans-serif body text
- **Layout**: Mobile-first responsive design
- **Components**: Cards, buttons, navigation with hover effects

## Admin Features

Access the admin panel at `/admin/` to:
- Manage verses (mark as featured, activate/deactivate)
- Create and publish news items
- Approve testimonials
- Upload gallery images with categories

## HTMX Features

- **Load More News**: Dynamically loads additional news items without page refresh
- **Gallery Filtering**: Filter gallery images by category
- **Mobile Menu**: Smooth mobile navigation toggle

## Development Notes

- The application uses Tailwind CSS via CDN for styling
- Alpine.js is used for interactive components (mobile menu, lightbox)
- HTMX handles dynamic content loading
- Media files are served in development mode automatically
- For production, configure proper static file serving and use PostgreSQL

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in `settings.py`
2. Configure `ALLOWED_HOSTS`
3. Set up PostgreSQL database
4. Configure static file serving (WhiteNoise is included)
5. Set up proper media file storage (AWS S3, etc.)
6. Use environment variables for `SECRET_KEY`
7. Set up SSL/HTTPS

## License

This project is created for GraceCommunity Church.
