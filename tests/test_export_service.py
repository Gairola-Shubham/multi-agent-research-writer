import os
import pytest
from backend.utils.export_service import ExportService


@pytest.fixture
def sample_report():
    return {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Future",
        "final_markdown": "# Quantum Computing Future\n\nThis is the final report content with **bold** text and `inline code`.\n\n## Section 1\n- Bullet item 1\n- Bullet item 2\n\n### Sub-section\n```python\nprint('hello world')\n```",
        "review": {
            "score": 92,
            "strengths": ["Clear intro", "Good structure"],
            "issues": ["Typo in paragraph 2"],
            "suggestions": ["Correct typo"],
            "ready_for_editing": True
        },
        "changes_applied": ["Fixed grammar in section 1", "Addressed review suggestions"]
    }


def test_export_markdown(tmp_path, sample_report):
    """
    Verify that export_markdown generates a valid Markdown file and returns its path.
    """
    output_path = str(tmp_path / "report.md")
    
    # Run export
    res_path = ExportService.export_markdown(sample_report, output_path)
    
    # Assertions
    assert os.path.exists(res_path)
    assert res_path == os.path.abspath(output_path)
    
    # Read back and verify content
    with open(res_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == sample_report["final_markdown"]


def test_export_pdf(tmp_path, sample_report):
    """
    Verify that export_pdf generates a valid PDF file with ReportLab and returns its path.
    """
    output_path = str(tmp_path / "report.pdf")
    
    res_path = ExportService.export_pdf(sample_report, output_path)
    
    assert os.path.exists(res_path)
    assert res_path == os.path.abspath(output_path)
    assert os.path.getsize(res_path) > 0


def test_export_docx(tmp_path, sample_report):
    """
    Verify that export_docx generates a valid DOCX file using python-docx and returns its path.
    """
    output_path = str(tmp_path / "report.docx")
    
    res_path = ExportService.export_docx(sample_report, output_path)
    
    assert os.path.exists(res_path)
    assert res_path == os.path.abspath(output_path)
    assert os.path.getsize(res_path) > 0


def test_export_invalid_path(tmp_path, sample_report):
    """
    Verify that export functions raise a ValueError when target directory does not exist or target is a directory.
    """
    # Parent directory does not exist
    invalid_dir_path = str(tmp_path / "non_existent_folder" / "report.md")
    with pytest.raises(ValueError, match="Target directory does not exist"):
        ExportService.export_markdown(sample_report, invalid_dir_path)
        
    # Output path is a directory
    dir_path = str(tmp_path)
    with pytest.raises(ValueError, match="Output path is a directory"):
        ExportService.export_markdown(sample_report, dir_path)


def test_export_missing_fields(tmp_path, sample_report):
    """
    Verify that export functions validate missing fields and raise a ValueError.
    """
    output_path = str(tmp_path / "report.md")
    
    # Missing topic
    bad_report = sample_report.copy()
    del bad_report["topic"]
    with pytest.raises(ValueError, match="Missing required field: topic"):
        ExportService.export_markdown(bad_report, output_path)
        
    # Missing title
    bad_report = sample_report.copy()
    del bad_report["title"]
    with pytest.raises(ValueError, match="Missing required field: title"):
        ExportService.export_markdown(bad_report, output_path)
        
    # Missing review
    bad_report = sample_report.copy()
    del bad_report["review"]
    with pytest.raises(ValueError, match="Missing required field: review"):
        ExportService.export_markdown(bad_report, output_path)
        
    # Review is not a dictionary
    bad_report = sample_report.copy()
    bad_report["review"] = "excellent"
    with pytest.raises(ValueError, match="Field 'review' must be a dictionary"):
        ExportService.export_markdown(bad_report, output_path)
        
    # changes_applied is not a list
    bad_report = sample_report.copy()
    bad_report["changes_applied"] = "none"
    with pytest.raises(ValueError, match="Field 'changes_applied' must be a list"):
        ExportService.export_markdown(bad_report, output_path)


def test_export_overwrite_existing_file(tmp_path, sample_report):
    """
    Verify that export functions successfully overwrite existing files.
    """
    output_path = str(tmp_path / "report.md")
    
    # Write dummy file content
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Old stale data")
        
    # Run export
    res_path = ExportService.export_markdown(sample_report, output_path)
    
    # Assertions to verify the file was overwritten
    with open(res_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == sample_report["final_markdown"]
    assert content != "Old stale data"
