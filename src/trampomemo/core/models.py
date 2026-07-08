# Import domain models so Base.metadata contains the complete schema.
from trampomemo.answers.models import Answer  # noqa: F401
from trampomemo.chunks.models import Chunk  # noqa: F401
from trampomemo.core.base import Base
from trampomemo.evidence.models import Evidence  # noqa: F401
from trampomemo.memory.models import Memory  # noqa: F401
from trampomemo.source_content.models import SourceContent  # noqa: F401
from trampomemo.sources.models import Source  # noqa: F401

__all__ = ["Base"]
