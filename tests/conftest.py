# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from unittest.mock import patch, MagicMock
import pytest
import google.auth
import google.auth.credentials

# Ensure standard test env vars
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "onboarding-project-fde")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")


@pytest.fixture(autouse=True, scope="session")
def mock_google_auth_default_if_missing():
    """Autouse fixture to provide mock GCP credentials if no ADC is configured in test environment."""
    try:
        google.auth.default()
    except Exception:
        mock_creds = MagicMock(spec=google.auth.credentials.Credentials)
        mock_creds.token = "mock-token-for-testing"
        mock_creds.valid = True

        def _mock_default(*args, **kwargs):
            return mock_creds, os.environ.get("GOOGLE_CLOUD_PROJECT", "onboarding-project-fde")

        with patch("google.auth.default", side_effect=_mock_default):
            yield
    else:
        yield
