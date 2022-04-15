import csv
import pandas as pd
import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QGridLayout, QLabel, QSplitter, QHBoxLayout, QComboBox, \
    QPushButton, \
    QFileDialog, QTextEdit, QCheckBox

from src.sections import FrameDrawing, CheckableComboBox
from src.utils import query_by_areas, query_to_text, read_csv, find_ranges


class NetlistGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.data = {}  # store data dictionary (see netlist_reader.py)
        self.equipment_syb_list_name = None # store data dictionary (see netlist_reader.py)
        self.column = {}  # store column name dictionary (see netlist_reader.py)
        self.minX = 0  # store minX, minY, maxX, maxY of all coordinates available in CSV file
        self.minY = 0
        self.maxX = 0
        self.maxY = 0
        self.selectedData = {}  # store components (e.g. queried pipelines, equipments)
        self.selectedAreas = []

        #
        self.initUI()

    #### define GUI components
    def initUI(self):
        hbox = QHBoxLayout(self)

        # 1 - LEFT QFrame
        leftFrame = QFrame(self)
        leftFrame.setFrameShape(QFrame.StyledPanel)
        leftFrame.setMaximumWidth(400)

        gridLeft = QGridLayout()  # the left QFrame uses grid layout to place GUI components
        gridLeft.setSpacing(12)

        self.btnFile = QPushButton('Browse')
        gridLeft.addWidget(self.btnFile, 1, 0)
        self.btnFile.clicked.connect(self.showFileDialog)

        self.lblFile = QLabel('File name')
        gridLeft.addWidget(self.lblFile, 1, 1)

        self.ckPipeline = QCheckBox("Pipelines", self)
        self.ckPipeline.setChecked(True)
        gridLeft.addWidget(self.ckPipeline, 2, 0)
        self.ckPipeline.stateChanged.connect(self.onCkPipeline)

        self.ckEquipment = QCheckBox("Equipments", self)
        self.ckEquipment.setChecked(True)
        gridLeft.addWidget(self.ckEquipment, 2, 1)
        self.ckEquipment.stateChanged.connect(self.onCkEquipment)

        self.ckContinuity = QCheckBox("Cont. Labels", self)
        self.ckContinuity.setChecked(True)
        gridLeft.addWidget(self.ckContinuity, 3, 0)
        self.ckContinuity.stateChanged.connect(self.onCkContinuity)

        self.ckAreabreaks = QCheckBox("Area Breaks", self)
        self.ckAreabreaks.setChecked(True)
        gridLeft.addWidget(self.ckAreabreaks, 3, 1)
        self.ckAreabreaks.stateChanged.connect(self.onCkAreabreaks)

        self.ckSectionbreaks = QCheckBox("Sect. Breaks", self)
        self.ckSectionbreaks.setChecked(True)
        gridLeft.addWidget(self.ckSectionbreaks, 4, 0)
        self.ckSectionbreaks.stateChanged.connect(self.onCkSectionbreaks)

        self.ckCompositionbreaks = QCheckBox("Comp. Breaks", self)
        self.ckCompositionbreaks.setChecked(True)
        gridLeft.addWidget(self.ckCompositionbreaks, 4, 1)
        self.ckCompositionbreaks.stateChanged.connect(self.onCkCompositionbreaks)

        #        self.ckSensor= QCheckBox("Sensors", self)
        #        gridLeft.addWidget(self.ckSensor, 3, 1)
        #        self.ckSensor.stateChanged.connect(self.onCkSensor)

        lblArea = QLabel('Area Breaks')
        gridLeft.addWidget(lblArea, 5, 0)

        self.cboArea = CheckableComboBox()
        gridLeft.addWidget(self.cboArea, 6, 0)
        areaItemList = ['CELLAR', 'PROC', 'GTM']
        for i in range(len(areaItemList)):
            self.cboArea.addItem(areaItemList[i])
            item = self.cboArea.model().item(i, 0)
            item.setCheckState(Qt.Unchecked)

        self.btnQueryArea = QPushButton('Query')
        gridLeft.addWidget(self.btnQueryArea, 6, 1)
        self.btnQueryArea.clicked.connect(self.runQueryArea)

        searchArea = QLabel('Search by Tag')
        gridLeft.addWidget(searchArea, 7, 0)

        searchArea = QLabel('Search by Location')
        gridLeft.addWidget(searchArea, 7, 1)

        self.searchSection = QComboBox()
        gridLeft.addWidget(self.searchSection, 8, 0)
        # searchItemList = ["To", "Be", "Populated", "When", "File", "Loads"]
        # for item in searchItemList:
        #     self.searchSection.addItem(item)

        self.searchSection = QComboBox()
        gridLeft.addWidget(self.searchSection, 8, 1)
        # searchItemList = ["To", "Be", "Populated", "When", "File", "Loads"]
        # for item in searchItemList:
        #     self.searchSection.addItem(item)

        lblSection = QLabel('Section Breaks')
        gridLeft.addWidget(lblSection, 9, 0)

        self.cboSection = CheckableComboBox()
        gridLeft.addWidget(self.cboSection, 10, 0)
        sectionItemList = ['RJAS', 'JASIN', 'FLARE', 'METHANOL']
        for i in range(len(sectionItemList)):
            self.cboSection.addItem(sectionItemList[i])
            item = self.cboSection.model().item(i, 0)
            item.setCheckState(Qt.Unchecked)

        self.btnQuerySection = QPushButton('Query')
        gridLeft.addWidget(self.btnQuerySection, 10, 1)
        self.btnQuerySection.clicked.connect(self.runQuerySection)

        lblComp = QLabel('Composition Breaks')
        gridLeft.addWidget(lblComp, 11, 0)
        self.cboComp = CheckableComboBox()
        gridLeft.addWidget(self.cboComp, 12, 0)
        compositionItemList = ['METHANOL', 'WELL FLUIDS']
        for i in range(len(compositionItemList)):
            self.cboComp.addItem(compositionItemList[i])
            item = self.cboComp.model().item(i, 0)
            item.setCheckState(Qt.Unchecked)

        self.btnQueryComp = QPushButton('Query')
        gridLeft.addWidget(self.btnQueryComp, 12, 1)
        self.btnQueryComp.clicked.connect(self.runQueryComp)

        #        self.cboCompDir = CheckableComboBox()
        #        gridLeft.addWidget(self.cboCompDir, 11, 0)
        #        compDirItemList = ['left-up', 'right-up', 'right-down', 'left-down']
        #        for i in range(len(compDirItemList)):
        #            self.cboCompDir.addItem(compDirItemList[i])
        #            item = self.cboCompDir.model().item(i, 0)
        #            item.setCheckState(Qt.Unchecked)

        lblResult = QLabel('Shapes within:')
        gridLeft.addWidget(lblResult, 13, 0)
        self.txtResult = QTextEdit('')
        self.txtResult.setAcceptRichText(False)
        gridLeft.addWidget(self.txtResult, 14, 0, 8, 2)

        #        gridLeft.addWidget(QFrame(), 6, 0, 10, 2)    # placeholder

        #
        leftFrame.setLayout(gridLeft)

        # 2 - RIGHT QFrame
        self.rightFrame = FrameDrawing(self)  # the right QFrame is a FrameDrawing declared above
        self.rightFrame.setFrameShape(QFrame.StyledPanel)

        gridRight = QGridLayout()
        gridRight.setSpacing(10)

        #
        self.rightFrame.setLayout(gridRight)

        # 3 - Splitter
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(leftFrame)
        splitter1.addWidget(self.rightFrame)

        hbox.addWidget(splitter1)
        self.setLayout(hbox)

        # size of the main window
        self.setGeometry(100, 100, 1300, 700)
        self.setWindowTitle('Netlist GUI')
        self.show()

    #### button QueryArea
    def runQueryArea(self):
        CELLAR_areas = [(self.minX, 3600, 2558, self.maxY)]  # define rectangle(s) for CELLAR, PROC, GTM queries
        PROC_areas = [(self.minX, 2200, 2558, 2600), (2558, self.minY, 3593, self.maxY), (3593, 1531, self.maxX, 2500)]
        GTM_areas = [(3593, self.minY, self.maxX, 1500)]
        all_areas = [CELLAR_areas, PROC_areas, GTM_areas]

        self.selectedAreas = []
        for i in range(self.cboArea.model().rowCount()):  # check to see which Area Breaks are selected
            item = self.cboArea.model().item(i, 0)
            if item.checkState() == Qt.Checked:
                self.selectedAreas.extend(all_areas[i])
        print('selectedAreas =', self.selectedAreas)

        self.selectedData = query_by_areas(self.data, self.selectedAreas)  # call query_by_areas()
        #
        resultStr = query_to_text(self.data, self.selectedData)
        print("resultStr =" + resultStr)
        self.txtResult.setText(resultStr)

        # repaint
        print("selectedData =")
        print(self.selectedData)
        self.rightFrame.repaint()

    #### button QuerySection
    def runQuerySection(self):
        RJAS_areas = [(self.minX, 3600, 1262, 4000)]  # define rectangle(s) for RJAS, JASIN, FLARE, METHANOL queries
        JASIN_areas = [(1262, 2729, 4000, self.maxY), (2519, 2333, 4000, 2729), (2519, self.minY + 300, 2900, 2333),
                       (2519, self.minY, self.maxX, self.minY + 300)]
        FLARE_areas = [(3700, 1500, self.maxX, 2333)]
        METHANOL_areas = [(self.minX, 2200, 2519, 2600)]
        all_areas = [RJAS_areas, JASIN_areas, FLARE_areas, METHANOL_areas]

        self.selectedAreas = []
        for i in range(self.cboSection.model().rowCount()):  # check to see which Section Breaks are selected
            item = self.cboSection.model().item(i, 0)
            if item.checkState() == Qt.Checked:
                self.selectedAreas.extend(all_areas[i])
        print('selectedAreas =', self.selectedAreas)

        self.selectedData = query_by_areas(self.data, self.selectedAreas)  # call query_by_areas()

        #
        resultStr = query_to_text(self.data, self.selectedData)
        print("resultStr =" + resultStr)
        self.txtResult.setText(resultStr)

        # repaint
        print("selectedData =")
        print(self.selectedData)
        self.rightFrame.repaint()

    #### button QueryComp
    def runQueryComp(self):
        METHANOL_areas = [(self.minX, 2450, 2744, 2600)]
        WELLFLUID_areas = [(2743, self.minY, self.maxX, self.maxY), (self.minX, 3600, 2744, self.maxY)]
        all_areas = [METHANOL_areas, WELLFLUID_areas]

        self.selectedAreas = []
        for i in range(self.cboComp.model().rowCount()):  # check to see which Composition Breaks are selected
            item = self.cboComp.model().item(i, 0)
            if item.checkState() == Qt.Checked:
                self.selectedAreas.extend(all_areas[i])
        print('selectedAreas =', self.selectedAreas)

        self.selectedData = query_by_areas(self.data, self.selectedAreas)  # call query_by_areas()

        #
        resultStr = query_to_text(self.data, self.selectedData)
        print("resultStr =" + resultStr)
        self.txtResult.setText(resultStr)

        # repaint
        print("selectedData =")
        print(self.selectedData)
        self.rightFrame.repaint()

    #### repaint the rightFrame with new state of checkbox
    def onCkPipeline(self):
        self.rightFrame.repaint()

    def onCkEquipment(self):
        self.rightFrame.repaint()

    def onCkContinuity(self):
        self.rightFrame.repaint()

    #    def onCkSensor(self):
    #        self.rightFrame.repaint()

    def onCkAreabreaks(self):
        self.rightFrame.repaint()

    def onCkSectionbreaks(self):
        self.rightFrame.repaint()

    def onCkCompositionbreaks(self):
        self.rightFrame.repaint()

    #### button Browse
    def showFileDialog(self):
        fName = QFileDialog.getOpenFileName(self, 'Open file')  # show a Dialogbox to choose Netlist file
        if fName[0]:
            pos = fName[0].rfind('/')
            self.lblFile.setText(fName[0][pos + 1:])

            self.data, self.columns = read_csv(fName[0])

            self.minX, self.minY, self.maxX, self.maxY, self.equipment_syb_list_name = find_ranges(self.data)
            for item in set(self.equipment_syb_list_name):
                self.searchSection.addItem(item)
            
            self.selectedData = self.data


# if __name__ == '__main__':
#     app = QApplication(sys.argv)  # invoke the main application and show the main window "NetlistGUI"
#     ex = NetlistGUI()
#     sys.exit(app.exec_())

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName('NetlistGUI')
    main = NetlistGUI()
    main.setWindowTitle("NetlistGUI")
    main.show()

sys.exit(app.exec_())
