from enum import StrEnum


class UploadStatus(StrEnum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class ParseJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class ReviewTaskStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FIXED = "fixed"


class EntityType(StrEnum):
    NOTE = "note"
    PROBLEM = "problem"
    SOLUTION = "solution"


class ReviewTaskType(StrEnum):
    TAG_REVIEW = "tag_review"
    PARSE_REVIEW = "parse_review"
    SOLVE_REVIEW = "solve_review"
