from collections import defaultdict
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker for patch operations
    
    Rules:
    - If more than 5 failures in a job → auto-stop further patching
    - Prevents cascading failures
    - Protects against systematic issues
    """
    
    FAILURE_THRESHOLD = 5
    
    def __init__(self):
        # Track failures per job
        self.failures: Dict[str, int] = defaultdict(int)
        self.tripped: Dict[str, bool] = defaultdict(bool)
        
        logger.info(f"CircuitBreaker initialized: threshold={self.FAILURE_THRESHOLD}")
    
    def record_failure(self, job_id: str) -> bool:
        """
        Record a failure for a job
        
        Returns: True if circuit breaker tripped (should stop)
        """
        self.failures[job_id] += 1
        
        if self.failures[job_id] >= self.FAILURE_THRESHOLD:
            if not self.tripped[job_id]:
                self.tripped[job_id] = True
                logger.error(
                    f"🔴 CIRCUIT BREAKER TRIPPED for job {job_id}: "
                    f"{self.failures[job_id]} failures. "
                    f"Auto-stopping further patches."
                )
            return True
        
        logger.warning(
            f"Failure recorded for job {job_id}: "
            f"{self.failures[job_id]}/{self.FAILURE_THRESHOLD}"
        )
        return False
    
    def record_success(self, job_id: str):
        """Record a successful patch (resets failure count)"""
        if self.failures[job_id] > 0:
            logger.info(
                f"Success recorded for job {job_id}, "
                f"resetting failure count from {self.failures[job_id]}"
            )
            self.failures[job_id] = 0
    
    def is_tripped(self, job_id: str) -> bool:
        """Check if circuit breaker is tripped for a job"""
        return self.tripped.get(job_id, False)
    
    def get_failure_count(self, job_id: str) -> int:
        """Get current failure count for a job"""
        return self.failures.get(job_id, 0)
    
    def reset(self, job_id: str):
        """Reset circuit breaker for a job"""
        self.failures[job_id] = 0
        self.tripped[job_id] = False
        logger.info(f"Circuit breaker reset for job {job_id}")
    
    def get_status(self, job_id: str) -> dict:
        """Get circuit breaker status for a job"""
        return {
            "job_id": job_id,
            "failures": self.failures.get(job_id, 0),
            "threshold": self.FAILURE_THRESHOLD,
            "tripped": self.tripped.get(job_id, False),
            "remaining_attempts": max(0, self.FAILURE_THRESHOLD - self.failures.get(job_id, 0))
        }


# Global singleton instance
circuit_breaker = CircuitBreaker()

