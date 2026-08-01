"""Tests for the architecture module."""

# Pre-load brain.stages to prevent circular import between
# brain.architecture.generator and brain.stages.__init__ during pytest collection.
import brain.stages  # noqa: F401
