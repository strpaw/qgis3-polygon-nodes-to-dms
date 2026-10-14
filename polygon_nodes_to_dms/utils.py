"""Helper Plugin functions"""


from qgis._core import QgsVectorLayer, QgsWkbTypes


from .exceptions import (
    InvalidLayerGeometryTypeError,
    OneFeatureNotSelectedError
)

_ALLOWED_GEOMETRY: tuple[QgsWkbTypes.Type, ...] = (
    QgsWkbTypes.Polygon,
    QgsWkbTypes.MultiPolygon,
)


def ensure_geometry_type(layer: QgsVectorLayer,
                         allowed: tuple[QgsWkbTypes.Type] = _ALLOWED_GEOMETRY) -> None:
    """Ensures that the geometry is of the correct type.

    :param layer: Layer to be checked.
    :param allowed: list of allowed geometry types.
    :raises: InvalidLayerGeometryTypeError: If the layer geometry type is not among the allowed types
    """
    if layer.wkbType() not in allowed:
        raise InvalidLayerGeometryTypeError(f"Geometry type {QgsWkbTypes.displayString(layer.wkbType())} is not supported.")


def ensure_single_feature_selected(layer: QgsVectorLayer) -> None:
    """Ensure exactly one feature is selected in the layer.

    :param layer: Layer to be checked
    :raises OneFeatureNotSelectedError: If the number of selected features is not exactly one.
    """
    if layer.selectedFeatureCount() != 1:
        raise OneFeatureNotSelectedError(f"Not exactly one feature is selected.")


def validate_layer(layer: QgsVectorLayer) -> None:
    """Validate input layer.

    :param layer: Vector layer to validate.
    :raises InvalidLayerGeometryTypeError: If the geometry type is unsupported.
    :raises OneFeatureNotSelectedError: If exactly one feature is not selected.
    """
    ensure_geometry_type(layer)
    ensure_single_feature_selected(layer)
