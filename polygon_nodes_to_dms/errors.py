"""Custom exceptions."""


class NodesToDMSBaseError(Exception):
    """Plugin base exception."""


class LayerNotSelectedError(NodesToDMSBaseError):
    """Risen when there is no active layer (layer is not selected from layer list)."""


class LayerNotPolygonMultiPolygonError(NodesToDMSBaseError):
    """Risen when active layer is not Polygon or MultiPolygon type."""


class OneFeatureNotSelectedError(NodesToDMSBaseError):
    """Risen when active layers has no or more than 1 selected features."""
