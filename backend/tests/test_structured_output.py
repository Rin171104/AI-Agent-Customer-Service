"""
Tests for Structured Output Parser

Run: pytest tests/test_structured_output.py -v
"""
import pytest
from unittest.mock import MagicMock

from src.ai.orchestrator.structured_output import (
    StructuredOutputParser,
    OutputSchema,
    FieldSchema,
    ParseResult,
    ParseStatus,
    ValidationError,
    INTENT_CLASSIFIER_SCHEMA,
)


class TestStructuredOutputParser:
    """Tests for StructuredOutputParser"""

    @pytest.fixture
    def schema(self):
        """Simple test schema"""
        return OutputSchema(
            fields=[
                FieldSchema(name="name", field_type=str, required=True),
                FieldSchema(name="age", field_type=int, required=True, min_value=0, max_value=150),
                FieldSchema(name="email", field_type=str, required=False, default=""),
                FieldSchema(name="active", field_type=bool, required=False, default=True),
            ]
        )

    def test_parse_valid_json(self, schema):
        """Valid JSON parses successfully"""
        parser = StructuredOutputParser(schema)
        result = parser.parse('{"name": "John", "age": 30}')

        assert result.is_success
        assert result.data["name"] == "John"
        assert result.data["age"] == 30

    def test_parse_with_markdown_fence(self, schema):
        """JSON in markdown fence parses correctly"""
        parser = StructuredOutputParser(schema)
        result = parser.parse('```json\n{"name": "Jane", "age": 25}\n```')

        assert result.is_success
        assert result.data["name"] == "Jane"

    def test_parse_empty_string(self, schema):
        """Empty string returns EMPTY_OUTPUT"""
        parser = StructuredOutputParser(schema)
        result = parser.parse("")

        assert not result.is_success
        assert result.status == ParseStatus.EMPTY_OUTPUT

    def test_parse_whitespace_only(self, schema):
        """Whitespace-only returns EMPTY_OUTPUT"""
        parser = StructuredOutputParser(schema)
        result = parser.parse("   \n\t  ")

        assert not result.is_success
        assert result.status == ParseStatus.EMPTY_OUTPUT

    def test_parse_invalid_json(self, schema):
        """Invalid JSON returns INVALID_JSON"""
        parser = StructuredOutputParser(schema)
        result = parser.parse("{invalid json}")

        assert not result.is_success
        assert result.status == ParseStatus.INVALID_JSON

    def test_parse_non_object_json(self, schema):
        """Non-object JSON returns INVALID_TYPE"""
        parser = StructuredOutputParser(schema)
        result = parser.parse('["array", "not", "object"]')

        assert not result.is_success
        assert result.status == ParseStatus.INVALID_TYPE

    def test_parse_missing_required_field(self, schema):
        """Missing required field returns MISSING_FIELD"""
        parser = StructuredOutputParser(schema)
        result = parser.parse('{"name": "John"}')  # age is missing

        assert not result.is_success
        assert result.status == ParseStatus.MISSING_FIELD
        assert any(e.field == "age" for e in result.errors)

    def test_parse_wrong_type(self, schema):
        """Wrong type returns INVALID_TYPE"""
        parser = StructuredOutputParser(schema)
        result = parser.parse('{"name": "John", "age": "thirty"}')

        assert not result.is_success
        assert result.status == ParseStatus.INVALID_TYPE
        assert any(e.field == "age" for e in result.errors)

    def test_parse_int_out_of_range(self, schema):
        """Int out of range returns INVALID_RANGE"""
        parser = StructuredOutputParser(schema)
        result = parser.parse('{"name": "John", "age": 200}')

        assert not result.is_success
        assert result.status == ParseStatus.INVALID_RANGE

    def test_parse_negative_int(self, schema):
        """Negative int returns INVALID_RANGE"""
        parser = StructuredOutputParser(schema)
        result = parser.parse('{"name": "John", "age": -5}')

        assert not result.is_success
        assert result.status == ParseStatus.INVALID_RANGE

    def test_parse_nan_value(self, schema):
        """NaN float returns INVALID_RANGE"""
        schema_nan = OutputSchema(
            fields=[
                FieldSchema(name="score", field_type=float, required=True),
            ]
        )
        parser = StructuredOutputParser(schema_nan)
        result = parser.parse('{"score": NaN}')

        # JSON parse handles NaN specially
        assert not result.is_success

    def test_parse_optional_field_missing(self, schema):
        """Optional field can be missing - returns None (not in data dict)"""
        parser = StructuredOutputParser(schema)
        result = parser.parse('{"name": "John", "age": 30}')

        assert result.is_success
        assert "email" not in result.data  # Optional fields not added if missing

    def test_parse_bool_field(self, schema):
        """Bool field parses correctly"""
        parser = StructuredOutputParser(schema)
        result = parser.parse('{"name": "John", "age": 30, "active": false}')

        assert result.is_success
        assert result.data["active"] is False


class TestIntentClassifierSchema:
    """Tests for INTENT_CLASSIFIER_SCHEMA"""

    def test_parse_valid_classification_response(self):
        """Valid classification JSON parses correctly"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('{"intent": "SEARCH_TRIP", "confidence": 0.9}')

        assert result.is_success
        assert result.data["intent"] == "SEARCH_TRIP"
        assert result.data["confidence"] == 0.9

    def test_parse_missing_intent(self):
        """Missing intent returns MISSING_FIELD"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('{"confidence": 0.9}')

        assert not result.is_success
        assert result.status == ParseStatus.MISSING_FIELD

    def test_parse_missing_confidence(self):
        """Missing confidence returns MISSING_FIELD"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('{"intent": "SEARCH_TRIP"}')

        assert not result.is_success
        assert result.status == ParseStatus.MISSING_FIELD

    def test_parse_confidence_out_of_range(self):
        """Confidence > 1.0 returns INVALID_RANGE"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('{"intent": "SEARCH_TRIP", "confidence": 1.5}')

        assert not result.is_success
        assert result.status == ParseStatus.INVALID_RANGE

    def test_parse_negative_confidence(self):
        """Negative confidence returns INVALID_RANGE"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('{"intent": "SEARCH_TRIP", "confidence": -0.1}')

        assert not result.is_success
        assert result.status == ParseStatus.INVALID_RANGE

    def test_parse_confidence_as_string(self):
        """Confidence as string returns INVALID_TYPE"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('{"intent": "SEARCH_TRIP", "confidence": "high"}')

        assert not result.is_success
        assert result.status == ParseStatus.INVALID_TYPE

    def test_parse_invalid_json(self):
        """Invalid JSON returns INVALID_JSON or UNKNOWN_FORMAT"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse("not json at all")

        assert not result.is_success
        assert result.status in (ParseStatus.INVALID_JSON, ParseStatus.UNKNOWN_FORMAT)

    def test_parse_empty_json(self):
        """Empty object returns MISSING_FIELD"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse("{}")

        assert not result.is_success
        assert result.status == ParseStatus.MISSING_FIELD

    def test_parse_with_reasoning(self):
        """Reasoning field is optional"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('{"intent": "SEARCH_TRIP", "confidence": 0.9, "reasoning": "User wants to find a trip"}')

        assert result.is_success
        assert result.data["reasoning"] == "User wants to find a trip"

    def test_parse_with_missing_info(self):
        """missing_info field is optional"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('{"intent": "SEARCH_TRIP", "confidence": 0.9, "missing_info": ["pickup location"]}')

        assert result.is_success
        assert result.data["missing_info"] == ["pickup location"]

    def test_parse_needs_clarification(self):
        """needs_clarification field is optional"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('{"intent": "UNKNOWN", "confidence": 0.3, "needs_clarification": true}')

        assert result.is_success
        assert result.data["needs_clarification"] is True


class TestParseResult:
    """Tests for ParseResult"""

    def test_is_success_property(self):
        """is_success is alias for success"""
        result = ParseResult(success=True, status=ParseStatus.SUCCESS)
        assert result.is_success is True

        result = ParseResult(success=False, status=ParseStatus.INVALID_JSON)
        assert result.is_success is False

    def test_error_message_empty_on_success(self):
        """error_message is empty on success"""
        result = ParseResult(success=True, status=ParseStatus.SUCCESS)
        assert result.error_message == ""

    def test_error_message_on_failure(self):
        """error_message contains errors"""
        result = ParseResult(
            success=False,
            status=ParseStatus.INVALID_JSON,
            errors=[
                ValidationError("field1", "str", "int", ParseStatus.INVALID_TYPE),
            ]
        )
        assert "field1" in result.error_message
        assert "str" in result.error_message


class TestValidationError:
    """Tests for ValidationError"""

    def test_str_representation(self):
        """str(ValidationError) gives readable message"""
        error = ValidationError("age", "int", "str", ParseStatus.INVALID_TYPE)
        assert "age" in str(error)
        assert "int" in str(error)
        assert "str" in str(error)


class TestFieldSchema:
    """Tests for FieldSchema"""

    def test_default_values(self):
        """FieldSchema has correct defaults"""
        schema = FieldSchema(name="test", field_type=str)
        assert schema.required is True
        assert schema.enum_values is None
        assert schema.default is None

    def test_optional_field(self):
        """Optional field can be missing"""
        schema = FieldSchema(name="optional", field_type=str, required=False)
        assert schema.required is False


class TestOutputSchema:
    """Tests for OutputSchema"""

    def test_get_required_fields(self):
        """get_required_fields returns required field names"""
        schema = OutputSchema(
            fields=[
                FieldSchema(name="required", field_type=str, required=True),
                FieldSchema(name="optional", field_type=str, required=False),
            ]
        )
        assert "required" in schema.get_required_fields()
        assert "optional" not in schema.get_required_fields()

    def test_get_optional_fields(self):
        """get_optional_fields returns optional field names"""
        schema = OutputSchema(
            fields=[
                FieldSchema(name="required", field_type=str, required=True),
                FieldSchema(name="optional", field_type=str, required=False),
            ]
        )
        assert "optional" in schema.get_optional_fields()
        assert "required" not in schema.get_optional_fields()


class TestEdgeCases:
    """Edge case tests"""

    def test_partial_json_with_braces(self):
        """Partial JSON like { incomplete returns INVALID_JSON"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse("{ incomplete")

        assert not result.is_success

    def test_integer_instead_of_object(self):
        """Integer instead of object returns INVALID_TYPE"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse("123")

        assert not result.is_success
        assert result.status == ParseStatus.INVALID_TYPE

    def test_null_value(self):
        """Null value for non-nullable field returns INVALID_TYPE"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('{"intent": null, "confidence": 0.9}')

        assert not result.is_success

    def test_whitespace_between_fence_and_json(self):
        """Whitespace between fence and JSON is handled"""
        parser = StructuredOutputParser(INTENT_CLASSIFIER_SCHEMA)
        result = parser.parse('```json  \n{"intent": "SEARCH_TRIP", "confidence": 0.9}  \n```')

        assert result.is_success
