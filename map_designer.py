from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QImage, QPainter, QBrush, QPen, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QEvent
import sys
import math
import datetime

from prompt_toolkit.key_binding.bindings.named_commands import undo


class Window(QMainWindow):
	def __init__(self):
		super().__init__()

		top = 400
		left = 400
		width = 1200
		height = 500

		self.maximum_undo = 20

		self.obj_type = 'wall'
		self.obj_width = 10

		self.pix_per_meter = 10

		self.bgc = Qt.white

		self.shift_pressed = False

		icon = "icon.png"

		self.setGeometry(top, left, width, height)
		self.setWindowTitle("Map Designer")
		self.setWindowIcon(QIcon(icon))
		self.setFixedSize(width, height)

		self.hidden_obstacle_layer = QImage(1000, 500, QImage.Format_RGB32)
		self.hidden_obstacle_layer.fill(self.bgc)
		self.backup_hidden_obstacle = []
		self.backup_hidden_obstacle.append(self.hidden_obstacle_layer)
		self.temp_hidden_obstacle_layer = self.hidden_obstacle_layer

		self.hidden_railing_brush = QBrush(Qt.SolidPattern)
		self.hidden_railing_brush.setColor(Qt.red)
		self.hidden_wall_brush = QBrush(Qt.SolidPattern)
		self.hidden_wall_brush.setColor(Qt.black)
		self.hidden_pillar_brush = QBrush(Qt.SolidPattern)
		self.hidden_pillar_brush.setColor(Qt.green)
		self.hidden_counter_brush = QBrush(Qt.SolidPattern)
		self.hidden_counter_brush.setColor(Qt.blue)

		self.hidden_destination_layer = QImage(1000, 500, QImage.Format_RGB32)
		self.hidden_destination_layer.fill(self.bgc)
		self.backup_hidden_destination = []
		self.backup_hidden_destination.append(self.hidden_destination_layer)
		self.temp_hidden_destination_layer = self.hidden_destination_layer

		self.hidden_exit_brush = QBrush(Qt.SolidPattern)
		self.hidden_exit_brush.setColor(Qt.red)
		self.hidden_entry_brush = QBrush(Qt.SolidPattern)
		self.hidden_entry_brush.setColor(Qt.black)
		self.hidden_passage_brush = QBrush(Qt.SolidPattern)
		self.hidden_passage_brush.setColor(Qt.green)
		self.hidden_waiting_brush = QBrush(Qt.SolidPattern)
		self.hidden_waiting_brush.setColor(Qt.blue)

		self.hidden_pen = QPen()
		self.hidden_pen.setColor(self.bgc)


		self.left_layout = QHBoxLayout()
		self.left_zone = QWidget(self)
		self.left_zone.setLayout(self.left_layout)

		self.image = QImage(1000, 500, QImage.Format_RGB32)
		self.image.fill(self.bgc)

		self.image_label = QLabel(self)
		self.image_label.setGeometry(0, 0, 1000, 500)
		self.image_label.setPixmap(QPixmap.fromImage(self.image))

		self.left_layout.addWidget(self.image_label)
		self.left_layout.setSpacing(0)
		self.left_layout.setContentsMargins(0, 0, 0, 0)
		self.left_layout.setStretch(0, 0)
		self.left_layout.setGeometry(QRect(QPoint(0, 0), QPoint(1000, 500)))

		self.splitter = QSplitter(self)
		self.splitter.setOrientation(Qt.Horizontal)
		self.splitter.setContentsMargins(0, 0, 0, 0)
		self.splitter.setFixedSize(1200, 500)
		self.splitter.setHandleWidth(0)
		self.splitter.addWidget(self.left_zone)

		self.backup_image = []
		self.backup_image.append(self.image)

		self.draw_record = []

		self.temp_image = QImage(1000, 500, QImage.Format_RGB32)
		self.temp_image.fill(self.bgc)

		self.drawing = False


		self.lastPoint = QPoint()


		# mainMenu = self.menuBar()
		# mainMenu.setNativeMenuBar(False)
		# fileMenu = mainMenu.addMenu("File")
		# brushMenu = mainMenu.addMenu("Brush Size")
		# brushColor = mainMenu.addMenu("Brush Color")
		#
		# saveAction = QAction("Save", self)
		# saveAction.setShortcut("Ctrl+S")
		# fileMenu.addAction(saveAction)
		#
		# clearAction = QAction("Clear", self)
		# clearAction.setShortcut("Ctrl+C")
		# fileMenu.addAction(clearAction)
		#
		# px3Action = QAction("3px", self)
		# px3Action.setShortcut("Ctrl+3")
		# brushMenu.addAction(px3Action)
		#
		# px5Action = QAction("5px", self)
		# px5Action.setShortcut("Ctrl+5")
		# brushMenu.addAction(px5Action)
		#
		# px9Action = QAction("9px", self)
		# px9Action.setShortcut("Ctrl+9")
		# brushMenu.addAction(px5Action)
		#
		# blackAction = QAction("Black", self)
		# blackAction.setShortcut("Ctrl+B")
		# brushColor.addAction(blackAction)
		#
		# whiteAction = QAction("White", self)
		# whiteAction.setShortcut("Ctrl+W")
		# brushColor.addAction(whiteAction)


		# #按钮控件
		#
		# self.btn_obstacle = QPushButton(self)
		# self.btn_obstacle.setGeometry(1020, 40, 20, 20)
		# self.btn_obstacle.setText("■")
		# self.btn_obstacle.setStyleSheet("QPushButton{color: black; padding-bottom: 2px;}"
		# 								"QPushButton:hover{background-color: darkgrey}")
		#
		# self.btn_dest = QPushButton(self)
		# self.btn_dest.setGeometry(1020, 80, 20, 20)
		# self.btn_dest.setText("■")
		# self.btn_dest.setStyleSheet("color: green; padding-bottom: 2px")

		#绘制选项
		self.right_layout = QVBoxLayout()
		self.right_zone = QWidget(self)
		self.right_zone.setLayout(self.right_layout)
		self.splitter.addWidget(self.right_zone)
		#self.right_layout.addWidget(self.image_label)

		#0.坐标显示区
		self.right_layout.addStretch()
		self.coordinates_label = QLabel(self)
		self.coordinates_label.setText("当前坐标(m): ")
		self.coordinates_label.setFont(QFont("Noto Sans CJK SC"))
		self.right_layout.addWidget(self.coordinates_label)

		self.coordinates_disp= QLabel(self)
		self.coordinates_disp.setText("坐标： x =  0.0, \ty =  0.0")
		self.coordinates_disp.setFont(QFont("Noto Sans CJK SC"))
		self.right_layout.addWidget(self.coordinates_disp)

		#1. 绘制障碍物标题
		self.right_layout.addStretch()
		self.obstacle_label = QLabel(self)
		self.obstacle_label.setText("绘制障碍物: ")
		self.obstacle_label.setFont(QFont("Noto Sans CJK SC"))
		#self.obstacle_label.setGeometry(1010, 40, 100, 30)
		self.right_layout.addWidget(self.obstacle_label)

		self.obstacle_pen = QPen(Qt.SolidLine)
		self.obstacle_pen.setColor(Qt.black)

		#1.1 绘制护栏
		#1.1.1 护栏选择框
		self.select_railing = QRadioButton(self)
		self.select_railing.setText("护栏. ")
		self.select_railing.setFont(QFont("Noto Sans CJK SC"))
		self.select_railing.toggled.connect(self.drawTypeChange)
		self.right_layout.addWidget(self.select_railing)
		#self.select_railing.setGeometry(1030, 65, 60, 30)
		#1.1.2 护栏笔刷
		self.railing_brush = QBrush(Qt.BDiagPattern)
		self.railing_brush.setColor(Qt.darkGray)
		self.railing_width = 0.5

		# 1.2.1 墙体选择框
		self.wall_box = QHBoxLayout()
		self.select_wall= QRadioButton(self)
		self.select_wall.setText("墙体, ")
		self.select_wall.setFont(QFont("Noto Sans CJK SC"))
		self.select_wall.toggled.connect(self.drawTypeChange)
		#self.select_wall.setGeometry(1030, 90, 60, 30)
		self.wall_box.addWidget(self.select_wall)
		# 1.2.2 墙体笔刷
		self.wall_brush = QBrush(Qt.Dense6Pattern)
		self.wall_brush.setColor(Qt.darkGray)
		self.wall_width = 1
		#1.2.3 墙体宽度标签
		self.wall_width_label = QLabel(self)
		self.wall_width_label.setText("宽度(m): ")
		self.wall_width_label.setFont(QFont("Noto Sans CJK SC"))
		#self.wall_width_label.setGeometry(1090, 90, 60, 30)
		self.wall_box.addWidget(self.wall_width_label)
		# 1.2.3 墙体宽度输入框
		self.wall_width_input = QLineEdit(self)
		self.wall_width_input.setText("1")
		#self.wall_width_input.setGeometry(1140, 95, 30, 20)
		self.wall_width_input.setAlignment(Qt.AlignRight)
		self.wall_box.addWidget(self.wall_width_input)
		self.wall_width_input.textChanged.connect(self.widthChange)

		self.right_layout.addLayout(self.wall_box)

		# 1.3.1 立柱选择框
		self.pillar_box = QHBoxLayout()
		self.select_pillar = QRadioButton(self)
		self.select_pillar.setText("立柱, ")
		self.select_pillar.setFont(QFont("Noto Sans CJK SC"))
		self.select_pillar.toggled.connect(self.drawTypeChange)
		#self.select_pillar.setGeometry(1030, 90, 60, 30)
		self.pillar_box.addWidget(self.select_pillar)
		# 1.3.2 立柱笔刷
		self.pillar_brush = QBrush(Qt.Dense4Pattern)
		self.pillar_brush.setColor(Qt.darkGray)
		self.pillar_width = 1
		# 1.3.3 立柱宽度标签
		self.pillar_width_label = QLabel(self)
		self.pillar_width_label.setText("宽度(m): ")
		self.pillar_width_label.setFont(QFont("Noto Sans CJK SC"))
		# self.wall_width_label.setGeometry(1090, 90, 60, 30)
		self.pillar_box.addWidget(self.pillar_width_label)
		# 1.3.3 立柱宽度输入框
		self.pillar_width_input = QLineEdit(self)
		self.pillar_width_input.setText("1")
		# self.wall_width_input.setGeometry(1140, 95, 30, 20)
		self.pillar_width_input.setAlignment(Qt.AlignRight)
		self.pillar_box.addWidget(self.pillar_width_input)
		self.pillar_width_input.textChanged.connect(self.widthChange)

		self.right_layout.addLayout(self.pillar_box)

		# 1.4.1 柜台选择框
		#self.counter_box = QHBoxLayout()
		self.select_counter = QRadioButton(self)
		self.select_counter.setText("柜台. ")
		self.select_counter.setFont(QFont("Noto Sans CJK SC"))
		self.select_counter.toggled.connect(self.drawTypeChange)
		#self.select_counter.setGeometry(1030, 90, 60, 30)
		self.right_layout.addWidget(self.select_counter)
		#self.counter_box.addWidget(self.select_counter)
		# 1.4.2 柜台笔刷
		self.counter_brush = QBrush(Qt.HorPattern)
		self.counter_brush.setColor(Qt.darkGray)
		self.counter_width = 1
		# # 1.4.3 柜台宽度标签
		# self.counter_width_label = QLabel(self)
		# self.counter_width_label.setText("宽度(m): ")
		# self.counter_width_label.setFont(QFont("Noto Sans CJK SC"))
		# # self.wall_width_label.setGeometry(1090, 90, 60, 30)
		# self.counter_box.addWidget(self.counter_width_label)
		# # 1.4.3 柜台宽度输入框
		# self.counter_width_input = QLineEdit(self)
		# self.counter_width_input.setText("1")
		# # self.wall_width_input.setGeometry(1140, 95, 30, 20)
		# self.counter_width_input.setAlignment(Qt.AlignRight)
		# self.counter_box.addWidget(self.counter_width_input)
		# self.counter_width_input.textChanged.connect(self.widthChange)

		#self.right_layout.addLayout(self.counter_box)

		# 2. 绘制障碍物标题
		self.right_layout.addStretch()
		self.destination_label = QLabel(self)
		self.destination_label.setText("绘制出入口及休息区: ")
		self.destination_label.setFont(QFont("Noto Sans CJK SC"))
		# self.obstacle_label.setGeometry(1010, 40, 100, 30)
		self.right_layout.addWidget(self.destination_label)

		self.destination_pen = QPen(Qt.DashDotDotLine)
		self.destination_pen.setColor(Qt.lightGray)

		# 2.1 绘制出口
		# 2.1.1 出口选择框
		self.select_exit = QRadioButton(self)
		self.select_exit.setText("出口. ")
		self.select_exit.setFont(QFont("Noto Sans CJK SC"))
		self.select_exit.toggled.connect(self.drawTypeChange)
		self.right_layout.addWidget(self.select_exit)
		# self.select_railing.setGeometry(1030, 65, 60, 30)
		# 2.1.2 出口笔刷
		self.exit_brush = QBrush(Qt.BDiagPattern)
		color = QColor(0, 255, 0, 130)
		self.exit_brush.setColor(color)
		self.exit_width = 2

		# 2.2 绘制入口
		# 2.2.1 入口选择框
		self.select_entry = QRadioButton(self)
		self.select_entry.setText("入口. ")
		self.select_entry.setFont(QFont("Noto Sans CJK SC"))
		self.select_entry.toggled.connect(self.drawTypeChange)
		self.right_layout.addWidget(self.select_entry)
		# self.select_railing.setGeometry(1030, 65, 60, 30)
		# 2.2.2 入口笔刷
		self.entry_brush = QBrush(Qt.DiagCrossPattern)
		color = QColor(0, 255, 0, 130)
		self.entry_brush.setColor(color)
		self.entry_width = 2

		# 2.3 绘制出入口
		# 2.3.1 出入口选择框
		self.select_passage = QRadioButton(self)
		self.select_passage.setText("出入口. ")
		self.select_passage.setFont(QFont("Noto Sans CJK SC"))
		self.select_passage.toggled.connect(self.drawTypeChange)
		self.right_layout.addWidget(self.select_passage)
		# self.select_railing.setGeometry(1030, 65, 60, 30)
		# 2.3.2 出入口笔刷
		self.passage_brush = QBrush(Qt.Dense6Pattern)
		color = QColor(0, 255, 0, 120)
		self.passage_brush.setColor(color)
		self.passage_width = 2

		# 2.4 绘制休息区
		# 2.4.1 休息区选择框
		self.select_waiting = QRadioButton(self)
		self.select_waiting.setText("休息区. ")
		self.select_waiting.setFont(QFont("Noto Sans CJK SC"))
		self.select_waiting.toggled.connect(self.drawTypeChange)
		self.right_layout.addWidget(self.select_waiting)
		# self.select_railing.setGeometry(1030, 65, 60, 30)
		# 2.4.2 休息区笔刷
		self.waiting_brush = QBrush(Qt.SolidPattern)
		color = QColor(0, 255, 0, 25)
		self.waiting_brush.setColor(color)

		self.right_layout.addStretch()

		# 3. 保存图片按键
		self.save_button = QPushButton(self)
		self.save_button.setText("保存地图")
		self.save_button.setFont(QFont("Noto Sans CJK SC"))
		self.save_button.clicked.connect(self.saveMap)
		self.right_layout.addWidget(self.save_button)

		self.right_layout.addStretch()
		self.right_layout.addStretch()
		self.right_layout.addStretch()

		self.brush = self.railing_brush
		self.pen = self.obstacle_pen
		self.draw_type = "railing"
		self.width = self.railing_width

		self.setCentralWidget(self.splitter)

		self.setCentralWidget(self.splitter)

		self.splitter.setMouseTracking(True)
		self.setMouseTracking(True)
		self.image_label.setMouseTracking(True)
		self.image_label.installEventFilter(self)

		self.select_railing.setChecked(True)

		self.update()

	def saveMap(self):
		timenow = datetime.datetime.now()
		timestamp = datetime.datetime.strftime(timenow, '%Y-%m-%d_%H_%M_%S')

		filename = "./Maps/map_" +timestamp

		print(filename)
		pixmap = QPixmap.fromImage(self.image)
		pixmap.save(filename + "_map.bmp")

		pixmap1 = QPixmap.fromImage(self.hidden_obstacle_layer)
		pixmap1.save(filename + "_obs.bmp")

		pixmap2 = QPixmap.fromImage(self.hidden_destination_layer)
		pixmap2.save(filename + "_des.bmp")


	def widthChange(self):
		self.wall_width = int(self.wall_width_input.text())
		self.pillar_width = int(self.pillar_width_input.text())


	def drawTypeChange(self):
		if self.select_railing.isChecked():
			#print("railing")
			self.brush = self.railing_brush
			self.draw_type = "railing"
			self.width = self.railing_width
			self.pen = self.obstacle_pen
		elif self.select_wall.isChecked():
			#print("wall")
			self.brush = self.wall_brush
			self.draw_type = "wall"
			self.width = self.wall_width
			self.pen = self.obstacle_pen
		elif self.select_pillar.isChecked():
			#print("pillar")
			self.brush = self.pillar_brush
			self.draw_type = "pillar"
			self.width = self.pillar_width
			self.pen = self.obstacle_pen
		elif self.select_counter.isChecked():
			#print("counter")
			self.brush = self.counter_brush
			self.draw_type = "counter"
			self.width = self.counter_width
			self.pen = self.obstacle_pen
		elif self.select_exit.isChecked():
			# print("exit")
			self.brush = self.exit_brush
			self.draw_type = "exit"
			self.width = self.exit_width
			self.pen = self.destination_pen
		elif self.select_entry.isChecked():
			# print("entry")
			self.brush = self.entry_brush
			self.draw_type = "entry"
			self.width = self.entry_width
			self.pen = self.destination_pen
		elif self.select_passage.isChecked():
			# print("passage")
			self.brush = self.passage_brush
			self.draw_type = "passage"
			self.width = self.passage_width
			self.pen = self.destination_pen
		elif self.select_waiting.isChecked():
			# print("waiting")
			self.brush = self.waiting_brush
			self.draw_type = "waiting"
			self.pen = self.destination_pen

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.drawing = True
			self.startPoint = event.pos()
			self.lastPoint = event.pos()
			self.temp_image = self.image.copy()

			if self.draw_type == "railing" or self.draw_type == "wall" or self.draw_type == "pillar" or self.draw_type == "counter":
				self.temp_hidden_obstacle_layer = self.hidden_obstacle_layer.copy()
			else:
				self.temp_hidden_destination_layer = self.hidden_destination_layer.copy()

			self.draw_record.insert(0, self.draw_type)
			if self.draw_record.__len__() > self.maximum_undo + 2:
				self.draw_record.pop()

			#print(self.startPoint)
			if self.draw_type == "pillar":
				self.image = self.temp_image.copy()
				painter = QPainter(self.image)
				painter.setPen(self.obstacle_pen)
				painter.setBrush(self.pillar_brush)
				start = QPoint(self.startPoint.x()-(self.pillar_width*self.pix_per_meter)/2-1, self.startPoint.y()-(self.pillar_width*self.pix_per_meter)/2-1)
				end = QPoint(self.startPoint.x()+(self.pillar_width*self.pix_per_meter)/2-1, self.startPoint.y()+(self.pillar_width*self.pix_per_meter)/2-1)
				rect = QRect(start, end)
				painter.drawEllipse(rect)

				self.backup_image.insert(0, self.image)
				if self.backup_image.__len__() > self.maximum_undo + 2:
					self.backup_image.pop()

				##
				self.hidden_obstacle_layer = self.temp_hidden_obstacle_layer.copy()
				painter1 = QPainter(self.hidden_obstacle_layer)
				painter1.setPen(self.hidden_pen)
				painter1.setBrush(self.hidden_pillar_brush)
				painter1.drawEllipse(rect)

				self.backup_hidden_obstacle.insert(0, self.hidden_obstacle_layer)
				if self.backup_hidden_obstacle.__len__() > self.maximum_undo + 2:
					self.backup_hidden_obstacle.pop()

				self.drawing = False
				self.update()

	def eventFilter(self, Object, event):
		if event.type() == QEvent.MouseMove:
			x = event.x()
			y = event.y()
			if 0 <= x < 1000 and 0 <= y < 500:
				x = x / 10.0
				y = y / 10.0
				message = "坐标： x = " + str(float('%.1f' % x)) + ", \ty = " + str(float('%.1f' % y))
				self.coordinates_disp.setText(message)
		return QWidget.eventFilter(self, Object, event)

	def mouseMoveEvent(self, event):
		# x = event.x()
		# y = event.y()
		# #if 0 <= x < 1000 and 0 <= y < 500:
		# x = x / 10.0
		# y = y / 10.0
		# message = "坐标： x = " + str(float('%.1f' % x)) + ", y = " + str(float('%.1f' % y))
		# self.coordinates_disp.setText(message)

		if (event.buttons() and Qt.LeftButton) and self.drawing:
			self.lastPoint = event.pos()

			self.image = self.temp_image.copy()
			painter = QPainter(self.image)
			painter.setBrush(self.brush)
			painter.setPen(self.pen)

			if self.draw_type == "railing" or self.draw_type == "wall" or self.draw_type == "pillar" or self.draw_type == "counter":
				self.hidden_obstacle_layer = self.temp_hidden_obstacle_layer.copy()
				painter1 = QPainter(self.hidden_obstacle_layer)
				if self.draw_type == "railing":
					painter1.setBrush(self.hidden_railing_brush)
				elif self.draw_type == "wall":
					painter1.setBrush(self.hidden_wall_brush)
				elif self.draw_type == "pillar":
					painter1.setBrush(self.hidden_pillar_brush)
				elif self.draw_type == "counter":
					painter1.setBrush(self.hidden_counter_brush)
				painter1.setPen(self.hidden_pen)
			else:
				self.hidden_destination_layer = self.temp_hidden_destination_layer.copy()
				painter1 = QPainter(self.hidden_destination_layer)
				if self.draw_type == "exit":
					painter1.setBrush(self.hidden_exit_brush)
				elif self.draw_type == "entry":
					painter1.setBrush(self.hidden_entry_brush)
				elif self.draw_type == "passage":
					painter1.setBrush(self.hidden_passage_brush)
				elif self.draw_type == "waiting":
					painter1.setBrush(self.hidden_waiting_brush)
				painter1.setPen(self.hidden_pen)

			w = self.width * self.pix_per_meter

			startx = self.startPoint.x()
			starty = self.startPoint.y()
			endx = self.lastPoint.x()
			endy = self.lastPoint.y()

			if self.shift_pressed == False and self.draw_type != "waiting":
				degree, length = self.get_degree(self.startPoint, self.lastPoint)

				painter.translate(self.startPoint)
				painter.rotate(degree)

				painter1.translate(self.startPoint)
				painter1.rotate(degree)

				start = QPoint(0, 0)
				end = QPoint(length, w)

				# if self.draw_type == "counter":
				# 	if abs(starty - endy) >= abs(startx - endx):
				# 		print("no shift, ver pattern")
				# 		temp_brush = self.brush
				# 		temp_brush.setStyle(Qt.HorPattern)
				# 		painter.setBrush(temp_brush)
				# 	else:
				# 		print("no shift, hor pattern")
				# 		temp_brush = self.brush
				# 		temp_brush.setStyle(Qt.HorPattern)
				# 		painter.setBrush(temp_brush)

				painter.drawRect(QRect(start, end))
				painter1.drawRect(QRect(start, end))

			elif self.shift_pressed == True and self.draw_type != "waiting":
				if abs(starty - endy) >= abs(startx - endx):
					if self.draw_type == "counter":
						temp_brush = self.brush
						temp_brush.setStyle(Qt.VerPattern)
						painter.setBrush(temp_brush)

					if startx < endx:
						painter.drawRect(QRect(QPoint(startx, starty), QPoint(startx + w, endy)))
						painter1.drawRect(QRect(QPoint(startx, starty), QPoint(startx + w, endy)))
					else:
						painter.drawRect(QRect(QPoint(startx, starty), QPoint(startx - w - 2, endy)))
						painter1.drawRect(QRect(QPoint(startx, starty), QPoint(startx - w - 2, endy)))
				else:
					if self.draw_type == "counter":
						temp_brush = self.brush
						temp_brush.setStyle(Qt.HorPattern)
						painter.setBrush(temp_brush)

					if starty < endy:
						painter.drawRect(QRect(QPoint(startx, starty), QPoint(endx, starty + w)))
						painter1.drawRect(QRect(QPoint(startx, starty), QPoint(endx, starty + w)))
					else:
						painter.drawRect(QRect(QPoint(startx, starty), QPoint(endx, starty - w - 2)))
						painter1.drawRect(QRect(QPoint(startx, starty), QPoint(endx, starty - w - 2)))
			else:
				painter.drawRect(QRect(self.startPoint, self.lastPoint))
				painter1.drawRect(QRect(self.startPoint, self.lastPoint))

	def get_degree(self,start, end):
		startx = start.x()
		starty = start.y()
		endx = end.x()
		endy = end.y()

		if endx >= startx:
			if endx == startx:
				if endy > starty:
					degree = 90
				else:
					degree = 270
			else:
				degree = math.atan((endy - starty + 0.0) / (endx - startx + 0.0))
				degree = (degree / 3.14) * 180
		else:
			degree = math.atan((endy - starty + 0.0) / (startx - endx + 0.0))
			degree = (degree / 3.14) * 180
			degree = 180 - degree

		length = math.sqrt((startx - endx) * (startx - endx) + (starty - endy) * (starty - endy))
		return degree, length

	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton :
			if self.draw_type != "pillar":
				self.drawing = False
				self.backup_image.insert(0, self.image)
				if self.backup_image.__len__() > self.maximum_undo + 2:
					self.backup_image.pop()

				if self.draw_type == "railing" or self.draw_type == "wall" or self.draw_type == "pillar" or self.draw_type == "counter":
					self.backup_hidden_obstacle.insert(0, self.hidden_obstacle_layer)
					if self.backup_hidden_obstacle.__len__() > self.maximum_undo + 2:
						self.backup_hidden_obstacle.pop()
				else:
					self.backup_hidden_destination.insert(0, self.hidden_destination_layer)
					if self.backup_hidden_destination.__len__() > self.maximum_undo + 2:
						self.backup_hidden_destination.pop()

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Z:
			self.undo()
		elif event.modifiers() == Qt.ShiftModifier:
			self.shift_pressed = True
		elif event.key() == Qt.Key_1:
			self.wall_width_input.setText("1")
			self.wall_width = 1
			self.pillar_width_input.setText("1")
			self.pillar_width = 1
		elif event.key() == Qt.Key_2:
			self.wall_width_input.setText("2")
			self.wall_width = 2
			self.pillar_width_input.setText("2")
			self.pillar_width = 2
		elif event.key() == Qt.Key_3:
			self.wall_width_input.setText("3")
			self.wall_width = 3
			self.pillar_width_input.setText("3")
			self.pillar_width = 3
		elif event.key() == Qt.Key_4:
			self.wall_width_input.setText("4")
			self.wall_width = 4
			self.pillar_width_input.setText("4")
			self.pillar_width = 4
		elif event.key() == Qt.Key_5:
			self.wall_width_input.setText("5")
			self.wall_width = 5
			self.pillar_width_input.setText("5")
			self.pillar_width = 5
		elif event.key() == Qt.Key_6:
			self.wall_width_input.setText("6")
			self.wall_width = 6
			self.pillar_width_input.setText("6")
			self.pillar_width = 6
		elif event.key() == Qt.Key_7:
			self.wall_width_input.setText("7")
			self.wall_width = 7
			self.pillar_width_input.setText("7")
			self.pillar_width = 7
		elif event.key() == Qt.Key_8:
			self.wall_width_input.setText("8")
			self.wall_width = 8
			self.pillar_width_input.setText("8")
			self.pillar_width = 8
		elif event.key() == Qt.Key_9:
			self.wall_width_input.setText("9")
			self.wall_width = 9
			self.pillar_width_input.setText("9")
			self.pillar_width = 9
		elif event.key() == Qt.Key_0:
			self.wall_width_input.setText("10")
			self.wall_width = 10
			self.pillar_width_input.setText("10")
			self.pillar_width = 10
		self.drawTypeChange()

	def undo(self):
		if self.backup_image.__len__() > 1:
			#print(self.backup_image.__len__())
			self.image = self.backup_image[1]
			self.backup_image.pop(0)
			self.update()
		if self.draw_record[0] == "railing" or self.draw_record[0] == "wall" or self.draw_record[0] == "pillar" or self.draw_record[0] == "counter":
			if self.backup_hidden_obstacle.__len__() > 1:
				print(self.backup_hidden_obstacle.__len__())
				self.hidden_obstacle_layer = self.backup_hidden_obstacle[1]
				self.backup_hidden_obstacle.pop(0)
				self.update()
		else:
			if self.backup_hidden_destination.__len__() > 1:
				print(self.backup_hidden_destination.__len__())
				self.hidden_destination_layer = self.backup_hidden_destination[1]
				self.backup_hidden_destination.pop(0)
				self.update()
		self.draw_record.pop(0)

	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Shift:
			self.shift_pressed = False

	def paintEvent(self, event):
		self.image_label.setPixmap(QPixmap.fromImage(self.image))

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = Window()
	window.show()
	app.exec()
