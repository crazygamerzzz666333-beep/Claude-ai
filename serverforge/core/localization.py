"""Localization helpers for command names, descriptions, and responses."""

from collections.abc import Mapping

DEFAULT_LOCALE = "en-US"

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en-US": {
        "command.ai.help": "Ask ServerForge AI to design or modify your server.",
        "command.template.help": "Save, load, import, export, and publish server templates.",
        "command.backup.help": "Create, compare, undo, redo, and restore server backups.",
        "command.moderation.help": "Moderate users and protect the server.",
        "command.ticket.help": "Manage support tickets.",
        "command.welcome.help": "Configure welcome messages and verification.",
        "command.analytics.help": "View server growth and activity analytics.",
        "command.theme.help": "Apply themes and font styles to the server.",
        "error.permissions": "You do not have permission to run this command.",
        "error.cooldown": "This command is on cooldown. Try again shortly.",
        "error.guild_only": "This command can only be used in a server.",
        "success.completed": "ServerForge AI completed the requested action.",
    }
}


def translate(key: str, locale: str | None = None, variables: Mapping[str, object] | None = None) -> str:
    """Translate a message key and format it with optional variables."""
    language = locale or DEFAULT_LOCALE
    template = _TRANSLATIONS.get(language, _TRANSLATIONS[DEFAULT_LOCALE]).get(key, key)
    if variables:
        return template.format(**variables)
    return template


def command_localizations(key: str) -> dict[str, str]:
    """Return localizations supported by Disnake command descriptors."""
    return {locale: values[key] for locale, values in _TRANSLATIONS.items() if key in values}
