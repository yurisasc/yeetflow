# Database Migrations with Alembic

This project uses Alembic for database schema migrations with SQLModel models.

## Setup

Alembic has been configured to work with SQLModel and async SQLite operations.

## Available Commands

### Using Alembic directly
```bash
# Show current migration
uv run alembic current

# Show migration history
uv run alembic history

# Apply all pending migrations
uv run alembic upgrade head

# Downgrade to previous migration
uv run alembic downgrade -1

# Create a new migration
uv run alembic revision --autogenerate -m "Description of changes"
```

### Using npm scripts (via package.json)
```bash
# Show current migration
npm run db:current

# Show migration history
npm run db:history

# Apply all pending migrations
npm run db:upgrade

# Downgrade one migration
npm run db:downgrade

# Reset database (remove all tables)
npm run db:reset

# Create new migration (provide message)
npm run db:migrate -- "Description of changes"

# Mark database as up-to-date
npm run db:stamp
```

## Configuration

- **alembic.ini**: Alembic configuration (DB URL is read from environment in `alembic/env.py`)
- **alembic/env.py**: Configured for async SQLModel operations
- **alembic/versions/**: Migration files are stored here

## Creating New Migrations

1. Make changes to your SQLModel models in `app/models.py`
2. Generate a new migration:
   ```bash
   uv run alembic revision --autogenerate -m "Description of changes"
   ```
3. Review the generated migration file
4. Apply the migration:
   ```bash
   uv run alembic upgrade head
   ```

## Initial Setup

The initial migration (`b9f712cd6fa9_initial_schema_creation_with_sqlmodel`) represents the current SQLModel schema. Since the database already exists with the correct schema, this is a baseline migration that serves as the starting point for future changes.

## Troubleshooting

- **SQLite ALTER TABLE limitations**: SQLite has limited ALTER TABLE support. For complex schema changes, you may need to create new tables and migrate data.
- **Async operations**: The migration environment is configured for async SQLAlchemy operations.
- **Model imports**: All models are imported in `alembic/env.py` to ensure they're registered with SQLModel.metadata.
