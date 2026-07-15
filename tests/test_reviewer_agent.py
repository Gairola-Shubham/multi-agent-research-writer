import pytest

from backend.agents.reviewer_agent import ReviewerAgent


def test_reviewer_agent_import():
    """Verify ReviewerAgent can be imported."""
    agent = ReviewerAgent()
    assert agent is not None


def test_reviewer_agent_review_perfect_report():
    """Verify ReviewerAgent assigns high/perfect score for a
    comprehensive, well-structured report.
    """
    agent = ReviewerAgent()

    # A long report (length > 1000) with a title and content in all sections
    perfect_markdown = (
        "# Quantum Computing Overview\n\n"
        "## Introduction\n"
        "Quantum computing is a rapidly-emerging technology that harnesses "
        "the laws of quantum mechanics to solve problems too complex for "
        "classical computers. It utilizes qubits rather than standard bits. "
        "This allows parallel processing capabilities that could revolutionize "
        "fields like chemistry, optimization, and cryptography. The "
        "development of physical quantum processors requires sophisticated "
        "engineering.\n\n"
        "## Core Concepts\n"
        "Key principles of quantum physics include superposition, entanglement, "
        "and interference. Superposition allows a qubit to exist in multiple "
        "states simultaneously until measured. Entanglement links the state "
        "of one qubit with another instantly, regardless of distance. "
        "Interference is used to bias the measurement probabilities towards "
        "correct solutions. Together, these form the computational basis for "
        "quantum algorithms.\n\n"
        "## Applications\n"
        "Applications of quantum computing are vast. In pharmaceutical "
        "research, quantum computers can simulate molecular interactions to "
        "accelerate drug discovery. In finance, they can optimize large "
        "portfolios and improve risk assessment. For logistics, they solve "
        "routing optimization problems that grow exponentially. Cryptography "
        "will also be impacted by Shor's algorithm for factoring primes.\n\n"
        "## Challenges\n"
        "The primary challenge is quantum decoherence, where qubits lose "
        "their quantum state due to environmental noise. Researchers use "
        "quantum error correction codes, but these require substantial "
        "physical qubit overhead. Cooling systems must keep processors near "
        "absolute zero, adding immense physical and financial complexity.\n\n"
        "## Conclusion\n"
        "In conclusion, while practical fault-tolerant quantum computers "
        "are still years away, progress in hardware development and quantum "
        "algorithms is steady. The next decade will likely see the first "
        "commercial-scale quantum superiority application demonstrated in "
        "specialized industries."
    )

    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": perfect_markdown,
        "sections": [
            "Introduction",
            "Core Concepts",
            "Applications",
            "Challenges",
            "Conclusion",
        ],
    }

    results = agent.review_report(report_output)

    assert results["score"] == 100
    assert "Report generated successfully" in results["strengths"]
    assert "All planned sections completed" in results["strengths"]
    assert "Markdown structure is valid" in results["strengths"]
    assert not results["issues"]
    assert results["ready_for_editing"] is True


def test_reviewer_agent_review_short_report():
    """Verify ReviewerAgent scores short/incomplete report lower."""
    agent = ReviewerAgent()

    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": "# Quantum Computing Overview\n\n## Introduction\nToo short.",
        "sections": ["Introduction", "Core Concepts"],
    }

    results = agent.review_report(report_output)

    # Score should be lower because it is < 200 characters and missing sections
    assert results["score"] < 100
    assert any("short" in issue or "brief" in issue for issue in results["issues"])
    assert any("Missing planned sections" in issue for issue in results["issues"])


def test_reviewer_agent_missing_sections():
    """Verify that missing sections are detected and score is reduced."""
    agent = ReviewerAgent()

    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": (
            "# Quantum Computing Overview\n\n"
            "## Introduction\n"
            "This is the intro section content.\n\n"
            "## Conclusion\n"
            "This is the conclusion section content."
        ),
        # Plan expects Core Concepts, but they are missing from markdown
        "sections": ["Introduction", "Core Concepts", "Conclusion"],
    }

    results = agent.review_report(report_output)

    # Score should not be 100 because of missing Core Concepts
    assert results["score"] < 100
    assert any("Missing planned sections" in issue for issue in results["issues"])
    assert any("Core Concepts" in issue for issue in results["issues"])


def test_reviewer_agent_empty_sections():
    """Verify that empty sections are detected and reduce the score."""
    agent = ReviewerAgent()

    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": (
            "# Quantum Computing Overview\n\n"
            "## Introduction\n\n\n"
            "## Conclusion\n"
            "This section has content."
        ),
        "sections": ["Introduction", "Conclusion"],
    }

    results = agent.review_report(report_output)

    assert results["score"] < 100
    assert any("Empty sections detected" in issue for issue in results["issues"])
    assert any("Introduction" in issue for issue in results["issues"])


def test_reviewer_agent_duplicate_headings():
    """Verify that duplicate headings are flagged and reduce the score."""
    agent = ReviewerAgent()

    report_output = {
        "topic": "Quantum Computing",
        "title": "Quantum Computing Overview",
        "markdown": (
            "# Quantum Computing Overview\n\n"
            "## Introduction\n"
            "Intro content\n\n"
            "## Introduction\n"
            "Duplicate intro content"
        ),
        "sections": ["Introduction"],
    }

    results = agent.review_report(report_output)

    assert results["score"] < 100
    assert any("Duplicate headings found" in issue for issue in results["issues"])
    assert any("Introduction" in issue for issue in results["issues"])


def test_reviewer_agent_invalid_report_inputs():
    """Verify review_report validates its input dictionary."""
    agent = ReviewerAgent()

    # Non-dictionary input
    with pytest.raises(ValueError, match="Input report_output must be a dictionary"):
        agent.review_report("not a dict")

    # Missing topic
    with pytest.raises(ValueError, match="Input report_output is missing 'topic'"):
        agent.review_report({"title": "A Title", "markdown": "Some md"})

    # Missing title
    with pytest.raises(ValueError, match="Input report_output is missing 'title'"):
        agent.review_report({"topic": "Quantum Computing", "markdown": "Some md"})

    # Missing markdown
    with pytest.raises(ValueError, match="Input report_output is missing 'markdown'"):
        agent.review_report({"topic": "Quantum Computing", "title": "A Title"})
