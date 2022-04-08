from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QStandardItemModel
from PyQt5.QtWidgets import QFrame, QComboBox

from src.utils import draw_continuity_labels, draw_pipelines, draw_junctions, draw_equipments, draw_area_breaks, \
    draw_section_breaks, draw_composition_breaks, draw_vessels, draw_query_areas


class FrameDrawing(QFrame):
    def paintEvent(self, e):  # override paintEvent() to draw what we want
        super().paintEvent(e)
        #
        qp = QPainter()
        qp.begin(self)

        qp.setPen(QPen(Qt.blue, 2))
        #
        p_Widget = self.parent().parent()
        minX = p_Widget.minX - 200
        minY = p_Widget.minY - 200
        maxX = p_Widget.maxX + 200
        maxY = p_Widget.maxY + 200
        if 'Continuity Labels' in p_Widget.selectedData:
            draw_continuity_labels(self, p_Widget.selectedData['Continuity Labels'], minX, minY, maxX, maxY,
                                   color=Qt.cyan)
        if 'Pipelines' in p_Widget.selectedData:
            draw_pipelines(self, p_Widget.selectedData['Pipelines'], minX, minY, maxX, maxY, color=Qt.black)
        if 'Pipeline Junctions' in p_Widget.selectedData:
            draw_junctions(self, p_Widget.selectedData['Pipeline Junctions'], minX, minY, maxX, maxY, color=Qt.magenta)
        if 'Equipment symbols' in p_Widget.selectedData:
            draw_equipments(self, p_Widget.selectedData['Equipment symbols'], minX, minY, maxX, maxY,
                            color=Qt.darkYellow)
        #        if p_Widget.ckSensor.isChecked() and 'Sensors' in p_Widget.selectedData:
        #            draw_sensors(self, p_Widget.selectedData['Sensors'], minX, minY, maxX, maxY, color=Qt.black)
        if 'Area Breaks' in p_Widget.selectedData:
            draw_area_breaks(self, p_Widget.selectedData['Area Breaks'], minX, minY, maxX, maxY, color=Qt.green)
        if 'Section Breaks' in p_Widget.selectedData:
            draw_section_breaks(self, p_Widget.selectedData['Section Breaks'], minX, minY, maxX, maxY, color=Qt.red)
        if 'Composition Breaks' in p_Widget.selectedData:
            draw_composition_breaks(self, p_Widget.selectedData['Composition Breaks'], minX, minY, maxX, maxY,
                                    color=Qt.blue)
        if 'Vessels' in p_Widget.selectedData:
            draw_vessels(self, p_Widget.selectedData['Vessels'], minX, minY, maxX, maxY, color=Qt.yellow)

        # draw selectedAreas
        draw_query_areas(self, p_Widget.selectedAreas, minX, minY, maxX, maxY, color=Qt.black)

        #
        qp.end()


#### the combobox with checkable items, used for Area/Section/Composition Breaks selection
class CheckableComboBox(QComboBox):
    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self.view().pressed.connect(self.handleItemPressed)  # connect the clicked event to function handleItemPressed()
        self.setModel(QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)