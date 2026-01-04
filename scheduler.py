"""
Task Scheduler for Morocco Market Scraper
Handles scheduled scraping, monitoring, and maintenance tasks
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ScheduledTask:
    """Definition of a scheduled task"""
    id: str
    name: str
    func: Callable
    interval_seconds: int
    args: tuple = field(default_factory=tuple)
    kwargs: Dict = field(default_factory=dict)
    is_enabled: bool = True
    run_on_start: bool = False
    market_hours_only: bool = False
    weekdays_only: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    last_duration: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'interval_seconds': self.interval_seconds,
            'is_enabled': self.is_enabled,
            'run_on_start': self.run_on_start,
            'market_hours_only': self.market_hours_only,
            'weekdays_only': self.weekdays_only,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'run_count': self.run_count,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'last_duration': self.last_duration
        }


@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    status: TaskStatus
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    result: Any = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': round(self.duration_seconds, 2),
            'error': self.error
        }


class MarketScheduler:
    """
    Scheduler for market data collection tasks
    Handles scheduling based on market hours and intervals
    """
    
    # Casablanca Stock Exchange hours (Morocco time - WET/WEST)
    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 30
    MARKET_CLOSE_HOUR = 15
    MARKET_CLOSE_MINUTE = 30
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_history: List[TaskResult] = []
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def add_task(self, task: ScheduledTask):
        """Add a task to the scheduler"""
        if task.run_on_start:
            task.next_run = datetime.now()
        else:
            task.next_run = datetime.now() + timedelta(seconds=task.interval_seconds)
        
        self.tasks[task.id] = task
        logger.info(f"Added task: {task.name} (every {task.interval_seconds}s)")
    
    def remove_task(self, task_id: str):
        """Remove a task from the scheduler"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Removed task: {task_id}")
    
    def enable_task(self, task_id: str):
        """Enable a task"""
        if task_id in self.tasks:
            self.tasks[task_id].is_enabled = True
    
    def disable_task(self, task_id: str):
        """Disable a task"""
        if task_id in self.tasks:
            self.tasks[task_id].is_enabled = False
    
    def is_market_hours(self) -> bool:
        """Check if current time is within market hours"""
        now = datetime.now()
        
        # Check weekday (Monday=0 to Friday=4)
        if now.weekday() > 4:
            return False
        
        # Check time
        market_open = now.replace(
            hour=self.MARKET_OPEN_HOUR, 
            minute=self.MARKET_OPEN_MINUTE, 
            second=0
        )
        market_close = now.replace(
            hour=self.MARKET_CLOSE_HOUR, 
            minute=self.MARKET_CLOSE_MINUTE, 
            second=0
        )
        
        return market_open <= now <= market_close
    
    def is_weekday(self) -> bool:
        """Check if today is a weekday"""
        return datetime.now().weekday() < 5
    
    def _should_run_task(self, task: ScheduledTask) -> bool:
        """Determine if a task should run now"""
        if not task.is_enabled:
            return False
        
        now = datetime.now()
        
        # Check if it's time to run
        if task.next_run and now < task.next_run:
            return False
        
        # Check market hours restriction
        if task.market_hours_only and not self.is_market_hours():
            return False
        
        # Check weekday restriction
        if task.weekdays_only and not self.is_weekday():
            return False
        
        return True
    
    def _run_task(self, task: ScheduledTask) -> TaskResult:
        """Execute a task and record the result"""
        start_time = datetime.now()
        status = TaskStatus.RUNNING
        result = None
        error = None
        
        try:
            logger.info(f"Running task: {task.name}")
            result = task.func(*task.args, **task.kwargs)
            status = TaskStatus.COMPLETED
        except Exception as e:
            status = TaskStatus.FAILED
            error = str(e)
            task.error_count += 1
            task.last_error = error
            logger.error(f"Task {task.name} failed: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Update task state
        task.last_run = start_time
        task.next_run = datetime.now() + timedelta(seconds=task.interval_seconds)
        task.run_count += 1
        task.last_duration = duration
        
        # Create result
        task_result = TaskResult(
            task_id=task.id,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            result=result,
            error=error
        )
        
        # Store in history (keep last 1000)
        self.task_history.append(task_result)
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-1000:]
        
        return task_result
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Scheduler started")
        
        while not self._stop_event.is_set():
            for task_id, task in list(self.tasks.items()):
                if self._stop_event.is_set():
                    break
                
                if self._should_run_task(task):
                    self._run_task(task)
            
            # Sleep for a short interval before checking again
            self._stop_event.wait(1)
        
        logger.info("Scheduler stopped")
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self._running:
            logger.warning("Scheduler is already running")
            return
        
        self._running = True
        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True
        )
        self._scheduler_thread.start()
        logger.info("Scheduler started in background")
    
    def stop(self, wait: bool = True):
        """Stop the scheduler"""
        if not self._running:
            return
        
        self._stop_event.set()
        if wait and self._scheduler_thread:
            self._scheduler_thread.join(timeout=10)
        
        self._running = False
        logger.info("Scheduler stopped")
    
    def run_blocking(self):
        """Run the scheduler in the main thread (blocking)"""
        self._running = True
        self._stop_event.clear()
        
        try:
            self._scheduler_loop()
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
        finally:
            self._running = False
    
    def run_task_now(self, task_id: str) -> Optional[TaskResult]:
        """Manually run a specific task immediately"""
        if task_id not in self.tasks:
            logger.error(f"Task not found: {task_id}")
            return None
        
        task = self.tasks[task_id]
        return self._run_task(task)
    
    def get_status(self) -> Dict:
        """Get scheduler status"""
        return {
            'is_running': self._running,
            'is_market_hours': self.is_market_hours(),
            'is_weekday': self.is_weekday(),
            'current_time': datetime.now().isoformat(),
            'tasks': {
                task_id: task.to_dict() 
                for task_id, task in self.tasks.items()
            },
            'recent_runs': [
                r.to_dict() for r in self.task_history[-10:]
            ]
        }
    
    def save_state(self, filepath: str = "data/scheduler_state.json"):
        """Save scheduler state to file"""
        state = {
            'saved_at': datetime.now().isoformat(),
            'tasks': {
                task_id: {
                    'is_enabled': task.is_enabled,
                    'last_run': task.last_run.isoformat() if task.last_run else None,
                    'run_count': task.run_count,
                    'error_count': task.error_count
                }
                for task_id, task in self.tasks.items()
            }
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str = "data/scheduler_state.json"):
        """Load scheduler state from file"""
        if not Path(filepath).exists():
            return
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        for task_id, task_state in state.get('tasks', {}).items():
            if task_id in self.tasks:
                self.tasks[task_id].is_enabled = task_state.get('is_enabled', True)
                self.tasks[task_id].run_count = task_state.get('run_count', 0)
                self.tasks[task_id].error_count = task_state.get('error_count', 0)


def create_market_scheduler():
    """Create a pre-configured scheduler for market monitoring"""
    from main import MarketMonitor
    
    scheduler = MarketScheduler()
    monitor = MarketMonitor()
    
    # Stock scraping task - every 5 minutes during market hours
    scheduler.add_task(ScheduledTask(
        id="scrape_stocks",
        name="Stock Data Scraping",
        func=monitor.scrape_stocks,
        interval_seconds=300,  # 5 minutes
        market_hours_only=True,
        weekdays_only=True,
        run_on_start=True
    ))
    
    # News scraping task - every 15 minutes
    scheduler.add_task(ScheduledTask(
        id="scrape_news",
        name="News Scraping",
        func=monitor.scrape_news,
        interval_seconds=900,  # 15 minutes
        market_hours_only=False,
        weekdays_only=False,
        run_on_start=True
    ))
    
    # Daily report generation - once per day at market close
    def generate_daily_report():
        from utils.analysis import MarketAnalytics
        analytics = MarketAnalytics()
        stocks = monitor.db.get_latest_stocks()
        indices = monitor.db.get_latest_indices()
        report = analytics.generate_daily_report(stocks, indices)
        
        # Save report
        report_path = f"data/reports/daily_{datetime.now().strftime('%Y%m%d')}.json"
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    scheduler.add_task(ScheduledTask(
        id="daily_report",
        name="Daily Report Generation",
        func=generate_daily_report,
        interval_seconds=86400,  # 24 hours
        market_hours_only=False,
        weekdays_only=True
    ))
    
    # Database cleanup - weekly
    def cleanup_old_data():
        # Keep only last 90 days of detailed data
        logger.info("Running database cleanup...")
        # Implementation depends on database schema
        return {"status": "completed"}
    
    scheduler.add_task(ScheduledTask(
        id="db_cleanup",
        name="Database Cleanup",
        func=cleanup_old_data,
        interval_seconds=604800,  # 1 week
        market_hours_only=False,
        weekdays_only=False
    ))
    
    return scheduler


if __name__ == "__main__":
    import sys
    
    print("Market Scheduler Demo")
    print("=" * 60)
    
    # Create a simple test scheduler
    scheduler = MarketScheduler()
    
    # Add a simple test task
    def test_task():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Test task executed!")
        return {"status": "ok"}
    
    scheduler.add_task(ScheduledTask(
        id="test",
        name="Test Task",
        func=test_task,
        interval_seconds=5,
        run_on_start=True,
        market_hours_only=False,
        weekdays_only=False
    ))
    
    print(f"\nCurrent time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Market hours: {scheduler.is_market_hours()}")
    print(f"Weekday: {scheduler.is_weekday()}")
    
    print("\nScheduler status:")
    status = scheduler.get_status()
    for task_id, task in status['tasks'].items():
        print(f"  - {task['name']}: enabled={task['is_enabled']}, "
              f"next_run={task['next_run']}")
    
    print("\nRunning scheduler for 15 seconds...")
    print("Press Ctrl+C to stop\n")
    
    scheduler.start()
    
    try:
        time.sleep(15)
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.stop()
        print("\nScheduler stopped")
        print(f"Total runs: {len(scheduler.task_history)}")
