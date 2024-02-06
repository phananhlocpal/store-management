# Python Library
import sys
import datetime
import time
import re
import locale
locale.setlocale(locale.LC_ALL, 'vi_VN')

#Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

# GUI Libaray
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QWidget, QStackedWidget, QLineEdit, QCompleter, QListView, QVBoxLayout, QWidget, QTableWidgetItem, QGridLayout, QSpinBox, QPushButton, QTextEdit, QSizePolicy
from PyQt5.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QPoint, QRect, QDateTime, QTimer

# Send Email Libray
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Import UI file
import ui.ui_home
import ui.ui_login
import ui.ui_notiWindow
import ui.ui_confirmBE
import ui.ui_editItem
import ui.ui_changePassword
import ui.ui_EditUser

# Import Database
import pyodbc
connection = pyodbc.connect('DRIVER = {ODBC Driver 18 for SQL Server}; SERVER=PAL; DATABASE=InventorySaleManagement; DSN=InventorySaleManagement; Trusted_Connection=yes; encrypt=yes; TrustServerCertificate=yes')
db=connection.cursor()




