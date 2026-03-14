from pydantic import BaseModel


class DashboardData(BaseModel):
    today_problem_count: int
    today_note_count: int
    pending_review_count: int
    pending_parse_job_count: int
    failed_parse_job_count: int


class MonitorOverviewData(BaseModel):
    service_status: str
    parse_job_total: int
    parse_job_pending: int
    parse_job_failed: int
    review_task_pending: int
    latest_error_messages: list[str]
