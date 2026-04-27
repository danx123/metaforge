#!/usr/bin/env python3
"""
MetaForge - Professional Image Metadata Injector
Enterprise-grade PySide6 application for injecting EXIF metadata into JPG/PNG files
"""

import sys
import os
import json
import math
import struct
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QLineEdit,
    QFileDialog, QScrollArea, QFrame, QSplitter, QGroupBox,
    QProgressBar, QStatusBar, QTabWidget, QListWidget, QListWidgetItem,
    QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox, QSlider,
    QToolButton, QSizePolicy, QMessageBox, QDialog, QDialogButtonBox,
    QStackedWidget
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve,
    QPoint, QRect, QSize, QObject, Slot, QRunnable, QThreadPool
)
from PySide6.QtGui import (
    QPixmap, QImage, QPainter, QColor, QPalette, QFont, QIcon,
    QLinearGradient, QPen, QBrush, QPainterPath, QFontDatabase,
    QCursor, QAction, QKeySequence
)

from PIL import Image, ImageStat, ImageFilter
import piexif
import piexif.helper


# ─────────────────────────────────────────────────────────────────────
#  CAMERA PRESET DATABASE
# ─────────────────────────────────────────────────────────────────────

CAMERA_PRESETS = {
    # ── SONY ──────────────────────────────────────────────────────────
    "Sony Alpha A7R V": {
        "make": "SONY", "model": "ILCE-7RM5",
        "lens_make": "Sony", "lens_model": "FE 24-70mm F2.8 GM II",
        "software": "ILCE-7RM5 v2.00",
        "sensor_type": "Full Frame BSI-CMOS 61MP",
        "max_iso": 102400, "base_iso": 100,
        "focal_length_range": (24, 70),
        "aperture_range": (1.0, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 35.9, "focal_plane_y": 24.0,
        "color_space": 1, "metering_mode": 5,
        "category": "Sony",
        "exif_extras": {
            "ExifIFD.LensSpecification": [(24, 1), (70, 1), (28, 10), (28, 10)],
        }
    },
    "Sony Alpha A7 IV": {
        "make": "SONY", "model": "ILCE-7M4",
        "lens_make": "Sony", "lens_model": "FE 35mm F1.4 GM",
        "software": "ILCE-7M4 v1.10",
        "sensor_type": "Full Frame BSI-CMOS 33MP",
        "max_iso": 51200, "base_iso": 100,
        "focal_length_range": (35, 35),
        "aperture_range": (1.4, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 35.9, "focal_plane_y": 23.9,
        "color_space": 1, "metering_mode": 5,
        "category": "Sony",
    },
    "Sony ZV-E1": {
        "make": "SONY", "model": "ZV-E1",
        "lens_make": "Sony", "lens_model": "FE 28-60mm F4-5.6",
        "software": "ZV-E1 v1.00",
        "sensor_type": "Full Frame CMOS 12.1MP",
        "max_iso": 80000, "base_iso": 100,
        "focal_length_range": (28, 60),
        "aperture_range": (4.0, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 35.6, "focal_plane_y": 23.8,
        "color_space": 1, "metering_mode": 5,
        "category": "Sony",
    },
    "Sony RX100 VII": {
        "make": "SONY", "model": "DSC-RX100M7",
        "lens_make": "Sony", "lens_model": "24-200mm F2.8-4.5",
        "software": "DSC-RX100M7 v1.20",
        "sensor_type": "1-inch Stacked CMOS 20.1MP",
        "max_iso": 12800, "base_iso": 125,
        "focal_length_range": (24, 200),
        "aperture_range": (2.8, 11.0),
        "shutter_range": (1/32000, 30),
        "focal_plane_x": 13.2, "focal_plane_y": 8.8,
        "color_space": 1, "metering_mode": 5,
        "category": "Sony",
    },
    "Sony A6700": {
        "make": "SONY", "model": "ILCE-6700",
        "lens_make": "Sony", "lens_model": "E 18-135mm F3.5-5.6 OSS",
        "software": "ILCE-6700 v1.00",
        "sensor_type": "APS-C BSI-CMOS 26MP",
        "max_iso": 51200, "base_iso": 100,
        "focal_length_range": (18, 135),
        "aperture_range": (3.5, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 23.5, "focal_plane_y": 15.6,
        "color_space": 1, "metering_mode": 5,
        "category": "Sony",
    },
    # ── CANON ─────────────────────────────────────────────────────────
    "Canon EOS R5": {
        "make": "Canon", "model": "Canon EOS R5",
        "lens_make": "Canon", "lens_model": "RF24-70mm F2.8 L IS USM",
        "software": "Firmware Version 1.8.2",
        "sensor_type": "Full Frame CMOS 45MP",
        "max_iso": 51200, "base_iso": 100,
        "focal_length_range": (24, 70),
        "aperture_range": (2.8, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 36.0, "focal_plane_y": 24.0,
        "color_space": 1, "metering_mode": 5,
        "category": "Canon",
    },
    "Canon EOS R6 Mark II": {
        "make": "Canon", "model": "Canon EOS R6m2",
        "lens_make": "Canon", "lens_model": "RF50mm F1.2 L USM",
        "software": "Firmware Version 1.5.0",
        "sensor_type": "Full Frame CMOS 24.2MP",
        "max_iso": 102400, "base_iso": 100,
        "focal_length_range": (50, 50),
        "aperture_range": (1.2, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 35.9, "focal_plane_y": 23.9,
        "color_space": 1, "metering_mode": 5,
        "category": "Canon",
    },
    "Canon EOS 5D Mark IV": {
        "make": "Canon", "model": "Canon EOS 5D Mark IV",
        "lens_make": "Canon", "lens_model": "EF24-70mm f/2.8L II USM",
        "software": "Firmware Version 1.3.6",
        "sensor_type": "Full Frame CMOS 30.4MP",
        "max_iso": 32000, "base_iso": 100,
        "focal_length_range": (24, 70),
        "aperture_range": (2.8, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 36.0, "focal_plane_y": 24.0,
        "color_space": 1, "metering_mode": 5,
        "category": "Canon",
    },
    "Canon EOS 90D": {
        "make": "Canon", "model": "Canon EOS 90D",
        "lens_make": "Canon", "lens_model": "EF-S18-135mm f/3.5-5.6 IS USM",
        "software": "Firmware Version 1.1.1",
        "sensor_type": "APS-C CMOS 32.5MP",
        "max_iso": 25600, "base_iso": 100,
        "focal_length_range": (18, 135),
        "aperture_range": (3.5, 22.0),
        "shutter_range": (1/7500, 30),
        "focal_plane_x": 22.3, "focal_plane_y": 14.9,
        "color_space": 1, "metering_mode": 5,
        "category": "Canon",
    },
    "Canon PowerShot G7X Mark III": {
        "make": "Canon", "model": "Canon PowerShot G7 X Mark III",
        "lens_make": "Canon", "lens_model": "8.8-36.8mm f/1.8-2.8",
        "software": "Firmware Version 1.2.0",
        "sensor_type": "1-inch CMOS 20.1MP",
        "max_iso": 12800, "base_iso": 125,
        "focal_length_range": (24, 100),
        "aperture_range": (1.8, 11.0),
        "shutter_range": (1/2000, 30),
        "focal_plane_x": 13.2, "focal_plane_y": 8.8,
        "color_space": 1, "metering_mode": 5,
        "category": "Canon",
    },
    # ── NIKON ─────────────────────────────────────────────────────────
    "Nikon Z9": {
        "make": "NIKON CORPORATION", "model": "NIKON Z 9",
        "lens_make": "Nikon", "lens_model": "NIKKOR Z 24-70mm f/2.8 S",
        "software": "Ver.4.10",
        "sensor_type": "Full Frame Stacked CMOS 45.7MP",
        "max_iso": 102400, "base_iso": 64,
        "focal_length_range": (24, 70),
        "aperture_range": (2.8, 22.0),
        "shutter_range": (1/32000, 30),
        "focal_plane_x": 35.9, "focal_plane_y": 23.9,
        "color_space": 1, "metering_mode": 5,
        "category": "Nikon",
    },
    "Nikon Z8": {
        "make": "NIKON CORPORATION", "model": "NIKON Z 8",
        "lens_make": "Nikon", "lens_model": "NIKKOR Z 50mm f/1.2 S",
        "software": "Ver.1.10",
        "sensor_type": "Full Frame Stacked CMOS 45.7MP",
        "max_iso": 102400, "base_iso": 64,
        "focal_length_range": (50, 50),
        "aperture_range": (1.2, 16.0),
        "shutter_range": (1/32000, 30),
        "focal_plane_x": 35.9, "focal_plane_y": 23.9,
        "color_space": 1, "metering_mode": 5,
        "category": "Nikon",
    },
    "Nikon Z6 III": {
        "make": "NIKON CORPORATION", "model": "NIKON Z 6_3",
        "lens_make": "Nikon", "lens_model": "NIKKOR Z 35mm f/1.8 S",
        "software": "Ver.1.00",
        "sensor_type": "Full Frame Partial Stacked CMOS 24.5MP",
        "max_iso": 64000, "base_iso": 100,
        "focal_length_range": (35, 35),
        "aperture_range": (1.8, 16.0),
        "shutter_range": (1/16000, 30),
        "focal_plane_x": 35.9, "focal_plane_y": 23.9,
        "color_space": 1, "metering_mode": 5,
        "category": "Nikon",
    },
    "Nikon D850": {
        "make": "NIKON CORPORATION", "model": "NIKON D850",
        "lens_make": "Nikon", "lens_model": "AF-S NIKKOR 24-70mm f/2.8E ED VR",
        "software": "Ver.1.10",
        "sensor_type": "Full Frame BSI-CMOS 45.7MP",
        "max_iso": 102400, "base_iso": 64,
        "focal_length_range": (24, 70),
        "aperture_range": (2.8, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 35.9, "focal_plane_y": 23.9,
        "color_space": 1, "metering_mode": 5,
        "category": "Nikon",
    },
    "Nikon D7500": {
        "make": "NIKON CORPORATION", "model": "NIKON D7500",
        "lens_make": "Nikon", "lens_model": "AF-S DX NIKKOR 18-140mm f/3.5-5.6G ED VR",
        "software": "Ver.1.10",
        "sensor_type": "APS-C CMOS 20.9MP",
        "max_iso": 1640000, "base_iso": 100,
        "focal_length_range": (18, 140),
        "aperture_range": (3.5, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 23.5, "focal_plane_y": 15.7,
        "color_space": 1, "metering_mode": 5,
        "category": "Nikon",
    },
    # ── FUJIFILM ──────────────────────────────────────────────────────
    "Fujifilm X-T5": {
        "make": "FUJIFILM", "model": "X-T5",
        "lens_make": "Fujifilm", "lens_model": "XF16-80mmF4 R OIS WR",
        "software": "Version 2.10",
        "sensor_type": "APS-C X-Trans CMOS 5 HR 40.2MP",
        "max_iso": 51200, "base_iso": 125,
        "focal_length_range": (16, 80),
        "aperture_range": (4.0, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 23.5, "focal_plane_y": 15.6,
        "color_space": 1, "metering_mode": 5,
        "category": "Fujifilm",
    },
    "Fujifilm X100VI": {
        "make": "FUJIFILM", "model": "X100VI",
        "lens_make": "Fujifilm", "lens_model": "FUJINON 23mm F2",
        "software": "Version 1.10",
        "sensor_type": "APS-C X-Trans CMOS 5 HR 40.2MP",
        "max_iso": 51200, "base_iso": 125,
        "focal_length_range": (23, 23),
        "aperture_range": (2.0, 16.0),
        "shutter_range": (1/180000, 30),
        "focal_plane_x": 23.5, "focal_plane_y": 15.6,
        "color_space": 1, "metering_mode": 5,
        "category": "Fujifilm",
    },
    "Fujifilm GFX 100S II": {
        "make": "FUJIFILM", "model": "GFX100SII",
        "lens_make": "Fujifilm", "lens_model": "GF45-100mmF4 R LM OIS WR",
        "software": "Version 1.00",
        "sensor_type": "Medium Format BSI-CMOS 102MP",
        "max_iso": 102400, "base_iso": 100,
        "focal_length_range": (45, 100),
        "aperture_range": (4.0, 32.0),
        "shutter_range": (1/4000, 60),
        "focal_plane_x": 43.8, "focal_plane_y": 32.9,
        "color_space": 1, "metering_mode": 5,
        "category": "Fujifilm",
    },
    # ── PANASONIC ─────────────────────────────────────────────────────
    "Panasonic Lumix S5 II": {
        "make": "Panasonic", "model": "DC-S5M2",
        "lens_make": "Panasonic", "lens_model": "LUMIX S 50mm F1.8",
        "software": "Ver.2.10",
        "sensor_type": "Full Frame CMOS 24.2MP",
        "max_iso": 51200, "base_iso": 100,
        "focal_length_range": (50, 50),
        "aperture_range": (1.8, 22.0),
        "shutter_range": (1/8000, 60),
        "focal_plane_x": 35.6, "focal_plane_y": 23.8,
        "color_space": 1, "metering_mode": 5,
        "category": "Panasonic",
    },
    "Panasonic Lumix G9 II": {
        "make": "Panasonic", "model": "DC-G9M2",
        "lens_make": "Panasonic", "lens_model": "LEICA DG SUMMILUX 25mm F1.4 II",
        "software": "Ver.1.00",
        "sensor_type": "Micro 4/3 Live MOS 25.2MP",
        "max_iso": 25600, "base_iso": 100,
        "focal_length_range": (25, 25),
        "aperture_range": (1.4, 16.0),
        "shutter_range": (1/8000, 60),
        "focal_plane_x": 17.3, "focal_plane_y": 13.0,
        "color_space": 1, "metering_mode": 5,
        "category": "Panasonic",
    },
    # ── OLYMPUS / OM SYSTEM ───────────────────────────────────────────
    "OM System OM-1 Mark II": {
        "make": "OM Digital Solutions", "model": "OM-1MarkII",
        "lens_make": "Olympus", "lens_model": "M.Zuiko Digital ED 12-40mm F2.8 PRO II",
        "software": "Ver.1.3",
        "sensor_type": "Micro 4/3 Stacked CMOS 20.4MP",
        "max_iso": 102400, "base_iso": 200,
        "focal_length_range": (12, 40),
        "aperture_range": (2.8, 22.0),
        "shutter_range": (1/32000, 60),
        "focal_plane_x": 17.3, "focal_plane_y": 13.0,
        "color_space": 1, "metering_mode": 5,
        "category": "OM System",
    },
    # ── LEICA ─────────────────────────────────────────────────────────
    "Leica Q3": {
        "make": "Leica Camera AG", "model": "LEICA Q3",
        "lens_make": "Leica", "lens_model": "Summilux 28 f/1.7 ASPH.",
        "software": "Leica Q3 v3.0.4",
        "sensor_type": "Full Frame BSI-CMOS 60MP",
        "max_iso": 100000, "base_iso": 100,
        "focal_length_range": (28, 28),
        "aperture_range": (1.7, 16.0),
        "shutter_range": (1/16000, 60),
        "focal_plane_x": 36.0, "focal_plane_y": 24.0,
        "color_space": 1, "metering_mode": 5,
        "category": "Leica",
    },
    "Leica M11": {
        "make": "Leica Camera AG", "model": "LEICA M11",
        "lens_make": "Leica", "lens_model": "APO-Summicron-M 50mm f/2 ASPH.",
        "software": "Leica M11 v2.0.4",
        "sensor_type": "Full Frame BSI-CMOS 60MP",
        "max_iso": 50000, "base_iso": 64,
        "focal_length_range": (50, 50),
        "aperture_range": (2.0, 16.0),
        "shutter_range": (1/4000, 60),
        "focal_plane_x": 36.0, "focal_plane_y": 24.0,
        "color_space": 1, "metering_mode": 5,
        "category": "Leica",
    },
    # ── HASSELBLAD ────────────────────────────────────────────────────
    "Hasselblad X2D 100C": {
        "make": "Hasselblad", "model": "X2D 100C",
        "lens_make": "Hasselblad", "lens_model": "XCD 4/45P",
        "software": "Hasselblad X2D v2.3.0",
        "sensor_type": "Medium Format BSI-CMOS 100MP",
        "max_iso": 51200, "base_iso": 64,
        "focal_length_range": (45, 45),
        "aperture_range": (4.0, 32.0),
        "shutter_range": (1/2000, 68),
        "focal_plane_x": 43.8, "focal_plane_y": 32.9,
        "color_space": 1, "metering_mode": 5,
        "category": "Hasselblad",
    },
    # ── PHASE ONE ─────────────────────────────────────────────────────
    "Phase One IQ4 150MP": {
        "make": "Phase One", "model": "IQ4 150MP",
        "lens_make": "Schneider Kreuznach", "lens_model": "SK 80mm f/2.8 LS",
        "software": "IQ4 System v7.3.0",
        "sensor_type": "Medium Format CMOS 150MP",
        "max_iso": 51200, "base_iso": 50,
        "focal_length_range": (80, 80),
        "aperture_range": (2.8, 32.0),
        "shutter_range": (1/1600, 60),
        "focal_plane_x": 53.4, "focal_plane_y": 40.0,
        "color_space": 1, "metering_mode": 5,
        "category": "Phase One",
    },
    # ── RICOH / PENTAX ────────────────────────────────────────────────
    "Pentax K-3 Mark III": {
        "make": "RICOH IMAGING COMPANY, LTD.", "model": "PENTAX K-3 Mark III",
        "lens_make": "smc PENTAX", "lens_model": "smc PENTAX-DA* 16-50mm F2.8 ED AL [IF] SDM",
        "software": "K-3 Mark III Ver 1.80",
        "sensor_type": "APS-C CMOS 25.7MP",
        "max_iso": 819200, "base_iso": 100,
        "focal_length_range": (16, 50),
        "aperture_range": (2.8, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 23.5, "focal_plane_y": 15.6,
        "color_space": 1, "metering_mode": 5,
        "category": "Pentax",
    },
    # ── SIGMA ─────────────────────────────────────────────────────────
    "Sigma fp L": {
        "make": "Sigma", "model": "SIGMA fp L",
        "lens_make": "Sigma", "lens_model": "45mm F2.8 DG DN | Contemporary",
        "software": "Ver.4.00",
        "sensor_type": "Full Frame BSI-CMOS 61MP",
        "max_iso": 102400, "base_iso": 100,
        "focal_length_range": (45, 45),
        "aperture_range": (2.8, 22.0),
        "shutter_range": (1/8000, 30),
        "focal_plane_x": 35.9, "focal_plane_y": 24.0,
        "color_space": 1, "metering_mode": 5,
        "category": "Sigma",
    },
    # ── DRONES ────────────────────────────────────────────────────────
    "DJI Mavic 3 Pro": {
        "make": "DJI", "model": "FC3582",
        "lens_make": "DJI", "lens_model": "DJI Mavic 3 Pro Hasselblad L-Format",
        "software": "v01.01.0400",
        "sensor_type": "4/3 CMOS 20MP",
        "max_iso": 6400, "base_iso": 100,
        "focal_length_range": (24, 70),
        "aperture_range": (2.8, 11.0),
        "shutter_range": (1/8000, 8),
        "focal_plane_x": 17.3, "focal_plane_y": 13.0,
        "color_space": 1, "metering_mode": 5,
        "category": "Drone",
    },
    "DJI Mini 4 Pro": {
        "make": "DJI", "model": "FC4582",
        "lens_make": "DJI", "lens_model": "DJI Mini 4 Pro 24mm",
        "software": "v01.00.0500",
        "sensor_type": "1/1.3-inch CMOS 48MP",
        "max_iso": 6400, "base_iso": 100,
        "focal_length_range": (24, 70),
        "aperture_range": (1.7, 11.0),
        "shutter_range": (1/2000, 10),
        "focal_plane_x": 9.6, "focal_plane_y": 7.2,
        "color_space": 1, "metering_mode": 5,
        "category": "Drone",
    },
    # ── SMARTPHONES ───────────────────────────────────────────────────
    "Apple iPhone 15 Pro Max": {
        "make": "Apple", "model": "iPhone 15 Pro Max",
        "lens_make": "Apple", "lens_model": "iPhone 15 Pro Max back camera 6.765mm f/1.78",
        "software": "17.5.1",
        "sensor_type": "1/1.28-inch CMOS 48MP",
        "max_iso": 2500, "base_iso": 50,
        "focal_length_range": (13, 120),
        "aperture_range": (1.78, 2.2),
        "shutter_range": (1/2000, 1),
        "focal_plane_x": 9.0, "focal_plane_y": 6.7,
        "color_space": 1, "metering_mode": 5,
        "category": "Smartphone",
    },
    "Samsung Galaxy S24 Ultra": {
        "make": "samsung", "model": "SM-S928B",
        "lens_make": "Samsung", "lens_model": "Samsung Galaxy S24 Ultra rear camera 6.3mm f/1.7",
        "software": "S928BXXS3AXFE",
        "sensor_type": "1/1.3-inch ISOCELL HP2 200MP",
        "max_iso": 3200, "base_iso": 50,
        "focal_length_range": (13, 230),
        "aperture_range": (1.7, 10.0),
        "shutter_range": (1/2500, 30),
        "focal_plane_x": 8.9, "focal_plane_y": 6.7,
        "color_space": 1, "metering_mode": 5,
        "category": "Smartphone",
    },
    "Google Pixel 9 Pro": {
        "make": "Google", "model": "Pixel 9 Pro",
        "lens_make": "Google", "lens_model": "Pixel 9 Pro rear camera 6.27mm f/1.68",
        "software": "AP1A.240505.005",
        "sensor_type": "1/1.31-inch CMOS 50MP",
        "max_iso": 3200, "base_iso": 50,
        "focal_length_range": (13, 113),
        "aperture_range": (1.68, 2.2),
        "shutter_range": (1/3000, 30),
        "focal_plane_x": 8.8, "focal_plane_y": 6.6,
        "color_space": 1, "metering_mode": 5,
        "category": "Smartphone",
    },
    # ── ACTION CAM ────────────────────────────────────────────────────
    "GoPro HERO13 Black": {
        "make": "GoPro", "model": "HERO13 Black",
        "lens_make": "GoPro", "lens_model": "GoPro SuperView",
        "software": "HD13.01.01.10.00",
        "sensor_type": "1/1.9-inch CMOS 27MP",
        "max_iso": 6400, "base_iso": 100,
        "focal_length_range": (15, 15),
        "aperture_range": (2.0, 2.0),
        "shutter_range": (1/400, 30),
        "focal_plane_x": 7.7, "focal_plane_y": 5.8,
        "color_space": 1, "metering_mode": 5,
        "category": "Action Camera",
    },
}

CATEGORY_ICONS = {
    "Sony": "📷",
    "Canon": "📷",
    "Nikon": "📷",
    "Fujifilm": "📷",
    "Panasonic": "📷",
    "OM System": "📷",
    "Leica": "📷",
    "Hasselblad": "📷",
    "Phase One": "📷",
    "Pentax": "📷",
    "Sigma": "📷",
    "Drone": "🚁",
    "Smartphone": "📱",
    "Action Camera": "🎬",
}


# ─────────────────────────────────────────────────────────────────────
#  AUTO DETECTION ENGINE
# ─────────────────────────────────────────────────────────────────────

class ImageAnalyzer:
    """Analyzes image characteristics to suggest best matching camera preset"""

    @staticmethod
    def analyze(image_path: str) -> Dict[str, Any]:
        try:
            img = Image.open(image_path)
            w, h = img.size
            mp = (w * h) / 1_000_000
            aspect = w / h if h > 0 else 1.0
            
            # Color analysis
            if img.mode != 'RGB':
                img_rgb = img.convert('RGB')
            else:
                img_rgb = img
            
            stat = ImageStat.Stat(img_rgb)
            brightness = sum(stat.mean) / 3
            contrast = sum(stat.stddev) / 3
            
            # Edge / sharpness heuristic
            gray = img_rgb.convert('L')
            edges = gray.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            sharpness_score = edge_stat.mean[0]

            # Estimate noise level (dark image → likely high ISO)
            dark_pixels = brightness < 80
            
            # Dynamic range (difference between max and min)
            dyn_range = max(stat.extrema[0][1], stat.extrema[1][1], stat.extrema[2][1]) - \
                        min(stat.extrema[0][0], stat.extrema[1][0], stat.extrema[2][0])
            
            # Dominant color temperature
            r, g, b = stat.mean[:3]
            if r > b * 1.1:
                color_temp_est = "warm"  # low color temp
            elif b > r * 1.1:
                color_temp_est = "cool"  # high color temp
            else:
                color_temp_est = "neutral"
            
            return {
                "width": w, "height": h,
                "megapixels": mp,
                "aspect_ratio": aspect,
                "brightness": brightness,
                "contrast": contrast,
                "sharpness": sharpness_score,
                "dark_scene": dark_pixels,
                "dynamic_range": dyn_range,
                "color_temp": color_temp_est,
                "mode": img.mode,
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def score_preset(analysis: Dict, preset_name: str, preset: Dict) -> float:
        """Score how well a preset matches image analysis"""
        score = 0.0
        mp = analysis.get("megapixels", 0)
        sensor_w = preset.get("focal_plane_x", 24)

        # Megapixel match scoring
        sensor_type = preset.get("sensor_type", "")
        # Extract MP from sensor_type string
        preset_mp = 24  # default
        for token in sensor_type.split():
            token_clean = token.replace("MP", "").replace("mp", "")
            try:
                preset_mp = float(token_clean)
                break
            except:
                pass

        mp_diff = abs(mp - preset_mp)
        mp_score = max(0, 10 - mp_diff * 0.3)
        score += mp_score

        # Sensor size scoring based on image dimensions
        sensor_area = sensor_w * preset.get("focal_plane_y", 16)
        if sensor_area > 800:  # MF
            size_cat = "MF"
        elif sensor_area > 700:  # FF
            size_cat = "FF"
        elif sensor_area > 280:  # APS-C
            size_cat = "APSC"
        elif sensor_area > 150:  # MFT
            size_cat = "MFT"
        elif sensor_area > 50:   # 1-inch
            size_cat = "1inch"
        else:
            size_cat = "small"

        img_mp = analysis.get("megapixels", 0)
        if img_mp > 50 and size_cat in ("MF", "FF"):
            score += 8
        elif 25 <= img_mp <= 50 and size_cat in ("FF", "APSC"):
            score += 7
        elif 10 <= img_mp < 25 and size_cat in ("APSC", "MFT", "1inch"):
            score += 6
        elif img_mp < 10 and size_cat in ("small", "1inch"):
            score += 5

        # Brightness → ISO heuristic
        brightness = analysis.get("brightness", 128)
        max_iso = preset.get("max_iso", 6400)
        if brightness < 60 and max_iso >= 51200:
            score += 5
        elif brightness < 100 and max_iso >= 12800:
            score += 3
        elif brightness >= 100 and max_iso < 12800:
            score += 2

        # Sharpness → lens quality
        sharpness = analysis.get("sharpness", 10)
        if sharpness > 20:
            if "L" in preset.get("lens_model", "") or "GM" in preset.get("lens_model", "") \
               or "S-Line" in preset.get("lens_model", "") or "PRO" in preset.get("lens_model", ""):
                score += 4

        # Dynamic range
        dyn_range = analysis.get("dynamic_range", 200)
        if dyn_range > 220 and size_cat in ("FF", "MF"):
            score += 3

        # Category-specific bonuses
        category = preset.get("category", "")
        aspect = analysis.get("aspect_ratio", 1.5)
        if abs(aspect - 1.0) < 0.1 and category == "Smartphone":
            score += 3
        if abs(aspect - 1.0) < 0.15 and category in ("Drone", "Action Camera"):
            score += 2

        return score

    @staticmethod
    def detect_best_preset(image_path: str) -> List[Tuple[str, float]]:
        analysis = ImageAnalyzer.analyze(image_path)
        if "error" in analysis:
            return []
        
        scores = []
        for name, preset in CAMERA_PRESETS.items():
            s = ImageAnalyzer.score_preset(analysis, name, preset)
            scores.append((name, s))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:5], analysis


# ─────────────────────────────────────────────────────────────────────
#  METADATA INJECTOR
# ─────────────────────────────────────────────────────────────────────

def rational(numerator: int, denominator: int) -> Tuple[int, int]:
    return (numerator, denominator)

def float_to_rational(value: float) -> Tuple[int, int]:
    if value == 0:
        return (0, 1)
    denom = 1000000
    numer = int(value * denom)
    from math import gcd
    g = gcd(abs(numer), denom)
    return (numer // g, denom // g)

def apex_to_rational(value: float) -> Tuple[int, int]:
    return float_to_rational(value)


class MetadataInjector:
    @staticmethod
    def build_exif(preset: Dict, overrides: Dict) -> Dict:
        """Build complete EXIF data dict from preset + overrides"""
        p = {**preset, **overrides}

        make = p.get("make", "Unknown").encode()
        model = p.get("model", "Unknown").encode()
        software = p.get("software", "").encode()
        lens_make = p.get("lens_make", "").encode()
        lens_model = p.get("lens_model", "").encode()

        focal_len = p.get("focal_length", preset["focal_length_range"][0])
        aperture = p.get("aperture", preset["aperture_range"][0])
        shutter_raw = p.get("shutter", 1/125)
        iso = p.get("iso", preset.get("base_iso", 100))
        exp_bias = p.get("exp_bias", 0.0)
        date_str = p.get("date", datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S"))
        color_space = p.get("color_space", 1)

        # Shutter speed
        if shutter_raw >= 1:
            shutter_r = (int(shutter_raw), 1)
        else:
            shutter_r = (1, int(round(1 / shutter_raw)))

        # F-number
        aperture_r = float_to_rational(aperture)

        # APEX values
        ev_aperture = 2 * math.log2(aperture)
        ev_shutter = -math.log2(shutter_raw) if shutter_raw > 0 else 0

        exif_ifd = {
            piexif.ExifIFD.ExposureTime: shutter_r,
            piexif.ExifIFD.FNumber: aperture_r,
            piexif.ExifIFD.ExposureProgram: 2,  # Program AE
            piexif.ExifIFD.ISOSpeedRatings: int(iso),
            piexif.ExifIFD.ExifVersion: b"0232",
            piexif.ExifIFD.DateTimeOriginal: date_str.encode(),
            piexif.ExifIFD.DateTimeDigitized: date_str.encode(),
            piexif.ExifIFD.ShutterSpeedValue: float_to_rational(ev_shutter),
            piexif.ExifIFD.ApertureValue: float_to_rational(ev_aperture),
            piexif.ExifIFD.ExposureBiasValue: float_to_rational(exp_bias),
            piexif.ExifIFD.MaxApertureValue: float_to_rational(2 * math.log2(preset["aperture_range"][0])),
            piexif.ExifIFD.MeteringMode: p.get("metering_mode", 5),
            piexif.ExifIFD.Flash: 16,  # Flash did not fire
            piexif.ExifIFD.FocalLength: float_to_rational(focal_len),
            piexif.ExifIFD.ColorSpace: color_space,
            piexif.ExifIFD.FocalLengthIn35mmFilm: int(focal_len * (36 / max(p.get("focal_plane_x", 36), 1))),
            piexif.ExifIFD.SceneCaptureType: 0,
            piexif.ExifIFD.WhiteBalance: 0,
            piexif.ExifIFD.LightSource: 0,
            piexif.ExifIFD.SensingMethod: 2,
            piexif.ExifIFD.CustomRendered: 0,
            piexif.ExifIFD.ExposureMode: 0,
            piexif.ExifIFD.DigitalZoomRatio: (1, 1),
            piexif.ExifIFD.GainControl: 0,
            piexif.ExifIFD.Contrast: 0,
            piexif.ExifIFD.Saturation: 0,
            piexif.ExifIFD.Sharpness: 0,
            piexif.ExifIFD.SubjectDistanceRange: 0,
        }

        if lens_make:
            exif_ifd[piexif.ExifIFD.LensMake] = lens_make
        if lens_model:
            exif_ifd[piexif.ExifIFD.LensModel] = lens_model

        # Lens spec
        fl_min = preset["focal_length_range"][0]
        fl_max = preset["focal_length_range"][1]
        ap_min = preset["aperture_range"][0]
        exif_ifd[piexif.ExifIFD.LensSpecification] = [
            (fl_min, 1), (fl_max, 1),
            float_to_rational(ap_min), float_to_rational(ap_min)
        ]

        zeroth_ifd = {
            piexif.ImageIFD.Make: make,
            piexif.ImageIFD.Model: model,
            piexif.ImageIFD.Software: software,
            piexif.ImageIFD.DateTime: date_str.encode(),
            piexif.ImageIFD.XResolution: (72, 1),
            piexif.ImageIFD.YResolution: (72, 1),
            piexif.ImageIFD.ResolutionUnit: 2,
            piexif.ImageIFD.YCbCrPositioning: 1,
        }

        exif_dict = {
            "0th": zeroth_ifd,
            "Exif": exif_ifd,
            "GPS": {},
            "1st": {},
        }
        return exif_dict

    @staticmethod
    def inject(src_path: str, dst_path: str, preset: Dict, overrides: Dict) -> bool:
        try:
            img = Image.open(src_path)
            exif_dict = MetadataInjector.build_exif(preset, overrides)
            exif_bytes = piexif.dump(exif_dict)
            
            if src_path.lower().endswith(".png"):
                # Convert PNG to JPEG for EXIF support
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(dst_path, "JPEG", exif=exif_bytes, quality=95)
            else:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(dst_path, "JPEG", exif=exif_bytes, quality=95)
            return True
        except Exception as e:
            print(f"Inject error: {e}")
            return False


# ─────────────────────────────────────────────────────────────────────
#  WORKER THREAD
# ─────────────────────────────────────────────────────────────────────

class WorkerSignals(QObject):
    progress = Signal(int, str)
    finished = Signal(list)
    analysis_done = Signal(list, dict)
    error = Signal(str)


class InjectWorker(QRunnable):
    def __init__(self, files, dst_dir, preset, overrides, preset_name):
        super().__init__()
        self.files = files
        self.dst_dir = dst_dir
        self.preset = preset
        self.overrides = overrides
        self.preset_name = preset_name
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        results = []
        total = len(self.files)
        for i, src in enumerate(self.files):
            try:
                fname = Path(src).stem + "_metaforge.jpg"
                dst = str(Path(self.dst_dir) / fname)
                ok = MetadataInjector.inject(src, dst, self.preset, self.overrides)
                results.append((src, dst, ok))
                pct = int((i + 1) / total * 100)
                self.signals.progress.emit(pct, Path(src).name)
            except Exception as e:
                results.append((src, "", False))
                self.signals.error.emit(str(e))
        self.signals.finished.emit(results)


class AnalyzeWorker(QRunnable):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            results, analysis = ImageAnalyzer.detect_best_preset(self.image_path)
            self.signals.analysis_done.emit(results, analysis)
        except Exception as e:
            self.signals.error.emit(str(e))


# ─────────────────────────────────────────────────────────────────────
#  CUSTOM WIDGETS
# ─────────────────────────────────────────────────────────────────────

DARK_THEME = """
QMainWindow, QDialog {
    background-color: #0d1117;
}
QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', 'SF Pro Display', Ubuntu, sans-serif;
}
QFrame#card {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
}
QFrame#cardHighlight {
    background-color: #161b22;
    border: 1px solid #388bfd;
    border-radius: 10px;
}
QLabel#sectionTitle {
    color: #58a6ff;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
QLabel#heading {
    color: #e6edf3;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.5px;
}
QLabel#subheading {
    color: #8b949e;
    font-size: 13px;
}
QLabel#statValue {
    color: #3fb950;
    font-size: 18px;
    font-weight: 700;
}
QLabel#statLabel {
    color: #8b949e;
    font-size: 10px;
    letter-spacing: 0.5px;
}
QLabel#badge {
    color: #58a6ff;
    background-color: #1f3552;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
    color: #e6edf3;
}
QPushButton:pressed {
    background-color: #1c2128;
}
QPushButton#primary {
    background-color: #238636;
    color: #ffffff;
    border: 1px solid #2ea043;
    font-weight: 600;
}
QPushButton#primary:hover {
    background-color: #2ea043;
}
QPushButton#primary:pressed {
    background-color: #1a7f37;
}
QPushButton#accent {
    background-color: #1f6feb;
    color: #ffffff;
    border: 1px solid #388bfd;
    font-weight: 600;
}
QPushButton#accent:hover {
    background-color: #388bfd;
}
QPushButton#danger {
    background-color: #da3633;
    color: #ffffff;
    border: 1px solid #f85149;
}
QPushButton#danger:hover {
    background-color: #f85149;
}
QComboBox {
    background-color: #161b22;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    min-height: 28px;
}
QComboBox:hover {
    border-color: #58a6ff;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8b949e;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #1c2128;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    selection-background-color: #1f3552;
    selection-color: #58a6ff;
    outline: none;
}
QLineEdit {
    background-color: #0d1117;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    min-height: 28px;
}
QLineEdit:focus {
    border-color: #58a6ff;
    background-color: #161b22;
}
QSpinBox, QDoubleSpinBox {
    background-color: #0d1117;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 13px;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #58a6ff;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #21262d;
    border: none;
    width: 18px;
}
QListWidget {
    background-color: #0d1117;
    border: 1px solid #21262d;
    border-radius: 8px;
    color: #e6edf3;
    font-size: 13px;
    outline: none;
}
QListWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #21262d;
    border-radius: 0px;
}
QListWidget::item:hover {
    background-color: #1c2128;
}
QListWidget::item:selected {
    background-color: #1f3552;
    color: #58a6ff;
}
QScrollBar:vertical {
    background-color: #0d1117;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background-color: #0d1117;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 4px;
}
QProgressBar {
    background-color: #21262d;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #238636, stop:1 #3fb950);
    border-radius: 4px;
}
QTextEdit {
    background-color: #0d1117;
    color: #8b949e;
    border: 1px solid #21262d;
    border-radius: 8px;
    font-family: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px;
    padding: 8px;
}
QCheckBox {
    color: #c9d1d9;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #30363d;
    background-color: #0d1117;
}
QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #388bfd;
}
QTabWidget::pane {
    border: 1px solid #21262d;
    border-radius: 8px;
    background-color: #161b22;
}
QTabBar::tab {
    background-color: transparent;
    color: #8b949e;
    padding: 8px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #e6edf3;
    border-bottom: 2px solid #388bfd;
}
QTabBar::tab:hover:!selected {
    color: #c9d1d9;
}
QGroupBox {
    color: #8b949e;
    border: 1px solid #21262d;
    border-radius: 8px;
    margin-top: 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    top: -6px;
    padding: 0 6px;
    background-color: #0d1117;
}
QStatusBar {
    background-color: #161b22;
    border-top: 1px solid #21262d;
    color: #8b949e;
    font-size: 12px;
}
QSplitter::handle {
    background-color: #21262d;
    width: 1px;
    height: 1px;
}
QToolTip {
    background-color: #1c2128;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}
"""


class DropZone(QFrame):
    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self.setMinimumHeight(160)
        self._animating = False
        self._alpha = 0

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        self.icon_label = QLabel("⬆", self)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 36px; color: #484f58;")

        self.text_label = QLabel("Drop images here or click to browse", self)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("color: #8b949e; font-size: 14px; font-weight: 500;")

        self.sub_label = QLabel("JPG, PNG · Multiple files supported", self)
        self.sub_label.setAlignment(Qt.AlignCenter)
        self.sub_label.setStyleSheet("color: #484f58; font-size: 12px;")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addWidget(self.sub_label)

        self.setStyleSheet("""
            QFrame#dropZone {
                background-color: #0d1117;
                border: 2px dashed #30363d;
                border-radius: 12px;
            }
            QFrame#dropZone:hover {
                border-color: #388bfd;
                background-color: #0d1f33;
            }
        """)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Images", "",
                "Images (*.jpg *.jpeg *.png);;JPEG (*.jpg *.jpeg);;PNG (*.png)"
            )
            if files:
                self.files_dropped.emit(files)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame#dropZone {
                    background-color: #0d1f33;
                    border: 2px dashed #388bfd;
                    border-radius: 12px;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame#dropZone {
                background-color: #0d1117;
                border: 2px dashed #30363d;
                border-radius: 12px;
            }
            QFrame#dropZone:hover {
                border-color: #388bfd;
                background-color: #0d1f33;
            }
        """)

    def dropEvent(self, event):
        self.dragLeaveEvent(event)
        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith((".jpg", ".jpeg", ".png")):
                files.append(path)
        if files:
            self.files_dropped.emit(files)


class PreviewLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 200)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            background-color: #0d1117;
            border: 1px solid #21262d;
            border-radius: 8px;
            color: #484f58;
            font-size: 12px;
        """)
        self.setText("No preview")
        self._pixmap = None

    def set_image(self, path: str):
        try:
            pm = QPixmap(path)
            if not pm.isNull():
                pm = pm.scaled(self.width() - 4, self.height() - 4,
                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self._pixmap = pm
                self.setPixmap(pm)
        except:
            self.setText("Preview error")

    def clear_preview(self):
        self._pixmap = None
        self.clear()
        self.setText("No preview")


class ScoreBar(QFrame):
    def __init__(self, name: str, score: float, max_score: float = 30, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        name_lbl = QLabel(name)
        name_lbl.setFixedWidth(200)
        name_lbl.setStyleSheet("color: #c9d1d9; font-size: 12px;")
        name_lbl.setWordWrap(False)
        name_lbl.setToolTip(name)

        bar = QProgressBar()
        bar.setRange(0, int(max_score))
        bar.setValue(int(score))
        bar.setFixedHeight(6)
        bar.setTextVisible(False)
        pct = int(score / max_score * 100) if max_score > 0 else 0
        
        if pct >= 70:
            color = "#3fb950"
        elif pct >= 40:
            color = "#d29922"
        else:
            color = "#f85149"
        
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #21262d;
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)

        pct_lbl = QLabel(f"{pct}%")
        pct_lbl.setFixedWidth(36)
        pct_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pct_lbl.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600;")

        layout.addWidget(name_lbl)
        layout.addWidget(bar, 1)
        layout.addWidget(pct_lbl)


# ─────────────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────

class MetaForgeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MetaForge — Image Metadata Injector")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 860)

        self.thread_pool = QThreadPool()
        self.loaded_files: List[str] = []
        self.preview_file: Optional[str] = None
        self.analysis_result: Optional[Dict] = None
        self.output_dir: str = ""

        self._build_ui()
        self._populate_presets()
        self.setStyleSheet(DARK_THEME)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready — MetaForge v1.0")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── TOP BAR ─────────────────────────────────────────────────
        topbar = QFrame()
        topbar.setFixedHeight(58)
        topbar.setStyleSheet("background-color:#161b22; border-bottom:1px solid #21262d;")
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("⬡  <b>MetaForge</b>")
        logo.setStyleSheet("color:#e6edf3; font-size:18px; letter-spacing:-0.3px;")
        
        version_badge = QLabel("v1.0")
        version_badge.setObjectName("badge")
        version_badge.setFixedWidth(36)

        tb_layout.addWidget(logo)
        tb_layout.addWidget(version_badge)
        tb_layout.addStretch()

        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(24)

        self.stat_files = self._make_stat("0", "FILES")
        self.stat_presets = self._make_stat(str(len(CAMERA_PRESETS)), "PRESETS")
        self.stat_processed = self._make_stat("0", "PROCESSED")

        for s in [self.stat_files, self.stat_presets, self.stat_processed]:
            stats_layout.addWidget(s)

        tb_layout.addWidget(stats_frame)
        root.addWidget(topbar)

        # ── MAIN SPLIT ──────────────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        root.addWidget(splitter, 1)

        # LEFT PANEL
        left = QWidget()
        left.setFixedWidth(340)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)
        splitter.addWidget(left)

        # Drop zone
        drop_title = QLabel("INPUT FILES")
        drop_title.setObjectName("sectionTitle")
        left_layout.addWidget(drop_title)

        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self._on_files_dropped)
        left_layout.addWidget(self.drop_zone)

        # File list
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(200)
        self.file_list.currentRowChanged.connect(self._on_file_selected)
        left_layout.addWidget(self.file_list)

        # File actions
        fa = QHBoxLayout()
        self.btn_clear = QPushButton("✕  Clear All")
        self.btn_clear.setObjectName("danger")
        self.btn_clear.clicked.connect(self._clear_files)
        fa.addWidget(self.btn_clear)
        left_layout.addLayout(fa)

        # Preview
        prev_title = QLabel("PREVIEW")
        prev_title.setObjectName("sectionTitle")
        left_layout.addWidget(prev_title)

        self.preview = PreviewLabel()
        left_layout.addWidget(self.preview, alignment=Qt.AlignHCenter)

        self.preview_info = QLabel("")
        self.preview_info.setStyleSheet("color:#8b949e; font-size:11px;")
        self.preview_info.setAlignment(Qt.AlignCenter)
        self.preview_info.setWordWrap(True)
        left_layout.addWidget(self.preview_info)

        left_layout.addStretch()

        # ── CENTER PANEL ────────────────────────────────────────────
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 16, 0, 16)
        center_layout.setSpacing(12)
        splitter.addWidget(center)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        center_layout.addWidget(tabs, 1)

        # ── TAB 1: PRESET SELECTION ──────────────────────────────────
        preset_tab = QWidget()
        pt_layout = QVBoxLayout(preset_tab)
        pt_layout.setContentsMargins(20, 16, 20, 16)
        pt_layout.setSpacing(12)
        tabs.addTab(preset_tab, "  📷  Camera Preset  ")

        # Category filter
        cat_row = QHBoxLayout()
        cat_lbl = QLabel("CATEGORY")
        cat_lbl.setObjectName("sectionTitle")
        self.cat_combo = QComboBox()
        cats = ["All"] + sorted(set(p["category"] for p in CAMERA_PRESETS.values()))
        self.cat_combo.addItems(cats)
        self.cat_combo.currentTextChanged.connect(self._filter_presets)
        cat_row.addWidget(cat_lbl)
        cat_row.addStretch()
        cat_row.addWidget(self.cat_combo)
        pt_layout.addLayout(cat_row)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search camera model, brand, lens...")
        self.search_input.textChanged.connect(self._filter_presets)
        pt_layout.addWidget(self.search_input)

        # Preset list
        self.preset_list = QListWidget()
        self.preset_list.currentRowChanged.connect(self._on_preset_selected)
        pt_layout.addWidget(self.preset_list, 1)

        # Preset info card
        self.preset_card = QFrame()
        self.preset_card.setObjectName("card")
        self.preset_card.setFixedHeight(130)
        pc_layout = QGridLayout(self.preset_card)
        pc_layout.setContentsMargins(16, 12, 16, 12)

        self.pc_name = QLabel("Select a preset")
        self.pc_name.setStyleSheet("color:#e6edf3; font-size:14px; font-weight:700;")
        self.pc_sensor = QLabel("")
        self.pc_sensor.setObjectName("subheading")
        self.pc_lens = QLabel("")
        self.pc_lens.setStyleSheet("color:#8b949e; font-size:12px;")

        self.pc_iso = QLabel("")
        self.pc_iso.setStyleSheet("color:#f0883e; font-size:12px;")
        self.pc_sensor_size = QLabel("")
        self.pc_sensor_size.setStyleSheet("color:#d2a8ff; font-size:12px;")

        pc_layout.addWidget(self.pc_name, 0, 0, 1, 2)
        pc_layout.addWidget(self.pc_sensor, 1, 0, 1, 2)
        pc_layout.addWidget(self.pc_lens, 2, 0, 1, 2)
        pc_layout.addWidget(self.pc_iso, 3, 0)
        pc_layout.addWidget(self.pc_sensor_size, 3, 1)
        pt_layout.addWidget(self.preset_card)

        # ── TAB 2: PARAMETERS ────────────────────────────────────────
        param_tab = QWidget()
        pm_layout = QVBoxLayout(param_tab)
        pm_layout.setContentsMargins(20, 16, 20, 16)
        pm_layout.setSpacing(12)
        tabs.addTab(param_tab, "  ⚙️  Parameters  ")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        pm_layout.addWidget(scroll, 1)

        params_widget = QWidget()
        scroll.setWidget(params_widget)
        params_inner = QVBoxLayout(params_widget)
        params_inner.setSpacing(16)

        # Exposure settings
        exp_group = QGroupBox("EXPOSURE")
        exp_g = QGridLayout(exp_group)
        exp_g.setSpacing(10)

        exp_g.addWidget(QLabel("Focal Length (mm)"), 0, 0)
        self.spin_focal = QSpinBox()
        self.spin_focal.setRange(1, 2000)
        self.spin_focal.setValue(50)
        exp_g.addWidget(self.spin_focal, 0, 1)

        exp_g.addWidget(QLabel("Aperture f/"), 1, 0)
        self.spin_aperture = QDoubleSpinBox()
        self.spin_aperture.setRange(0.8, 64.0)
        self.spin_aperture.setSingleStep(0.1)
        self.spin_aperture.setValue(2.8)
        exp_g.addWidget(self.spin_aperture, 1, 1)

        exp_g.addWidget(QLabel("Shutter (1/x sec)"), 2, 0)
        self.spin_shutter = QSpinBox()
        self.spin_shutter.setRange(1, 32000)
        self.spin_shutter.setValue(125)
        exp_g.addWidget(self.spin_shutter, 2, 1)

        exp_g.addWidget(QLabel("ISO"), 3, 0)
        self.spin_iso = QSpinBox()
        self.spin_iso.setRange(50, 1640000)
        self.spin_iso.setSingleStep(100)
        self.spin_iso.setValue(400)
        exp_g.addWidget(self.spin_iso, 3, 1)

        exp_g.addWidget(QLabel("Exp. Bias (EV)"), 4, 0)
        self.spin_bias = QDoubleSpinBox()
        self.spin_bias.setRange(-5.0, 5.0)
        self.spin_bias.setSingleStep(0.3)
        self.spin_bias.setValue(0.0)
        exp_g.addWidget(self.spin_bias, 4, 1)

        params_inner.addWidget(exp_group)

        # Date/time settings
        dt_group = QGroupBox("DATE & TIME")
        dt_g = QGridLayout(dt_group)
        dt_g.setSpacing(10)

        self.chk_use_now = QCheckBox("Use current date/time")
        self.chk_use_now.setChecked(True)
        self.chk_use_now.toggled.connect(self._toggle_datetime)
        dt_g.addWidget(self.chk_use_now, 0, 0, 1, 2)

        dt_g.addWidget(QLabel("Date (YYYY:MM:DD)"), 1, 0)
        self.edit_date = QLineEdit()
        self.edit_date.setPlaceholderText("2024:01:15")
        self.edit_date.setEnabled(False)
        dt_g.addWidget(self.edit_date, 1, 1)

        dt_g.addWidget(QLabel("Time (HH:MM:SS)"), 2, 0)
        self.edit_time = QLineEdit()
        self.edit_time.setPlaceholderText("14:30:00")
        self.edit_time.setEnabled(False)
        dt_g.addWidget(self.edit_time, 2, 1)

        params_inner.addWidget(dt_group)
        params_inner.addStretch()

        # ── TAB 3: AUTO DETECT ───────────────────────────────────────
        auto_tab = QWidget()
        at_layout = QVBoxLayout(auto_tab)
        at_layout.setContentsMargins(20, 16, 20, 16)
        at_layout.setSpacing(12)
        tabs.addTab(auto_tab, "  🔍  Auto Detect  ")

        detect_row = QHBoxLayout()
        detect_lbl = QLabel("Analyze the selected image to find matching camera presets")
        detect_lbl.setObjectName("subheading")
        detect_lbl.setWordWrap(True)
        self.btn_detect = QPushButton("🔍  Run Analysis")
        self.btn_detect.setObjectName("accent")
        self.btn_detect.setFixedWidth(150)
        self.btn_detect.clicked.connect(self._run_auto_detect)
        detect_row.addWidget(detect_lbl, 1)
        detect_row.addWidget(self.btn_detect)
        at_layout.addLayout(detect_row)

        # Analysis info
        self.analysis_frame = QFrame()
        self.analysis_frame.setObjectName("card")
        af_layout = QGridLayout(self.analysis_frame)
        af_layout.setContentsMargins(16, 12, 16, 12)
        af_layout.setSpacing(8)

        self.an_mp = self._make_analysis_row("Megapixels", "–")
        self.an_res = self._make_analysis_row("Resolution", "–")
        self.an_brightness = self._make_analysis_row("Avg Brightness", "–")
        self.an_contrast = self._make_analysis_row("Contrast", "–")
        self.an_sharpness = self._make_analysis_row("Sharpness", "–")
        self.an_color = self._make_analysis_row("Color Temp Est.", "–")

        for i, (lbl, val) in enumerate([
            self.an_mp, self.an_res, self.an_brightness,
            self.an_contrast, self.an_sharpness, self.an_color
        ]):
            af_layout.addWidget(lbl, i, 0)
            af_layout.addWidget(val, i, 1)

        at_layout.addWidget(self.analysis_frame)

        # Match results
        match_lbl = QLabel("BEST MATCHES")
        match_lbl.setObjectName("sectionTitle")
        at_layout.addWidget(match_lbl)

        self.match_scroll = QScrollArea()
        self.match_scroll.setWidgetResizable(True)
        self.match_scroll.setFrameShape(QFrame.NoFrame)
        at_layout.addWidget(self.match_scroll, 1)

        self.match_container = QWidget()
        self.match_layout = QVBoxLayout(self.match_container)
        self.match_layout.setSpacing(4)
        self.match_layout.addStretch()
        self.match_scroll.setWidget(self.match_container)

        self.btn_apply_best = QPushButton("✓  Apply Best Match")
        self.btn_apply_best.setObjectName("primary")
        self.btn_apply_best.clicked.connect(self._apply_best_match)
        self.btn_apply_best.setEnabled(False)
        at_layout.addWidget(self.btn_apply_best)

        # ── RIGHT PANEL ─────────────────────────────────────────────
        right = QWidget()
        right.setFixedWidth(260)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 16, 16, 16)
        right_layout.setSpacing(12)
        splitter.addWidget(right)

        out_title = QLabel("OUTPUT")
        out_title.setObjectName("sectionTitle")
        right_layout.addWidget(out_title)

        out_card = QFrame()
        out_card.setObjectName("card")
        oc_layout = QVBoxLayout(out_card)
        oc_layout.setContentsMargins(12, 12, 12, 12)
        oc_layout.setSpacing(8)

        oc_layout.addWidget(QLabel("Output Directory:"))
        self.edit_outdir = QLineEdit()
        self.edit_outdir.setPlaceholderText("Same as source")
        self.edit_outdir.setReadOnly(True)
        oc_layout.addWidget(self.edit_outdir)

        self.btn_browse_out = QPushButton("📁  Choose Folder")
        self.btn_browse_out.clicked.connect(self._choose_output)
        oc_layout.addWidget(self.btn_browse_out)

        right_layout.addWidget(out_card)

        # Progress
        prog_title = QLabel("PROGRESS")
        prog_title.setObjectName("sectionTitle")
        right_layout.addWidget(prog_title)

        prog_card = QFrame()
        prog_card.setObjectName("card")
        pc2_layout = QVBoxLayout(prog_card)
        pc2_layout.setContentsMargins(12, 12, 12, 12)
        pc2_layout.setSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        pc2_layout.addWidget(self.progress_bar)

        self.progress_file = QLabel("–")
        self.progress_file.setStyleSheet("color:#8b949e; font-size:11px;")
        self.progress_file.setWordWrap(True)
        pc2_layout.addWidget(self.progress_file)

        right_layout.addWidget(prog_card)

        # Log
        log_title = QLabel("ACTIVITY LOG")
        log_title.setObjectName("sectionTitle")
        right_layout.addWidget(log_title)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Logs will appear here...")
        right_layout.addWidget(self.log_text, 1)

        # Action buttons
        self.btn_inject = QPushButton("▶  Inject Metadata")
        self.btn_inject.setObjectName("primary")
        self.btn_inject.setFixedHeight(42)
        self.btn_inject.setStyleSheet(self.btn_inject.styleSheet() + "font-size:14px;")
        self.btn_inject.clicked.connect(self._run_inject)
        right_layout.addWidget(self.btn_inject)

        self.btn_open_out = QPushButton("📂  Open Output Folder")
        self.btn_open_out.clicked.connect(self._open_output)
        right_layout.addWidget(self.btn_open_out)

        splitter.setSizes([340, 800, 260])
        self._best_matches = []

    def _make_stat(self, value, label):
        w = QFrame()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(0)
        vl = QLabel(value)
        vl.setObjectName("statValue")
        vl.setAlignment(Qt.AlignCenter)
        ll = QLabel(label)
        ll.setObjectName("statLabel")
        ll.setAlignment(Qt.AlignCenter)
        l.addWidget(vl)
        l.addWidget(ll)
        return w

    def _make_analysis_row(self, label, value):
        lbl = QLabel(label + ":")
        lbl.setStyleSheet("color:#8b949e; font-size:12px;")
        val = QLabel(value)
        val.setStyleSheet("color:#e6edf3; font-size:12px; font-weight:500;")
        return lbl, val

    def _populate_presets(self, filter_cat="All", filter_text=""):
        self.preset_list.clear()
        for name, preset in CAMERA_PRESETS.items():
            cat = preset.get("category", "")
            if filter_cat != "All" and cat != filter_cat:
                continue
            if filter_text and filter_text.lower() not in name.lower() and \
               filter_text.lower() not in preset.get("make", "").lower() and \
               filter_text.lower() not in preset.get("lens_model", "").lower():
                continue
            icon = CATEGORY_ICONS.get(cat, "📷")
            item = QListWidgetItem(f"{icon}  {name}")
            item.setData(Qt.UserRole, name)
            self.preset_list.addItem(item)

        if self.preset_list.count() > 0:
            self.preset_list.setCurrentRow(0)

    def _filter_presets(self):
        cat = self.cat_combo.currentText()
        text = self.search_input.text().strip()
        self._populate_presets(cat, text)

    def _on_preset_selected(self, row):
        if row < 0:
            return
        item = self.preset_list.item(row)
        if not item:
            return
        name = item.data(Qt.UserRole)
        preset = CAMERA_PRESETS.get(name)
        if not preset:
            return
        self._current_preset_name = name
        self._current_preset = preset
        # Update card
        self.pc_name.setText(name)
        self.pc_sensor.setText(preset.get("sensor_type", ""))
        self.pc_lens.setText(f"  {preset.get('lens_model', '')}")
        self.pc_iso.setText(f"ISO {preset.get('base_iso', 100)} – {preset.get('max_iso', 6400):,}")
        w = preset.get("focal_plane_x", 0)
        h = preset.get("focal_plane_y", 0)
        self.pc_sensor_size.setText(f"Sensor: {w}×{h} mm")
        # Update param defaults
        fl_min, fl_max = preset["focal_length_range"]
        self.spin_focal.setValue(fl_min)
        ap_min = preset["aperture_range"][0]
        self.spin_aperture.setValue(ap_min)
        self.spin_iso.setValue(preset.get("base_iso", 100))

    def _on_files_dropped(self, files):
        new = [f for f in files if f not in self.loaded_files]
        self.loaded_files.extend(new)
        self._refresh_file_list()
        self._log(f"Added {len(new)} file(s)")

    def _refresh_file_list(self):
        self.file_list.clear()
        for f in self.loaded_files:
            item = QListWidgetItem(Path(f).name)
            item.setToolTip(f)
            self.file_list.addItem(item)
        # Update stat
        self.stat_files.findChild(QLabel).setText(str(len(self.loaded_files)))
        # auto-select first
        if self.file_list.count() > 0 and self.file_list.currentRow() < 0:
            self.file_list.setCurrentRow(0)

    def _on_file_selected(self, row):
        if row < 0 or row >= len(self.loaded_files):
            return
        path = self.loaded_files[row]
        self.preview_file = path
        self.preview.set_image(path)
        try:
            img = Image.open(path)
            w, h = img.size
            mp = w * h / 1_000_000
            self.preview_info.setText(f"{w}×{h}px  ·  {mp:.1f}MP  ·  {Path(path).suffix.upper()}")
        except:
            self.preview_info.setText(Path(path).name)

    def _clear_files(self):
        self.loaded_files.clear()
        self.file_list.clear()
        self.preview.clear_preview()
        self.preview_info.setText("")
        self.preview_file = None
        self._log("Cleared file list")

    def _toggle_datetime(self, checked):
        self.edit_date.setEnabled(not checked)
        self.edit_time.setEnabled(not checked)

    def _choose_output(self):
        d = QFileDialog.getExistingDirectory(self, "Choose Output Directory")
        if d:
            self.output_dir = d
            self.edit_outdir.setText(d)
            self._log(f"Output: {d}")

    def _get_overrides(self):
        overrides = {
            "focal_length": self.spin_focal.value(),
            "aperture": self.spin_aperture.value(),
            "shutter": 1 / max(self.spin_shutter.value(), 1),
            "iso": self.spin_iso.value(),
            "exp_bias": self.spin_bias.value(),
        }
        if not self.chk_use_now.isChecked():
            date_str = self.edit_date.text().strip() or datetime.datetime.now().strftime("%Y:%m:%d")
            time_str = self.edit_time.text().strip() or datetime.datetime.now().strftime("%H:%M:%S")
            overrides["date"] = f"{date_str} {time_str}"
        else:
            overrides["date"] = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
        return overrides

    def _run_inject(self):
        if not self.loaded_files:
            QMessageBox.warning(self, "No Files", "Please add image files first.")
            return
        if not hasattr(self, '_current_preset'):
            QMessageBox.warning(self, "No Preset", "Please select a camera preset.")
            return

        dst_dir = self.output_dir or str(Path(self.loaded_files[0]).parent)
        overrides = self._get_overrides()

        self.btn_inject.setEnabled(False)
        self.progress_bar.setValue(0)
        self._log(f"Starting injection: {len(self.loaded_files)} file(s)...")

        worker = InjectWorker(
            self.loaded_files, dst_dir,
            self._current_preset, overrides,
            self._current_preset_name
        )
        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(self._on_inject_done)
        worker.signals.error.connect(lambda e: self._log(f"Error: {e}"))
        self.thread_pool.start(worker)

    @Slot(int, str)
    def _on_progress(self, pct, filename):
        self.progress_bar.setValue(pct)
        self.progress_file.setText(filename)
        self.status_bar.showMessage(f"Processing: {filename} ({pct}%)")

    @Slot(list)
    def _on_inject_done(self, results):
        self.btn_inject.setEnabled(True)
        ok = sum(1 for _, _, s in results if s)
        fail = len(results) - ok
        self._log(f"Done: {ok} injected, {fail} failed")
        self.status_bar.showMessage(f"Complete: {ok}/{len(results)} files processed")
        # Update stat
        processed_lbl = self.stat_processed.findChild(QLabel)
        processed_lbl.setText(str(int(processed_lbl.text() or "0") + ok))
        if fail > 0:
            QMessageBox.warning(self, "Partial Success", f"{ok} succeeded, {fail} failed.")
        else:
            QMessageBox.information(self, "Success", f"All {ok} file(s) injected successfully.")

    def _run_auto_detect(self):
        if not self.preview_file:
            QMessageBox.warning(self, "No File", "Select an image file first.")
            return
        self.btn_detect.setEnabled(False)
        self.btn_detect.setText("Analyzing...")
        self._log(f"Analyzing: {Path(self.preview_file).name}")

        worker = AnalyzeWorker(self.preview_file)
        worker.signals.analysis_done.connect(self._on_analysis_done)
        worker.signals.error.connect(lambda e: (
            self._log(f"Analysis error: {e}"),
            self.btn_detect.setEnabled(True),
            self.btn_detect.setText("🔍  Run Analysis")
        ))
        self.thread_pool.start(worker)

    @Slot(list, dict)
    def _on_analysis_done(self, matches, analysis):
        self.btn_detect.setEnabled(True)
        self.btn_detect.setText("🔍  Run Analysis")
        self.analysis_result = analysis
        self._best_matches = matches

        # Update analysis panel
        mp = analysis.get("megapixels", 0)
        w = analysis.get("width", 0)
        h = analysis.get("height", 0)
        self.an_mp[1].setText(f"{mp:.1f} MP")
        self.an_res[1].setText(f"{w} × {h}")
        self.an_brightness[1].setText(f"{analysis.get('brightness', 0):.1f} / 255")
        self.an_contrast[1].setText(f"{analysis.get('contrast', 0):.1f}")
        self.an_sharpness[1].setText(f"{analysis.get('sharpness', 0):.1f}")
        self.an_color[1].setText(analysis.get("color_temp", "–").capitalize())

        # Clear match layout
        while self.match_layout.count() > 1:
            item = self.match_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        max_score = matches[0][1] if matches else 30
        for name, score in matches:
            bar = ScoreBar(name, score, max_score)
            self.match_layout.insertWidget(self.match_layout.count() - 1, bar)

        self.btn_apply_best.setEnabled(bool(matches))
        self._log(f"Analysis complete. Best: {matches[0][0] if matches else '–'}")

    def _apply_best_match(self):
        if not self._best_matches:
            return
        best_name = self._best_matches[0][0]
        # Find in preset list and select
        for i in range(self.preset_list.count()):
            item = self.preset_list.item(i)
            if item.data(Qt.UserRole) == best_name:
                self.preset_list.setCurrentRow(i)
                self._log(f"Applied preset: {best_name}")
                return
        # If not visible due to filter, reset filter
        self.cat_combo.setCurrentText("All")
        self.search_input.clear()
        for i in range(self.preset_list.count()):
            item = self.preset_list.item(i)
            if item.data(Qt.UserRole) == best_name:
                self.preset_list.setCurrentRow(i)
                self._log(f"Applied preset: {best_name}")
                return

    def _open_output(self):
        d = self.output_dir or (str(Path(self.loaded_files[0]).parent) if self.loaded_files else "")
        if d:
            import subprocess
            try:
                subprocess.Popen(["xdg-open", d])
            except:
                pass

    def _log(self, msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f'<span style="color:#484f58;">[{ts}]</span> {msg}')


# ─────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MetaForge")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("MacanAngkasa")

    # App font
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.PreferFullHinting)
    app.setFont(font)

    window = MetaForgeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
