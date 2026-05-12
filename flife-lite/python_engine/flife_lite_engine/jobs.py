from __future__ import annotations

import concurrent.futures
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .api import run_fatigue_analysis


@dataclass
class AnalysisJob:
    id: str
    submitted_at: str
    future: concurrent.futures.Future
    progress: int = 0
    status: str = "queued"
    messages: list[str] = field(default_factory=list)


class AnalysisJobManager:
    def __init__(self, max_workers: int = 2, timeout_seconds: int = 900) -> None:
        self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
        self.timeout_seconds = timeout_seconds
        self.jobs: dict[str, AnalysisJob] = {}

    def submit(self, payload: dict[str, Any]) -> AnalysisJob:
        job_id = str(uuid.uuid4())
        future = self.executor.submit(_run_job, payload)
        job = AnalysisJob(id=job_id, submitted_at=datetime.now(timezone.utc).isoformat(), future=future)
        job.messages.append("Queued fatigue solver process.")
        self.jobs[job_id] = job
        return job

    def status(self, job_id: str) -> dict[str, Any]:
        job = self.jobs[job_id]
        if job.future.cancelled():
            job.status = "cancelled"
            job.progress = 100
        elif job.future.done():
            job.status = "completed"
            job.progress = 100
        else:
            job.status = "running"
            job.progress = max(job.progress, 35)
        return {"id": job.id, "status": job.status, "progress": job.progress, "messages": job.messages}

    def result(self, job_id: str) -> dict[str, Any]:
        job = self.jobs[job_id]
        response = job.future.result(timeout=self.timeout_seconds)
        job.status = "completed"
        job.progress = 100
        return response

    def cancel(self, job_id: str) -> bool:
        job = self.jobs[job_id]
        cancelled = job.future.cancel()
        if cancelled:
            job.status = "cancelled"
            job.progress = 100
            job.messages.append("Analysis was cancelled before execution.")
        return cancelled


def _run_job(payload: dict[str, Any]) -> dict[str, Any]:
    return run_fatigue_analysis(payload).model_dump()
