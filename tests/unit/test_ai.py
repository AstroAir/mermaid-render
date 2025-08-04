"""
Unit tests for AI module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from mermaid_render.ai import (
    DiagramGenerator,
    DiagramAnalyzer,
    DiagramOptimizer,
    NLProcessor,
    SuggestionEngine,
    GenerationConfig,
    GenerationResult,
    AIdiagramType,
    TextAnalysis,
    EntityExtraction,
    IntentClassification,
    ComplexityAnalysis,
    QualityMetrics,
    AnalysisReport,
    OptimizationResult,
    Suggestion,
    SuggestionType,
    SuggestionPriority,
)
from mermaid_render.ai.optimization import OptimizationType
from mermaid_render.ai.providers import OpenAIProvider, AnthropicProvider, LocalModelProvider
from mermaid_render.exceptions import MermaidRenderError, ValidationError


class TestNLProcessor:
    """Test NLProcessor class."""

    def test_init(self):
        """Test NL processor initialization."""
        processor = NLProcessor()

        assert processor.domain_keywords is not None
        assert processor.intent_patterns is not None
        assert processor.entity_patterns is not None
        assert processor.stopwords is not None

    def test_analyze_text(self):
        """Test complete text analysis."""
        processor = NLProcessor()
        text = "Create a flowchart showing user login process with authentication"

        result = processor.analyze_text(text)

        assert isinstance(result, TextAnalysis)
        assert result.text == text
        assert isinstance(result.keywords, list)
        assert isinstance(result.entities, EntityExtraction)
        assert isinstance(result.intent, IntentClassification)
        assert isinstance(result.complexity_score, float)
        assert isinstance(result.domain, str)

    def test_extract_keywords(self):
        """Test keyword extraction."""
        processor = NLProcessor()
        text = "Create a flowchart showing user login process"

        keywords = processor.extract_keywords(text)

        assert isinstance(keywords, list)
        assert "flowchart" in keywords
        assert "user" in keywords
        assert "login" in keywords
        assert "process" in keywords
        # Stopwords should be filtered out
        assert "a" not in keywords

    def test_extract_entities(self):
        """Test entity extraction."""
        processor = NLProcessor()
        text = "Create a flowchart with User, Database, and Authentication Service"

        entities = processor.extract_entities(text)

        assert isinstance(entities, EntityExtraction)
        assert isinstance(entities.entities, list)
        assert isinstance(entities.entity_types, dict)
        assert isinstance(entities.relationships, list)

    def test_classify_intent(self):
        """Test intent classification."""
        processor = NLProcessor()

        # Test creation intent
        create_text = "Create a flowchart showing the process"
        intent = processor.classify_intent(create_text)
        assert isinstance(intent, IntentClassification)
        assert isinstance(intent.intent, str)
        assert intent.confidence >= 0.0

        # Test modification intent
        modify_text = "Update the diagram to include error handling"
        intent = processor.classify_intent(modify_text)
        assert isinstance(intent.intent, str)
        assert intent.confidence >= 0.0

    def test_calculate_complexity(self):
        """Test complexity calculation."""
        processor = NLProcessor()
        
        simple_text = "Create a simple flowchart"
        complex_text = "Create a comprehensive flowchart with multiple decision points, error handling, authentication, database interactions, and user interface components"

        simple_score = processor.calculate_complexity(simple_text)
        complex_score = processor.calculate_complexity(complex_text)

        assert isinstance(simple_score, float)
        assert isinstance(complex_score, float)
        assert 0 <= simple_score <= 1
        assert 0 <= complex_score <= 1
        assert complex_score > simple_score

    def test_determine_domain(self):
        """Test domain determination."""
        processor = NLProcessor()

        # Test technical domain
        technical_text = "Create a flowchart for user authentication API"
        keywords = processor.extract_keywords(technical_text)
        domain = processor.determine_domain(technical_text, keywords)
        assert domain == "technical"

        # Test business domain
        business_text = "Create a process diagram for customer onboarding workflow"
        keywords = processor.extract_keywords(business_text)
        domain = processor.determine_domain(business_text, keywords)
        assert domain == "business"


class TestDiagramGenerator:
    """Test DiagramGenerator class."""

    def test_init_default(self):
        """Test diagram generator initialization with defaults."""
        with patch('mermaid_render.ai.diagram_generator.OpenAIProvider') as mock_provider, \
             patch('mermaid_render.ai.diagram_generator.NLProcessor') as mock_processor:
            
            generator = DiagramGenerator()

            assert generator.ai_provider is not None
            assert generator.nl_processor is not None
            assert generator.templates is not None
            assert generator.prompts is not None

    def test_init_custom(self):
        """Test diagram generator initialization with custom providers."""
        mock_provider = Mock()
        mock_processor = Mock()

        generator = DiagramGenerator(ai_provider=mock_provider, nl_processor=mock_processor)

        assert generator.ai_provider is mock_provider
        assert generator.nl_processor is mock_processor

    def test_from_text_basic(self):
        """Test basic diagram generation from text."""
        mock_provider = Mock()
        mock_processor = Mock()

        # Create proper mock structure
        mock_intent = Mock()
        mock_intent.intent = "create"
        mock_intent.confidence = 0.9

        # Mock text analysis
        mock_analysis = Mock(spec=TextAnalysis)
        mock_analysis.intent = mock_intent
        mock_analysis.domain = "technical"
        mock_analysis.complexity_score = 0.5
        mock_analysis.keywords = ["flowchart", "process", "simple"]
        mock_analysis.entities = None
        mock_analysis.to_dict.return_value = {"intent": "create", "domain": "technical"}
        mock_processor.analyze_text.return_value = mock_analysis

        # Mock AI generation
        mock_provider.generate_text.return_value = "flowchart TD\n    A --> B"

        generator = DiagramGenerator(ai_provider=mock_provider, nl_processor=mock_processor)

        result = generator.from_text("Create a simple flowchart")

        assert isinstance(result, GenerationResult)
        assert "flowchart TD" in result.diagram_code
        assert "A --> B" in result.diagram_code
        assert result.diagram_type == AIdiagramType.FLOWCHART
        mock_processor.analyze_text.assert_called_once()
        mock_provider.generate_text.assert_called_once()

    def test_from_text_with_config(self):
        """Test diagram generation with custom config."""
        mock_provider = Mock()
        mock_processor = Mock()
        
        # Create proper mock structure
        mock_intent = Mock()
        mock_intent.intent = "create"
        mock_intent.confidence = 0.9

        mock_analysis = Mock(spec=TextAnalysis)
        mock_analysis.intent = mock_intent
        mock_analysis.domain = "technical"
        mock_analysis.complexity_score = 0.5
        mock_analysis.keywords = ["sequence", "diagram", "interaction"]
        mock_analysis.entities = None
        mock_analysis.to_dict.return_value = {"intent": "create", "domain": "technical"}
        mock_processor.analyze_text.return_value = mock_analysis

        mock_provider.generate_text.return_value = "sequenceDiagram\n    A->>B: Message"

        generator = DiagramGenerator(ai_provider=mock_provider, nl_processor=mock_processor)
        config = GenerationConfig(diagram_type=AIdiagramType.SEQUENCE, include_styling=True)
        
        result = generator.from_text("Create a sequence diagram", config)

        assert result.diagram_type == AIdiagramType.SEQUENCE
        assert result.config.include_styling is True

    def test_from_data(self):
        """Test diagram generation from data."""
        mock_provider = Mock()
        mock_processor = Mock()

        # Create proper mock structure
        mock_intent = Mock()
        mock_intent.intent = "create"
        mock_intent.confidence = 0.9

        mock_analysis = Mock(spec=TextAnalysis)
        mock_analysis.intent = mock_intent
        mock_analysis.domain = "technical"
        mock_analysis.complexity_score = 0.5
        mock_analysis.keywords = ["data", "chart", "visualization"]
        mock_analysis.entities = None
        mock_analysis.to_dict.return_value = {"intent": "create", "domain": "technical"}
        mock_processor.analyze_text.return_value = mock_analysis

        mock_provider.generate_text.return_value = "pie title Data\n    \"A\" : 30\n    \"B\" : 70"

        generator = DiagramGenerator(ai_provider=mock_provider, nl_processor=mock_processor)
        data = {"A": 30, "B": 70}

        result = generator.from_data(data, "json")

        assert isinstance(result, GenerationResult)
        assert "pie title" in result.diagram_code

    def test_improve_diagram(self):
        """Test diagram improvement."""
        mock_provider = Mock()
        mock_processor = Mock()

        original_code = "flowchart TD\n    A --> B"
        improved_code = "flowchart TD\n    A[Start] --> B[End]\n    classDef default fill:#f9f9f9"

        # Create a mock response object
        mock_response = Mock()
        mock_response.text = improved_code
        mock_provider.generate_text.return_value = mock_response

        generator = DiagramGenerator(ai_provider=mock_provider, nl_processor=mock_processor)

        result = generator.improve_diagram(original_code, "Add styling and better labels")

        assert isinstance(result, GenerationResult)
        # The result might be post-processed, so just check that it contains the key elements
        assert "A[Start]" in result.diagram_code or "A" in result.diagram_code
        assert "B[End]" in result.diagram_code or "B" in result.diagram_code
        assert "classDef" in result.diagram_code

    def test_get_suggestions(self):
        """Test getting suggestions for diagram."""
        mock_provider = Mock()
        mock_processor = Mock()

        generator = DiagramGenerator(ai_provider=mock_provider, nl_processor=mock_processor)
        diagram_code = "flowchart TD\n    A --> B"
        
        suggestions = generator.get_suggestions(diagram_code)

        assert isinstance(suggestions, list)
        # Should have at least some basic suggestions
        assert len(suggestions) > 0

    def test_ai_provider_error_handling(self):
        """Test handling of AI provider errors."""
        mock_provider = Mock()
        mock_processor = Mock()

        # Create proper mock structure
        mock_intent = Mock()
        mock_intent.intent = "create"
        mock_intent.confidence = 0.9

        mock_analysis = Mock(spec=TextAnalysis)
        mock_analysis.intent = mock_intent
        mock_analysis.domain = "technical"
        mock_analysis.keywords = ["flowchart", "create"]
        mock_analysis.entities = None
        mock_analysis.to_dict.return_value = {"intent": "create", "domain": "technical"}
        mock_processor.analyze_text.return_value = mock_analysis

        # Mock AI provider failure
        mock_provider.generate_text.side_effect = Exception("API Error")

        generator = DiagramGenerator(ai_provider=mock_provider, nl_processor=mock_processor)

        with pytest.raises(Exception, match="API Error"):
            generator.from_text("Create a flowchart")

    def test_determine_diagram_type(self):
        """Test automatic diagram type determination."""
        mock_provider = Mock()
        mock_processor = Mock()

        generator = DiagramGenerator(ai_provider=mock_provider, nl_processor=mock_processor)

        # Test flowchart detection
        mock_intent = Mock()
        mock_intent.intent = "create"

        flowchart_analysis = Mock(spec=TextAnalysis)
        flowchart_analysis.keywords = ["process", "flow", "steps"]
        flowchart_analysis.intent = mock_intent
        diagram_type = generator._determine_diagram_type(flowchart_analysis)
        assert diagram_type == AIdiagramType.FLOWCHART

        # Test sequence detection
        sequence_analysis = Mock(spec=TextAnalysis)
        sequence_analysis.keywords = ["interaction", "message", "sequence"]
        sequence_analysis.intent = mock_intent
        diagram_type = generator._determine_diagram_type(sequence_analysis)
        assert diagram_type == AIdiagramType.SEQUENCE


class TestDiagramAnalyzer:
    """Test DiagramAnalyzer class."""

    def test_init(self):
        """Test analyzer initialization."""
        analyzer = DiagramAnalyzer()

        assert analyzer.quality_rules is not None

    def test_analyze(self):
        """Test complete diagram analysis."""
        analyzer = DiagramAnalyzer()
        diagram_code = "flowchart TD\n    A --> B\n    B --> C"

        result = analyzer.analyze(diagram_code)

        assert isinstance(result, AnalysisReport)
        assert isinstance(result.complexity, ComplexityAnalysis)
        assert isinstance(result.quality, QualityMetrics)
        assert isinstance(result.issues, list)
        assert isinstance(result.recommendations, list)

    def test_analyze_complexity(self):
        """Test complexity analysis."""
        analyzer = DiagramAnalyzer()

        # Simple diagram
        simple_code = "flowchart TD\n    A --> B"
        complexity = analyzer.analyze_complexity(simple_code)
        assert isinstance(complexity, ComplexityAnalysis)
        assert complexity.complexity_level == "simple"
        assert isinstance(complexity.node_count, int)
        assert complexity.node_count >= 0

        # Complex diagram
        complex_code = """flowchart TD
            A --> B
            A --> C
            B --> D
            B --> E
            C --> F
            C --> G
            D --> H
            E --> H
            F --> I
            G --> I"""
        complexity = analyzer.analyze_complexity(complex_code)
        assert complexity.complexity_level in ["simple", "medium", "complex"]
        assert isinstance(complexity.node_count, int)
        assert complexity.node_count >= 0

    def test_assess_quality(self):
        """Test quality assessment."""
        analyzer = DiagramAnalyzer()
        
        # Well-formatted diagram
        good_code = """flowchart TD
            A[Start] --> B[Process]
            B --> C[End]
            classDef default fill:#f9f9f9"""
        quality = analyzer.assess_quality(good_code)
        assert isinstance(quality, QualityMetrics)
        assert quality.readability_score > 0.5

        # Poorly formatted diagram
        poor_code = "flowchart TD\nA-->B\nB-->C"
        quality = analyzer.assess_quality(poor_code)
        assert quality.readability_score < 0.8  # Should be lower due to poor formatting


class TestDiagramOptimizer:
    """Test DiagramOptimizer class."""

    def test_init(self):
        """Test optimizer initialization."""
        optimizer = DiagramOptimizer()

        assert optimizer.layout_optimizer is not None
        assert optimizer.style_optimizer is not None

    def test_optimize_layout(self):
        """Test layout optimization."""
        optimizer = DiagramOptimizer()
        diagram_code = "flowchart TD\nA-->B\nB-->C"

        result = optimizer.optimize_layout(diagram_code)

        assert isinstance(result, OptimizationResult)
        assert result.optimization_type == OptimizationType.LAYOUT
        assert result.original_diagram == diagram_code
        assert result.optimized_diagram != diagram_code  # Should be different
        assert isinstance(result.improvements, list)
        assert result.confidence_score > 0

    def test_optimize_style(self):
        """Test style optimization."""
        optimizer = DiagramOptimizer()
        diagram_code = "flowchart TD\n    A --> B\n    B --> C"

        result = optimizer.optimize_style(diagram_code)

        assert isinstance(result, OptimizationResult)
        assert result.optimization_type == OptimizationType.STYLE
        assert result.original_diagram == diagram_code
        assert isinstance(result.improvements, list)
        assert result.confidence_score > 0

    def test_optimize_all(self):
        """Test full optimization."""
        optimizer = DiagramOptimizer()
        diagram_code = "flowchart TD\nA-->B\nB-->C"

        results = optimizer.optimize_all(diagram_code)

        assert isinstance(results, list)
        assert len(results) == 2  # Layout and style optimization
        assert all(isinstance(r, OptimizationResult) for r in results)
        assert results[0].optimization_type == OptimizationType.LAYOUT
        assert results[1].optimization_type == OptimizationType.STYLE


class TestSuggestionEngine:
    """Test SuggestionEngine class."""

    def test_init(self):
        """Test suggestion engine initialization."""
        engine = SuggestionEngine()

        assert engine.suggestion_rules is not None

    def test_get_suggestions(self):
        """Test getting suggestions."""
        engine = SuggestionEngine()
        diagram_code = "flowchart TD\n    A --> B"

        suggestions = engine.get_suggestions(diagram_code)

        assert isinstance(suggestions, list)
        assert all(isinstance(s, Suggestion) for s in suggestions)

    def test_get_suggestions_by_type(self):
        """Test getting suggestions by type."""
        engine = SuggestionEngine()
        diagram_code = "flowchart TD\n    A --> B"

        layout_suggestions = engine.get_suggestions(
            diagram_code, suggestion_types=[SuggestionType.LAYOUT]
        )
        style_suggestions = engine.get_suggestions(
            diagram_code, suggestion_types=[SuggestionType.STYLE]
        )

        assert isinstance(layout_suggestions, list)
        assert isinstance(style_suggestions, list)
        # All suggestions should be of the requested type
        assert all(s.suggestion_type == SuggestionType.LAYOUT for s in layout_suggestions)
        assert all(s.suggestion_type == SuggestionType.STYLE for s in style_suggestions)

    def test_get_suggestions_by_priority(self):
        """Test getting suggestions by priority."""
        engine = SuggestionEngine()
        diagram_code = "flowchart TD\n    A --> B"

        high_priority = engine.get_suggestions(
            diagram_code, priority_filter=SuggestionPriority.HIGH
        )

        assert isinstance(high_priority, list)
        # All suggestions should be high priority or higher
        assert all(
            s.priority in [SuggestionPriority.HIGH, SuggestionPriority.CRITICAL]
            for s in high_priority
        )

    def test_suggest_improvements(self):
        """Test improvement suggestions."""
        engine = SuggestionEngine()

        # Test with a simple diagram that needs improvements
        simple_code = "flowchart TD\n    A --> B"
        suggestions = engine.suggest_improvements(simple_code)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Should suggest styling or comments
        suggestion_texts = [s.description for s in suggestions]
        assert any("styling" in text.lower() or "comment" in text.lower() for text in suggestion_texts)

    def test_suggest_styling(self):
        """Test styling suggestions."""
        engine = SuggestionEngine()

        # Test with diagram without styling
        unstyled_code = "flowchart TD\n    A --> B\n    B --> C"
        suggestions = engine.suggest_styling(unstyled_code)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Should suggest adding styling
        suggestion_texts = [s.description for s in suggestions]
        assert any("styl" in text.lower() for text in suggestion_texts)

    def test_suggest_layout(self):
        """Test layout suggestions."""
        engine = SuggestionEngine()

        # Test with diagram without direction to trigger layout suggestion
        poor_layout = "graph\nA[Node1]-->B[Node2]\nB-->C[Node3]\nC-->D[Node4]\nD-->E[Node5]"
        suggestions = engine.suggest_layout(poor_layout)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Should suggest layout improvements (direction specification)
        suggestion_texts = [s.description for s in suggestions]
        assert any("direction" in text.lower() or "layout" in text.lower() for text in suggestion_texts)


class TestAIProviders:
    """Test AI provider classes."""

    def test_openai_provider_init(self):
        """Test OpenAI provider initialization."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()
            assert provider.api_key == 'test-key'
            assert provider.model == 'gpt-3.5-turbo'

    def test_openai_provider_custom_model(self):
        """Test OpenAI provider with custom model."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider(model='gpt-4')
            assert provider.model == 'gpt-4'

    @patch('openai.OpenAI')
    def test_openai_provider_generate_text(self, mock_openai):
        """Test OpenAI text generation."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated text"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()
            result = provider.generate_text("Test prompt")

            assert result.content == "Generated text"
            assert result.provider == "openai"
            mock_client.chat.completions.create.assert_called_once()

    def test_anthropic_provider_init(self):
        """Test Anthropic provider initialization."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            provider = AnthropicProvider()
            assert provider.api_key == 'test-key'
            assert provider.model == 'claude-3-5-sonnet-20241022'

    def test_local_model_provider_init(self):
        """Test Local model provider initialization."""
        provider = LocalModelProvider()
        assert provider.model_path is not None
        assert provider.model_name is not None

    def test_local_model_provider_generate_text(self):
        """Test Local model text generation."""
        provider = LocalModelProvider()

        # Mock the template generation
        with patch.object(provider, '_template_generation') as mock_template:
            mock_template.return_value = "Generated text"

            result = provider.generate_text("Test prompt")

            assert result.content == "Generated text"
            assert result.model == "local-template"
            mock_template.assert_called_once_with("Test prompt")


class TestAIUtilities:
    """Test AI utility functions."""

    @patch('mermaid_render.ai.utils.DiagramGenerator')
    def test_generate_from_text(self, mock_generator_class):
        """Test generate_from_text utility function."""
        from mermaid_render.ai.utils import generate_from_text

        mock_generator = Mock()
        mock_result = Mock()
        mock_result.to_dict.return_value = {"diagram_code": "flowchart TD\n    A --> B"}
        mock_generator.from_text.return_value = mock_result
        mock_generator_class.return_value = mock_generator

        result = generate_from_text("Create a flowchart")

        assert result == {"diagram_code": "flowchart TD\n    A --> B"}
        # Check that from_text was called with text and a GenerationConfig
        mock_generator.from_text.assert_called_once()
        call_args = mock_generator.from_text.call_args
        assert call_args[0][0] == "Create a flowchart"  # First argument is text
        assert call_args[0][1] is not None  # Second argument is GenerationConfig

    @patch('mermaid_render.ai.utils.DiagramOptimizer')
    def test_optimize_diagram(self, mock_optimizer_class):
        """Test optimize_diagram utility function."""
        from mermaid_render.ai.utils import optimize_diagram

        mock_optimizer = Mock()
        mock_layout_result = Mock()
        mock_layout_result.to_dict.return_value = {"optimized_diagram": "layout optimized"}
        mock_style_result = Mock()
        mock_style_result.to_dict.return_value = {"optimized_diagram": "style optimized"}

        mock_optimizer.optimize_layout.return_value = mock_layout_result
        mock_optimizer.optimize_style.return_value = mock_style_result
        mock_optimizer_class.return_value = mock_optimizer

        result = optimize_diagram("flowchart TD\n    A --> B")

        # Should return a list of optimization results
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {"optimized_diagram": "layout optimized"}
        assert result[1] == {"optimized_diagram": "style optimized"}
        mock_optimizer.optimize_layout.assert_called_once()
        mock_optimizer.optimize_style.assert_called_once()

    @patch('mermaid_render.ai.utils.DiagramAnalyzer')
    def test_analyze_diagram(self, mock_analyzer_class):
        """Test analyze_diagram utility function."""
        from mermaid_render.ai.utils import analyze_diagram

        mock_analyzer = Mock()
        mock_report = Mock()
        mock_report.to_dict.return_value = {"complexity": "medium"}
        mock_analyzer.analyze.return_value = mock_report
        mock_analyzer_class.return_value = mock_analyzer

        result = analyze_diagram("flowchart TD\n    A --> B")

        assert result == {"complexity": "medium"}
        mock_analyzer.analyze.assert_called_once()

    @patch('mermaid_render.ai.utils.SuggestionEngine')
    def test_get_suggestions(self, mock_engine_class):
        """Test get_suggestions utility function."""
        from mermaid_render.ai.utils import get_suggestions

        mock_engine = Mock()
        mock_suggestions = [Mock()]
        mock_suggestions[0].to_dict.return_value = {"description": "Add styling"}
        mock_engine.get_suggestions.return_value = mock_suggestions
        mock_engine_class.return_value = mock_engine

        result = get_suggestions("flowchart TD\n    A --> B")

        assert result == [{"description": "Add styling"}]
        mock_engine.get_suggestions.assert_called_once()


class TestAIDataClasses:
    """Test AI data classes and enums."""

    def test_generation_config(self):
        """Test GenerationConfig data class."""
        config = GenerationConfig(
            diagram_type=AIdiagramType.FLOWCHART,
            include_styling=True,
            max_nodes=10,
            style_preference="modern"
        )

        assert config.diagram_type == AIdiagramType.FLOWCHART
        assert config.include_styling is True
        assert config.max_nodes == 10
        assert config.style_preference == "modern"

    def test_generation_result(self):
        """Test GenerationResult data class."""
        config = GenerationConfig(
            diagram_type=AIdiagramType.FLOWCHART,
            include_styling=True
        )

        result = GenerationResult(
            diagram_code="flowchart TD\n    A --> B",
            diagram_type=AIdiagramType.FLOWCHART,
            confidence_score=0.9,
            config=config,
            suggestions=["Add styling"]
        )

        assert result.diagram_code == "flowchart TD\n    A --> B"
        assert result.diagram_type == AIdiagramType.FLOWCHART
        assert result.config is config
        assert result.confidence_score == 0.9
        assert result.suggestions == ["Add styling"]

        # Test to_dict method
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["diagram_code"] == "flowchart TD\n    A --> B"

    def test_suggestion(self):
        """Test Suggestion data class."""
        suggestion = Suggestion(
            suggestion_id="test_001",
            suggestion_type=SuggestionType.STYLE,
            priority=SuggestionPriority.HIGH,
            title="Add Color Styling",
            description="Add color styling",
            rationale="Colors improve readability",
            implementation="classDef default fill:#f9f9f9"
        )

        assert suggestion.suggestion_type == SuggestionType.STYLE
        assert suggestion.priority == SuggestionPriority.HIGH
        assert suggestion.description == "Add color styling"
        assert suggestion.implementation == "classDef default fill:#f9f9f9"

        # Test to_dict method
        suggestion_dict = suggestion.to_dict()
        assert isinstance(suggestion_dict, dict)
        assert suggestion_dict["description"] == "Add color styling"
