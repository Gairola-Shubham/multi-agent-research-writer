from unittest.mock import MagicMock, patch

import pytest
import requests
from streamlit.testing.v1 import AppTest


@pytest.fixture(autouse=True)
def mock_export_service():
    """Globally mock ExportService in frontend tests to avoid file generation."""
    with patch("frontend.app.ExportService") as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_requests_post():
    """Globally mock requests.post in frontend tests to avoid outbound HTTP calls."""
    with patch("requests.post") as mock:
        # Mock successful response by default
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "topic": "AI Research",
            "title": "Compelling Title",
            "final_markdown": "# Compelling Title\n\nDeep research content.",
            "review": {
                "score": 95,
                "strengths": ["Clear structure"],
                "issues": ["Typo in heading"],
                "suggestions": ["Fix heading typo"],
                "ready_for_editing": True,
            },
            "changes_applied": ["Polished draft", "Corrected grammar"],
            "sources": [{"title": "Source Alpha", "url": "http://alpha.com"}],
            "memory_hits": ["Hit 1 from memory"],
        }
        mock.return_value = mock_response
        yield mock


def test_streamlit_app_imports():
    """Verify frontend/app.py can be imported and executed using Streamlit AppTest."""
    at = AppTest.from_file("frontend/app.py").run()
    assert not at.exception


def test_streamlit_widgets_exist():
    """Verify that all main widgets exist on the Streamlit page."""
    at = AppTest.from_file("frontend/app.py").run()

    # Selectboxes
    selectbox_labels = [s.label for s in at.selectbox]
    assert "Writing Style" in selectbox_labels
    assert "Research Depth" in selectbox_labels

    # Text input for topic
    text_input_labels = [t.label for t in at.text_input]
    assert "Research Topic" in text_input_labels

    # Standard Buttons
    button_labels = [b.label for b in at.button]
    assert "Generate Research" in button_labels
    assert "Clear Results" in button_labels

    # Download Buttons (treated as UnknownElements in AppTest)
    download_buttons = at.get("download_button")
    download_labels = [el.proto.label for el in download_buttons]
    assert "Download PDF" in download_labels
    assert "Download DOCX" in download_labels
    assert "Download Markdown" in download_labels


def test_streamlit_session_state_initializes():
    """Verify session state initializes correctly."""
    at = AppTest.from_file("frontend/app.py").run()
    assert at.session_state["topic"] == ""
    assert at.session_state["style"] == "Academic"
    assert at.session_state["depth"] == "Standard"
    assert at.session_state["result"] is None


def test_streamlit_generate_button_click_success(mock_requests_post):
    """Verify the generate button click makes a POST request and updates state."""
    at = AppTest.from_file("frontend/app.py").run()

    # Set the text input topic
    at.text_input[0].set_value("AI Research").run()

    # Click the generate button (first button is 'Generate Research')
    at.button[0].click().run()

    # Verify requests.post was called with correct payload
    mock_requests_post.assert_called_once()
    args, kwargs = mock_requests_post.call_args
    assert "AI Research" in kwargs["json"]["topic"]
    assert kwargs["json"]["style"] == "Academic"
    assert kwargs["json"]["depth"] == "Standard"

    # Check that session state result is updated
    assert at.session_state["result"] is not None
    assert at.session_state["result"]["title"] == "Compelling Title"


def test_streamlit_generate_button_click_empty_topic(mock_requests_post):
    """Verify error checking for empty topic."""
    at = AppTest.from_file("frontend/app.py").run()
    at.text_input[0].set_value("").run()
    at.button[0].click().run()

    # requests.post should not be called for empty topic
    mock_requests_post.assert_not_called()
    assert at.session_state["result"] is None


def test_streamlit_generate_button_click_failure(mock_requests_post):
    """Verify handling of backend server connection failure."""
    # Force ConnectionError
    mock_requests_post.side_effect = requests.exceptions.ConnectionError(
        "Backend connection refused"
    )

    at = AppTest.from_file("frontend/app.py").run()
    at.text_input[0].set_value("AI Research").run()
    at.button[0].click().run()

    # Verify result is still None
    assert at.session_state["result"] is None
