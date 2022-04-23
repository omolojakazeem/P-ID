# System Files
import csv
import pandas as pd
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen


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
def find_ranges(data, useful_column_index):  # data: the dictionary of all frames read in read_csv() function
    cl_column_data, ab_column_data, sb_column_data, cb_column_data, vs_column_data, pl_column_data, pj_column_data, ts_column_data, es_column_data, et_column_data, ss_column_data = useful_column_index

    data_x = []
    data_y = []
    location_list_name = []
    if 'Continuity Labels' in data.keys():
        # each Continuity Labels has x1=rec[2], x2=rec[2] + rec[4], y1=rec[3], y2=rec[3] + rec[5]
        for rec in data['Continuity Labels']:
            location_list_name.append(rec[cl_column_data["Location"]])
            data_x.extend([rec[cl_column_data["x"]], rec[cl_column_data["x"]] + rec[cl_column_data["w"]]])
            data_y.extend([rec[cl_column_data["y"]], rec[cl_column_data["y"]] + rec[cl_column_data["h"]]])

    if 'Sensors' in data.keys():
        for rec in data['Sensors']:  # each Sensors is (x,y,r)
            location_list_name.append(rec[ss_column_data["Location"]])
            data_x.extend([rec[ss_column_data["x"]] - rec[ss_column_data["r"]], rec[ss_column_data["x"]] + rec[ss_column_data["r"]]])
            data_y.extend([rec[ss_column_data["y"]] - rec[ss_column_data["r"]], rec[ss_column_data["y"]] + rec[ss_column_data["r"]]])
    if 'Pipelines' in data.keys():
        for rec in data['Pipelines']:
            location_list_name.append(rec[pl_column_data["Location"]])
            data_x.extend([rec[pl_column_data["x1"]], rec[pl_column_data["x2"]]])
            data_y.extend([rec[pl_column_data["y1"]], rec[pl_column_data["y2"]]])
    if 'Equipment symbols' in data.keys():
        for rec in data['Equipment symbols']:
            location_list_name.append(rec[es_column_data["Location"]])
            data_x.extend([rec[es_column_data["x"]], rec[es_column_data["x"]] + rec[es_column_data["w"]]])
            data_y.extend([rec[es_column_data["y"]], rec[es_column_data["y"]] + rec[es_column_data["h"]]])
    if 'Area Breaks' in data.keys():
        for rec in data['Area Breaks']:
            location_list_name.append(rec[ab_column_data["Location"]])
            data_x.append(rec[ab_column_data["x"]])
            data_y.append(rec[ab_column_data["y"]])
    if 'Composition Breaks' in data.keys():
        for rec in data['Composition Breaks']:
            location_list_name.append(rec[cb_column_data["Location"]])
            data_x.append(rec[cb_column_data["x"]])
            data_y.append(rec[cb_column_data["y"]])
    if 'Section Breaks' in data.keys():
        for rec in data['Section Breaks']:
            location_list_name.append(rec[sb_column_data["Location"]])
            data_x.append(rec[sb_column_data["x"]])
            data_y.append(rec[sb_column_data["y"]])
    if 'Text Strings' in data.keys():
        for rec in data['Text Strings']:
            location_list_name.append(rec[ts_column_data["Location"]])
            data_x.extend([rec[ts_column_data["x"]], rec[ts_column_data["x"]] + rec[ts_column_data["w"]]])
            data_y.extend([rec[ts_column_data["y"]], rec[ts_column_data["y"]] + rec[ts_column_data["h"]]])
    if 'Pipeline Junctions' in data.keys():
        for rec in data['Pipeline Junctions']:
            location_list_name.append(rec[pj_column_data["Location"]])
            data_x.append(rec[pj_column_data["x"]])
            data_y.append(rec[pj_column_data["y"]])
    if 'Vessels' in data.keys():
        for rec in data['Vessels']:
            location_list_name.append(rec[vs_column_data["Location"]])
            data_x.extend([rec[vs_column_data["x"]], rec[vs_column_data["x"]] + rec[vs_column_data["w"]]])
            data_y.extend([rec[vs_column_data["y"]], rec[vs_column_data["y"]] + rec[vs_column_data["h"]]])
    location_list_name.sort()
    return min(data_x), min(data_y), max(data_x), max(data_y), location_list_name   # means minX, minY, maxX, maxY


#### check if (x,y) is inside any rectangle of 'areas' or not
def check_in_area(areas, x, y):
    #print(areas)
    for area in areas:  # each area is a rectangle defined by (x1,y1,x2,y2)

        x1 = area[0]
        y1 = area[1]
        x2 = area[2]
        y2 = area[3]

        if x1 <= x and x <= x2 and y1 <= y and y <= y2:
            return True
    return False


#### scan the data dictionary and add components that cross any rectangle in "areas"
def query_by_areas(data, areas, useful_column_index):

    cl_column_data, ab_column_data, sb_column_data, cb_column_data, vs_column_data, pl_column_data, pj_column_data, ts_column_data, es_column_data, et_column_data, ss_column_data = useful_column_index

    ret = {}
    # continuity labels
    if 'Continuity Labels' in data.keys():
        frameL = []
        for rec in data['Continuity Labels']:
            x1 = rec[cl_column_data['x']]
            y1 = rec[cl_column_data['y']]
            x2 = rec[cl_column_data['x']] + rec[cl_column_data['w']]
            y2 = rec[cl_column_data['y']] + rec[cl_column_data['h']]
            if check_in_area(areas, x1, y1) or check_in_area(areas, x2, y2):  # AND/OR
                frameL.append(rec)
        ret['Continuity Labels'] = frameL

    # pipelines
    if 'Pipelines' in data.keys():
        frameP = []
        for rec in data['Pipelines']:
            x1 = rec[pl_column_data['x1']]
            y1 = rec[pl_column_data['y1']]
            x2 = rec[pl_column_data['x2']]
            y2 = rec[pl_column_data['y2']]
            if check_in_area(areas, x1, y1) and check_in_area(areas, x2, y2):  # AND/OR
                frameP.append(rec)
        ret['Pipelines'] = frameP

    # equipments
    if 'Equipment symbols' in data.keys():
        frameE = []
        for rec in data['Equipment symbols']:

            x1 = rec[es_column_data['x']]
            x2 = rec[es_column_data['x']] + rec[es_column_data['w']]
            y1 = rec[es_column_data['y']]
            y2 = rec[es_column_data['y']] + rec[es_column_data['h']]
            if check_in_area(areas, x1, y1) or check_in_area(areas, x2, y2):  # AND/OR
                frameE.append(rec)
        ret['Equipment symbols'] = frameE

    if 'Equipment Tags' in data.keys():
        frameE = []
        for rec in data['Equipment Tags']:

            x1 = rec[et_column_data['x']]
            x2 = rec[et_column_data['x']] + rec[et_column_data['r']]
            y1 = rec[et_column_data['y']]
            y2 = rec[et_column_data['y']] + rec[et_column_data['r']]
            if check_in_area(areas, x1, y1) or check_in_area(areas, x2, y2):  # AND/OR
                frameE.append(rec)
        ret['Equipment Tags'] = frameE

    if 'Sensors' in data.keys():
        frameE = []
        for rec in data['Sensors']:

            x1 = rec[ss_column_data['x']]
            x2 = rec[ss_column_data['x']] + rec[ss_column_data['r']]
            y1 = rec[ss_column_data['y']]
            y2 = rec[ss_column_data['y']] + rec[ss_column_data['r']]
            if check_in_area(areas, x1, y1) or check_in_area(areas, x2, y2):  # AND/OR
                frameE.append(rec)
        ret['Sensors'] = frameE

    # junctions
    if 'Pipeline Junctions' in data.keys():
        frameJ = []
        for rec in data['Pipeline Junctions']:
            x1 = rec[pj_column_data['x']]
            y1 = rec[pj_column_data['y']]
            if check_in_area(areas, x1, y1):
                frameJ.append(rec)
        ret['Pipeline Junctions'] = frameJ

    # vessels
    if 'Vessels' in data.keys():
        frameV = []
        for rec in data['Vessels']:
            x1 = rec[vs_column_data['x']]
            y1 = rec[vs_column_data['y']]
            x2 = rec[vs_column_data['x']] + rec[vs_column_data['w']]
            y2 = rec[vs_column_data['y']] + rec[vs_column_data['h']]
            if check_in_area(areas, x1, y1) or check_in_area(areas, x2, y2):  # AND/OR
                frameV.append(rec)
        ret['Vessels'] = frameV

    # breaks
    if 'Area Breaks' in data.keys():
        frameA = []
        for rec in data['Area Breaks']:
            x1 = rec[ab_column_data['x']]
            y1 = rec[ab_column_data['y']]
            if check_in_area(areas, x1, y1):
                frameA.append(rec)
            ret['Area Breaks'] = frameA

    if 'Section Breaks' in data.keys():
        frameS = []
        for rec in data['Section Breaks']:
            x1 = rec[sb_column_data['x']]
            y1 = rec[sb_column_data['y']]
            if check_in_area(areas, x1, y1):
                frameS.append(rec)
            ret['Section Breaks'] = frameS

    if 'Composition Breaks' in data.keys():
        frameC = []
        for rec in data['Composition Breaks']:
            x1 = rec[cb_column_data['x']]
            y1 = rec[cb_column_data['x']]
            if check_in_area(areas, x1, y1):
                frameC.append(rec)
            ret['Composition Breaks'] = frameC

    #
    return ret


#### convert a dictionary (selectedData) to text string
def query_to_text(data, selectedData, selected_location=None, selected_part=None, useful_column_index=None, column_list=None):

    cl_column_data, ab_column_data, sb_column_data, cb_column_data, vs_column_data, pl_column_data, pj_column_data, ts_column_data, es_column_data, et_column_data, ss_column_data = useful_column_index
    ret = ""
    # if 'Continuity Labels' in data.keys():
    #     ret = 'Continuity labels ---------------\n'
    #     for rec in selectedData['Continuity Labels']:
    #         if selected_location:
    #             if rec[cl_column_data['Location']] in selected_location:
    #                 ret += str(rec) + '\n'
    # if 'Pipelines' in data.keys():
    #     ret += 'Pipelines ---------------\n'
    #     for rec in selectedData['Pipelines']:
    #         if rec[pl_column_data['Location']] in selected_location:
    #             ret += str(rec) + '\n'
    # if 'Equipment symbols' in data.keys():
    #     ret += 'Equipment symbols ---------------\n'
    #     for rec in selectedData['Equipment symbols']:
    #         if rec[es_column_data['Location']] in selected_location:
    #             ret += str(rec) + '\n'
    # if 'Vessels' in data.keys():
    #     ret += 'Vessels ---------------\n'
    #     for rec in selectedData['Vessels']:
    #         if rec[vs_column_data['Location']] in selected_location:
    #             ret += str(rec) + '\n'
    #
    # if 'Sensors' in data.keys():
    #
    #     ret += 'Sensors ---------------\n'
    #     if 'Sensors' in selectedData:
    #         for rec in selectedData['Sensors']:
    #             if rec[vs_column_data['Location']] in selected_location:
    #                 ret += str(rec) + '\n'

    if column_list:
        for i in column_list:
            if i in data.keys():
                    ret += f"{i} ----------------\n"
                    if i in selectedData:
                        for rec in selectedData[i]:
                            if i == 'Vessels':
                                if selected_part:
                                    pass
                                elif selected_location:
                                    if rec[vs_column_data['Location']] in selected_location:
                                        ret += str(rec) + '\n'
                                else:
                                    ret += str(rec) + '\n'

                            if i == 'Pipelines':
                                if selected_part:
                                    pass
                                elif selected_location:
                                    if rec[pl_column_data['Location']] in selected_location:
                                        ret += str(rec) + '\n'
                                else:
                                    ret += str(rec) + '\n'

                            if i == 'Continuity Labels':
                                if selected_part:
                                    pass
                                elif selected_location:
                                    if rec[cl_column_data['Location']] in selected_location:
                                        ret += str(rec) + '\n'
                                else:
                                    ret += str(rec) + '\n'

                            if i == 'Pipeline Junctions':
                                if selected_part:
                                    pass
                                elif selected_location:
                                    if rec[pj_column_data['Location']] in selected_location:
                                        ret += str(rec) + '\n'
                                else:
                                    ret += str(rec) + '\n'

                            if i == 'Equipment symbols':
                                if selected_part:
                                    if selected_part[0] == 'Equipment symbols':
                                        if rec[es_column_data['class']] in selected_part:
                                            ret += str(rec) + '\n'
                                elif selected_location:
                                    if rec[es_column_data['Location']] in selected_location:
                                        ret += str(rec) + '\n'
                                    else:
                                        pass
                                else:
                                    ret += str(rec) + '\n'
                            if i == 'Equipment Tags':
                                if selected_part:
                                    pass
                                elif selected_location:
                                    if rec[et_column_data['Location']] in selected_location:
                                        ret += str(rec) + '\n'
                                else:
                                    ret += str(rec) + '\n'

                            if i == 'Sensors':
                                if selected_part:
                                    if selected_part[0] == 'Sensors':
                                        if rec[ss_column_data['tag']] in selected_part:
                                            ret += str(rec) + '\n'
                                    else:
                                        pass
                                elif selected_location:
                                    if rec[ss_column_data['Location']] in selected_location:
                                        ret += str(rec) + '\n'
                                else:
                                    ret += str(rec) + '\n'
                            if i == 'Area Breaks':
                                if selected_part:
                                    pass
                                elif selected_location:
                                    if rec[ab_column_data['Location']] in selected_location:
                                        ret += str(rec) + '\n'
                                else:
                                    ret += str(rec) + '\n'
                            if i == 'Section Breaks':
                                if selected_part:
                                    pass
                                elif selected_location:
                                    if rec[sb_column_data['Location']] in selected_location:
                                        ret += str(rec) + '\n'
                                else:
                                    ret += str(rec) + '\n'

                            if i == 'Composition Breaks':
                                if selected_part:
                                    pass
                                elif selected_location:
                                    if rec[cb_column_data['Location']] in selected_location:
                                        ret += str(rec) + '\n'
                                else:
                                    ret += str(rec) + '\n'


    return ret


# GUI
# draw a line from (px1,py1) to (px2, py2) resizing to viewport (minX, minY, maxX, maxY) with width=sizeX, height=sizeY
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


# draw a circle center at (px,py) resizing to viewport (minX, minY, maxX, maxY) with width=sizeX, height=sizeY
def drawCircle(qp, px, py, pr, minX, minY, maxX, maxY, sizeX, sizeY):
    x = sizeX * (px - minX) / (maxX - minX)
    y = sizeY * (py - minY) / (maxY - minY)  # Y-axis top-to-bottom

    qp.drawEllipse(QPoint(x, y), 10, 10)


# draw a "text" at (px,py) resizing to viewport (minX, minY, maxX, maxY) with width=sizeX, height=sizeY
def drawText(qp, px, py, text, minX, minY, maxX, maxY, sizeX, sizeY):
    x = sizeX * (px - minX) / (maxX - minX)
    y = sizeY * (py - minY) / (maxY - minY)  # Y-axis top-to-bottom

    qp.drawText(QPoint(x + 5, y - 5), text)


def drawMyText(frame, px, py, text, minX, minY, maxX, maxY, sizeX, sizeY, color):
    x = sizeX * (px - minX) / (maxX - minX)
    y = sizeY * (py - minY) / (maxY - minY)  # Y-axis top-to-bottom

    text_msg = frame._scene.addText(text)
    text_msg.setPos(x + 5, y - 5)
    text_msg.setDefaultTextColor(color)
    return text_msg


def drawMyLine(frame, px1, py1, px2, py2, minX, minY, maxX, maxY, sizeX, sizeY, color):  # qp is a QPen for drawing
    x1 = sizeX * (px1 - minX) / (maxX - minX)
    y1 = sizeY * (py1 - minY) / (maxY - minY)  # Y-axis top-to-bottom

    x2 = sizeX * (px2 - minX) / (maxX - minX)
    y2 = sizeY * (py2 - minY) / (maxY - minY)  # Y-axis top-to-bottom

    line = frame._scene.addLine(x1, y1, x2, y2, QPen(color))
    return line


def drawMyRec(frame, px1, py1, px2, py2, minX, minY, maxX, maxY, sizeX, sizeY, color):  # qp is a QPen for drawing
    drawMyLine(frame, px1, py1, px2, py1, minX, minY, maxX, maxY, sizeX, sizeY, color)
    drawMyLine(frame, px1, py1, px1, py2, minX, minY, maxX, maxY, sizeX, sizeY, color)
    drawMyLine(frame, px1, py2, px2, py2, minX, minY, maxX, maxY, sizeX, sizeY, color)
    drawMyLine(frame, px2, py1, px2, py2, minX, minY, maxX, maxY, sizeX, sizeY, color)


def drawMyCircle(frame, px, py, pr, minX, minY, maxX, maxY, sizeX, sizeY, color):
    x = sizeX * (px - minX) / (maxX - minX)
    y = sizeY * (py - minY) / (maxY - minY)  # Y-axis top-to-bottom

    ellipse = frame._scene.addEllipse(x, y, 10, 10, color)
    return ellipse


def draw_pipelines(frame, data, minX, minY, maxX, maxY,selected_location=None, selected_part=None, column_data=None, color=Qt.blue):

    if frame.parent().parent().select_pipeline_checkbox.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 3))  # set brush width=3
        #
        sizeX = frame.size().width()  # sizeX, sizeY will be used in drawLine(), drawText() declared above
        sizeY = frame.size().height()

        # draw
        for rec in data:
            if selected_location:
                if rec[column_data["Location"]] in selected_location:
                    #         qp.setPen(QPen(color, int(rec[6])))        # Thickness
                    drawMyLine(frame, rec[column_data['x1']], rec[column_data['y1']], rec[column_data['x2']],
                               rec[column_data['y2']], minX, minY, maxX, maxY, sizeX, sizeY, color)
                    x = (rec[column_data['x1']] + rec[column_data['x2']]) / 2
                    y = (rec[column_data['y1']] + rec[column_data['y2']]) / 2
                    #            if frame.parent().parent().ckPipeline.isChecked():
                    if rec[column_data['direction']] == 'horizontal':
                        drawMyText(frame, x, y, 'P' + str(rec[column_data['number']]) + 'H', minX, minY, maxX, maxY,sizeX,sizeY, color)
                    else:
                        drawMyText(frame, x, y, 'P' + str(rec[column_data['number']]) + 'V', minX, minY, maxX, maxY, sizeX+200, sizeY+100, color)
            elif selected_part:
                pass
            else:
                #         qp.setPen(QPen(color, int(rec[6])))        # Thickness
                # drawLine(qp, rec[column_data['x1']], rec[column_data['y1']], rec[column_data['x2']],
                #          rec[column_data['y2']], minX, minY, maxX, maxY, sizeX, sizeY)
                drawMyLine(frame, rec[column_data['x1']], rec[column_data['y1']], rec[column_data['x2']],
                         rec[column_data['y2']], minX, minY, maxX, maxY, sizeX, sizeY, color)


                x = (rec[column_data['x1']] + rec[column_data['x2']]) / 2
                y = (rec[column_data['y1']] + rec[column_data['y2']]) / 2
                #            if frame.parent().parent().ckPipeline.isChecked():
                if rec[column_data['direction']] == 'horizontal':
                    # drawText(qp, x, y, 'P' + str(rec[column_data['number']]) + 'H', minX, minY, maxX, maxY, sizeX,
                    #          sizeY)
                    drawMyText(frame, x, y, 'P' + str(rec[column_data['number']]) + 'H', minX, minY, maxX, maxY, sizeX,
                             sizeY, color)
                else:
                    drawMyText(frame, x, y, 'P' + str(rec[column_data['number']]) + 'V', minX, minY, maxX, maxY, sizeX-100,
                               sizeY, color)
        #
        qp.end()


def draw_equipments(frame, data, minX, minY, maxX, maxY, selected_location=None, selected_part=None, column_data=None, color=Qt.red):
    #
    if frame.parent().parent().select_equipment_checkbox.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 1))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            if selected_location:
                if rec[column_data["Location"]] in selected_location:
                    x1 = rec[column_data["x"]]
                    x2 = rec[column_data["x"]] + rec[column_data["w"]]
                    y1 = rec[column_data["y"]]
                    y2 = rec[column_data["y"]] + rec[column_data["h"]]
                    drawMyLine(frame, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    #drawText(qp, x1, y1, 'Eq' + str(rec[column_data["number"]]), minX, minY, maxX, maxY, sizeX, sizeY)
                    drawMyText(frame, x1, y1, 'Eq' + str(rec[column_data["number"]]), minX, minY, maxX, maxY, sizeX,
                               sizeY, color)
            elif selected_part:
                if selected_part[0] == 'Equipment symbols':
                    if rec[column_data["class"]] in selected_part:
                        x1 = rec[column_data["x"]]
                        x2 = rec[column_data["x"]] + rec[column_data["w"]]
                        y1 = rec[column_data["y"]]
                        y2 = rec[column_data["y"]] + rec[column_data["h"]]
                        drawMyLine(frame, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY, color)
                        drawMyLine(frame, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                        drawMyLine(frame, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                        drawMyLine(frame, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                        drawMyText(frame, x1, y1, 'Eq' + str(rec[column_data["number"]]), minX, minY, maxX, maxY, sizeX, sizeY, color)
                    else:
                        pass
            else:
                x1 = rec[column_data["x"]]
                x2 = rec[column_data["x"]] + rec[column_data["w"]]
                y1 = rec[column_data["y"]]
                y2 = rec[column_data["y"]] + rec[column_data["h"]]
                # drawLine(qp, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY)
                # drawLine(qp, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY)
                # drawLine(qp, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)
                # drawLine(qp, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)

                drawMyLine(frame, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)

                drawMyText(frame, x1, y1, 'Eq' + str(rec[column_data["number"]]), minX, minY, maxX, maxY, sizeX, sizeY, color)

            #            if frame.parent().parent().select_equipment_checkbox.isChecked():

        qp.end()


def draw_continuity_labels(frame, data, minX, minY, maxX, maxY, selected_location=None, selected_part=None, column_data=None, color=Qt.cyan):
    if frame.parent().parent().select_continuity_checkbox.isChecked():
        qp = QPainter()
        qp.begin(frame)
        qp.setPen(QPen(color, 2))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        for rec in data:
            if selected_location:
                if rec[column_data['Location']] in selected_location:
                    x1 = rec[column_data['x']]
                    x2 = rec[column_data['x']] + rec[column_data['w']]
                    y1 = rec[column_data['y']]
                    y2 = rec[column_data['y']] + rec[column_data['h']]
                    # drawLine(qp, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)

                    drawMyLine(frame, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)

            elif selected_part:
                pass
            else:
                x1 = rec[column_data['x']]
                x2 = rec[column_data['x']] + rec[column_data['w']]
                y1 = rec[column_data['y']]
                y2 = rec[column_data['y']] + rec[column_data['h']]
                drawMyLine(frame, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)

        #    qp.setPen(QPen(Qt.black, 1))
        for rec in data:
            if selected_location:
                if rec[column_data['Location']] in selected_location:
                    x1 = rec[column_data['x']]
                    x2 = rec[column_data['x']] + rec[column_data['w']]
                    y1 = rec[column_data['y']]
                    y2 = rec[column_data['y']] + rec[column_data['h']]


                    #        if frame.parent().parent().select_continuity_checkbox.isChecked():
                    #drawText(qp, x1 - ((x2 - x1) / 2), y1, rec[column_data['tag']], minX, minY, maxX, maxY, sizeX, sizeY)
                    drawMyText(frame, x1 - ((x2 - x1) / 2), y1, rec[column_data['tag']], minX, minY, maxX, maxY, sizeX, sizeY-20, color)

            elif selected_part:
                pass
            else:
                x1 = rec[column_data['x']]
                x2 = rec[column_data['x']] + rec[column_data['w']]
                y1 = rec[column_data['y']]
                y2 = rec[column_data['y']] + rec[column_data['h']]



                #        if frame.parent().parent().select_continuity_checkbox.isChecked():
                drawMyText(frame, x1 - ((x2 - x1) / 2), y1, rec[column_data['tag']], minX, minY, maxX, maxY, sizeX, sizeY-20, color)

        #
        qp.end()


def draw_vessels(frame, data, minX, minY, maxX, maxY, selected_location=None, selected_part=None, column_data=None, color=Qt.yellow):
    #
    if frame.parent().parent().select_vessel_checkbox.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 2))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            if selected_location:
                if rec[column_data["Location"]] in selected_location:
                    x1 = rec[column_data['x']]
                    x2 = rec[column_data['x']] + rec[column_data['w']]
                    y1 = rec[column_data['y']]
                    y2 = rec[column_data['y']] + rec[column_data['h']]
                    drawMyLine(frame, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)

                    qp.setPen(QPen(Qt.black, 1))
                    drawMyText(frame, (x1 + x2) / 2, (y1 + y2) / 2, 'V' + str(rec[column_data["number"]]), minX, minY, maxX, maxY, sizeX, sizeY, color)
            elif selected_part:
                pass
            else:
                x1 = rec[column_data['x']]
                x2 = rec[column_data['x']] + rec[column_data['w']]
                y1 = rec[column_data['y']]
                y2 = rec[column_data['y']] + rec[column_data['h']]
                # drawLine(qp, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY)
                # drawLine(qp, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY)
                # drawLine(qp, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)
                # drawLine(qp, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY)

                drawMyLine(frame, x1, y1, x2, y1, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x1, y1, x1, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x1, y2, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x2, y1, x2, y2, minX, minY, maxX, maxY, sizeX, sizeY, color)

                qp.setPen(QPen(Qt.black, 1))
                #drawText(qp, (x1 + x2) / 2, (y1 + y2) / 2, 'V' + str(rec[column_data["number"]]), minX, minY, maxX, maxY, sizeX, sizeY)
                drawMyText(frame, (x1 + x2) / 2, (y1 + y2) / 2, 'V' + str(rec[column_data["number"]]), minX, minY, maxX, maxY, sizeX, sizeY, color)
    #
        qp.end()


def draw_sensors(frame, data, minX, minY, maxX, maxY,selected_location=None, selected_part=None, column_data=None, color=Qt.yellow):
    #
    if frame.parent().parent().select_sensor_checkbox.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 1))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            if selected_location:
                if rec[column_data["Location"]] in selected_location:
                    x = rec[column_data['x']]
                    y = rec[column_data['y']]
                    r = rec[column_data['r']]
                    #drawCircle(qp, x, y, r, minX, minY, maxX, maxY, sizeX, sizeY)
                    drawMyCircle(frame, x, y, r, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    #drawText(qp, x, y, 'S' + str(rec[column_data['number']]), minX, minY, maxX, maxY, sizeX, sizeY)
                    drawMyText(frame, x, y, 'S' + str(rec[column_data['number']]), minX, minY, maxX, maxY, sizeX, sizeY, color)
            elif selected_part:
                if selected_part[0] == 'Sensors':
                    if rec[column_data["tag"]] in selected_part:
                        x = rec[column_data['x']]
                        y = rec[column_data['y']]
                        r = rec[column_data['r']]
                        drawMyCircle(frame, x, y, r, minX, minY, maxX, maxY, sizeX, sizeY, color)
                        #drawText(qp, x, y, 'S' + str(rec[column_data['number']]), minX, minY, maxX, maxY, sizeX, sizeY)
                        drawMyText(frame, x, y, 'S' + str(rec[column_data['number']]), minX, minY, maxX, maxY, sizeX,
                                   sizeY, color)
                    else:
                        pass

            else:
                x = rec[column_data['x']]
                y = rec[column_data['y']]
                r = rec[column_data['r']]
                drawMyCircle(frame, x, y, r, minX, minY, maxX, maxY, sizeX, sizeY, color)
                #drawText(qp, x, y, 'S' + str(rec[column_data['number']]), minX, minY, maxX, maxY, sizeX, sizeY)
                drawMyText(frame, x, y, 'S' + str(rec[column_data['number']]), minX, minY, maxX, maxY, sizeX, sizeY, color)
        #
        qp.end()


def draw_tag(frame, data, minX, minY, maxX, maxY,selected_location=None, selected_part=None, column_data=None, color=Qt.blue):
    #
    if frame.parent().parent().select_equipment_tag_checkbox.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 1))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            if selected_location:
                if rec[column_data["Location"]] in selected_location:
                    x = rec[column_data['x']]
                    y = rec[column_data['y']]
                    r = rec[column_data['r']]
                    drawMyCircle(frame, x, y, r, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    #drawText(qp, x, y, 'et' + str(rec[column_data['number']]), minX, minY, maxX, maxY, sizeX, sizeY)
                    drawMyText(frame, x, y, 'et' + str(rec[column_data['number']]), minX, minY, maxX, maxY, sizeX, sizeY, color)
            elif selected_part:
                pass
            else:
                x = rec[column_data['x']]
                y = rec[column_data['y']]
                r = rec[column_data['r']]
                #drawCircle(qp, x, y, r, minX, minY, maxX, maxY, sizeX, sizeY)
                drawMyCircle(frame, x, y, r, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyText(frame, x, y, 'et' + str(rec[column_data['number']]), minX, minY, maxX, maxY, sizeX, sizeY, color)

        #
        qp.end()


def draw_junctions(frame, data, minX, minY, maxX, maxY, selected_location=None, selected_part=None, column_data=None, color=Qt.blue):
    #
    if frame.parent().parent().select_pipeline_checkbox.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 3))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            if selected_location:
                if rec[column_data["Location"]] in selected_location:
                    x = rec[column_data['x']]
                    y = rec[column_data['y']]
                    drawMyLine(frame, x - 5, y - 5, x + 5, y + 5, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x - 5, y + 5, x + 5, y - 5, minX, minY, maxX, maxY, sizeX, sizeY, color)
            elif selected_part:
                pass
            else:
                x = rec[column_data['x']]
                y = rec[column_data['y']]
                # drawLine(qp, x - 5, y - 5, x + 5, y + 5, minX, minY, maxX, maxY, sizeX, sizeY)
                # drawLine(qp, x - 5, y + 5, x + 5, y - 5, minX, minY, maxX, maxY, sizeX, sizeY)

                drawMyLine(frame, x-5, y-5, x+5, y+5, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x-5, y+5, x+5, y-5, minX, minY, maxX, maxY, sizeX, sizeY, color)

        #
        qp.end()


def draw_area_breaks(frame, data, minX, minY, maxX, maxY, selected_location=None, selected_part=None, column_data=None, color=Qt.magenta):
    #
    if frame.parent().parent().select_area_break_checkbox.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 2))  # , Qt.DashLine))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            if selected_location:
                if rec[column_data["Location"]] in selected_location:
                    x = rec[column_data['x']]
                    y = rec[column_data['y']]
                    #         drawLine(qp, x, minY, x, maxY, minX, minY, maxX, maxY, sizeX, sizeY)
                    #         drawLine(qp, minX, y, maxX, y, minX, minY, maxX, maxY, sizeX, sizeY)
                    # small rectangle
                    # drawLine(qp, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)

                    drawMyLine(frame, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)

                    #            if frame.parent().parent().select_area_break_checkbox.isChecked():
                    #drawText(qp, x, y, rec[column_data['ab_look1']] + ' - ' + rec[column_data['ab_look2']], minX, minY, maxX, maxY, sizeX, sizeY)
                    drawMyText(frame, x, y, rec[column_data['ab_look1']] + ' - ' + rec[column_data['ab_look2']], minX, minY, maxX, maxY, sizeX, sizeY, color)
            elif selected_part:
                pass
            else:
                x = rec[column_data['x']]
                y = rec[column_data['y']]
                #         drawLine(qp, x, minY, x, maxY, minX, minY, maxX, maxY, sizeX, sizeY)
                #         drawLine(qp, minX, y, maxX, y, minX, minY, maxX, maxY, sizeX, sizeY)
                # small rectangle
                drawMyLine(frame, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)

                #            if frame.parent().parent().select_area_break_checkbox.isChecked():
                drawMyText(frame, x, y, rec[column_data['ab_look1']] + ' - ' + rec[column_data['ab_look2']], minX, minY, maxX, maxY, sizeX, sizeY, color)
        #
        qp.end()


def draw_section_breaks(frame, data, minX, minY, maxX, maxY, selected_location=None, selected_part=None, column_data=None, color=Qt.darkYellow):
    #
    if frame.parent().parent().select_section_break_checkbox.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 2))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            if selected_location:
                if rec[column_data["Location"]] in selected_location:
                    x = rec[column_data['x']]
                    y = rec[column_data['y']]
                    #         drawLine(qp, x, minY, x, maxY, minX, minY, maxX, maxY, sizeX, sizeY)
                    #         drawLine(qp, minX, y, maxX, y, minX, minY, maxX, maxY, sizeX, sizeY)
                    # small rectangle
                    # drawLine(qp, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)

                    drawMyLine(frame, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)

                    #        if frame.parent().parent().select_section_break_checkbox.isChecked():
                    #drawText(qp, x, y, rec[column_data['id']] + ':' + rec[column_data['sb_look1']] + ' - ' + rec[column_data['sb_look2']], minX, minY, maxX, maxY, sizeX, sizeY)
                    drawMyText(frame, x, y, rec[column_data['id']] + ':' + rec[column_data['sb_look1']] + ' - ' + rec[column_data['sb_look2']], minX, minY, maxX, maxY, sizeX, sizeY, color)
            elif selected_part:
                pass
            else:
                x = rec[column_data['x']]
                y = rec[column_data['y']]
                #         drawLine(qp, x, minY, x, maxY, minX, minY, maxX, maxY, sizeX, sizeY)
                #         drawLine(qp, minX, y, maxX, y, minX, minY, maxX, maxY, sizeX, sizeY)
                # small rectangle
                drawMyLine(frame, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)

                #        if frame.parent().parent().select_section_break_checkbox.isChecked():

                drawMyText(frame, x, y, rec[column_data['id']] + ':' + rec[column_data['sb_look1']] + ' - ' + rec[
                    column_data['sb_look2']], minX, minY, maxX, maxY, sizeX, sizeY, color)

        #
        qp.end()


def draw_composition_breaks(frame, data, minX, minY, maxX, maxY, selected_location=None, selected_part=None, column_data=None, color=Qt.green):
    #
    if frame.parent().parent().select_composition_break_checkbox.isChecked():
        qp = QPainter()
        qp.begin(frame)

        qp.setPen(QPen(color, 2))
        #
        sizeX = frame.size().width()
        sizeY = frame.size().height()

        # draw
        for rec in data:
            if selected_location:
                if rec[column_data["Location"]] in selected_location:
                    x = rec[column_data['x']]
                    y = rec[column_data['y']]
                    #         drawLine(qp, x, minY, x, maxY, minX, minY, maxX, maxY, sizeX, sizeY)
                    #         drawLine(qp, minX, y, maxX, y, minX, minY, maxX, maxY, sizeX, sizeY)
                    # small rectangle
                    # drawLine(qp, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)
                    # drawLine(qp, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY)

                    drawMyLine(frame, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                    drawMyLine(frame, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)

                    #            if frame.parent().parent().select_composition_break_checkbox.isChecked():
                    #drawText(qp, x, y + 50, rec[column_data['cb_look1']] + ' - ' + rec[column_data['cb_look2']], minX, minY, maxX, maxY, sizeX, sizeY)
                    drawMyText(frame, x, y + 50, rec[column_data['cb_look1']] + ' - ' + rec[column_data['cb_look2']], minX, minY, maxX, maxY, sizeX, sizeY, color)

                #
            elif selected_part:
                pass
            else:
                x = rec[column_data['x']]
                y = rec[column_data['y']]
                #         drawLine(qp, x, minY, x, maxY, minX, minY, maxX, maxY, sizeX, sizeY)
                #         drawLine(qp, minX, y, maxX, y, minX, minY, maxX, maxY, sizeX, sizeY)
                # small rectangle
                drawMyLine(frame, x - 50, y - 50, x + 50, y - 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x - 50, y + 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x - 50, y - 50, x - 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)
                drawMyLine(frame, x + 50, y - 50, x + 50, y + 50, minX, minY, maxX, maxY, sizeX, sizeY, color)

                #            if frame.parent().parent().select_composition_break_checkbox.isChecked():
                drawMyText(frame, x, y + 50, rec[column_data['cb_look1']] + ' - ' + rec[column_data['cb_look2']], minX, minY, maxX, maxY, sizeX, sizeY, color)


            #
        qp.end()


def draw_query_areas(frame, selectedAreas, minX, minY, maxX, maxY, selected_location=None, selected_part=None, column_data=None, color=Qt.black):
    #
    qp = QPainter()
    qp.begin(frame)

    qp.setPen(QPen(color, 1, Qt.DashLine))
    #
    sizeX = frame.size().width()
    sizeY = frame.size().height()

    # draw
    for rect in selectedAreas:
        drawMyRec(frame, rect[0], rect[1], rect[2], rect[3], minX, minY, maxX, maxY, sizeX, sizeY, color)
    #
    qp.end()
