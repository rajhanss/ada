from __future__ import annotations

import pytest


@pytest.fixture
def settings():
    from ada.config import Settings
    return Settings(
        environment="test",
        debug=True,
        secret_key="test-secret-key-min-32-chars-padding",
        supabase_url="http://localhost:54321",
        supabase_anon_key="test-anon-key",
        supabase_service_role_key="test-service-role-key",
    )
