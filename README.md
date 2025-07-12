# MeteorMate Backend

Roommate matching platform for college students. Find your perfect living situation through AI-powered compatibility matching.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Database (via Supabase)
- **Firebase Auth** - User authentication
- **Alembic** - Database migrations

## Setup

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd meteormate_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Environment setup**
   ```bash
   cp .env.example .env
   # Fill in your actual values
   ```

6. **Database setup**
   ```bash
   alembic upgrade head
   ```

## Environment Variables

Create a `.env` file with:

```env
DATABASE_URL=postgresql://user:password@localhost/meteormate
SECRET_KEY=your-super-secret-key-here
FIREBASE_CREDENTIALS_PATH=path/to/firebase-key.json
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
DEBUG=true
```

## Development

**Run the server:**
```bash
uvicorn app.main:app --reload
```

**Formatting:**
- Code is auto-formatted on commit using YAPF
- Manual format: `yapf --in-place --recursive .`

**Database migrations:**
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `GET /api/auth/me` - Get current user

### Survey
- `POST /api/survey/` - Create roommate preference survey
- `GET /api/survey/me` - Get user's survey
- `PUT /api/survey/` - Update survey

### Matches
- `GET /api/matches/potential` - Get potential roommate matches
- `POST /api/matches/like/{user_id}` - Like a potential match
- `POST /api/matches/pass/{user_id}` - Pass on a match
- `GET /api/matches/mutual` - Get mutual matches

## Project Structure

```
app/
├── api/          # Route handlers
├── models/       # Database models
├── schemas/      # Pydantic schemas
├── services/     # Business logic
├── utils/        # Utility functions
└── main.py       # FastAPI app
```

## Contributing

1. Create feature branch
2. Make changes
3. Pre-commit hooks will format code
4. Submit PR

The matching algorithm considers budget overlap, lifestyle compatibility, and shared interests to find the best roommate fits.
This will be re-done by the AI dev(s), this is just an interim solution.