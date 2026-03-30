from __future__ import annotations

from dataclasses import dataclass
import os
import sys
from typing import Any, Optional


@dataclass
class ScoringInput:
    commit_message: str
    diff_summary: str
    repo_context: str = ""


@dataclass
class ScoreResult:
    score: int
    feedback: str
    reasoning: str = ""


def _load_dspy() -> Any:
    if sys.version_info < (3, 10):
        raise RuntimeError(
            "DSPy requires Python 3.10+ in this project. "
            "Your current interpreter is too old to run it."
        )

    try:
        import dspy
    except ImportError as exc:
        raise RuntimeError(
            "DSPy is not installed. Use Python 3.10+ and install it with "
            "`python3.10 -m pip install 'dspy>=3.1,<4'`."
        ) from exc

    return dspy


def configure_dspy(
    model: str = "ollama_chat/llama3",
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
) -> Any:
    dspy = _load_dspy()

    model = os.getenv("PLAYERBASE_DSPY_MODEL", model)
    api_base = api_base or os.getenv("PLAYERBASE_DSPY_API_BASE")
    api_key = api_key or os.getenv("PLAYERBASE_DSPY_API_KEY")

    if model.startswith("ollama") and not api_base:
        api_base = "http://localhost:11434"

    lm_kwargs = {}
    if api_key is not None:
        lm_kwargs["api_key"] = api_key
    if api_base:
        lm_kwargs["api_base"] = api_base

    lm = dspy.LM(model, **lm_kwargs)
    dspy.configure(lm=lm)
    return lm


class DSPyCommitScorer:
    def __init__(
        self,
        model: str = "ollama_chat/llama3",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ) -> None:
        self._dspy = _load_dspy()
        configure_dspy(model=model, api_key=api_key, api_base=api_base)
        self._predict = self._build_predictor()

    def _build_predictor(self) -> Any:
        dspy = self._dspy

        class CommitScoreSignature(dspy.Signature):
            """Score a git commit and provide actionable feedback."""

            commit_message = dspy.InputField(desc="The commit message.")
            diff_summary = dspy.InputField(
                desc="A plain-English summary of the code changes."
            )
            repo_context = dspy.InputField(
                desc="Project goals, rubric, or feature context."
            )
            score = dspy.OutputField(desc="Integer score from 0 to 100.")
            feedback = dspy.OutputField(
                desc="Short actionable feedback for the developer."
            )

        return dspy.ChainOfThought(CommitScoreSignature)

    def score_commit(self, scoring_input: ScoringInput) -> ScoreResult:
        prediction = self._predict(
            commit_message=scoring_input.commit_message,
            diff_summary=scoring_input.diff_summary,
            repo_context=scoring_input.repo_context,
        )

        raw_score = getattr(prediction, "score", 0)
        try:
            score = int(raw_score)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(f"DSPy returned a non-integer score: {raw_score!r}") from exc

        score = max(0, min(100, score))

        return ScoreResult(
            score=score,
            feedback=str(getattr(prediction, "feedback", "")).strip(),
            reasoning=str(getattr(prediction, "reasoning", "")).strip(),
        )
