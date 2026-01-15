from celery import shared_task
from django.conf import settings
from django.utils import timezone

from observability import get_logger

from .models import AutomationTask

logger = get_logger(__name__)

# 配置: Stage 2 延迟时间 (秒)
STAGE2_DELAY_SECONDS = getattr(settings, "DAILY_BRIEFING_STAGE2_DELAY", 600)  # 默认 10 分钟


@shared_task(bind=True, max_retries=2)
def run_daily_briefing_scraper(self, task_id: str):
    """
    Stage 1: Scrape Briefing.com and write to Google Sheets.
    Upon completion, automatically schedules Stage 2 with a 10-minute delay.
    """
    from .services.briefing_scraper import BriefingScraperService

    task = None
    try:
        task = AutomationTask.objects.get(id=task_id)
        task.status = "scraping"
        task.started_at = timezone.now()
        task.save()

        logger.info(
            "Starting Daily Briefing Stage 1 (Scraping)",
            extra={"task_id": task_id, "celery_task_id": self.request.id}
        )

        service = BriefingScraperService()
        service.run()

        # Update status to waiting for Stage 2
        task.status = "waiting_stage2"
        task.stage1_completed_at = timezone.now()

        # Calculate scheduled time for Stage 2
        scheduled_time = timezone.now() + timezone.timedelta(seconds=STAGE2_DELAY_SECONDS)
        task.stage2_scheduled_at = scheduled_time
        task.save()

        logger.info(
            "Daily Briefing Stage 1 completed, scheduling Stage 2",
            extra={
                "task_id": task_id,
                "stage2_delay_seconds": STAGE2_DELAY_SECONDS,
                "stage2_scheduled_at": scheduled_time.isoformat()
            }
        )

        # Schedule Stage 2 with delay
        run_daily_briefing_generator.apply_async(
            args=[task_id],
            countdown=STAGE2_DELAY_SECONDS
        )

    except AutomationTask.DoesNotExist:
        logger.error(
            "Task not found for Daily Briefing scraper",
            extra={"task_id": task_id}
        )
        raise
    except Exception as e:
        logger.exception(
            "Daily Briefing Stage 1 failed",
            extra={"task_id": task_id, "error": str(e)}
        )
        if task is not None:
            task.status = "failed"
            task.error_message = str(e)
            task.save()
        raise


@shared_task(bind=True, max_retries=2, soft_time_limit=2700, time_limit=3600)
def run_daily_briefing_generator(self, task_id: str):
    """
    Stage 2: Read from Sheets, generate AI report, upload to Drive.
    Requires longer timeout as Perplexity Deep Research may take 15-30 minutes.
    """
    from .services.daily_briefing import DailyBriefingService

    task = None
    try:
        task = AutomationTask.objects.get(id=task_id)
        task.status = "generating"
        task.save()

        logger.info(
            "Starting Daily Briefing Stage 2 (AI Generation)",
            extra={"task_id": task_id, "celery_task_id": self.request.id}
        )

        service = DailyBriefingService()
        result_urls = service.run()

        task.status = "completed"
        task.result_urls = result_urls
        task.completed_at = timezone.now()
        task.save()

        logger.info(
            "Daily Briefing Stage 2 completed",
            extra={
                "task_id": task_id,
                "result_urls": result_urls
            }
        )

    except AutomationTask.DoesNotExist:
        logger.error(
            "Task not found for Daily Briefing generator",
            extra={"task_id": task_id}
        )
        raise
    except Exception as e:
        logger.exception(
            "Daily Briefing Stage 2 failed",
            extra={"task_id": task_id, "error": str(e)}
        )
        if task is not None:
            task.status = "failed"
            task.error_message = str(e)
            task.save()
        raise


@shared_task(bind=True)
def run_daily_briefing_full(self, task_id: str):
    """
    Trigger the complete Daily Briefing workflow.
    Only calls Stage 1; Stage 1 automatically schedules Stage 2 upon completion.
    """
    logger.info(
        "Triggering full Daily Briefing workflow",
        extra={"task_id": task_id, "celery_task_id": self.request.id}
    )
    run_daily_briefing_scraper.delay(task_id)


@shared_task(bind=True, max_retries=2, soft_time_limit=1800, time_limit=3600)
def run_forensic_accounting(self, task_id: str, companies: list[dict]):
    """
    Run forensic accounting analysis for a list of companies.
    Each company should have 'name' and 'ticker' fields.
    """
    from .services.forensic_accounting import ForensicAccountingService

    task = None
    try:
        task = AutomationTask.objects.get(id=task_id)
        task.status = "generating"
        task.started_at = timezone.now()
        task.save()

        logger.info(
            "Starting Forensic Accounting analysis",
            extra={
                "task_id": task_id,
                "celery_task_id": self.request.id,
                "company_count": len(companies)
            }
        )

        service = ForensicAccountingService()
        results = service.run(companies)

        task.status = "completed"
        task.result_urls = {"reports": results}
        task.completed_at = timezone.now()
        task.save()

        logger.info(
            "Forensic Accounting analysis completed",
            extra={
                "task_id": task_id,
                "reports_generated": len([r for r in results if r.get("status") == "success"])
            }
        )

    except AutomationTask.DoesNotExist:
        logger.error(
            "Task not found for Forensic Accounting",
            extra={"task_id": task_id}
        )
        raise
    except Exception as e:
        logger.exception(
            "Forensic Accounting analysis failed",
            extra={"task_id": task_id, "error": str(e)}
        )
        if task is not None:
            task.status = "failed"
            task.error_message = str(e)
            task.save()
        raise
