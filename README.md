# Riyadh Al Bilad Transport for KSA

A production-ready Django website for vehicle rental and transportation services in Saudi Arabia.

## Features
- Category-based vehicle catalog.
- Vehicle detail pages with image galleries.
- WhatsApp integration for bookings.
- Floating support button.
- AI-powered chatbot (Phase 1: Rule-based, Phase 2: DeepSeek).

## Tech Stack
- Backend: Django, Django Rest Framework
- Frontend: Django Templates, Tailwind CSS (CDN)
- Database: SQLite (Dev), PostgreSQL-ready

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Copy `.env.example` to `.env` and update the values:
   ```bash
   cp .env.example .env
   ```
   - `DEEPSEEK_API_KEY` is optional for Phase 2 chatbot replies.
   - `SUPPORT_WHATSAPP_NUMBER` is used as a fallback if no Site Setting exists.

3. **Migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Demo Data (Optional):**
   ```bash
   python manage.py loaddata demo_data.json
   ```

5. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Server:**
   ```bash
   python manage.py runserver
   ```

## Google Drive Images Note
When using `image_url` for Google Drive, ensure the link is public. The templates also support standard Drive share links (they are converted to direct image URLs automatically).

## Admin Notes
- Add or update the single **Site Setting** record to manage the global WhatsApp support number.
- Use the Vehicle Images inline to mark one image as primary and order the gallery.

## Project Structure
- `config/`: Configuration and settings.
- `apps/core/`: Homepage and site-wide settings.
- `apps/catalog/`: Categories, vehicles, and images.
- `apps/chatbot/`: API and logic for the support assistant.
- `templates/`: Global and app-specific templates.
