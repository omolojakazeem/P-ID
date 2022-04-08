import csv
import pandas as pd
import sys
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QGridLayout, QLabel, QSplitter, QHBoxLayout, QComboBox, \
    QPushButton, \
    QFileDialog, QTextEdit, QCheckBox


def get_number_of_parts(line):
    parts = None
    for item in csv.reader([line], delimiter=',', quotechar='"'):
        parts = item
    return len(parts)


def read_csv(file_name):  # file_name: name of the CSV file
    data = {}  # data is a dictionary : e.g. data['Pipelines'] = frame of pipelines
    columns = {}  # columns is a dictionary of column names for each frame
    with open(file_name, 'rt') as f:  # open "file_name" as a variable f
        lines = f.read().split('\n')  # read all data from f and split them to text lines

        i = 0
        # header info (2 lines)
        data['header'] = lines[:2]
        i += 2  # skip the first two lines

        # read all frames
        numeric_name_set = set(['Number', 'x', 'y', 'r', 'w', 'h', 'x1', 'y1', 'x2',
                                'y2'])  # the name of columns to be converted to numeric
        while True:
            # frame header
            section_name = lines[i]  # consider line[i]
            section_columns = lines[i + 1].split(',')  # split it to fields by comma: e.g "A,B,C" to "A", "B" and "C"
            n_comma = lines[i + 1].count(',')  # count the number of commas in the next line
            while n_comma == 0:  # skip non-record lines
                i += 1
                section_name = lines[i]  # save the frame name, e.g. "Pipelines"
                section_columns = lines[i + 1].split(',')  # save the frame's column names
                n_comma = lines[i + 1].count(',')
            #
            columns[section_name] = section_columns  # put section_columns into columns variable

            # data frame
            next_i = i + 2
            eof = False
            #             while lines[next_i].count(',') == n_comma:
            while get_number_of_parts(
                    lines[next_i]) == n_comma + 1:  # probe the last record of the frame, save the location in next_i
                next_i += 1
                if next_i == len(lines) or len(lines[next_i]) == 0:
                    eof = True
                    break
            #            print('n_comma =', n_comma, ', i = ', i+2, 'next_i = ', next_i)

            #
            frame = []
            for j in range(i + 2, next_i):  # read records from line i to line next_i
                #                 parts = lines[j].split(',')
                parts = None
                for item in csv.reader([lines[j]], delimiter=',',
                                       quotechar='"'):  # use csv library to read line[j], save to parts
                    parts = item

                rec = []  # the current record
                for k in range(len(parts)):
                    if section_columns[k] in numeric_name_set:  # convert the column k to a numeric value if possible
                        rec.append(int(parts[k]))
                    else:
                        rec.append(parts[k])
                frame.append(rec)  # add the current record to frame

            #
            data[section_name] = frame  # put frame to data, e.g. data["Pipelines"] = frame
            #
            if eof:
                break
            i = next_i  # ready for the next frame, e.g. "Area Breaks"

    # print ret
    #    print("DATA")
    #    for key, value in ret.items():
    #        print(key)
    #        for rec in ret[key]:
    #            print(rec)

    return data, columns


#### convert frame to Pandas DataFrame
def list2frame(data, columns):
    df = pd.concat([pd.DataFrame([row], columns=columns) for row in data], ignore_index=True)
    return df


#### find minX, minY, maxX, maxY of all coordinates available in CSV file
def find_ranges(data):  # data: the dictionary of all frames read in read_csv() function
    data_x = []
    data_y = []
    if 'Continuity Labels' in data.keys():
        for rec in data[
            'Continuity Labels']:  # each Continuity Labels has x1=rec[2], x2=rec[2] + rec[4], y1=rec[3], y2=rec[3] + rec[5]
            data_x.extend([rec[2], rec[2] + rec[4]])
            data_y.extend([rec[3], rec[3] + rec[5]])
    if 'Sensors' in data.keys():
        for rec in data['Sensors']:  # each Sensors is (x,y,r)
            data_x.extend([rec[3] - rec[5], rec[3] + rec[5]])
            data_y.extend([rec[4] - rec[5], rec[4] + rec[5]])
    if 'Pipelines' in data.keys():
        for rec in data['Pipelines']:
            data_x.extend([rec[2], rec[4]])
            data_y.extend([rec[3], rec[5]])
    if 'Equipment symbols' in data.keys():
        for rec in data['Equipment symbols']:
            data_x.extend([rec[2], rec[2] + rec[4]])
            data_y.extend([rec[3], rec[3] + rec[5]])
    if 'Area Breaks' in data.keys():
        for rec in data['Area Breaks']:
            data_x.append(rec[3])
            data_y.append(rec[4])
    if 'Composition Breaks' in data.keys():
        for rec in data['Composition Breaks']:
            data_x.append(rec[5])
            data_y.append(rec[6])
    if 'Section Breaks' in data.keys():
        for rec in data['Section Breaks']:
            data_x.append(rec[5])
            data_y.append(rec[6])
    if 'Text Strings' in data.keys():
        for rec in data['Text Strings']:
            data_x.extend([rec[4], rec[4] + rec[6]])
            data_y.extend([rec[5], rec[5] + rec[7]])
    if 'Pipeline Junctions' in data.keys():
        for rec in data['Pipeline Junctions']:
            data_x.append(rec[4])
            data_y.append(rec[5])
    if 'Vessels' in data.keys():
        for rec in data['Vessels']:
            data_x.extend([rec[1], rec[1] + rec[3]])
            data_y.extend([rec[2], rec[2] + rec[4]])

    return min(data_x), min(data_y), max(data_x), max(data_y)  # means minX, minY, maxX, maxY


#### check if (x,y) is inside any rectangle of 'areas' or not
def check_in_area(areas, x, y):
    for area in areas:  # each area is a rectangle defined by (x1,y1,x2,y2)
        x1 = area[0]
        y1 = area[1]
        x2 = area[2]
        y2 = area[3]
        if x1 <= x and x <= x2 and y1 <= y and y <= y2:
            return True
    return False


#### scan the data dictionary and add components that cross any rectangle in "areas"
def query_by_areas(data, areas):
    ret = {}

    # continuity labels
    if 'Continuity Labels' in data.keys():
        frameL = []
        for rec in data['Continuity Labels']:
            x1 = rec[2]
            y1 = rec[3]
            x2 = rec[2] + rec[4]
            y2 = rec[3] + rec[5]
            if check_in_area(areas, x1, y1) or check_in_area(areas, x2, y2):  # AND/OR
                frameL.append(rec)
        ret['Continuity Labels'] = frameL

    # pipelines
    if 'Pipelines' in data.keys():
        frameP = []
        for rec in data['Pipelines']:
            x1 = rec[2]
            y1 = rec[3]
            x2 = rec[4]
            y2 = rec[5]
            if check_in_area(areas, x1, y1) and check_in_area(areas, x2, y2):  # AND/OR
                frameP.append(rec)
        ret['Pipelines'] = frameP

    # equipments
    if 'Equipment symbols' in data.keys():
        frameE = []
        for rec in data['Equipment symbols']:
            x1 = rec[2]
            x2 = rec[2] + rec[4]
            y1 = rec[3]
            y2 = rec[3] + rec[5]
            if check_in_area(areas, x1, y1) or check_in_area(areas, x2, y2):  # AND/OR
                frameE.append(rec)
        ret['Equipment symbols'] = frameE

    # junctions
    if 'Pipeline Junctions' in data.keys():
        frameJ = []
        for rec in data['Pipeline Junctions']:
            x1 = rec[4]
            y1 = rec[5]
            if check_in_area(areas, x1, y1):
                frameJ.append(rec)
        ret['Pipeline Junctions'] = frameJ

    # vessels
    if 'Vessels' in data.keys():
        frameV = []
        for rec in data['Vessels']:
            x1 = rec[1]
            y1 = rec[2]
            x2 = rec[1] + rec[3]
            y2 = rec[2] + rec[4]
            if check_in_area(areas, x1, y1) or check_in_area(areas, x2, y2):  # AND/OR
                frameV.append(rec)
        ret['Vessels'] = frameV

    # breaks
    if 'Area Breaks' in data.keys():
        frameA = []
        for rec in data['Area Breaks']:
            x1 = rec[3]
            y1 = rec[4]
            if check_in_area(areas, x1, y1):
                frameA.append(rec)
            ret['Area Breaks'] = frameA

    if 'Section Breaks' in data.keys():
        frameS = []
        for rec in data['Section Breaks']:
            x1 = rec[5]
            y1 = rec[6]
            if check_in_area(areas, x1, y1):
                frameS.append(rec)
            ret['Section Breaks'] = frameS

    if 'Composition Breaks' in data.keys():
        frameC = []
        for rec in data['Composition Breaks']:
            x1 = rec[5]
            y1 = rec[6]
            if check_in_area(areas, x1, y1):
                frameC.append(rec)
            ret['Composition Breaks'] = frameC

    #
    return ret


#### convert a dictionary (selectedData) to text string
def query_to_text(data, selectedData):
    if 'Continuity Labels' in data.keys():
        ret = 'Continuity labels ---------------\n'
        for rec in selectedData['Continuity Labels']:
            ret += str(rec) + '\n'
    if 'Pipelines' in data.keys():
        ret += 'Pipelines ---------------\n'
        for rec in selectedData['Pipelines']:
            ret += str(rec) + '\n'
    if 'Equipment symbols' in data.keys():
        ret += 'Equipment symbols ---------------\n'
        for rec in selectedData['Equipment symbols']:
            ret += str(rec) + '\n'
    if 'Vessels' in data.keys():
        ret += 'Vessels ---------------\n'
        for rec in selectedData['Vessels']:
            ret += str(rec) + '\n'

    #
    return ret


#################### GUI ####################
#### draw a line from (px1,py1) to (px2, py2) resizing to viewport (minX, minY, maxX, maxY) with width=sizeX, height=sizeY
def drawLine(qp, px1, py1, px2, py2, minX, minY, maxX, maxY, sizeX, sizeY):  # qp is a QPen for drawing
    x1 = sizeX * (px1 - minX) / (maxX - minX)
    y1 = sizeY * (py1 - minY) / (maxY - minY)  # Y-axis top-to-bottom

    x2 = sizeX * (px2 - minX) / (maxX - minX)
    y2 = sizeY * (py2 - minY) / (maxY - minY)  # Y-axis top-to-bottom

    qp.drawLine(x1, y1, x2, y2)


def drawRectange(qp, px1, py1, px2, py2, minX, minY, maxX, maxY, sizeX, sizeY):  # qp is a QPen for drawing
    drawLine(qp, px1, py1, px2, py1, minX, minY, maxX, maxY, sizeX, sizeY)
    drawLine(qp, px1, py1, px1, py2, minX, minY, maxX, maxY, sizeX, sizeY)
    drawLine(qp, px1, py2, px2, py2, minX, minY, maxX, maxY, sizeX, sizeY)
    drawLine(qp, px2, py1, px2, py2, minX, minY, maxX, maxY, sizeX, sizeY)


#### draw a circle center at (px,py) resizing to viewport (minX, minY, maxX, maxY) with width=sizeX, height=sizeY
def drawCircle(qp, px, py, pr, minX, minY, maxX, maxY, sizeX, sizeY):
    x = sizeX * (px - minX) / (maxX - minX)
    y = sizeY * (py - minY) / (maxY - minY)  # Y-axis top-to-bottom

    qp.drawEllipse(QPoint(x, y), 10, 10)


#### draw a "text" at (px,py) resizing to viewport (minX, minY, maxX, maxY) with width=sizeX, height=sizeY
def drawText(qp, px, py, text, minX, minY, maxX, maxY, sizeX, sizeY):
    x = sizeX * (px - minX) / (maxX - minX)
    y = sizeY * (py - minY) / (maxY - minY)  # Y-axis top-to-bottom

    qp.drawText(QPoint(x + 5, y - 5), text)


########
def draw_pipelines(frame, data, minX, minY, maxX, maxY, color=Qt.blue):
    #
    if frame.parent().parent().ckPipeline.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 3))  # set brush width=3
        #
        sizeX = frame.size().width()  # sizeX, sizeY will be used in drawLine(), drawText() declared above
        sizeY = frame.size().height()

        # draw
        for rec in data:
            #         qp.setPen(QPen(color, int(rec[6])))        # Thickness
            drawLine(qp, rec[2], rec[3], rec[4], rec[5], minX, minY, maxX, maxY, sizeX, sizeY)

            x = (rec[2] + rec[4]) / 2
            y = (rec[3] + rec[5]) / 2
            #            if frame.parent().parent().ckPipeline.isChecked():
            if rec[1] == 'horizontal':
                drawText(qp, x, y, 'P' + str(rec[0]) + 'H', minX, minY, maxX, maxY, sizeX, sizeY)
            else:
                drawText(qp, x, y, 'P' + str(rec[0]) + 'V', minX, minY, maxX, maxY, sizeX, sizeY)

        #
        qp.end()


def draw_equipments(frame, data, minX, minY, maxX, maxY, color=Qt.red):
    #
    if frame.parent().parent().ckEquipment.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 1))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            x1 = rec[2]
            x2 = rec[2] + rec[4]
            y1 = rec[3]
            y2 = rec[3] + rec[5]
            drawLine(qp, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)

            #            if frame.parent().parent().ckEquipment.isChecked():
            drawText(qp, x1, y1, 'Eq' + str(rec[0]), minX, minY, maxX, maxY, sizeX, sizeY)

        #
        qp.end()


def draw_continuity_labels(frame, data, minX, minY, maxX, maxY, color=Qt.cyan):
    #
    if frame.parent().parent().ckContinuity.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 2))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            x1 = rec[2]
            x2 = rec[2] + rec[4]
            y1 = rec[3]
            y2 = rec[3] + rec[5]
            drawLine(qp, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)

        #    qp.setPen(QPen(Qt.black, 1))
        for rec in data:
            x1 = rec[2]
            x2 = rec[2] + rec[4]
            y1 = rec[3]
            y2 = rec[3] + rec[5]

            #        if frame.parent().parent().ckContinuity.isChecked():
            drawText(qp, x1 - ((x2 - x1) / 2), y1, rec[1], minX, minY, maxX, maxY, sizeX, sizeY)

        #
        qp.end()


def draw_vessels(frame, data, minX, minY, maxX, maxY, color=Qt.yellow):
    #
    if frame.parent().parent().ckEquipment.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 2))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            x1 = rec[1]
            x2 = rec[1] + rec[3]
            y1 = rec[2]
            y2 = rec[2] + rec[4]
            drawLine(qp, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)

            qp.setPen(QPen(Qt.black, 1))
            drawText(qp, (x1 + x2) / 2, (y1 + y2) / 2, 'V' + str(rec[0]), minX, minY, maxX, maxY, sizeX, sizeY)

    #
    qp.end()


def draw_sensors(frame, data, minX, minY, maxX, maxY, color=Qt.blue):
    #
    qp = QPainter()
    qp.begin(frame)

    qp.setPen(QPen(color, 1))
    #
    sizeX = frame.size().width()
    sizeY = frame.size().height()

    # draw
    for rec in data:
        x = rec[2]
        y = rec[3]
        r = rec[4]
        drawCircle(qp, x, y, r, minX, minY, maxX, maxY, sizeX, sizeY)

    #
    qp.end()


def draw_junctions(frame, data, minX, minY, maxX, maxY, color=Qt.blue):
    #
    if frame.parent().parent().ckPipeline.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 3))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            x = rec[4]
            y = rec[5]
            drawLine(qp, x - 5, y - 5, x + 5, y + 5, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x - 5, y + 5, x + 5, y - 5, minX, minY, maxX, maxY, sizeX, sizeY)

        #
        qp.end()


def draw_area_breaks(frame, data, minX, minY, maxX, maxY, color=Qt.magenta):
    #
    if frame.parent().parent().ckAreabreaks.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 2))  # , Qt.DashLine))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            x = rec[3]
            y = rec[4]
            #         drawLine(qp, x, minY, x, maxY, minX, minY, maxX, maxY, sizeX, sizeY)
            #         drawLine(qp, minX, y, maxX, y, minX, minY, maxX, maxY, sizeX, sizeY)
            # small rectangle
            drawLine(qp, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)

            #            if frame.parent().parent().ckAreabreaks.isChecked():
            drawText(qp, x, y, rec[1] + ' - ' + rec[2], minX, minY, maxX, maxY, sizeX, sizeY)

        #
        qp.end()


def draw_section_breaks(frame, data, minX, minY, maxX, maxY, color=Qt.darkYellow):
    #
    if frame.parent().parent().ckSectionbreaks.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 2))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            x = rec[5]
            y = rec[6]
            #         drawLine(qp, x, minY, x, maxY, minX, minY, maxX, maxY, sizeX, sizeY)
            #         drawLine(qp, minX, y, maxX, y, minX, minY, maxX, maxY, sizeX, sizeY)
            # small rectangle
            drawLine(qp, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)

            #        if frame.parent().parent().ckSectionbreaks.isChecked():
            drawText(qp, x, y, rec[0] + ':' + rec[3] + ' - ' + rec[4], minX, minY, maxX, maxY, sizeX, sizeY)

        #
        qp.end()


def draw_composition_breaks(frame, data, minX, minY, maxX, maxY, color=Qt.green):
    #
    if frame.parent().parent().ckCompositionbreaks.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 2))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            x = rec[5]
            y = rec[6]
            #         drawLine(qp, x, minY, x, maxY, minX, minY, maxX, maxY, sizeX, sizeY)
            #         drawLine(qp, minX, y, maxX, y, minX, minY, maxX, maxY, sizeX, sizeY)
            # small rectangle
            drawLine(qp, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
            drawLine(qp, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)

            #            if frame.parent().parent().ckCompositionbreaks.isChecked():
            drawText(qp, x, y + 50, rec[3] + ' - ' + rec[4], minX, minY, maxX, maxY, sizeX, sizeY)

        #
        qp.end()


####
def draw_query_areas(frame, selectedAreas, minX, minY, maxX, maxY, color=Qt.black):
    #
    qp = QPainter()
    qp.begin(frame)

    qp.setPen(QPen(color, 1, Qt.DashLine))
    #
    sizeX = frame.size().width()
    sizeY = frame.size().height()

    # draw
    for rect in selectedAreas:
        drawRectange(qp, rect[0], rect[1], rect[2], rect[3], minX, minY, maxX, maxY, sizeX, sizeY)
    #
    qp.end()


#### the right frame of the main window
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


####
class NetlistGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.data = {}  # store data dictionary (see netlist_reader.py)
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

        lblSection = QLabel('Section Breaks')
        gridLeft.addWidget(lblSection, 7, 0)
        self.cboSection = CheckableComboBox()
        gridLeft.addWidget(self.cboSection, 8, 0)
        sectionItemList = ['RJAS', 'JASIN', 'FLARE', 'METHANOL']
        for i in range(len(sectionItemList)):
            self.cboSection.addItem(sectionItemList[i])
            item = self.cboSection.model().item(i, 0)
            item.setCheckState(Qt.Unchecked)

        self.btnQuerySection = QPushButton('Query')
        gridLeft.addWidget(self.btnQuerySection, 8, 1)
        self.btnQuerySection.clicked.connect(self.runQuerySection)

        lblComp = QLabel('Composition Breaks')
        gridLeft.addWidget(lblComp, 9, 0)
        self.cboComp = CheckableComboBox()
        gridLeft.addWidget(self.cboComp, 10, 0)
        compositionItemList = ['METHANOL', 'WELL FLUIDS']
        for i in range(len(compositionItemList)):
            self.cboComp.addItem(compositionItemList[i])
            item = self.cboComp.model().item(i, 0)
            item.setCheckState(Qt.Unchecked)

        self.btnQueryComp = QPushButton('Query')
        gridLeft.addWidget(self.btnQueryComp, 10, 1)
        self.btnQueryComp.clicked.connect(self.runQueryComp)

        #        self.cboCompDir = CheckableComboBox()
        #        gridLeft.addWidget(self.cboCompDir, 11, 0)
        #        compDirItemList = ['left-up', 'right-up', 'right-down', 'left-down']
        #        for i in range(len(compDirItemList)):
        #            self.cboCompDir.addItem(compDirItemList[i])
        #            item = self.cboCompDir.model().item(i, 0)
        #            item.setCheckState(Qt.Unchecked)

        lblResult = QLabel('Shapes within:')
        gridLeft.addWidget(lblResult, 11, 0)
        self.txtResult = QTextEdit('')
        self.txtResult.setAcceptRichText(False)
        gridLeft.addWidget(self.txtResult, 12, 0, 8, 2)

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
            self.minX, self.minY, self.maxX, self.maxY = find_ranges(self.data)
            self.selectedData = self.data


##########################
if __name__ == '__main__':
    app = QApplication(sys.argv)  # invoke the main application and show the main window "NetlistGUI"
    ex = NetlistGUI()
    sys.exit(app.exec_())
