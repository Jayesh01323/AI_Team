"""
Intent Engine package.

Converts natural language conversations into structured Project Knowledge.
Determines WHAT the user is trying to build. Does NOT decide HOW to build it.

Public API::

    from brain.intent import IntentEngine, IntentResult
"""

from brain.intent.engine import IntentEngine
from brain.intent.models import IntentAnalysis, IntentResult

__all__ = [
    "IntentAnalysis",
    "IntentEngine",
    "IntentResult",
]