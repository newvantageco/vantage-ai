from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any
import json
import secrets

from sqlalchemy import String, Text, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Translation(Base):
    """Translation records for content items."""
    __tablename__ = "translations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # Clerk user ID
    
    # Translation details
    source_locale: Mapped[str] = mapped_column(String(10), nullable=False)  # en, es, fr, etc.
    target_locale: Mapped[str] = mapped_column(String(10), nullable=False)  # en, es, fr, etc.
    translated_content: Mapped[str] = mapped_column(Text, nullable=False)  # JSON of translated fields
    
    # Translation metadata
    translation_provider: Mapped[str] = mapped_column(String(50), nullable=False)  # google, azure, openai, manual
    translation_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # gpt-4, claude, etc.
    confidence_score: Mapped[Optional[float]] = mapped_column(nullable=True)  # 0.0 to 1.0
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, completed, failed, reviewed
    is_auto_translated: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_reviewed: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Review
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_translations_content_id", "content_id"),
        Index("ix_translations_org_id", "org_id"),
        Index("ix_translations_user_id", "user_id"),
        Index("ix_translations_target_locale", "target_locale"),
        Index("ix_translations_status", "status"),
        Index("ix_translations_created_at", "created_at"),
        UniqueConstraint("content_id", "target_locale", name="uq_translations_content_locale"),
    )

    def get_translated_content(self) -> Dict[str, Any]:
        """Get translated content as a dictionary."""
        try:
            return json.loads(self.translated_content)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_translated_content(self, content: Dict[str, Any]) -> None:
        """Set translated content from a dictionary."""
        self.translated_content = json.dumps(content)

    def update_field(self, field: str, value: str) -> None:
        """Update a specific field in the translated content."""
        content = self.get_translated_content()
        content[field] = value
        self.set_translated_content(content)

    def get_field(self, field: str) -> Optional[str]:
        """Get a specific field from the translated content."""
        content = self.get_translated_content()
        return content.get(field)


class TranslationJob(Base):
    """Translation jobs for batch processing."""
    __tablename__ = "translation_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # Clerk user ID
    
    # Job details
    content_ids: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of content IDs
    target_locales: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of target locales
    translation_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    translation_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, running, completed, failed
    progress_percent: Mapped[int] = mapped_column(default=0, nullable=False)
    total_items: Mapped[int] = mapped_column(default=0, nullable=False)
    completed_items: Mapped[int] = mapped_column(default=0, nullable=False)
    failed_items: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    failed_content_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_translation_jobs_org_id", "org_id"),
        Index("ix_translation_jobs_user_id", "user_id"),
        Index("ix_translation_jobs_status", "status"),
        Index("ix_translation_jobs_created_at", "created_at"),
    )

    def get_content_ids(self) -> list[str]:
        """Get content IDs as a list."""
        try:
            return json.loads(self.content_ids)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_content_ids(self, content_ids: list[str]) -> None:
        """Set content IDs from a list."""
        self.content_ids = json.dumps(content_ids)

    def get_target_locales(self) -> list[str]:
        """Get target locales as a list."""
        try:
            return json.loads(self.target_locales)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_target_locales(self, locales: list[str]) -> None:
        """Set target locales from a list."""
        self.target_locales = json.dumps(locales)

    def get_failed_content_ids(self) -> list[str]:
        """Get failed content IDs as a list."""
        if not self.failed_content_ids:
            return []
        try:
            return json.loads(self.failed_content_ids)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_failed_content_ids(self, content_ids: list[str]) -> None:
        """Set failed content IDs from a list."""
        self.failed_content_ids = json.dumps(content_ids)

    def add_failed_content_id(self, content_id: str) -> None:
        """Add a content ID to the failed list."""
        failed = self.get_failed_content_ids()
        if content_id not in failed:
            failed.append(content_id)
            self.set_failed_content_ids(failed)


class TranslationConfig(Base):
    """Translation configuration for organizations."""
    __tablename__ = "translation_config"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, unique=True)
    
    # Provider settings
    default_provider: Mapped[str] = mapped_column(String(50), default="google", nullable=False)
    default_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Supported locales
    supported_locales: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    default_source_locale: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    
    # Quality settings
    min_confidence_score: Mapped[float] = mapped_column(default=0.7, nullable=False)
    auto_review_threshold: Mapped[float] = mapped_column(default=0.9, nullable=False)
    
    # Features
    auto_translate_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    human_review_required: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_translation_config_org_id", "org_id"),
    )

    def get_supported_locales(self) -> list[str]:
        """Get supported locales as a list."""
        try:
            return json.loads(self.supported_locales)
        except (json.JSONDecodeError, TypeError):
            return ["en"]

    def set_supported_locales(self, locales: list[str]) -> None:
        """Set supported locales from a list."""
        self.supported_locales = json.dumps(locales)

    def is_locale_supported(self, locale: str) -> bool:
        """Check if a locale is supported."""
        return locale in self.get_supported_locales()


# Supported locales
SUPPORTED_LOCALES = {
    "en": {"name": "English", "native_name": "English"},
    "es": {"name": "Spanish", "native_name": "Español"},
    "fr": {"name": "French", "native_name": "Français"},
    "de": {"name": "German", "native_name": "Deutsch"},
    "it": {"name": "Italian", "native_name": "Italiano"},
    "pt": {"name": "Portuguese", "native_name": "Português"},
    "ru": {"name": "Russian", "native_name": "Русский"},
    "ja": {"name": "Japanese", "native_name": "日本語"},
    "ko": {"name": "Korean", "native_name": "한국어"},
    "zh": {"name": "Chinese", "native_name": "中文"},
    "ar": {"name": "Arabic", "native_name": "العربية"},
    "hi": {"name": "Hindi", "native_name": "हिन्दी"},
    "nl": {"name": "Dutch", "native_name": "Nederlands"},
    "sv": {"name": "Swedish", "native_name": "Svenska"},
    "da": {"name": "Danish", "native_name": "Dansk"},
    "no": {"name": "Norwegian", "native_name": "Norsk"},
    "fi": {"name": "Finnish", "native_name": "Suomi"},
    "pl": {"name": "Polish", "native_name": "Polski"},
    "tr": {"name": "Turkish", "native_name": "Türkçe"},
    "th": {"name": "Thai", "native_name": "ไทย"},
    "vi": {"name": "Vietnamese", "native_name": "Tiếng Việt"},
    "id": {"name": "Indonesian", "native_name": "Bahasa Indonesia"},
    "ms": {"name": "Malay", "native_name": "Bahasa Melayu"},
    "tl": {"name": "Filipino", "native_name": "Filipino"},
    "he": {"name": "Hebrew", "native_name": "עברית"},
    "uk": {"name": "Ukrainian", "native_name": "Українська"},
    "cs": {"name": "Czech", "native_name": "Čeština"},
    "hu": {"name": "Hungarian", "native_name": "Magyar"},
    "ro": {"name": "Romanian", "native_name": "Română"},
    "bg": {"name": "Bulgarian", "native_name": "Български"},
    "hr": {"name": "Croatian", "native_name": "Hrvatski"},
    "sk": {"name": "Slovak", "native_name": "Slovenčina"},
    "sl": {"name": "Slovenian", "native_name": "Slovenščina"},
    "et": {"name": "Estonian", "native_name": "Eesti"},
    "lv": {"name": "Latvian", "native_name": "Latviešu"},
    "lt": {"name": "Lithuanian", "native_name": "Lietuvių"},
    "el": {"name": "Greek", "native_name": "Ελληνικά"},
    "is": {"name": "Icelandic", "native_name": "Íslenska"},
    "ga": {"name": "Irish", "native_name": "Gaeilge"},
    "cy": {"name": "Welsh", "native_name": "Cymraeg"},
    "mt": {"name": "Maltese", "native_name": "Malti"},
    "eu": {"name": "Basque", "native_name": "Euskera"},
    "ca": {"name": "Catalan", "native_name": "Català"},
    "gl": {"name": "Galician", "native_name": "Galego"},
    "af": {"name": "Afrikaans", "native_name": "Afrikaans"},
    "sw": {"name": "Swahili", "native_name": "Kiswahili"},
    "am": {"name": "Amharic", "native_name": "አማርኛ"},
    "az": {"name": "Azerbaijani", "native_name": "Azərbaycan"},
    "be": {"name": "Belarusian", "native_name": "Беларуская"},
    "bn": {"name": "Bengali", "native_name": "বাংলা"},
    "bs": {"name": "Bosnian", "native_name": "Bosanski"},
    "fa": {"name": "Persian", "native_name": "فارسی"},
    "gu": {"name": "Gujarati", "native_name": "ગુજરાતી"},
    "ka": {"name": "Georgian", "native_name": "ქართული"},
    "kk": {"name": "Kazakh", "native_name": "Қазақ"},
    "km": {"name": "Khmer", "native_name": "ខ្មែរ"},
    "kn": {"name": "Kannada", "native_name": "ಕನ್ನಡ"},
    "ky": {"name": "Kyrgyz", "native_name": "Кыргыз"},
    "lo": {"name": "Lao", "native_name": "ລາວ"},
    "mk": {"name": "Macedonian", "native_name": "Македонски"},
    "ml": {"name": "Malayalam", "native_name": "മലയാളം"},
    "mn": {"name": "Mongolian", "native_name": "Монгол"},
    "mr": {"name": "Marathi", "native_name": "मराठी"},
    "my": {"name": "Burmese", "native_name": "မြန်မာ"},
    "ne": {"name": "Nepali", "native_name": "नेपाली"},
    "pa": {"name": "Punjabi", "native_name": "ਪੰਜਾਬੀ"},
    "si": {"name": "Sinhala", "native_name": "සිංහල"},
    "ta": {"name": "Tamil", "native_name": "தமிழ்"},
    "te": {"name": "Telugu", "native_name": "తెలుగు"},
    "ur": {"name": "Urdu", "native_name": "اردو"},
    "uz": {"name": "Uzbek", "native_name": "O'zbek"},
    "zu": {"name": "Zulu", "native_name": "IsiZulu"}
}

# Translation providers
TRANSLATION_PROVIDERS = {
    "google": {
        "name": "Google Translate",
        "description": "Google Cloud Translation API",
        "supports_auto_detection": True,
        "max_text_length": 100000,
        "supported_locales": list(SUPPORTED_LOCALES.keys())
    },
    "azure": {
        "name": "Azure Translator",
        "description": "Microsoft Azure Cognitive Services Translator",
        "supports_auto_detection": True,
        "max_text_length": 50000,
        "supported_locales": list(SUPPORTED_LOCALES.keys())
    },
    "openai": {
        "name": "OpenAI GPT",
        "description": "OpenAI GPT models for translation",
        "supports_auto_detection": False,
        "max_text_length": 4000,
        "supported_locales": list(SUPPORTED_LOCALES.keys())
    },
    "manual": {
        "name": "Manual Translation",
        "description": "Human translation",
        "supports_auto_detection": False,
        "max_text_length": 1000000,
        "supported_locales": list(SUPPORTED_LOCALES.keys())
    }
}
