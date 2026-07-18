import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.domain.models import Assessment, Career, Roadmap, RoadmapStep, Skill, UserProfile
from ai.service import (
    AIClient,
    AIService,
    PromptBuilder,
    ResponseValidator,
    _cache_key,
)


@pytest.fixture
def sample_assessment():
    return Assessment(
        user_profile=UserProfile(
            name="Test User",
            skills=[Skill(name="Linux", category="OS", difficulty="beginner")],
        ),
        target_career=Career(
            id="soc-analyst",
            title="SOC Analyst",
            description="Monitors security alerts",
            required_skills=["Linux", "Networking", "SIEM", "Log Analysis"],
        ),
        matched_skills=[Skill(name="Linux", category="OS", difficulty="beginner")],
        missing_skills=[
            Skill(name="Networking", category="Networking", difficulty="beginner"),
            Skill(name="SIEM", category="Defensive", difficulty="intermediate"),
        ],
        readiness_score=25,
    )


@pytest.fixture
def sample_roadmap():
    return Roadmap(
        steps=[
            RoadmapStep(step=1, skill=Skill(name="Networking", category="Networking", difficulty="beginner"), estimated_hours=15),
            RoadmapStep(step=2, skill=Skill(name="SIEM", category="Defensive", difficulty="intermediate"), estimated_hours=15),
        ],
        total_hours=30,
        estimated_weeks=3,
    )


class TestResponseValidator:
    def test_validate_json_valid(self):
        text = '{"skills": ["Linux", "Python"]}'
        result = ResponseValidator.validate_json(text)
        assert result is not None
        assert result["skills"] == ["Linux", "Python"]

    def test_validate_json_with_code_block(self):
        text = '```json\n{"skills": ["Linux"]}\n```'
        result = ResponseValidator.validate_json(text)
        assert result is not None
        assert result["skills"] == ["Linux"]

    def test_validate_json_malformed(self):
        assert ResponseValidator.validate_json("not json") is None
        assert ResponseValidator.validate_json("") is None
        assert ResponseValidator.validate_json("{incomplete") is None

    def test_validate_json_array(self):
        text = "[1, 2, 3]"
        result = ResponseValidator.validate_json(text)
        assert result is not None
        assert result == [1, 2, 3]

    def test_hallucination_check_passes(self):
        text = "You need Linux and Python skills for this role."
        known = ["Linux", "Python", "Networking"]
        assert ResponseValidator.validate_no_hallucinations(text, known) is True

    def test_hallucination_check_catches_unknown(self):
        text = "You need Quantum Computing skills."
        known = ["Linux", "Python"]
        assert ResponseValidator.validate_no_hallucinations(text, known) is False

    def test_hallucination_check_empty_text(self):
        assert ResponseValidator.validate_no_hallucinations("", ["Linux"]) is True

    def test_compute_confidence_high(self):
        text = "Based on your profile, you should learn SIEM and Networking next."
        known = ["Linux", "SIEM", "Networking"]
        confidence = ResponseValidator.compute_confidence(text, known)
        assert confidence > 0.7

    def test_compute_confidence_low(self):
        text = "Learn stuff."
        known = ["Linux", "Python"]
        confidence = ResponseValidator.compute_confidence(text, known)
        assert confidence < 0.6

    def test_extract_skills_from_json(self):
        data = {"skills": ["Linux", "Python"], "projects": ["Lab"], "certifications": ["Sec+"], "extra": "ignored"}
        result = ResponseValidator.extract_skills_from_json(data)
        assert result["skills"] == ["Linux", "Python"]
        assert result["projects"] == ["Lab"]
        assert result["certifications"] == ["Sec+"]

    def test_extract_skills_from_non_dict(self):
        result = ResponseValidator.extract_skills_from_json("not a dict")
        assert result == {"skills": [], "projects": [], "certifications": []}


class TestPromptBuilder:
    def test_resume_extraction(self):
        pb = PromptBuilder()
        system, prompt = pb.build_resume_extraction("John Doe, Linux admin, Python developer")
        assert "linux" in system.lower() or "resume" in system.lower()
        assert "John Doe" in prompt

    def test_roadmap_explanation(self, sample_assessment, sample_roadmap):
        pb = PromptBuilder()
        system, prompt = pb.build_roadmap_explanation(sample_assessment, sample_roadmap)
        assert "SOC Analyst" in prompt
        assert "25" in prompt
        assert "Networking" in prompt

    def test_career_explanation(self, sample_assessment):
        pb = PromptBuilder()
        system, prompt = pb.build_career_explanation(sample_assessment)
        assert "SOC Analyst" in prompt
        assert "25" in prompt

    def test_mentor_prompt(self, sample_assessment):
        pb = PromptBuilder()
        system, prompt = pb.build_mentor_prompt(sample_assessment, "How do I learn SIEM?")
        assert "How do I learn SIEM?" in prompt
        assert "SOC Analyst" in prompt

    def test_resume_review(self):
        pb = PromptBuilder()
        system, prompt = pb.build_resume_review("Skills: Linux, Python", "SOC Analyst")
        assert "SOC Analyst" in prompt
        assert "Linux" in prompt


class TestCacheKey:
    def test_same_inputs_same_key(self):
        k1 = _cache_key("test", "a", "b")
        k2 = _cache_key("test", "a", "b")
        assert k1 == k2

    def test_different_inputs_different_key(self):
        k1 = _cache_key("test", "a")
        k2 = _cache_key("test", "b")
        assert k1 != k2

    def test_different_prefix_different_key(self):
        k1 = _cache_key("prefix1", "a")
        k2 = _cache_key("prefix2", "a")
        assert k1 != k2


class TestAIClient:
    @pytest.mark.asyncio
    async def test_chat_success(self):
        client = AIClient(api_keys=["test-key"])
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Hello"}}]}
        mock_response.raise_for_status = MagicMock()

        with patch("ai.service.httpx.AsyncClient") as mock_httpx:
            mock_instance = AsyncMock()
            mock_instance.post.return_value = mock_response
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_httpx.return_value = mock_instance

            result = await client.chat("test prompt")
            assert result == "Hello"

    @pytest.mark.asyncio
    async def test_chat_retries_on_failure(self):
        client = AIClient(api_keys=["test-key"])

        with patch("ai.service.httpx.AsyncClient") as mock_httpx:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = httpx.RequestError("Network error")
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_httpx.return_value = mock_instance

            with pytest.raises(RuntimeError, match="Mistral API failed"):
                await client.chat("test prompt")

    @pytest.mark.asyncio
    async def test_chat_fallback_model_success(self):
        client = AIClient(api_keys=["test-key"])

        mock_response_ok = MagicMock()
        mock_response_ok.json.return_value = {"choices": [{"message": {"content": "Fallback Success"}}]}
        mock_response_ok.raise_for_status = MagicMock()

        call_count = 0
        async def mock_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise httpx.RequestError("Primary failed")
            return mock_response_ok

        with patch("ai.service.httpx.AsyncClient") as mock_httpx:
            mock_instance = AsyncMock()
            mock_instance.post.side_effect = mock_post
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=False)
            mock_httpx.return_value = mock_instance

            result = await client.chat("test prompt")
            assert result == "Fallback Success"


class TestAIService:
    @pytest.mark.asyncio
    async def test_extract_skills_fallback(self):
        client = AIClient(api_keys=["test-key"])
        service = AIService(client)

        with patch.object(client, "chat", side_effect=RuntimeError("API down")):
            result = await service.extract_skills_from_resume("some resume")
            assert "skills" in result
            assert isinstance(result["skills"], list)

    @pytest.mark.asyncio
    async def test_explain_roadmap_fallback(self, sample_assessment, sample_roadmap):
        client = AIClient(api_keys=["test-key"])
        service = AIService(client)

        with patch.object(client, "chat", side_effect=RuntimeError("API down")):
            text, confidence = await service.explain_roadmap(sample_assessment, sample_roadmap)
            assert isinstance(text, str)
            assert 0 <= confidence <= 1

    @pytest.mark.asyncio
    async def test_mentor_chat_raises_on_api_failure(self, sample_assessment):
        client = AIClient(api_keys=["test-key"])
        service = AIService(client)

        with patch.object(client, "chat_with_history", side_effect=RuntimeError("API down")):
            with pytest.raises(RuntimeError, match="API down"):
                await service.mentor_chat(sample_assessment, "What should I learn?")

    @pytest.mark.asyncio
    async def test_mentor_chat_with_session(self, sample_assessment):
        client = AIClient(api_keys=["test-key"])
        service = AIService(client)

        with patch.object(client, "chat_with_history", return_value="Great question!"):
            await service.mentor_chat(sample_assessment, "Question 1", session_id="test-session")
            await service.mentor_chat(sample_assessment, "Question 2", session_id="test-session")
            assert len(service._conversation_history["test-session"][0]) == 4

    def test_clear_session(self):
        client = AIClient(api_keys=["test-key"])
        service = AIService(client)
        service._conversation_history["test"] = [{"role": "user", "content": "hi"}]
        service.clear_session("test")
        assert "test" not in service._conversation_history
