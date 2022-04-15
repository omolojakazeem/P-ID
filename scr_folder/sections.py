# System packages
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QStandardItemModel
from PyQt5.QtWidgets import QFrame, QComboBox

# Relative files
from src_testing.utils import draw_continuity_labels, draw_pipelines, draw_junctions, draw_equipments, draw_area_breaks, \
    draw_section_breaks, draw_composition_breaks, draw_vessels, draw_query_areas, draw_sensors, draw_tag


class FrameDrawing(QFrame):
    def paintEvent(self, e):  # override paintEvent() to draw what we want
        super().paintEvent(e)
        #
        qp = QPainter()
        qp.begin(self)

        qp.setPen(QPen(Qt.blue, 2))
        #
        p_Widget = self.parent().parent()
        selected_location = p_Widget.selectedLocation
        selected_part = p_Widget.selectedPart
        #useful_column_index = p_Widget.get_useful_column_name()
        cl_column_data = p_Widget.cl_column_data
        ab_column_data = p_Widget.ab_column_data
        sb_column_data = p_Widget.sb_column_data
        cb_column_data = p_Widget.cb_column_data
        vs_column_data = p_Widget.vs_column_data
        pl_column_data = p_Widget.pl_column_data
        pj_column_data = p_Widget.pj_column_data
        ts_column_data = p_Widget.ts_column_data
        es_column_data = p_Widget.es_column_data
        et_column_data = p_Widget.et_column_data
        ss_column_data = p_Widget.ss_column_data

        # if selected_location:
        #     print(p_Widget.selectedData)
        # else:
        #     print("no", p_Widget.selectedData)
        minX = p_Widget.minX - 200
        minY = p_Widget.minY - 200
        maxX = p_Widget.maxX + 200
        maxY = p_Widget.maxY + 200

        if 'Continuity Labels' in p_Widget.selectedData:
            draw_continuity_labels(self, p_Widget.selectedData['Continuity Labels'], minX, minY, maxX, maxY, selected_location, selected_part, cl_column_data, color=Qt.cyan)
        if 'Pipelines' in p_Widget.selectedData:
            draw_pipelines(self, p_Widget.selectedData['Pipelines'], minX, minY, maxX, maxY,selected_location,  selected_part, pl_column_data, color=Qt.black)
        if 'Pipeline Junctions' in p_Widget.selectedData:
            draw_junctions(self, p_Widget.selectedData['Pipeline Junctions'], minX, minY, maxX, maxY, selected_location, selected_part, pj_column_data, color=Qt.magenta)
        if 'Equipment symbols' in p_Widget.selectedData:
            draw_equipments(self, p_Widget.selectedData['Equipment symbols'], minX, minY, maxX, maxY, selected_location, selected_part,es_column_data, color=Qt.darkYellow)
        if 'Equipment Tags' in p_Widget.selectedData:
            draw_tag(self, p_Widget.selectedData['Equipment Tags'], minX, minY, maxX, maxY, selected_location, selected_part,et_column_data, color=Qt.darkYellow)
        if 'Sensors' in p_Widget.selectedData:
            draw_sensors(self, p_Widget.selectedData['Sensors'], minX, minY, maxX, maxY, selected_location, selected_part,ss_column_data, color=Qt.darkYellow)
        #        if p_Widget.ckSensor.isChecked() and 'Sensors' in p_Widget.selectedData:
        #            draw_sensors(self, p_Widget.selectedData['Sensors'], minX, minY, maxX, maxY, color=Qt.black)
        if 'Area Breaks' in p_Widget.selectedData:
            draw_area_breaks(self, p_Widget.selectedData['Area Breaks'], minX, minY, maxX, maxY, selected_location,  selected_part, ab_column_data,  color=Qt.green)
        if 'Section Breaks' in p_Widget.selectedData:
            draw_section_breaks(self, p_Widget.selectedData['Section Breaks'], minX, minY, maxX, maxY, selected_location,  selected_part, sb_column_data,  color=Qt.red)
        if 'Composition Breaks' in p_Widget.selectedData:
            draw_composition_breaks(self, p_Widget.selectedData['Composition Breaks'], minX, minY, maxX, maxY, selected_location, selected_part, cb_column_data, color=Qt.blue)
        if 'Vessels' in p_Widget.selectedData:
            draw_vessels(self, p_Widget.selectedData['Vessels'], minX, minY, maxX, maxY, selected_location, selected_part, vs_column_data, color=Qt.yellow)

        # draw selectedAreas
        draw_query_areas(self, p_Widget.selectedAreas, minX, minY, maxX, maxY, color=Qt.black)

        qp.end()


# the combobox with checkable items, used for Area/Section/Composition Breaks selection
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

    def item_checked(self, index):

        # getting item at index
        item = self.model().item(index, 0)

        # return true if checked else false
        return item.checkState() == Qt.Checked

    # calling method
    def check_items(self):
        # blank list
        checkedItems = []

        # traversing the items
        for i in range(self.count()):

            # if item is checked add it to the list
            if self.item_checked(i):
                checkedItems.append(i)
        return checkedItems
