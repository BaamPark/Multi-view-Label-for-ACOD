from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel
from tools.logger_config import logger

class ClickableImageLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent) #https://www.educative.io/answers/what-is-super-in-python
        #This is separate from the concept of class inheritance. 
        #When the ClickableImageLabel object is created inside the MainWindow class, MainWindow becomes its parent widget.
        self.parent = parent
        self.start_pos = None
        self.end_pos = None
        self.drawing = False
        self.rectangles = []
        self.clicked_rect = []
        self.selected_rectangle_index = None
        self.last_pos = None
        self.active_corner = None


    def mousePressEvent(self, event):
        logger.info(f"<==mouse press event function called==>")
        logger.info(f"rectangle list: {self.rectangles}")
        if event.button() == Qt.LeftButton:
            self.active_corner = None
            break_outer_loop = False 
            for i, rect in enumerate(self.rectangles):
                top_left = rect['min_xy']
                bottom_right = rect['max_xy']
                top_right = QPoint(bottom_right.x(), top_left.y())
                bottom_left = QPoint(top_left.x(), bottom_right.y())

                resizing_condition = False
                relocating_condition = False

                #this for loop is used for resizing the box
                for j, corner in enumerate([top_left, top_right, bottom_left, bottom_right]):
                    if (corner - event.pos()).manhattanLength() < 10:  # 10 is the max distance to detect a corner
                        logger.info('trying to resize bounding box')
                        self.selected_rectangle_index = i
                        self.active_corner = j
                        resizing_condition = True

                    elif (corner - event.pos()).manhattanLength() >= 10 and QRect(top_left, bottom_right).contains(event.pos()) and not self.parent.btn_add_label.isChecked():
                        logger.info('trying to relocate bounding box')
                        self.selected_rectangle_index = i
                        relocating_condition = True
                
                    if resizing_condition or relocating_condition:
                        if self.parent.image_label.clicked_rect_index: 
                            past_index = self.parent.image_label.clicked_rect_index.pop()
                            self.rectangles[past_index]['focus'] = False
                            self.parent.image_label.clicked_rect_index.append(i)
                        
                        rect['focus'] = True
                        break_outer_loop = True  # Set flag to True to break outer loop
                        continue
            
                if break_outer_loop:
                    break

            #for else statement: The “else” block only executes when there is no break in the loop.
            else:
                logger.info('no bounding box selected')
                if self.parent.btn_add_label.isChecked():
                    logger.info('trying to draw bounding box')
                    self.start_pos = event.pos()
                    self.end_pos = event.pos()  # Also initialize end_pos here
                    self.drawing = True
                    self.selected_rectangle_index = None
                    self.active_corner = None

                else:
                    logger.info('invalid mouse event')
                    self.start_pos = None
                    self.end_pos = None 
                    self.active_corner = None
                    self.selected_rectangle_index = None

            self.last_pos = event.pos()


    def mouseMoveEvent(self, event):
        logger.info(f"<==mouse move event function called==>")
        logger.info(f"active corner: {self.active_corner}")
        logger.info(f"drawing: {self.drawing}")
        if self.drawing and self.active_corner is None:
            logger.info(f"drawing is on and active corner is None")
            self.end_pos = event.pos()

        #resize mode
        elif self.active_corner is not None: 
            rect = self.rectangles[self.selected_rectangle_index]
            if self.active_corner == 0:  # top left
                rect['min_xy'] = event.pos()
            elif self.active_corner == 1:  # top right
                rect['min_xy'].setY(event.pos().y())
                rect['max_xy'].setX(event.pos().x())
            elif self.active_corner == 2:  # bottom left
                rect['min_xy'].setX(event.pos().x())
                rect['max_xy'].setY(event.pos().y())
            else:  # bottom right
                rect['max_xy'] = event.pos()

        #relocation mode
        else:
            if self.selected_rectangle_index is None:
                return
            offset = event.pos() - self.last_pos
            logger.info(f"rectangle list: {self.rectangles}")
            logger.info(f"selected rectangle index: {self.selected_rectangle_index}")
            start, end = self.rectangles[self.selected_rectangle_index]['min_xy'], self.rectangles[self.selected_rectangle_index]['max_xy']
            self.rectangles[self.selected_rectangle_index]['min_xy'] = start + offset
            self.rectangles[self.selected_rectangle_index]['max_xy'] = end + offset

        self.last_pos = event.pos()
        self.update()


    def mouseReleaseEvent(self, event):
        logger.info(f"<==mouse release event function called==>")
        if self.drawing:
            self.drawing = False
            rect = {"min_xy":self.start_pos, "max_xy":self.end_pos, 'obj': '', 'id': '', 'attr': '', 'focus':False}
            rect = self.check_negative_box(rect)
            self.rectangles.append(rect)  # Store the rectangle's coordinates
            self.update()
            new_item_text = f"({rect['min_xy'].x()}, {rect['min_xy'].y()}, {rect['max_xy'].x() - rect['min_xy'].x()}, {rect['max_xy'].y() - rect['min_xy'].y()}), {rect['obj']}, {rect['id']}, {rect['attr']}"
            self.parent.bbox_list_widget.addItem(new_item_text)  # Update the list widget
        
        elif self.selected_rectangle_index is not None:
            rect = self.rectangles[self.selected_rectangle_index]
            logger.info(f"rect: {rect} at mouse release event")
            self.update()
            rect['focus'] = False
            new_item_text = f"({rect['min_xy'].x()}, {rect['min_xy'].y()}, {rect['max_xy'].x() - rect['min_xy'].x()}, {rect['max_xy'].y() - rect['min_xy'].y()}), {rect['obj']}, {rect['id']}, {rect['attr']}"
            self.parent.bbox_list_widget.item(self.selected_rectangle_index).setText(new_item_text)
        
            logger.info(f"annotations: {self.parent.video_annotations} (mouseReleaseEvent)")

        self.parent.btn_add_label.setChecked(False)


    def check_negative_box(self, rect):
        if rect['min_xy'].x() > rect['max_xy'].x() and rect['min_xy'].y() > rect['max_xy'].y():
            logger.info(f"trying to fix negative bounding box: {rect}")
            rect['min_xy'], rect['max_xy'] = rect['max_xy'], rect['min_xy']
            return rect
        
        elif rect['min_xy'].x() > rect['max_xy'].x() and rect['max_xy'].y() > rect['min_xy'].y():
            logger.info(f"trying to fix negative bounding box: {rect}")
            temp = rect['min_xy'].x()
            rect['min_xy'].setX(rect['max_xy'].x())
            rect['max_xy'].setX(temp)
            return rect
        
        elif rect['max_xy'].x() > rect['min_xy'].x() and rect['min_xy'].y() > rect['max_xy'].y():
            logger.info(f"trying to fix negative bounding box: {rect}")
            temp = rect['min_xy'].y()
            rect['min_xy'].setY(rect['max_xy'].y())
            rect['max_xy'].setY(temp)
            return rect
        
        else:
            return rect

    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        font = painter.font()
        font.setPointSize(14) #the size of text for id
        painter.setFont(font)
        for rect in self.rectangles:
            top_left = rect['min_xy']
            bottom_right = rect['max_xy']
            top_right = QPoint(bottom_right.x(), top_left.y())
            bottom_left = QPoint(top_left.x(), bottom_right.y())

            pen = QPen(QColor(135, 206, 235), 1)  #sky blue rgb code
            painter.setPen(pen)
            painter.setBrush(QColor(135, 206, 235))
            for corner in [top_left, top_right, bottom_left, bottom_right]:
                circle_radius = 5
                painter.drawEllipse(corner, circle_radius, circle_radius)

            pen = QPen(Qt.green, 1)
            if rect['focus']:
                pen = QPen(Qt.red, 2)

            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            if rect['id'] != '':  # Check if this rectangle has an ID
                # Calculate center x coordinate of the bounding box
                center_x = top_left.x() + ((bottom_right.x() - top_left.x()) / 2)
                # Draw the text at the top center of the bounding box
                painter.drawText(int(center_x - 5), int(top_left.y() - 5), f"id:{rect['id']}")  # The "-5" is for adjusting the position of the text
            painter.drawRect(QRect(top_left, bottom_right))
            
        painter.end()