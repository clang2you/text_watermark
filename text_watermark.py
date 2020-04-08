import Ui_mainform
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QWidget,QGraphicsPixmapItem,QGraphicsScene
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap,QImage
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageQt
import datetime


class MyMainForm(QMainWindow, Ui_mainform.Ui_MainWindow):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.dateEdit.setDate(datetime.datetime.now())
        self.fontSizeSlideBar.valueChanged.connect(self.DisplayFontSizeSlideBarValue)
        self.fontSize = self.fontSizeSlideBar.value()
        self.fontSizeLineEdit.setText(str(self.fontSizeSlideBar.value()))
        # self.fileLabel.setText("")
        # self.imageLabel.setStyleSheet("border: 2px solid grey")
        # QtCore.QMetaObject.connectSlotsByName(self)
        # self.resized.connect(self.TestDisplayImage)
    
    # def resizeEvent(self, event):
    #     self.resized.emit()
    #     return super(MyMainForm, self).resizeEvent(event)

    def DisplayFontSizeSlideBarValue(self):
        self.fontSizeLineEdit.setText(str(self.fontSizeSlideBar.value()))
    
    def m_resize(self,w_box, h_box, pil_image):  # 参数是：要适应的窗口宽、高、Image.open后的图片
        w, h = pil_image.width(), pil_image.height() # 获取图像的原始大小
        f1 = 1.0*w_box/w
        f2 = 1.0 * h_box / h
        factor = min([f1, f2])  
        width = int(w * factor)
        height = int(h * factor)
        #return pil_image.resize(width, height)
        return pil_image.smoothScaled(width, height)
    
    def AddTextWatermarkToImage(self):
        src = Image.open('test.jpg').convert('RGBA')
        text_overlay = Image.new("RGBA", src.size, (255, 255, 255, 0))
        image_draw = ImageDraw.Draw(text_overlay)
        # image_draw.ink = 255 + 0 * 256 + 0 * 256 * 256 
        text = 'Fengtay LN3'
        # self.fontSize = 80
        ratio = src.size[0] / 1024
        font_size_ratio = self.fontSize / 55
        fontSize = int(55 * ratio * font_size_ratio)
        size_x_offset = int(5 * ratio * font_size_ratio)
        size_y_offset = int(5* ratio * font_size_ratio)
        fnt = ImageFont.truetype(r'C:\Windows\Fonts\arial.TTF',fontSize)
        text_size_x, text_size_y = image_draw.textsize(text, font=fnt)
        text_xy = (src.size[0] - (text_size_x + size_x_offset), src.size[1] - (text_size_y + size_y_offset))
        image_draw.text(text_xy, text, font=fnt, fill= (211,211,211,100))
        time_text = '2020/04/08'
        time_x_offset = int(40 * ratio * font_size_ratio)
        time_y_offset = int(50 * ratio * font_size_ratio)
        time_text_xy = (text_xy[0] + time_x_offset, text_xy[1] - time_y_offset)
        image_draw.text(time_text_xy, time_text, font=fnt, fill=(211,211,211,100))
        image_with_text = Image.alpha_composite(src,text_overlay)
        image_with_text.convert('RGB').save(r'C:\Users\Lex Chen\Desktop\test.jpg')

        self.pil_image = ImageQt.ImageQt(image_with_text.convert('RGB'))
        pixmap = QPixmap.fromImage(self.pil_image)
        pixmap = pixmap.scaled(self.graphicsView.width(), self.graphicsView.height(),QtCore.Qt.AspectRatioMode.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
        self.item = QGraphicsPixmapItem(pixmap)
        self.scene = QGraphicsScene()
        self.scene.addItem(self.item)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.fitInView(self.item,QtCore.Qt.AspectRatioMode.KeepAspectRatio)        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywin = MyMainForm()
    mywin.show()
    # mywin.TestDisplayImage()
    mywin.AddTextWatermarkToImage()
    sys.exit(app.exec_())