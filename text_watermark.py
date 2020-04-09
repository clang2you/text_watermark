import Ui_mainform
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QWidget,QGraphicsPixmapItem,QGraphicsScene,QProgressBar,QLabel, QFileDialog
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap,QImage
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageQt
from configparser import ConfigParser
import datetime
import os
import sys

cfg = ConfigParser()
cfg.read('config.ini')

class MyMainForm(QMainWindow, Ui_mainform.Ui_MainWindow):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        global cfg
        super(MyMainForm, self).__init__(parent)
        self.colorDict = {"grey": (211,211,211), "black": (0,0,0), "white": (255, 255, 255)}
        self.setupUi(self)
        self.current_image_list= None
        self.fontSize = self.fontSizeSlideBar.value()
        self.text_content = self.textWatermarkContentsLineEdit.text()
        self.dateEdit.setDate(datetime.datetime.now())
        self.fontSizeSlideBar.valueChanged.connect(self.DisplayFontSizeSlideBarValue)
        self.fontSize = self.fontSizeSlideBar.value()
        self.fontSizeLineEdit.setText(str(self.fontSizeSlideBar.value()))
        self.textWatermarkContentsLineEdit.textChanged.connect(self.GetTextContent)
        self.previewBtn.clicked.connect(self.StartImageWorkingThread)
        self.thread = Worker(self.current_image_list,self)
        self.thread.finishSignal.connect(self.ShowImageOnGraphicsView)        
        self.progressBar = QProgressBar()
        self.statusBar().addPermanentWidget(self.progressBar)
        self.progressBar.setRange(0, 1)
        self.progressBar.hide()
        self.choiceImageFilesBtn.clicked.connect(self.ShowFileDialog)
        self.previewBtn.clicked.connect(self.StartPreview)
        self.addWatermarksBtn.clicked.connect(self.StartAddImageWatermarksAndSave)
        self.transparentRate = self.spinBox.value()
        self.spinBox.valueChanged.connect(self.ChangeTransparentRate)
        self.defaultCurrentDateCb.clicked.connect(self.SetDateEditEnable)
        self.textWatermarkContentsLineEdit.setText(cfg.get("CONFIG","Text"))
        self.spinBox.setValue(int(cfg.getint("CONFIG","TransparentRate")))
        self.defaultCurrentDateCb.setChecked(cfg.getboolean("CONFIG","DefaultToday"))
        self.SetDateEditEnable()
        self.fontSizeSlideBar.setValue(int(cfg.getint("CONFIG","FontSize")))
        self.realtimePreviewCb.setChecked(cfg.getboolean("CONFIG", "RealtimePreview"))
        self.radioBlack.clicked.connect(self.ChangeWaterMarkColor)
        self.radioWhite.clicked.connect(self.ChangeWaterMarkColor)
        self.radioGrey.clicked.connect(self.ChangeWaterMarkColor)
        self.dateEdit.dateChanged.connect(self.StartPreview)
        watermark_color = cfg.get("CONFIG", "Color")
        if watermark_color == "black":
            self.watermark_color = self.colorDict["black"]
            self.radioBlack.setChecked(True)
        elif watermark_color == "white":
            self.watermark_color = self.colorDict["white"]
            self.radioWhite.setChecked(True)
        else:
            self.watermark_color = self.colorDict["grey"]
            self.radioGrey.setChecked(True)
        if self.current_image_list  == None:
            # self.realtimePreviewCb.setEnabled(False)
            self.previewBtn.setEnabled(False)
            self.addWatermarksBtn.setEnabled(False)
    
    def ChangeWaterMarkColor(self):
        global cfg
        if self.radioBlack.isChecked():
            self.watermark_color = self.colorDict["black"]
            cfg.set("CONFIG", "Color", "black")
        elif self.radioWhite.isChecked():
            self.watermark_color = self.colorDict["white"]
            cfg.set("CONFIG", "Color", "white")
        else:
            self.watermark_color = self.colorDict["grey"]
            cfg.set("CONFIG", "Color", "grey")
        cfg.write(open("config.ini", "w"))
        self.thread.form = self
        self.StartPreview()

    def ChangeTransparentRate(self):
        global cfg
        self.transparentRate = self.spinBox.value()
        cfg.set("CONFIG", "TransparentRate", str(self.transparentRate))
        cfg.write(open("config.ini", "w"))
        self.thread.form = self
        self.StartPreview()
    
    def SetDateEditEnable(self):
        global cfg
        if self.defaultCurrentDateCb.isChecked():
            self.dateEdit.setEnabled(False)
            self.dateEdit.setDate(datetime.datetime.now())
        else:
            self.dateEdit.setEnabled(True)
        cfg.set("CONFIG", "DefaultToday", str(self.defaultCurrentDateCb.isChecked()))
        cfg.write(open("config.ini", "w"))

    def ShowFileDialog(self):
        self.current_image_list = QFileDialog.getOpenFileNames(self, '选择图片文件', "" , "JPG 文件 (*.jpg *.jpeg)")[0]
        if self.current_image_list != None and len(self.current_image_list) > 0:
            # self.realtimePreviewCb.setEnabled(True)
            self.previewBtn.setEnabled(True)
            self.addWatermarksBtn.setEnabled(True)
            self.thread.image_list = self.current_image_list
            print(self.current_image_list)
            self.save_image_path = os.path.abspath(os.path.dirname(self.current_image_list[0])) + "\\new\\"
            if self.realtimePreviewCb.isChecked():
                self.StartPreview()
        else:
            self.current_image_list = None
            # self.realtimePreviewCb.setEnabled(False)
            self.previewBtn.setEnabled(False)
            self.addWatermarksBtn.setEnabled(False)
            image_scene = QGraphicsScene()
            self.graphicsView.setScene(image_scene)
            # self.absFileName = os.path.basename(self.current_image_list[0])

    def ShowImageOnGraphicsView(self, count, pixmap, isPreview):
        pixmapItem = QGraphicsPixmapItem(pixmap)
        image_scene = QGraphicsScene()
        image_scene.addItem(pixmapItem)
        if isPreview == False:
            self.statusBar().showMessage("总计图片: {} 张,正在处理第 {} 张".format(len(self.current_image_list),count))
            self.progressBar.show()
            self.progressBar.setMaximum(len(self.current_image_list))
            self.progressBar.setValue(count)
        self.graphicsView.setScene(image_scene)
        self.graphicsView.fitInView(pixmapItem,QtCore.Qt.AspectRatioMode.KeepAspectRatio)  
        if len(self.current_image_list) == count:
            self.statusBar().showMessage("图片处理完成。")
            self.progressBar.hide()
            self.previewBtn.setEnabled(True)
            self.textWatermarkContentsLineEdit.setEnabled(True)
            self.fontSizeSlideBar.setEnabled(True)
            self.defaultCurrentDateCb.setEnabled(True)
            self.realtimePreviewCb.setEnabled(True)
            self.spinBox.setEnabled(True)
            self.radioGrey.setEnabled(True)
            self.radioBlack.setEnabled(True)
            self.radioWhite.setEnabled(True)
            self.addWatermarksBtn.setEnabled(True)

    def DisplayFontSizeSlideBarValue(self):
        global cfg
        self.fontSizeLineEdit.setText(str(self.fontSizeSlideBar.value()))
        self.fontSize = self.fontSizeSlideBar.value()
        cfg.set("CONFIG", "FontSize", str(self.fontSize))
        cfg.write(open("config.ini", "w"))
        self.thread.fontSize = self.fontSize
        self.StartPreview()
    
    def GetTextContent(self):
        self.text_content =  self.textWatermarkContentsLineEdit.text()
        cfg.set("CONFIG", "text", self.text_content)
        cfg.write(open("config.ini", "w"))
        self.thread.text_content = self.text_content
        self.StartPreview()
    
    def StartPreview(self):
        if self.realtimePreviewCb.isChecked() and self.current_image_list != None:
            self.statusBar().showMessage('')
            self.StartImageWorkingThread()
        elif self.realtimePreviewCb.isChecked():
            self.statusBar().showMessage("请先选择图片文件方可实时预览。")
    
    def StartImageWorkingThread(self):
        self.thread.isPreview = True
        self.thread.form = self
        self.thread.start()
    
    def StartAddImageWatermarksAndSave(self):
        self.thread.isPreview = False
        self.addWatermarksBtn.setEnabled(False)
        self.previewBtn.setEnabled(False)
        self.textWatermarkContentsLineEdit.setEnabled(False)
        self.fontSizeSlideBar.setEnabled(False)
        self.defaultCurrentDateCb.setEnabled(False)
        self.realtimePreviewCb.setEnabled(False)
        self.spinBox.setEnabled(False)
        self.radioGrey.setEnabled(False)
        self.radioBlack.setEnabled(False)
        self.radioWhite.setEnabled(False)
        self.thread.start()


class Worker(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(int,QPixmap, bool)
    def __init__(self, image_list, myWindow):
        super(Worker, self).__init__()
        self.form = myWindow
        self.image_list = image_list
        self.fontSize = myWindow.fontSize
        self.text_content = myWindow.text_content
        self.isPreview = True
        self.image_dimension = (myWindow.graphicsView.width(), myWindow.graphicsView.height())
    
    def run(self):
        if self.image_list != None:
            if len(self.image_list) > 0 and self.isPreview:
                self.AddTextWatermarkToImage(1, self.image_list[-1])
            elif len(self.image_list) > 0:
                for image_file in self.image_list:
                    print(image_file)
                    self.AddTextWatermarkToImage(self.image_list.index(image_file) + 1, image_file)

    def AddTextWatermarkToImage(self, count, image_path):
        if image_path != None:
            src = Image.open(image_path).convert('RGBA')
            text_overlay = Image.new("RGBA", src.size, (255, 255, 255, 0))
            image_draw = ImageDraw.Draw(text_overlay)

            ratio = src.size[0] / 1024
            font_size_ratio = self.fontSize / 55
            fontSize = int(55 * ratio * font_size_ratio)
            size_x_offset = int(5 * ratio * font_size_ratio)
            size_y_offset = int(8* ratio * font_size_ratio)
            fnt = ImageFont.truetype(r'C:\Windows\Fonts\arial.TTF',fontSize)
            color = self.form.watermark_color
            print(color)

            time_text = self.form.dateEdit.date().toPyDate().strftime("%Y/%m/%d")
            # image_draw.ink = 255 + 0 * 256 + 0 * 256 * 256 
            if self.text_content != '':
                text_size_x, text_size_y = image_draw.textsize(self.text_content, font=fnt)
                text_xy = (src.size[0] - (text_size_x + size_x_offset), src.size[1] - (text_size_y + size_y_offset))
                image_draw.text(text_xy, self.text_content, font=fnt, fill= (color[0],color[1],color[2],self.form.transparentRate))
                time_text_size = image_draw.textsize(time_text, font=fnt)
                time_text_x = src.size[0] - (time_text_size[0] + size_x_offset)
                time_y_offset = int(50 * ratio * font_size_ratio)
                time_text_xy = (time_text_x, text_xy[1] - time_y_offset)
                image_draw.text(time_text_xy, time_text, font=fnt, fill=(color[0],color[1],color[2],self.form.transparentRate))
                image_with_text = Image.alpha_composite(src,text_overlay)
            else:
                time_text_size = image_draw.textsize(time_text, font=fnt)
                time_text_x = src.size[0] - (time_text_size[0] + size_x_offset)
                time_text_xy = (time_text_x, src.size[1] - (time_text_size[1] + size_y_offset))
                image_draw.text(time_text_xy, time_text, font=fnt, fill=(color[0],color[1],color[2],self.form.transparentRate))
                image_with_text = Image.alpha_composite(src,text_overlay)
            
            if self.isPreview == False:
                if os.path.exists(self.form.save_image_path):
                    image_with_text.convert('RGB').save(self.form.save_image_path +  os.path.basename(image_path))
                else:
                    os.makedirs(self.form.save_image_path)
                    image_with_text.convert('RGB').save(self.form.save_image_path + os.path.basename(image_path))

            self.pil_image = ImageQt.ImageQt(image_with_text.convert('RGB'))
            pixmap = QPixmap.fromImage(self.pil_image)
            pixmap = pixmap.scaled(self.image_dimension[0], self.image_dimension[1],QtCore.Qt.AspectRatioMode.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
            self.finishSignal.emit(count, pixmap, self.isPreview)   


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywin = MyMainForm()
    mywin.show()
    sys.exit(app.exec_())