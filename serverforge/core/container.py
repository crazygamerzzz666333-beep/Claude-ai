"""Application dependency container."""

from dataclasses import dataclass

from redis.asyncio import Redis

from serverforge.core.config import Settings
from serverforge.core.rate_limit import RateLimiter
from serverforge.core.security import SecurityService
from serverforge.db.pool import Database
from serverforge.services.ai.service import AIPlanner
from serverforge.services.analytics.service import AnalyticsService
from serverforge.services.backup.service import BackupService
from serverforge.services.builder.service import ServerBuilder
from serverforge.services.font.service import FontService
from serverforge.services.logging.service import GuildLogService
from serverforge.services.moderation.service import ModerationService
from serverforge.services.premium.service import PremiumService
from serverforge.services.templates.service import TemplateService
from serverforge.services.theme.service import ThemeService
from serverforge.services.tickets.service import TicketService
from serverforge.services.verification.service import VerificationService
from serverforge.services.welcome.service import WelcomeService


@dataclass(slots=True)
class Container:
    """Resolved application services."""

    settings: Settings
    database: Database
    redis: Redis
    rate_limiter: RateLimiter
    security: SecurityService
    fonts: FontService
    themes: ThemeService
    ai: AIPlanner
    logs: GuildLogService
    analytics: AnalyticsService
    builder: ServerBuilder
    backups: BackupService
    templates: TemplateService
    moderation: ModerationService
    premium: PremiumService
    tickets: TicketService
    welcome: WelcomeService
    verification: VerificationService


async def create_container(settings: Settings) -> Container:
    """Create and connect all application dependencies."""
    database = Database(settings.database_dsn)
    await database.connect()
    redis = Redis.from_url(settings.redis_dsn, decode_responses=False)
    logs = GuildLogService(database)
    analytics = AnalyticsService(database)
    fonts = FontService()
    themes = ThemeService()
    return Container(
        settings=settings,
        database=database,
        redis=redis,
        rate_limiter=RateLimiter(redis, "commands"),
        security=SecurityService(redis, settings.dangerous_action_ttl_seconds),
        fonts=fonts,
        themes=themes,
        ai=AIPlanner(themes, fonts),
        logs=logs,
        analytics=analytics,
        builder=ServerBuilder(analytics, logs),
        backups=BackupService(database),
        templates=TemplateService(database),
        moderation=ModerationService(database, logs),
        premium=PremiumService(database),
        tickets=TicketService(database),
        welcome=WelcomeService(database),
        verification=VerificationService(database, redis),
    )
