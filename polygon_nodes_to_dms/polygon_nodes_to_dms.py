# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PolygonNodesToDMS
                                 A QGIS plugin
 Show polygon nodes in DMSH format
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-04-06
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Paweł Strzelewicz
        email                : @
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from datetime import datetime
import os.path

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QWidget
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsPalLayerSettings,
    QgsProject,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
    QgsWkbTypes
)

from .aviation_gis_toolkit.angle import Angle
from .aviation_gis_toolkit.const import AT_LATITUDE, AT_LONGITUDE
# Initialize Qt resources from file resources.py
from .resources import qInitResources
# Import the code for the dialog
from .polygon_nodes_to_dms_dialog import PolygonNodesToDMSDialog


class PolygonNodesToDMS:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.output_layer = None
        self.current_layer = None
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            f'PolygonNodesToDMS_{locale}.qm')

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&PolygonNodesToDMS')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PolygonNodesToDMS', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/polygon_nodes_to_dms/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'PolygonNodesToDMS'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&PolygonNodesToDMS'),
                action)
            self.iface.removeToolBarIcon(action)

    def set_initial_plugin_state(self):
        """ Initialize plugin state when opened. """
        self.output_layer = None
        self.dlg.radioButtonOrderLonLat.setChecked(True)

    @staticmethod
    def gen_output_layer_name():
        """ Generate output layer name with the following pattern:
        NodesDMS_<yyyy>_<mm>_<dd>_<hh><mm><sec><<frac_sec>
        """
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S.%f")
        return f'NodesDMS_{timestamp}'

    def create_output_layer(self, layer_name):
        """ Create output layer with polygons - memory layer. """
        self.output_layer = QgsVectorLayer('Point?crs=epsg:4326', layer_name, 'memory')
        provider = self.output_layer.dataProvider()
        self.output_layer.startEditing()
        provider.addAttributes([QgsField("NODE_DMS", QVariant.String, len=100)])
        self.output_layer.commitChanges()
        QgsProject.instance().addMapLayer(self.output_layer)

    def set_output_layer_labels(self):
        """Add labels with coordinates to the output layer"""
        labels_setting = QgsPalLayerSettings()
        labels_setting.isExpression = True
        labels_setting.fieldName = "NODE_DMS"
        lyr_set = QgsVectorLayerSimpleLabeling(labels_setting)
        self.output_layer.setLabelsEnabled(True)
        self.output_layer.setLabeling(lyr_set)
        self.output_layer.triggerRepaint()

    def set_output_layer(self):
        """ Set output layer for polygon nodes with DMS format as active. """
        if self.output_layer is None:
            layer_name = self.gen_output_layer_name()
            self.create_output_layer(layer_name)
            self.set_output_layer_labels()
        self.iface.setActiveLayer(self.output_layer)

    @staticmethod
    def is_layer_polygon(layer):
        """Check if active layer has Polygon/MultiPolygon geometry type

        :param layer: layer to be checked (active layer)
        :return: True if layer geometry is Polygon/MultiPolygon, False otherwise
        """
        if layer is None:
            QMessageBox.critical(QWidget(), "Message", "No active layer.")
            return False
        if layer.wkbType() in [QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon]:
            return True

        QMessageBox.critical(QWidget(), "Message", "Active layer is not type: Polygon, Multipolygon.")
        return False

    @staticmethod
    def one_feature_selected(layer):
        """Check if only one feature is selected from active layer

        :param layer: layer to be checked (active layer)
        :return: True if one feature is selected, False otherwise
        """
        selected_count = layer.selectedFeatureCount()
        if selected_count != 1:
            QMessageBox.critical(QWidget(), "Message", f"{selected_count} polygons selected.\n"
                                                       "Select one polygon.")
            return False

        return True

    def get_node_dms_pattern(self):
        """Return label value pattern"""
        if self.dlg.radioButtonOrderLonLat.isChecked():
            return "{lon} {lat}"
        # only radioButtonOrderLatLon can be checked
        return "{lat} {lon}"

    def show_nodes_dms(self):
        """Generate and display polygon nodes coordinates in DMS format"""
        canvas = self.iface.mapCanvas()
        current_layer = canvas.currentLayer()
        if PolygonNodesToDMS.is_layer_polygon(current_layer):
            if PolygonNodesToDMS.one_feature_selected(current_layer):
                selected_feature = current_layer.selectedFeatures()[0]
                geom = selected_feature.geometry()
                node_dms = self.get_node_dms_pattern()
                self.set_output_layer()

                feat = QgsFeature()
                prov = self.output_layer.dataProvider()

                self.output_layer.startEditing()
                # Remove previous node coordinates
                prov.truncate()
                ang = Angle()

                for node_location in geom.vertices():
                    lon_dms = ang.dd_to_dms_string(node_location.x(), AT_LONGITUDE)
                    lat_dms = ang.dd_to_dms_string(node_location.y(), AT_LATITUDE)
                    dms_string = node_dms.format(lon=lon_dms, lat=lat_dms)
                    feat.setGeometry(node_location)
                    feat.setAttributes([dms_string])
                    prov.addFeatures([feat])

                self.output_layer.commitChanges()
                self.output_layer.updateExtents()
                self.iface.mapCanvas().setExtent(self.output_layer.extent())
                self.iface.mapCanvas().refresh()
        self.iface.setActiveLayer(current_layer)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg = PolygonNodesToDMSDialog()
            self.dlg.pushButtonShowNodes.clicked.connect(self.show_nodes_dms)
            self.dlg.pushButtonCancel.clicked.connect(self.dlg.close)

        # show the dialog
        self.dlg.show()
        self.set_initial_plugin_state()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
