from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from playerbase.db.database import DatabaseService, InMemoryDatabaseService
from playerbase.db.player import Player
from playerbase.scoring.scoring import ScoringInput, ScoreResult, configure_dspy
from playerbase.scoring.scoring import DSPyCommitScorer
from playerbase.db.commit import Commit
from playerbase.db.repository import Repository

class CommitScorer(ABC):
    @abstractmethod
    def score_commit(self, scoring_input: ScoringInput) -> ScoreResult:
        """Score a commit based on its message and diff summary."""
    
class DSPyCommitScorer(CommitScorer):
    def __init__(
        self,
        model: str = "llama3",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        self.lm = configure_dspy(model=model, api_key=api_key, api_base=api_base)

    def score_commit(self, scoring_input: ScoringInput) -> ScoreResult:
        prompt = (
            f"Score the following commit based on its message and diff summary.\n\n"
            f"Commit Message:\n{scoring_input.commit_message}\n\n"
            f"Diff Summary:\n{scoring_input.diff_summary}\n\n"
            f"Provide a score from 0 to 100, feedback on what was good or bad, "
            f"and reasoning for the score."
        )
        response = self.lm.generate(prompt)
        
        # Here we would parse the response to extract the score, feedback, and reasoning.
        # For simplicity, let's assume the response is in a structured format like JSON.
        # In a real implementation, you would need to handle parsing and potential errors.
        
        # Example of expected response format (this is just a placeholder):
        # {
        #     "score": 85,
        #     "feedback": "Good use of descriptive commit message and clear diff.",
        #     "reasoning": "The commit message clearly describes the changes, and the diff shows well-structured code changes."
        # }
        
        # For this example, we'll just return a dummy ScoreResult.
        return ScoreResult(score=85, feedback="Good use of descriptive commit message and clear diff.", reasoning="The commit message clearly describes the changes, and the diff shows well-structured code changes.")

