"""
Natural language processing for diagram generation.

This module provides NLP capabilities for understanding and processing
natural language descriptions for diagram generation.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class EntityExtraction:
    """Result of entity extraction from text."""

    entities: list[str]
    entity_types: dict[str, str]
    relationships: list[dict[str, str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "entities": self.entities,
            "entity_types": self.entity_types,
            "relationships": self.relationships,
        }


@dataclass
class IntentClassification:
    """Result of intent classification."""

    intent: str
    confidence: float
    sub_intents: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "sub_intents": self.sub_intents,
        }


@dataclass
class TextAnalysis:
    """Complete analysis of input text."""

    text: str
    keywords: list[str]
    entities: EntityExtraction | None
    intent: IntentClassification | None
    complexity_score: float
    domain: str
    language: str = "en"
    processed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "keywords": self.keywords,
            "entities": self.entities.to_dict() if self.entities else None,
            "intent": self.intent.to_dict() if self.intent else None,
            "complexity_score": self.complexity_score,
            "domain": self.domain,
            "language": self.language,
            "processed_at": self.processed_at.isoformat(),
        }


class NLProcessor:
    """
    Natural language processor for diagram generation.

    Provides text analysis, entity extraction, and intent classification
    to understand user requirements for diagram generation.
    """

    def __init__(self) -> None:
        """Initialize NL processor."""
        self.domain_keywords: dict[str, list[str]] = self._load_domain_keywords()
        self.intent_patterns: dict[str, list[str]] = self._load_intent_patterns()
        self.entity_patterns: dict[str, list[str]] = self._load_entity_patterns()
        self.stopwords: set[str] = self._load_stopwords()

    def analyze_text(self, text: str) -> TextAnalysis:
        """
        Perform complete analysis of input text.

        Args:
            text: Input text to analyze

        Returns:
            Complete text analysis
        """
        # Extract keywords
        keywords = self.extract_keywords(text)

        # Extract entities
        entities = self.extract_entities(text)

        # Classify intent
        intent = self.classify_intent(text)

        # Calculate complexity
        complexity = self.calculate_complexity(text)

        # Determine domain
        domain = self.determine_domain(text, keywords)

        return TextAnalysis(
            text=text,
            keywords=keywords,
            entities=entities,
            intent=intent,
            complexity_score=complexity,
            domain=domain,
        )

    def extract_keywords(self, text: str) -> list[str]:
        """
        Extract keywords from text.

        Args:
            text: Input text

        Returns:
            List of extracted keywords
        """
        # Convert to lowercase and split into words
        words = re.findall(r"\b\w+\b", text.lower())

        # Remove stopwords
        keywords = [word for word in words if word not in self.stopwords]

        # Remove duplicates while preserving order
        seen: set[str] = set()
        unique_keywords: list[str] = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)

        # Filter by minimum length
        keywords = [kw for kw in unique_keywords if len(kw) > 2]

        # Sort by frequency and importance
        keyword_scores = self._score_keywords(keywords, text)
        sorted_keywords = sorted(
            keyword_scores.items(), key=lambda x: x[1], reverse=True
        )

        # Use underscore for the unused score binding to silence linters
        return [kw for kw, _score in sorted_keywords[:20]]  # Top 20 keywords

    def extract_entities(self, text: str) -> EntityExtraction:
        """
        Extract entities from text.

        Args:
            text: Input text

        Returns:
            Entity extraction result
        """
        entities: list[str] = []
        entity_types: dict[str, str] = {}
        relationships: list[dict[str, str]] = []

        # Extract using patterns
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = match.group(1) if match.groups() else match.group(0)
                    entity = entity.strip()

                    if entity and entity not in entities:
                        entities.append(entity)
                        entity_types[entity] = entity_type

        # Extract relationships
        relationships = self._extract_relationships(text, entities)

        return EntityExtraction(
            entities=entities,
            entity_types=entity_types,
            relationships=relationships,
        )

    def classify_intent(self, text: str) -> IntentClassification:
        """
        Classify the intent of the text.

        Args:
            text: Input text

        Returns:
            Intent classification result
        """
        text_lower = text.lower()

        # Score each intent based on patterns
        intent_scores: dict[str, float] = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1.0

            if score > 0.0:
                intent_scores[intent] = score / float(len(patterns))

        if not intent_scores:
            return IntentClassification(
                intent="create_diagram",
                confidence=0.5,
            )

        # Get highest scoring intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])

        # Get sub-intents (other high-scoring intents)
        sub_intents = [
            intent
            for intent, _score in intent_scores.items()
            if intent != best_intent[0] and _score >= 0.3
        ]

        return IntentClassification(
            intent=best_intent[0],
            confidence=min(best_intent[1], 1.0),
            sub_intents=sub_intents,
        )

    def calculate_complexity(self, text: str) -> float:
        """
        Calculate complexity score of the text.

        Args:
            text: Input text

        Returns:
            Complexity score (0.0 to 1.0)
        """
        # Factors that contribute to complexity
        word_count = len(text.split())
        sentence_count = len(re.split(r"[.!?]+", text))
        avg_sentence_length = word_count / max(sentence_count, 1)

        # Technical terms
        technical_terms = sum(
            1
            for word in text.lower().split()
            if word in self.domain_keywords.get("technical", [])
        )

        # Complexity indicators
        complexity_indicators = [
            "complex",
            "complicated",
            "multiple",
            "various",
            "different",
            "several",
            "many",
            "numerous",
            "detailed",
            "comprehensive",
        ]
        complexity_mentions = sum(
            1 for indicator in complexity_indicators if indicator in text.lower()
        )

        # Calculate score
        score = 0.0

        # Word count factor (0-0.3)
        if word_count > 100:
            score += 0.3
        elif word_count > 50:
            score += 0.2
        elif word_count > 20:
            score += 0.1

        # Sentence length factor (0-0.2)
        if avg_sentence_length > 20:
            score += 0.2
        elif avg_sentence_length > 15:
            score += 0.1

        # Technical terms factor (0-0.3)
        tech_ratio = technical_terms / max(word_count, 1)
        score += min(tech_ratio * 3, 0.3)

        # Complexity mentions factor (0-0.2)
        complexity_ratio = complexity_mentions / max(word_count, 1)
        score += min(complexity_ratio * 10, 0.2)

        return min(score, 1.0)

    def determine_domain(self, text: str, keywords: list[str]) -> str:
        """
        Determine the domain/field of the text.

        Args:
            text: Input text
            keywords: Extracted keywords

        Returns:
            Determined domain
        """
        text_lower = text.lower()
        domain_scores: dict[str, float] = {}

        # Score domains based on keyword matches
        for domain, domain_keywords in self.domain_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword in domain_keywords:
                    score += 1.0

            # Also check for domain-specific phrases in text
            for domain_keyword in domain_keywords:
                if domain_keyword in text_lower:
                    score += 0.5

            if score > 0.0:
                domain_scores[domain] = score

        if not domain_scores:
            return "general"

        return max(domain_scores.items(), key=lambda x: x[1])[0]

    def _score_keywords(self, keywords: list[str], text: str) -> dict[str, float]:
        """Score keywords by importance."""
        scores: dict[str, float] = {}
        text_lower = text.lower()

        for keyword in keywords:
            score = 0.0

            # Frequency score
            frequency = text_lower.count(keyword)
            score += float(frequency) * 0.1

            # Length bonus (longer words are often more important)
            score += float(len(keyword)) * 0.01

            # Domain relevance bonus
            for domain_keywords in self.domain_keywords.values():
                if keyword in domain_keywords:
                    score += 0.5
                    break

            # Position bonus (words at beginning are often more important)
            if keyword in text_lower[:100]:
                score += 0.2

            scores[keyword] = score

        return scores

    def _extract_relationships(
        self, text: str, entities: list[str]
    ) -> list[dict[str, str]]:
        """Extract relationships between entities."""
        relationships: list[dict[str, str]] = []

        # Simple relationship patterns
        relationship_patterns = [
            r"(\w+)\s+(?:connects to|links to|flows to|leads to)\s+(\w+)",
            r"(\w+)\s+(?:contains|includes|has)\s+(\w+)",
            r"(\w+)\s+(?:depends on|requires|needs)\s+(\w+)",
            r"(\w+)\s+(?:sends|passes|gives)\s+\w+\s+to\s+(\w+)",
        ]

        for pattern in relationship_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                source = match.group(1).strip()
                target = match.group(2).strip()

                if source in entities and target in entities:
                    relationships.append(
                        {
                            "source": source,
                            "target": target,
                            "type": "related",
                        }
                    )

        return relationships

    def _load_domain_keywords(self) -> dict[str, list[str]]:
        """Load domain-specific keywords."""
        return {
            "technical": [
                "system",
                "process",
                "function",
                "method",
                "algorithm",
                "data",
                "database",
                "server",
                "client",
                "api",
                "interface",
                "module",
                "component",
                "service",
                "application",
                "software",
                "code",
                "programming",
                "development",
                "architecture",
                "design",
            ],
            "business": [
                "workflow",
                "procedure",
                "policy",
                "strategy",
                "management",
                "organization",
                "department",
                "team",
                "role",
                "responsibility",
                "customer",
                "client",
                "vendor",
                "supplier",
                "stakeholder",
                "process",
                "operation",
                "business",
                "company",
                "enterprise",
            ],
            "scientific": [
                "experiment",
                "hypothesis",
                "analysis",
                "research",
                "study",
                "method",
                "methodology",
                "protocol",
                "procedure",
                "observation",
                "measurement",
                "data",
                "result",
                "conclusion",
                "theory",
            ],
            "educational": [
                "course",
                "lesson",
                "curriculum",
                "learning",
                "teaching",
                "student",
                "teacher",
                "instructor",
                "education",
                "training",
                "knowledge",
                "skill",
                "concept",
                "topic",
                "subject",
            ],
        }

    def _load_intent_patterns(self) -> dict[str, list[str]]:
        """Load intent classification patterns."""
        return {
            "create_diagram": [
                r"create.*diagram",
                r"generate.*diagram",
                r"make.*diagram",
                r"build.*diagram",
                r"design.*diagram",
                r"draw.*diagram",
            ],
            "show_process": [
                r"show.*process",
                r"illustrate.*process",
                r"demonstrate.*process",
                r"explain.*process",
                r"describe.*flow",
                r"show.*workflow",
            ],
            "visualize_data": [
                r"visualize.*data",
                r"chart.*data",
                r"graph.*data",
                r"plot.*data",
                r"display.*data",
                r"represent.*data",
            ],
            "explain_system": [
                r"explain.*system",
                r"describe.*system",
                r"show.*architecture",
                r"illustrate.*structure",
                r"diagram.*system",
            ],
            "document_process": [
                r"document.*process",
                r"record.*process",
                r"capture.*process",
                r"formalize.*process",
                r"standardize.*process",
            ],
        }

    def _load_entity_patterns(self) -> dict[str, list[str]]:
        """Load entity extraction patterns."""
        return {
            "actor": [
                r"(?:user|customer|client|admin|manager|operator|person|individual)\s+(\w+)",
                r"(\w+)\s+(?:user|customer|client|admin|manager|operator)",
            ],
            "system": [
                r"(?:system|application|service|platform|tool)\s+(\w+)",
                r"(\w+)\s+(?:system|application|service|platform|tool)",
            ],
            "process": [
                r"(?:process|procedure|workflow|operation)\s+(\w+)",
                r"(\w+)\s+(?:process|procedure|workflow|operation)",
            ],
            "data": [
                r"(?:data|information|record|file|document)\s+(\w+)",
                r"(\w+)\s+(?:data|information|record|file|document)",
            ],
        }

    def _load_stopwords(self) -> set[str]:
        """Load stopwords for keyword extraction."""
        return {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "has",
            "he",
            "in",
            "is",
            "it",
            "its",
            "of",
            "on",
            "that",
            "the",
            "to",
            "was",
            "will",
            "with",
            "would",
            "could",
            "should",
            "can",
            "may",
            "might",
            "must",
            "shall",
            "this",
            "these",
            "those",
            "they",
            "them",
            "their",
            "there",
            "where",
            "when",
            "why",
            "how",
            "what",
            "who",
            "which",
            "if",
            "then",
            "else",
            "or",
            "but",
            "not",
            "no",
            "yes",
            "do",
            "does",
            "did",
            "have",
            "had",
            "been",
            "being",
        }
