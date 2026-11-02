import os

# Dummy config so the fast suite never depends on a real .env or live services.
# Real env vars override .env in pydantic-settings, so these win over local secrets.
os.environ.update(
    SUPABASE_URL="https://test.supabase.co",
    SUPABASE_ANON_KEY="test-anon-key",
    SUPABASE_SERVICE_ROLE_KEY="test-service-role-key",
    DATABASE_URL="postgresql://postgres:test@localhost:5432/postgres",
    OPENAI_API_KEY="sk-test",
    ALLOWED_ORIGINS="http://localhost:5173",
)
