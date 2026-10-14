"""Handling output layer."""
from datetime import datetime

from qgis.core import (
    QgsField,
    QgsPalLayerSettings,
    QgsProject,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling
)
from qgis.PyQt.QtCore import QVariant


FIELD_NAME = "node_dms"
LAYER_NAME_PREFIX = "NodesDMS"
LAYER_NAME_SUFFIX_FORMAT = "%Y_%m_%d_%H%M"
LAYER_CRS = "epsg:4326"


def generate_name() -> str:
    """Generate layer name using current timestamp.

    :return: A name in the format <prefix>_<timestamp>
    """
    timestamp = datetime.now()
    return f"{LAYER_NAME_PREFIX}_{timestamp.strftime(LAYER_NAME_SUFFIX_FORMAT)}"


def create_layer(name: str) -> QgsVectorLayer:
    """Create output layer - to keep formatted polygon vertices with formatted DMS coordinates.
    
    :param name: Name of the output layer.
    :return: The created output layer (point, memory).
    """
    layer = QgsVectorLayer(
        path=f"Point?crs={LAYER_CRS}",
        baseName=name,
        providerLib="memory"
    )
    prov = layer.dataProvider()
    prov.addAttributes(
        [
            QgsField(
                name=FIELD_NAME,
                type=QVariant.String,
                len=100
            ),
        ]
    )
    layer.updateFields()
    return layer


def set_labels(layer: QgsVectorLayer) -> None:
    """Enable labeling using the output field.

    :param layer: output layer.
    """
    settings = QgsPalLayerSettings()
    settings.isExpression = True
    settings.fieldName = FIELD_NAME
    layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    layer.setLabelsEnabled(True)
    layer.triggerRepaint()


def get_output_layer() -> QgsVectorLayer:
    """Create, configure, and register the output layer.

    :return: The configured output layer added to the current project.
    """
    layer = create_layer(generate_name())
    set_labels(layer)
    QgsProject.instance().addMapLayer(layer)
    return layer
