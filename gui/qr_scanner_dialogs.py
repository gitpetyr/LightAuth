import sys
import cv2
from typing import List, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QComboBox, QMessageBox, QFileDialog, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QGuiApplication
from PIL import Image
import numpy as np

from utils.qr_utils import decode_qr_from_image


class CameraScanDialog(QDialog):
    """相机扫描对话框，允许选择相机并扫描其中的二维码"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("相机扫描二维码")
        self.cap = None
        self.timer = None
        self.detected_codes: List[str] = []
        self.selected_data: Optional[str] = None

        self.init_ui()
        self.enumerate_cameras()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 相机选择
        combo_layout = QHBoxLayout()
        self.camera_combo = QComboBox()
        combo_layout.addWidget(QLabel("选择相机:"))
        combo_layout.addWidget(self.camera_combo)
        self.open_btn = QPushButton("开始扫描")
        self.open_btn.clicked.connect(self.start_scanning)
        combo_layout.addWidget(self.open_btn)
        layout.addLayout(combo_layout)

        # 预览区域
        self.video_label = QLabel("无视频信号")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setFixedHeight(240)
        layout.addWidget(self.video_label)

        # 结果列表
        self.codes_list = QListWidget()
        layout.addWidget(self.codes_list)
        self.codes_list.itemDoubleClicked.connect(self.finish_selection)

        # 确定/取消
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.finish_selection)
        self.ok_btn.setEnabled(False)
        btn_layout.addWidget(self.ok_btn)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def enumerate_cameras(self):
        """尝试检测前几个索引的相机"""
        self.camera_combo.clear()
        for idx in range(5):  # 测试前5个索引
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)  # CAP_DSHOW提升在Windows中的速度
            if cap and cap.isOpened():
                self.camera_combo.addItem(f"相机 {idx}", idx)
                cap.release()
        if self.camera_combo.count() == 0:
            self.camera_combo.addItem("无可用相机", -1)
            self.open_btn.setEnabled(False)

    def start_scanning(self):
        cam_idx = self.camera_combo.currentData()
        if cam_idx is None or cam_idx == -1:
            QMessageBox.warning(self, "警告", "未选择有效的相机")
            return

        # 打开摄像头
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(int(cam_idx), cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "错误", "无法打开该相机")
            return

        # 创建定时器读取帧
        if not self.timer:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.open_btn.setEnabled(False)

    def update_frame(self):
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            return

        # 检测二维码
        decoded_list = []
        try:
            decoded = decode_qr_from_image(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            decoded_list = [d[0] for d in decoded]
        except Exception:
            pass

        if decoded_list and decoded_list != self.detected_codes:
            self.detected_codes = decoded_list
            self.populate_codes(decoded_list)

        # 显示视频
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg).scaled(
            self.video_label.width(), self.video_label.height(), Qt.AspectRatioMode.KeepAspectRatio))

    def populate_codes(self, codes: List[str]):
        self.codes_list.clear()
        for c in codes:
            item = QListWidgetItem(c)
            self.codes_list.addItem(item)
        self.ok_btn.setEnabled(bool(codes))

    def finish_selection(self, *args):
        current_item = self.codes_list.currentItem()
        if current_item is None:
            return
        self.selected_data = current_item.text()
        self.accept()

    def get_selected_data(self):
        return self.selected_data

    def closeEvent(self, event):
        if self.timer and self.timer.isActive():
            self.timer.stop()
        if self.cap:
            self.cap.release()
        super().closeEvent(event)


class ScreenScanDialog(QDialog):
    """屏幕扫描对话框，可选择屏幕并扫描二维码"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("屏幕扫描二维码")
        self.selected_data: Optional[str] = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        screen_layout = QHBoxLayout()
        screen_layout.addWidget(QLabel("选择屏幕:"))
        self.screen_combo = QComboBox()
        for idx, s in enumerate(QGuiApplication.screens()):
            self.screen_combo.addItem(f"屏幕 {idx + 1} ({s.name()})", idx)
        screen_layout.addWidget(self.screen_combo)
        self.scan_btn = QPushButton("扫描")
        self.scan_btn.clicked.connect(self.scan_screen)
        screen_layout.addWidget(self.scan_btn)
        layout.addLayout(screen_layout)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedHeight(240)
        layout.addWidget(self.image_label)

        self.codes_list = QListWidget()
        layout.addWidget(self.codes_list)
        self.codes_list.itemDoubleClicked.connect(self.finish_selection)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.finish_selection)
        self.ok_btn.setEnabled(False)
        btn_layout.addWidget(self.ok_btn)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def scan_screen(self):
        idx = self.screen_combo.currentData()
        screens = QGuiApplication.screens()
        if idx is None or idx >= len(screens):
            QMessageBox.warning(self, "警告", "屏幕选择无效")
            return
        pixmap = screens[idx].grabWindow(0)
        if pixmap.isNull():
            QMessageBox.critical(self, "错误", "无法抓取屏幕图像")
            return

        # 显示截图
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.width(), self.image_label.height(), Qt.AspectRatioMode.KeepAspectRatio))

        # 将 QPixmap 转换为 PIL.Image
        qimage = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        # PyQt6 的 sip.voidptr 支持 setsize，直接使用 buffer
        ptr.setsize(width * height * 4)
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4))
        pil_img = Image.fromarray(arr, 'RGBA')

        decoded = decode_qr_from_image(pil_img)
        codes = [d[0] for d in decoded]
        self.populate_codes(codes)

    def populate_codes(self, codes: List[str]):
        self.codes_list.clear()
        for c in codes:
            self.codes_list.addItem(QListWidgetItem(c))
        self.ok_btn.setEnabled(bool(codes))
        if not codes:
            QMessageBox.information(self, "提示", "未在屏幕上检测到二维码")

    def finish_selection(self, *args):
        item = self.codes_list.currentItem()
        if not item:
            return
        self.selected_data = item.text()
        self.accept()

    def get_selected_data(self):
        return self.selected_data


class ImageScanDialog(QDialog):
    """图片扫描二维码对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图片扫描二维码")
        self.selected_data: Optional[str] = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        browse_btn = QPushButton("选择图片文件 (jpg/png/jpeg)")
        browse_btn.clicked.connect(self.open_file)
        layout.addWidget(browse_btn)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedHeight(240)
        layout.addWidget(self.image_label)

        self.codes_list = QListWidget()
        layout.addWidget(self.codes_list)
        self.codes_list.itemDoubleClicked.connect(self.finish_selection)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.finish_selection)
        self.ok_btn.setEnabled(False)
        btn_layout.addWidget(self.ok_btn)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图像文件 (*.jpg *.jpeg *.png)"
        )
        if not file_path:
            return
        try:
            pil_img = Image.open(file_path)
            # 显示预览
            qimg = QPixmap(file_path)
            self.image_label.setPixmap(qimg.scaled(self.image_label.width(), self.image_label.height(), Qt.AspectRatioMode.KeepAspectRatio))

            decoded = decode_qr_from_image(pil_img)
            codes = [d[0] for d in decoded]
            self.populate_codes(codes)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开图片: {str(e)}")

    def populate_codes(self, codes: List[str]):
        self.codes_list.clear()
        for c in codes:
            self.codes_list.addItem(QListWidgetItem(c))
        self.ok_btn.setEnabled(bool(codes))
        if not codes:
            QMessageBox.information(self, "提示", "未在图片中检测到二维码")

    def finish_selection(self, *args):
        item = self.codes_list.currentItem()
        if item:
            self.selected_data = item.text()
            self.accept()

    def get_selected_data(self):
        return self.selected_data


# 测试入口，便于独立运行调试
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = CameraScanDialog()
    if dlg.exec() == QDialog.DialogCode.Accepted:
        print("选中的数据:", dlg.get_selected_data())
    sys.exit(0) 