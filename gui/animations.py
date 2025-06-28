#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
动画效果工具类
"""

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSize, QPoint, QTimer, Qt
from PyQt6.QtWidgets import QGraphicsOpacityEffect

class FadeAnimation:
    """渐显/渐隐动画"""
    
    @staticmethod
    def fade_in(widget, duration=300, finished_callback=None):
        """渐显动画"""
        # 创建透明度效果
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        # 创建动画
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        if finished_callback:
            animation.finished.connect(finished_callback)
        
        animation.start()
        return animation
    
    @staticmethod
    def fade_out(widget, duration=300, finished_callback=None):
        """渐隐动画"""
        # 创建透明度效果
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        # 创建动画
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        if finished_callback:
            animation.finished.connect(finished_callback)
        
        animation.start()
        return animation

class SlideAnimation:
    """滑动动画"""
    
    @staticmethod
    def slide_in(widget, direction="right", duration=300, finished_callback=None):
        """滑入动画
        
        Args:
            widget: 要应用动画的部件
            direction: 滑入方向 ("left", "right", "top", "bottom")
            duration: 动画持续时间（毫秒）
            finished_callback: 动画完成后的回调函数
        """
        # 获取部件大小
        geo = widget.geometry()
        
        # 创建动画
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 根据方向设置起始位置
        start_geo = geo.translated(
            geo.width() if direction == "left" else (-geo.width() if direction == "right" else 0),
            geo.height() if direction == "top" else (-geo.height() if direction == "bottom" else 0)
        )
        
        animation.setStartValue(start_geo)
        animation.setEndValue(geo)
        
        if finished_callback:
            animation.finished.connect(finished_callback)
        
        animation.start()
        return animation
    
    @staticmethod
    def slide_out(widget, direction="right", duration=300, finished_callback=None):
        """滑出动画
        
        Args:
            widget: 要应用动画的部件
            direction: 滑出方向 ("left", "right", "top", "bottom")
            duration: 动画持续时间（毫秒）
            finished_callback: 动画完成后的回调函数
        """
        # 获取部件大小
        geo = widget.geometry()
        
        # 创建动画
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 根据方向设置结束位置
        end_geo = geo.translated(
            geo.width() if direction == "right" else (-geo.width() if direction == "left" else 0),
            geo.height() if direction == "bottom" else (-geo.height() if direction == "top" else 0)
        )
        
        animation.setStartValue(geo)
        animation.setEndValue(end_geo)
        
        if finished_callback:
            animation.finished.connect(finished_callback)
        
        animation.start()
        return animation

class ScaleAnimation:
    """缩放动画"""
    
    @staticmethod
    def pulse(widget, scale_factor=1.05, duration=150, finished_callback=None):
        """脉冲动画，适用于按钮点击等效果"""
        original_size = widget.size()
        target_size = QSize(
            int(original_size.width() * scale_factor),
            int(original_size.height() * scale_factor)
        )
        
        # 创建放大动画
        grow_anim = QPropertyAnimation(widget, b"size")
        grow_anim.setDuration(duration // 2)
        grow_anim.setStartValue(original_size)
        grow_anim.setEndValue(target_size)
        grow_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 创建缩小动画
        shrink_anim = QPropertyAnimation(widget, b"size")
        shrink_anim.setDuration(duration // 2)
        shrink_anim.setStartValue(target_size)
        shrink_anim.setEndValue(original_size)
        shrink_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 连接动画
        grow_anim.finished.connect(shrink_anim.start)
        
        if finished_callback:
            shrink_anim.finished.connect(finished_callback)
        
        grow_anim.start()
        return grow_anim, shrink_anim 