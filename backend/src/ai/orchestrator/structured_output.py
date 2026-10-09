"""
Structured Output Parser - Reusable LLM response parsing and validation

Cung cấp cơ chế parse và validate JSON response từ LLM.
Không thực hiện nghiệp vụ, không gọi tools.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, TypeVar, Optional
import json
import re
import math

from src.utils.logger import logger


# ============================================================
# PARSING STATUS
# ============================================================

class ParseStatus(str, Enum):
    """Trạng thái parse"""
    SUCCESS = "SUCCESS"
    INVALID_JSON = "INVALID_JSON"
    EMPTY_OUTPUT = "EMPTY_OUTPUT"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_ENUM = "INVALID_ENUM"
    INVALID_RANGE = "INVALID_RANGE"
    UNKNOWN_FORMAT = "UNKNOWN_FORMAT"


# ============================================================
# VALIDATION ERROR
# ============================================================

@dataclass
class ValidationError:
    """Lỗi validation"""
    field: str
    expected: str
    actual: Any
    status: ParseStatus

    def __str__(self) -> str:
        return f"Field '{self.field}': expected {self.expected}, got {self.actual}"


# ============================================================
# PARSE RESULT
# ============================================================

T = TypeVar('T')


@dataclass
class ParseResult(Generic[T]):
    """
    Kết quả parse với generic type.

    Attributes:
        success: True nếu parse và validate thành công
        status: Trạng thái parse
        data: Dữ liệu đã parse (nếu success)
        errors: Danh sách lỗi validation (nếu có)
        raw_output: Raw response từ LLM (để debug)
    """
    success: bool
    status: ParseStatus
    data: Optional[T] = None
    errors: list[ValidationError] = field(default_factory=list)
    raw_output: str = ""

    @property
    def is_success(self) -> bool:
        """Alias for success"""
        return self.success

    @property
    def error_message(self) -> str:
        """Human-readable error message"""
        if self.success:
            return ""
        if self.errors:
            return "; ".join(str(e) for e in self.errors)
        return self.status.value


# ============================================================
# FIELD SCHEMA
# ============================================================

@dataclass
class FieldSchema:
    """Schema cho một field"""
    name: str
    field_type: type
    required: bool = True
    enum_values: Optional[list[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allow_null: bool = False
    default: Any = None


# ============================================================
# OUTPUT SCHEMA
# ============================================================

@dataclass
class OutputSchema:
    """
    Schema cho output.

    Định nghĩa các field bắt buộc và optional cùng validation rules.
    """
    fields: list[FieldSchema]

    def get_required_fields(self) -> set[str]:
        """Get set of required field names"""
        return {f.name for f in self.fields if f.required}

    def get_optional_fields(self) -> set[str]:
        """Get set of optional field names"""
        return {f.name for f in self.fields if not f.required}


# ============================================================
# STRUCTURED OUTPUT PARSER
# ============================================================

class StructuredOutputParser:
    """
    Parser cho structured LLM output.

    Parse JSON response và validate theo schema.
    """

    def __init__(self, schema: OutputSchema):
        """
        Khởi tạo parser.

        Args:
            schema: Output schema để validate
        """
        self.schema = schema

    def parse(self, raw_output: str) -> ParseResult[dict]:
        """
        Parse và validate LLM output.

        Args:
            raw_output: Raw response từ LLM

        Returns:
            ParseResult với dict đã validate hoặc errors
        """
        # Handle empty/whitespace
        if not raw_output or not raw_output.strip():
            return ParseResult(
                success=False,
                status=ParseStatus.EMPTY_OUTPUT,
                raw_output=raw_output,
            )

        # Clean and extract JSON
        cleaned = raw_output.strip()

        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(1)

        # Parse JSON
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON-like structure
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    return ParseResult(
                        success=False,
                        status=ParseStatus.INVALID_JSON,
                        errors=[
                            ValidationError(
                                field="root",
                                expected="valid JSON object",
                                actual=cleaned[:100],
                                status=ParseStatus.INVALID_JSON,
                            )
                        ],
                        raw_output=raw_output,
                    )
            else:
                return ParseResult(
                    success=False,
                    status=ParseStatus.UNKNOWN_FORMAT,
                    errors=[
                        ValidationError(
                            field="root",
                            expected="JSON object",
                            actual=cleaned[:100],
                            status=ParseStatus.UNKNOWN_FORMAT,
                        )
                    ],
                    raw_output=raw_output,
                )

        # Validate structure
        if not isinstance(data, dict):
            return ParseResult(
                success=False,
                status=ParseStatus.INVALID_TYPE,
                errors=[
                    ValidationError(
                        field="root",
                        expected="object (dict)",
                        actual=type(data).__name__,
                        status=ParseStatus.INVALID_TYPE,
                    )
                ],
                raw_output=raw_output,
            )

        # Validate fields
        errors = []
        validated_data = {}

        for field_schema in self.schema.fields:
            field_name = field_schema.name
            value = data.get(field_name)

            # Check required
            if value is None:
                if field_schema.required:
                    errors.append(ValidationError(
                        field=field_name,
                        expected=field_schema.field_type.__name__,
                        actual=None,
                        status=ParseStatus.MISSING_FIELD,
                    ))
                continue

            # Check null
            if value is None and not field_schema.allow_null:
                errors.append(ValidationError(
                    field=field_name,
                    expected="non-null value",
                    actual=None,
                    status=ParseStatus.INVALID_TYPE,
                ))
                continue

            # Validate type
            if not isinstance(value, field_schema.field_type):
                errors.append(ValidationError(
                    field=field_name,
                    expected=field_schema.field_type.__name__,
                    actual=type(value).__name__,
                    status=ParseStatus.INVALID_TYPE,
                ))
                continue

            # Validate enum
            if field_schema.enum_values is not None:
                if isinstance(value, Enum):
                    enum_value = value.value
                else:
                    enum_value = value

                # Handle string enum
                if isinstance(enum_value, str):
                    valid = any(
                        (isinstance(v, Enum) and v.value == enum_value) or v == enum_value
                        for v in field_schema.enum_values
                    )
                else:
                    valid = enum_value in field_schema.enum_values

                if not valid:
                    errors.append(ValidationError(
                        field=field_name,
                        expected=f"one of {[v.value if isinstance(v, Enum) else v for v in field_schema.enum_values]}",
                        actual=value,
                        status=ParseStatus.INVALID_ENUM,
                    ))
                    continue

            # Validate range for numeric types
            if isinstance(value, (int, float)) and not math.isnan(value) and not math.isinf(value):
                if field_schema.min_value is not None and value < field_schema.min_value:
                    errors.append(ValidationError(
                        field=field_name,
                        expected=f">= {field_schema.min_value}",
                        actual=value,
                        status=ParseStatus.INVALID_RANGE,
                    ))
                    continue

                if field_schema.max_value is not None and value > field_schema.max_value:
                    errors.append(ValidationError(
                        field=field_name,
                        expected=f"<= {field_schema.max_value}",
                        actual=value,
                        status=ParseStatus.INVALID_RANGE,
                    ))
                    continue

            # Check for NaN/Infinity
            if isinstance(value, float):
                if math.isnan(value) or math.isinf(value):
                    errors.append(ValidationError(
                        field=field_name,
                        expected="finite number",
                        actual=value,
                        status=ParseStatus.INVALID_RANGE,
                    ))
                    continue

            # Validated
            validated_data[field_name] = value

        # Return result
        if errors:
            # Determine primary status
            first_error = errors[0]
            return ParseResult(
                success=False,
                status=first_error.status,
                errors=errors,
                raw_output=raw_output,
            )

        return ParseResult(
            success=True,
            status=ParseStatus.SUCCESS,
            data=validated_data,
            raw_output=raw_output,
        )


# ============================================================
# INTENT CLASSIFIER SCHEMA
# ============================================================

# Schema độc lập để tránh vòng import với IntentClassifier.
INTENT_CLASSIFIER_SCHEMA = OutputSchema(
    fields=[
        FieldSchema(
            name="intent",
            field_type=str,
            enum_values=[
                "SEARCH_TRIP", "TRIP_INFO", "CHECK_SEATS", "BOOK_TICKET",
                "VIEW_BOOKING", "CANCEL_BOOKING", "PAYMENT_STATUS",
                "COMPLAINT", "REQUEST_REFUND", "GREETING", "UNKNOWN",
                "NEEDS_CLARIFICATION",
            ],
        ),
        FieldSchema(name="confidence", field_type=float, min_value=0.0, max_value=1.0),
        FieldSchema(name="reasoning", field_type=str, required=False, default=""),
        FieldSchema(name="needs_clarification", field_type=bool, required=False, default=False),
        FieldSchema(name="missing_info", field_type=list, required=False, default=[]),
    ]
)

# ============================================================
# BOOKING ACTION SCHEMA
# ============================================================

# Supported booking actions (maps to BookingAgent handlers)
BOOKING_ACTIONS = [
    "search_trip",
    "get_trip_info",
    "check_seats",
    "create_booking",
    "get_booking",
    "cancel_booking",
    "create_payment",
    "check_payment",
    "get_my_bookings",
]

# Schema for Booking Agent action proposal
BOOKING_ACTION_SCHEMA = OutputSchema(
    fields=[
        FieldSchema(
            name="action",
            field_type=str,
            required=True,
            enum_values=BOOKING_ACTIONS,
        ),
        FieldSchema(
            name="parameters",
            field_type=dict,
            required=False,
            default={},
        ),
        FieldSchema(
            name="needs_clarification",
            field_type=bool,
            required=False,
            default=False,
        ),
        FieldSchema(
            name="missing_info",
            field_type=list,
            required=False,
            default=[],
        ),
        FieldSchema(
            name="response_language",
            field_type=str,
            required=False,
            default="vi",
        ),
        FieldSchema(
            name="message",
            field_type=str,
            required=False,
            default="",
        ),
    ]
)
