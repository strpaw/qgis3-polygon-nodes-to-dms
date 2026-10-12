"""Custom exceptions for the Nodes to DMS plugin"""


class NodesToDMSBaseError(Exception):
    """Base exception for Nodes to DMS Plugin."""


class LayerNotSelectedError(NodesToDMSBaseError):
    """Raised when no active layer is selected."""


class LayerNotPolygonMultiPolygonError(NodesToDMSBaseError):
    """Raised when the layer geometry type is not Polygon or MultiPolygon."""


class OneFeatureNotSelectedError(NodesToDMSBaseError):
    """Raised when exactly one feature is not selected."""
