"""Handling output layer."""
from datetime import datetime

from qgis.core import (
    QgsField,
    QgsPalLayerSettings,
    QgsProject,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QVariant

FIELD_NAME = "node_dms"


class OutputLayer:
    """Output layer handling."""

    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.name = None
        self.layer = None

    def _generate_name(self) -> None:
        """Generate name based in format: NodesDMS_<YYYY>_<MM>_<DD>_<HH><MM>."""
        timestamp = datetime.now()
        self.name = f'NodesDMS_{timestamp.strftime("%Y_%m_%d_%H%M")}'

    def create(self) -> None:
        """Create result layer as Point layer. Note this is memory layer so before closing QGIS save it on the disk
        to keep results.
        """
        self._generate_name()
        self.layer = QgsVectorLayer(
            path="Point?crs=epsg:4326",
            baseName=self.name,
            providerLib="memory"
        )
        self.layer.startEditing()
        prov = self.layer.dataProvider()
        prov.addAttributes(
            [
                QgsField(
                    name=FIELD_NAME,
                    type=QVariant.String,
                    len=100
                ),
            ]
        )
        self.layer.commitChanges()

    def set_labels(self) -> None:
        """Set labels with coordinates to the output layer."""
        labels_setting = QgsPalLayerSettings()
        labels_setting.isExpression = True
        labels_setting.fieldName = FIELD_NAME
        lyr_set = QgsVectorLayerSimpleLabeling(labels_setting)
        self.layer.setLabelsEnabled(True)
        self.layer.setLabeling(lyr_set)
        self.layer.triggerRepaint()

    def is_registered(self) -> bool:
        """Check if result layer is added to the layer list in the current project - layer was created
         and not removed from layers list in QGIS Project."""
        return bool(QgsProject.instance().mapLayersByName(self.name))

    def setup(self) -> None:
        """Prepare result layer for editing."""
        if not self.name or not self.is_registered():
            self.create()
            self.set_labels()
            QgsProject.instance().addMapLayer(self.layer)

        self.iface.setActiveLayer(self.layer)
