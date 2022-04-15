import sys

# System packages
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QGridLayout, QLabel, QSplitter, QHBoxLayout, QComboBox, \
    QPushButton, \
    QFileDialog, QTextEdit, QCheckBox, QLineEdit, QMessageBox, QFontDialog, QTableWidget, QTableWidgetItem, QSizePolicy, \
    QScrollArea

# Relative files


from src_testing.sections import FrameDrawing, CheckableComboBox
from src_testing.utils import query_by_areas, query_to_text, read_csv, find_ranges


class NetListGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.data = {}  # store data dictionary (see netlist_reader.py)
        self.location_list_name = None  # store data dictionary (see netlist_reader.py)
        self.column = {}  # store column name dictionary (see netlist_reader.py)
        self.columns = {}  # store column name dictionary (see netlist_reader.py)
        self.minX = 0  # store minX, minY, maxX, maxY of all coordinates available in CSV file
        self.minY = 0
        self.maxX = 0
        self.maxY = 0
        self.selectedData = {}  # store components (e.g. queried pipelines, equipments)
        self.selectedAreas = []
        self.selectedLocation = []
        self.selectedPart = []
        self.location_list_name_sorted = []
        self.column_list = []

        self.cl_column_data = None
        self.ab_column_data = None
        self.sb_column_data = None
        self.cb_column_data = None
        self.vs_column_data = None
        self.pl_column_data = None
        self.pj_column_data = None
        self.ts_column_data = None
        self.es_column_data = None
        self.et_column_data = None
        self.ss_column_data = None

        #
        self.initUI()

    # define GUI components
    def initUI(self):
        hbox = QHBoxLayout(self)

        # 1 - LEFT QFrame
        left_frame = QFrame(self)
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setMaximumWidth(400)

        # the left QFrame uses grid layout to place GUI components

        left_grid = QGridLayout()
        left_grid.setSpacing(12)

        # Create the Upload file control
        self.load_file_btn = QPushButton('Browse')
        left_grid.addWidget(self.load_file_btn, 1, 0)
        self.load_file_btn.clicked.connect(self.on_load_file_btn)

        self.load_file_label = QLabel('File name')
        left_grid.addWidget(self.load_file_label, 1, 1)

        self.show_current_data_btn = QPushButton('Show Data')
        left_grid.addWidget(self.show_current_data_btn, 1, 2)
        self.show_current_data_btn.clicked.connect(self.message_display)

        # Part Display Selection

        # Part - Pipeline

        self.select_pipeline_checkbox = QCheckBox("Pipelines", self)
        self.select_pipeline_checkbox.setChecked(True)
        left_grid.addWidget(self.select_pipeline_checkbox, 2, 0)
        self.select_pipeline_checkbox.stateChanged.connect(self.on_select_pipeline_checkbox)

        # Part - Equipment

        self.select_equipment_checkbox = QCheckBox("Equipment", self)
        self.select_equipment_checkbox.setChecked(True)
        left_grid.addWidget(self.select_equipment_checkbox, 2, 1)
        self.select_equipment_checkbox.stateChanged.connect(self.on_select_equipment_checkbox)

        # Part - Continuity Labels

        self.select_continuity_checkbox = QCheckBox("Cont. Labels", self)
        self.select_continuity_checkbox.setChecked(True)
        left_grid.addWidget(self.select_continuity_checkbox, 2, 2)
        self.select_continuity_checkbox.stateChanged.connect(self.on_select_continuity_checkbox)

        # Part - Area Breaks

        self.select_area_break_checkbox = QCheckBox("Area Breaks", self)
        self.select_area_break_checkbox.setChecked(True)
        left_grid.addWidget(self.select_area_break_checkbox, 3, 0)
        self.select_area_break_checkbox.stateChanged.connect(self.on_select_area_break_checkbox)

        # Part - Section Breaks

        self.select_section_break_checkbox = QCheckBox("Sect. Breaks", self)
        self.select_section_break_checkbox.setChecked(True)
        left_grid.addWidget(self.select_section_break_checkbox, 3, 1)
        self.select_section_break_checkbox.stateChanged.connect(self.on_select_section_break_checkbox)

        # Part - Composition Breaks

        self.select_composition_break_checkbox = QCheckBox("Comp. Breaks", self)
        self.select_composition_break_checkbox.setChecked(True)
        left_grid.addWidget(self.select_composition_break_checkbox, 3, 2)
        self.select_composition_break_checkbox.stateChanged.connect(self.on_select_composition_break_checkbox)

        self.select_vessel_checkbox = QCheckBox("Vessels", self)
        self.select_vessel_checkbox.setChecked(True)
        left_grid.addWidget(self.select_vessel_checkbox, 4, 0)
        self.select_vessel_checkbox.stateChanged.connect(self.on_select_vessel_checkbox)

        self.select_sensor_checkbox = QCheckBox("Sensors", self)
        self.select_sensor_checkbox.setChecked(True)
        left_grid.addWidget(self.select_sensor_checkbox, 4, 1)
        self.select_sensor_checkbox.stateChanged.connect(self.on_select_sensor_checkbox)

        self.select_equipment_tag_checkbox = QCheckBox("Equip Tags", self)
        self.select_equipment_tag_checkbox.setChecked(True)
        left_grid.addWidget(self.select_equipment_tag_checkbox, 4, 2)
        self.select_equipment_tag_checkbox.stateChanged.connect(self.on_select_equipment_tag_checkbox)

        # Filter Parts by location

        part_location_label = QLabel('Select Location')
        left_grid.addWidget(part_location_label, 5, 0)

        # part_location_search_label = QLabel('Select Part to Search')
        # left_grid.addWidget(part_location_search_label, 4, 1)

        self.part_location_options = CheckableComboBox()
        left_grid.addWidget(self.part_location_options, 5, 1)

        # self.part_query_options = CheckableComboBox()
        # left_grid.addWidget(self.part_query_options, 5, 1)

        self.part_query_btn = QPushButton('Query')
        left_grid.addWidget(self.part_query_btn, 5, 2)
        self.part_query_btn.clicked.connect(self.part_lookup_by_location)


        # Area Break
        area_break_label = QLabel('Area Section')
        left_grid.addWidget(area_break_label, 6, 0)

        self.area_break_query_options = CheckableComboBox()
        left_grid.addWidget(self.area_break_query_options, 6, 1)

        self.area_break_query_btn = QPushButton('Query')
        left_grid.addWidget(self.area_break_query_btn, 6, 2)
        self.area_break_query_btn.clicked.connect(self.on_area_break_query_btn)

        ##

        # Section Break
        section_break_label = QLabel('Section Break')
        left_grid.addWidget(section_break_label, 7, 0)

        self.section_break_query_options = CheckableComboBox()
        left_grid.addWidget(self.section_break_query_options, 7, 1)

        self.section_break_query_btn = QPushButton('Query')
        left_grid.addWidget(self.section_break_query_btn, 7, 2)
        self.section_break_query_btn.clicked.connect(self.on_section_break_query_btn)

        ##

        # Composition Break
        composition_break_label = QLabel('Composition Break')
        left_grid.addWidget(composition_break_label, 8, 0)

        self.composition_break_query_options = CheckableComboBox()
        left_grid.addWidget(self.composition_break_query_options, 8, 1)

        self.composition_break_query_btn = QPushButton('Query')
        left_grid.addWidget(self.composition_break_query_btn, 8, 2)
        self.composition_break_query_btn.clicked.connect(self.on_composition_break_query_btn)

        ##

        part_search_textbox = QLineEdit(self)
        part_search_textbox.setPlaceholderText("Type part name / number")
        left_grid.addWidget(part_search_textbox, 9, 0, 1, 2)

        self.part_search_btn = QPushButton('Query')
        left_grid.addWidget(self.part_search_btn, 9, 2)
        self.part_search_btn.clicked.connect(self.on_part_search_btn)

        operation_result_label = QLabel('Shapes within:')
        left_grid.addWidget(operation_result_label, 10, 0)

        self.operation_result_text = QTextEdit('')
        self.operation_result_text.setAcceptRichText(False)
        left_grid.addWidget(self.operation_result_text, 11, 0, 8, 3)

        left_frame.setLayout(left_grid)

        # Right Frame Config
        self.right_frame = FrameDrawing(self)  # the right QFrame is a FrameDrawing declared above
        self.right_frame.setFrameShape(QFrame.StyledPanel)

        right_grid = QGridLayout()
        right_grid.setSpacing(10)

        self.right_frame.setLayout(right_grid)

        # 3 - Splitter
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(left_frame)
        splitter1.addWidget(self.right_frame)

        hbox.addWidget(splitter1)
        self.setLayout(hbox)

        # size of the main window
        self.setGeometry(100, 100, 1300, 700)
        self.setWindowTitle('Netlist GUI')
        self.show()

    def part_lookup_by_location(self):
        self.selectedLocation = []
        self.selectedPart = []
        selected_item = []
        all_location = self.location_list_name_sorted
        all_part = list(self.columns)

        self.selectedAreas = [(self.minX - 200, self.minY - 200, self.maxX + 200, self.maxY + 200)]
        for i in range(
                self.part_location_options.model().rowCount()):
            item = self.part_location_options.model().item(i, 0)
            if item.checkState() == Qt.Checked:
                self.selectedLocation.append(all_location[i])

        # for i in range(
        #         self.part_query_options.model().rowCount()):
        #     item = self.part_query_options.model().item(i, 0)
        #     if item.checkState() == Qt.Checked:
        #         self.selectedPart.append(all_part[i])

        self.selectedData = query_by_areas(self.data, self.selectedAreas, self.get_useful_column_name)
        result_string = query_to_text(self.data, self.selectedData, self.selectedLocation, selected_item, self.get_useful_column_name, self.column_list)

        self.operation_result_text.setText(result_string)
        self.right_frame.repaint()

    def on_area_break_query_btn(self):
        areas = self.area_break_query_options

        self.selectedAreas = [(self.minX - 200, self.minY - 200, self.maxX + 200, self.maxY + 200)]
        selected_index = areas.check_items()
        selected_item = []
        cl_column_data, ab_column_data, sb_column_data, cb_column_data, vs_column_data, pl_column_data, pj_column_data, ts_column_data, es_column_data, et_column_data, ss_column_data = self.get_useful_column_name

        for i in selected_index:
            selected_item.append(self.area_list[i])
        if selected_item:
            self.selectedAreas = []
        for i in range(len(selected_item)):
            for k in self.data['Area Breaks']:
                sdata = []
                if k[ab_column_data['ab_look1']] == selected_item[i] or k[ab_column_data['ab_look2']] == selected_item[i]:
                    if k[ab_column_data['x']] > self.minX:
                        minx = self.minX
                        maxx = k[ab_column_data['x']]
                    else:
                        maxx = self.minX
                        minx = k[ab_column_data['x']]

                    if k[ab_column_data['y']] > self.minY:
                        miny = self.minY
                        maxy = k[ab_column_data['y']]
                    else:
                        maxy = self.minY
                        miny = k[ab_column_data['y']]
                    sdata = [(minx, miny, maxx, maxy)]
                self.selectedAreas.extend(sdata)
        result_string = query_to_text(self.data, self.selectedData, self.selectedLocation, selected_item, self.get_useful_column_name, self.column_list)
        self.operation_result_text.setText(result_string)
        self.right_frame.repaint()

    def on_section_break_query_btn(self):
        sections = self.section_break_query_options

        self.selectedAreas = [(self.minX - 200, self.minY - 200, self.maxX + 200, self.maxY + 200)]
        selected_index = sections.check_items()

        selected_item = []
        cl_column_data, ab_column_data, sb_column_data, cb_column_data, vs_column_data, pl_column_data, pj_column_data, ts_column_data, es_column_data, et_column_data, ss_column_data = self.get_useful_column_name

        for i in selected_index:
            selected_item.append(self.section_list[i])

        if selected_item:
            self.selectedAreas = []

        for i in range(len(selected_item)):
            for k in self.data['Section Breaks']:
                sdata = []
                if k[sb_column_data['sb_look1']] == selected_item[i] or k[sb_column_data['sb_look2']] == selected_item[i]:
                    if k[sb_column_data['x']] > self.minX:
                        minx = self.minX
                        maxx = k[sb_column_data['x']]
                    else:
                        maxx = self.minX
                        minx = k[sb_column_data['x']]

                    if k[sb_column_data['y']] > self.minY:
                        miny = self.minY
                        maxy = k[sb_column_data['y']]
                    else:
                        maxy = self.minY
                        miny = k[sb_column_data['y']]
                    sdata = [(minx, miny, maxx, maxy)]
                self.selectedAreas.extend(sdata)

        self.selectedData = query_by_areas(self.data, self.selectedAreas,
                                           self.get_useful_column_name)  # call query_by_areas()
        self.right_frame.repaint()

    def on_composition_break_query_btn(self):
        compositions = self.composition_break_query_options
        selected_index = compositions.check_items()
        self.selectedAreas = [(self.minX - 200, self.minY - 200, self.maxX + 200, self.maxY + 200)]
        selected_item = []
        cl_column_data, ab_column_data, sb_column_data, cb_column_data, vs_column_data, pl_column_data, pj_column_data, ts_column_data, es_column_data, et_column_data, ss_column_data = self.get_useful_column_name

        for i in selected_index:
            selected_item.append(self.composition_list[i])

        if selected_item:
            self.selectedAreas = []

        for i in range(len(selected_item)):
            for k in self.data['Composition Breaks']:
                sdata = []
                if k[cb_column_data['cb_look1']] == selected_item[i] or k[cb_column_data['cb_look2']] == selected_item[i]:
                    if k[cb_column_data['x']] > self.minX:
                        minx = self.minX
                        maxx = k[cb_column_data['x']]
                    else:
                        maxx = self.minX
                        minx = k[cb_column_data['x']]

                    if k[cb_column_data['y']] > self.minY:
                        miny = self.minY
                        maxy = k[cb_column_data['y']]
                    else:
                        maxy = self.minY
                        miny = k[cb_column_data['y']]
                    sdata = [(minx, miny, maxx, maxy)]

                self.selectedAreas.extend(sdata)

        self.selectedData = query_by_areas(self.data, self.selectedAreas,
                                           self.get_useful_column_name)  # call query_by_areas()

        self.right_frame.repaint()

    def on_select_pipeline_checkbox(self):
        self.right_frame.repaint()

    def on_select_equipment_checkbox(self):
        self.right_frame.repaint()

    def on_select_equipment_tag_checkbox(self):
        self.right_frame.repaint()

    def on_select_vessel_checkbox(self):
        self.right_frame.repaint()

    def on_select_sensor_checkbox(self):
        self.right_frame.repaint()

    def on_select_continuity_checkbox(self):
        self.right_frame.repaint()

    def on_select_area_break_checkbox(self):
        self.right_frame.repaint()

    def on_select_section_break_checkbox(self):
        self.right_frame.repaint()

    def on_select_composition_break_checkbox(self):
        self.right_frame.repaint()

    def on_part_query_btn(self):
        self.right_frame.repaint()

    def on_part_search_btn(self):
        self.rightFrame.repaint()

    def msgbox(self, title, message):
        # msg = QMessageBox(title, message, QMessageBox.Ok)
        msg = QMessageBox()
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStyleSheet("width: 1500px; overflow: auto; white-space: nowrap;")
        msg.exec()

    def message_display(self):
        title = 'Parts Statistics'
        columns = ""
        rows = ""
        column_data = ""
        row_data = ""
        for key, val in self.data.items():
            if key not in ["header", "Text Strings"]:
                column_data += '<td>' + key + '</td>'
                row_data += '<td>' + str(len(val)) + '</td>'
        columns += "<tr>" + column_data + "<tr>"
        rows += "<tr>" + row_data + "<tr>"
        message = '<table border=1>' + columns + row_data + '</table>'
        self.msgbox(title, message)

    def error_display(self, message, title, type="Information"):
        self.msg = QMessageBox()
        # Set the information icon
        if type == "Critical":
            self.msg.setIcon(QMessageBox.Critical)
        elif type == "Information":
            self.msg.setIcon(QMessageBox.Information)
        elif type == "Warning":
            self.msg.setIcon(QMessageBox.Warning)
        elif type == "Question":
            self.msg.setIcon(QMessageBox.Question)

        # Set the main message
        self.msg.setText(message)
        # Set the title of the window
        self.msg.setWindowTitle(title)
        # Display the message box
        self.msg.show()

        return False

    @property
    def get_useful_column_name(self):
        cl_location_column = None
        cl_x_column = None
        cl_y_column = None
        cl_w_column = None
        cl_h_column = None
        cl_tag_column = None

        self.cl_column_data = {
            "Location": cl_location_column,
            "x": cl_x_column,
            "y": cl_y_column,
            "w": cl_w_column,
            "h": cl_h_column,
            "tag": cl_tag_column,
        }

        if 'Continuity Labels' in self.columns:
            cl = self.columns['Continuity Labels']
            for i in cl:
                if i == "Location" or i == "location":
                    self.cl_column_data["Location"] = cl.index(i)
                elif i == 'x' or i == 'X':
                    self.cl_column_data["x"] = cl.index(i)
                elif i == 'y' or i == 'Y':
                    self.cl_column_data["y"] = cl.index(i)
                elif i == 'w' or i == 'W':
                    self.cl_column_data["w"] = cl.index(i)
                elif i == 'h' or i == 'H':
                    self.cl_column_data["h"] = cl.index(i)
                elif i == 'tag' or i == 'Tag':
                    self.cl_column_data["tag"] = cl.index(i)

        ab_location_column = None
        ab_x_column = None
        ab_y_column = None
        ab_look1 = None
        ab_look2 = None

        self.ab_column_data = {
            "Location": ab_location_column,
            "x": ab_x_column,
            "y": ab_y_column,
            "ab_look1": ab_look1,
            "ab_look2": ab_look2,
        }

        if 'Area Breaks' in self.columns:
            cl = self.columns['Area Breaks']
            for i in cl:
                if i == "Location" or i == "location":
                    self.ab_column_data["Location"] = cl.index(i)
                elif i == 'x' or i == 'X':
                    self.ab_column_data["x"] = cl.index(i)
                elif i == 'y' or i == 'Y':
                    self.ab_column_data["y"] = cl.index(i)
                elif i == 'Area (left/up)':
                    self.ab_column_data["ab_look1"] = cl.index(i)
                elif i == 'Area (right/down)':
                    self.ab_column_data["ab_look2"] = cl.index(i)

        sb_location_column = None
        sb_x_column = None
        sb_y_column = None
        sb_look1 = None
        sb_look2 = None
        sb_id = None

        self.sb_column_data = {
            "Location": sb_location_column,
            "x": sb_x_column,
            "y": sb_y_column,
            "sb_look1": sb_look1,
            "sb_look2": sb_look2,
            "id": sb_id,
        }

        if 'Section Breaks' in self.columns:
            cl = self.columns['Section Breaks']
            for i in cl:
                if i == "Location" or i == "location":
                    self.sb_column_data["Location"] = cl.index(i)
                elif i == 'x' or i == 'X':
                    self.sb_column_data["x"] = cl.index(i)
                elif i == 'y' or i == 'Y':
                    self.sb_column_data["y"] = cl.index(i)
                elif i == 'Section (left/up)':
                    self.sb_column_data["sb_look1"] = cl.index(i)
                elif i == 'Section (right/down)':
                    self.sb_column_data["sb_look2"] = cl.index(i)
                elif i == 'Equipment ID':
                    self.sb_column_data["id"] = cl.index(i)

        cb_location_column = None
        cb_x_column = None
        cb_y_column = None
        cb_look1 = None
        cb_look2 = None

        self.cb_column_data = {
            "Location": cb_location_column,
            "x": cb_x_column,
            "y": cb_y_column,
            "cb_look1": cb_look1,
            "cb_look2": cb_look2,
        }

        if 'Composition Breaks' in self.columns:
            cl = self.columns['Composition Breaks']
            for i in cl:
                if i == "Location" or i == "location":
                    self.cb_column_data["Location"] = cl.index(i)
                elif i == 'x' or i == 'X':
                    self.cb_column_data["x"] = cl.index(i)
                elif i == 'y' or i == 'Y':
                    self.cb_column_data["y"] = cl.index(i)
                elif i == 'Phase (vessel left/up or incoming pipeline)' or i == 'Phase (left/up or incoming pipeline)':
                    self.cb_column_data["cb_look1"] = cl.index(i)
                elif i == 'Phase (vessel right/down vessel or remaining pipeline)' or i == 'Phase (right/down or remaining pipeline)':
                    self.cb_column_data["cb_look2"] = cl.index(i)

        ts_location_column = None
        ts_x_column = None
        ts_y_column = None
        ts_w_column = None
        ts_h_column = None

        self.ts_column_data = {
            "Location": ts_location_column,
            "x": ts_x_column,
            "y": ts_y_column,
            "w": ts_w_column,
            "h": ts_h_column,
        }

        if 'Text Strings' in self.columns:
            cl = self.columns['Text Strings']
            for i in cl:
                if i == "Location" or i == "location":
                    self.ts_column_data["Location"] = cl.index(i)
                elif i == 'x' or i == 'X':
                    self.ts_column_data["x"] = cl.index(i)
                elif i == 'y' or i == 'Y':
                    self.ts_column_data["y"] = cl.index(i)
                elif i == 'w' or i == 'W':
                    self.ts_column_data["w"] = cl.index(i)
                elif i == 'h' or i == 'H':
                    self.ts_column_data["h"] = cl.index(i)

        pl_location_column = None
        pl_x1_column = None
        pl_y1_column = None
        pl_x2_column = None
        pl_y2_column = None
        pl_number_column = None
        pl_direction_column = None

        self.pl_column_data = {
            "Location": pl_location_column,
            "x1": pl_x1_column,
            "y1": pl_y1_column,
            "x2": pl_x2_column,
            "y2": pl_y2_column,
            "number": pl_number_column,
            "direction": pl_direction_column,
        }

        if 'Pipelines' in self.columns:
            cl = self.columns['Pipelines']
            for i in cl:
                if i == "Location" or i == "location":
                    self.pl_column_data["Location"] = cl.index(i)
                elif i == 'x1' or i == 'X1':
                    self.pl_column_data["x1"] = cl.index(i)
                elif i == 'x2' or i == 'X2':
                    self.pl_column_data["x2"] = cl.index(i)
                elif i == 'y1' or i == 'Y1':
                    self.pl_column_data["y1"] = cl.index(i)
                elif i == 'y2' or i == 'Y2':
                    self.pl_column_data["y2"] = cl.index(i)
                elif i == 'number' or i == 'Number':
                    self.pl_column_data["number"] = cl.index(i)
                elif i == 'Orientation' or i == 'orientation':
                    self.pl_column_data["direction"] = cl.index(i)

        pj_location_column = None
        pj_x_column = None
        pj_y_column = None
        pj_r_column = None

        self.pj_column_data = {
            "Location": pj_location_column,
            "x": pj_x_column,
            "y": pj_y_column,
            "r": pj_r_column,
        }

        if 'Pipeline Junctions' in self.columns:
            cl = self.columns['Pipeline Junctions']
            for i in cl:
                if i == "Location" or i == "location":
                    self.pj_column_data["Location"] = cl.index(i)
                elif i == 'x' or i == 'X':
                    self.pj_column_data["x"] = cl.index(i)
                elif i == 'y' or i == 'Y':
                    self.pj_column_data["y"] = cl.index(i)
                elif i == 'r' or i == 'R':
                    self.pj_column_data["r"] = cl.index(i)

        ss_location_column = None
        ss_x_column = None
        ss_y_column = None
        ss_r_column = None
        ss_number_column = None

        self.ss_column_data = {
            "Location": ss_location_column,
            "x": ss_x_column,
            "y": ss_y_column,
            "r": ss_r_column,
            "number": ss_number_column,
        }

        if 'Sensors' in self.columns:
            cl = self.columns['Sensors']
            for i in cl:
                if i == "Location" or i == "location":
                    self.ss_column_data["Location"] = cl.index(i)
                elif i == 'x' or i == 'X':
                    self.ss_column_data["x"] = cl.index(i)
                elif i == 'y' or i == 'Y':
                    self.ss_column_data["y"] = cl.index(i)
                elif i == 'r' or i == 'R':
                    self.ss_column_data["r"] = cl.index(i)
                elif i == 'number' or i == 'Number':
                    self.ss_column_data["number"] = cl.index(i)

        es_location_column = None
        es_x_column = None
        es_y_column = None
        es_w_column = None
        es_h_column = None
        es_number_column = None

        self.es_column_data = {
            "Location": es_location_column,
            "x": es_x_column,
            "y": es_y_column,
            "w": es_w_column,
            "h": es_h_column,
            "number": es_number_column,
        }

        if 'Equipment symbols' in self.columns:
            cl = self.columns['Equipment symbols']
            for i in cl:
                if i == "Location" or i == "location":
                    self.es_column_data["Location"] = cl.index(i)
                elif i == 'x' or i == 'X':
                    self.es_column_data["x"] = cl.index(i)
                elif i == 'y' or i == 'Y':
                    self.es_column_data["y"] = cl.index(i)
                elif i == 'w' or i == 'W':
                    self.es_column_data["w"] = cl.index(i)
                elif i == 'h' or i == 'H':
                    self.es_column_data["h"] = cl.index(i)
                elif i == 'number' or i == 'Number':
                    self.es_column_data["number"] = cl.index(i)

        et_location_column = None
        et_x_column = None
        et_y_column = None
        et_r_column = None
        et_number_column = None

        self.et_column_data = {
            "Location": et_location_column,
            "x": et_x_column,
            "y": et_y_column,
            "r": et_r_column,
            "number": et_number_column,
        }

        if 'Equipment Tags' in self.columns:
            cl = self.columns['Equipment Tags']
            for i in cl:
                if i == "Location" or i == "location":
                    self.et_column_data["Location"] = cl.index(i)
                elif i == 'x' or i == 'X':
                    self.et_column_data["x"] = cl.index(i)
                elif i == 'y' or i == 'Y':
                    self.et_column_data["y"] = cl.index(i)
                elif i == 'r' or i == 'R':
                    self.et_column_data["r"] = cl.index(i)
                elif i == 'Number' or i == 'number':
                    self.et_column_data["number"] = cl.index(i)

        vs_location_column = None
        vs_x_column = None
        vs_y_column = None
        vs_w_column = None
        vs_h_column = None
        vs_number_column = None

        self.vs_column_data = {
            "Location": vs_location_column,
            "x": vs_x_column,
            "y": vs_y_column,
            "w": vs_w_column,
            "h": vs_h_column,
            "number": vs_number_column,
        }

        if 'Vessels' in self.columns:
            cl = self.columns['Vessels']
            for i in cl:
                if i == "Location" or i == "location":
                    self.vs_column_data["Location"] = cl.index(i)
                elif i == 'x' or i == 'X':
                    self.vs_column_data["x"] = cl.index(i)
                elif i == 'y' or i == 'Y':
                    self.vs_column_data["y"] = cl.index(i)
                elif i == 'w' or i == 'W':
                    self.vs_column_data["w"] = cl.index(i)
                elif i == 'h' or i == 'H':
                    self.vs_column_data["h"] = cl.index(i)
                elif i == 'number' or i == 'Number':
                    self.vs_column_data["number"] = cl.index(i)

        return (
            self.cl_column_data,
            self.ab_column_data,
            self.sb_column_data,
            self.cb_column_data,
            self.vs_column_data,
            self.pl_column_data,
            self.pj_column_data,
            self.ts_column_data,
            self.es_column_data,
            self.et_column_data,
            self.ss_column_data
        )

    def on_load_file_btn(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open file')  # show a Dialogbox to choose Netlist file

        if file_name[0]:
            file_extention = file_name[0].split(".")[-1]
            if file_extention != 'csv':
                self.error_display(message="Only CSV files allowed!", title="File Error", type="Critical")
            else:
                self.minX = 0
                self.minY = 0
                self.maxX = 0
                self.maxY = 0

                self.selectedLocation = []
                self.selectedPart = []
                self.area_list = []
                self.section_list = []
                self.composition_list = []

                self.area_section_data = []
                self.section_break_data = []
                self.composition_break_data = []

                if self.composition_break_query_options.count() > 0:
                    self.composition_break_query_options.clear()
                if self.section_break_query_options.count() > 0:
                    self.section_break_query_options.clear()
                if self.area_break_query_options.count() > 0:
                    self.area_break_query_options.clear()

                pos = file_name[0].rfind('/')
                self.load_file_label.setText(file_name[0][pos + 1:])
                # read_csv(file_name[0])
                self.data, self.columns = read_csv(file_name[0])
                useful_column_index = self.get_useful_column_name
                self.minX, self.minY, self.maxX, self.maxY, self.location_list_name = find_ranges(self.data,
                                                                                                  useful_column_index)
                cl_column_data, ab_column_data, sb_column_data, cb_column_data, vs_column_data, pl_column_data, pj_column_data, ts_column_data, es_column_data, et_column_data, ss_column_data = self.get_useful_column_name

                location_list_set = set(self.location_list_name)
                location_list = list(location_list_set)
                location_list.sort()
                self.location_list_name_sorted = location_list

                if self.part_location_options.count() > 0:
                    self.part_location_options.clear()
                self.part_location_options.addItems(location_list)

                # if self.part_query_options.count() > 0:
                #     self.part_query_options.clear()
                # self.part_query_options.addItems(list(self.columns))

                for i in range(len(location_list)):
                    item = self.part_location_options.model().item(i, 0)
                    item.setCheckState(Qt.Unchecked)

                # for i in range(len(self.part_query_options)):
                #     item = self.part_query_options.model().item(i, 0)
                #     item.setCheckState(Qt.Unchecked)
                self.column_list = list(self.columns.keys())

                # Area Break
                if "Area Breaks" in self.data:
                    for i in range(0, len(self.data["Area Breaks"])):
                        for k in range(0, len(self.data["Area Breaks"][i])):
                            if k == ab_column_data["ab_look1"] or k == ab_column_data["ab_look2"]:
                                self.area_list.append(self.data["Area Breaks"][i][k])
                    self.area_list.sort()

                    self.area_list = set(self.area_list)
                    self.area_list = list(self.area_list)
                    self.area_list.sort()

                    self.area_break_query_options.addItems(self.area_list)
                    for i in range(len(self.area_list)):
                        item = self.area_break_query_options.model().item(i, 0)
                        item.setCheckState(Qt.Unchecked)

                if "Section Breaks" in self.data:
                    for i in range(0, len(self.data["Section Breaks"])):
                        for k in range(0, len(self.data["Section Breaks"][i])):
                            if k == sb_column_data["sb_look1"] or k == sb_column_data["sb_look2"]:
                                self.section_list.append(self.data["Section Breaks"][i][k])
                    self.section_list = set(self.section_list)
                    self.section_list = list(self.section_list)
                    self.section_list.sort()

                    self.section_break_query_options.addItems(self.section_list)
                    for i in range(len(self.section_list)):
                        item = self.section_break_query_options.model().item(i, 0)
                        item.setCheckState(Qt.Unchecked)

                if "Composition Breaks" in self.data:
                    for i in range(0, len(self.data["Composition Breaks"])):
                        for k in range(0, len(self.data["Composition Breaks"][i])):
                            if k == cb_column_data["cb_look1"] or k == cb_column_data["cb_look2"]:
                                self.composition_list.append(self.data["Composition Breaks"][i][k])
                    self.composition_list = set(self.composition_list)
                    self.composition_list = list(self.composition_list)
                    self.composition_list.sort()

                    self.composition_break_query_options.addItems(self.composition_list)
                    for i in range(len(self.composition_list)):
                        item = self.composition_break_query_options.model().item(i, 0)
                        item.setCheckState(Qt.Unchecked)

                self.selectedData = self.data

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName('NetlistGUI')
    main = NetListGUI()
    main.setWindowTitle("NetlistGUI")
    main.show()

sys.exit(app.exec_())
