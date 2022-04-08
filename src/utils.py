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
    area_break_list = []  # columns is a dictionary of column names for each frame
    with open(file_name, 'rt') as f:  # open "file_name" as a variable f
        lines = f.read().split('\n')  # read all data from f and split them to text lines

        i = 0
        # header info (2 lines)
        data['header'] = lines[:2]
        i += 2  # skip the first two lines

        # read all frames
        list1 = ['Number', 'x', 'y', 'r', 'w', 'h', 'x1', 'y1', 'x2','y2']
        numeric_name_set = set(list1)  # the name of columns to be converted to numeric
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
    equipment_syb_list_name = ""
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
            # equipment_syb_list_name.append(rec[1])
            # #print(rec[1])
            # equipment_syb_list_name = rec[1]
            # # for i in rec[1]:
            # #     equipment_syb_list_name = ","+i
            # # print(equipment_syb_list_name)
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

    return min(data_x), min(data_y), max(data_x), max(data_y), equipment_syb_list_name  # means minX, minY, maxX, maxY


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
