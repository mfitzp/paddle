from __future__ import unicode_literals
import sys
import os

# ReadTheDocs
ON_RTD = os.environ.get('READTHEDOCS', None) == 'True'
if not ON_RTD:

    import PyQt5
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtPrintSupport import *
    from PyQt5.QtSvg import *
    os.environ['QT_API'] = 'pyqt5'


    # Create a Qt application
    app = QApplication(sys.argv)
    # app.setStyle('fusion')
    app.setOrganizationName("Paddle")
    app.setOrganizationDomain("paddle.org")
    app.setApplicationName("Paddle")

else:

    # For Qt a Mock in the conf.py will not work for ReadTheDocs so we have to Mock
    # separately here. Any class used in Qt must end up here and accessed attributes added.

    class QMockObject(object):
        def __init__(self, *args, **kwargs):
            super(QMockObject, self).__init__()

        def __call__(self, *args, **kwargs):
            return None


    class QApplication(QMockObject):
        pass


    class pyqtSignal(QMockObject):
        pass


    class pyqtSlot(QMockObject):
        pass


    class QObject(QMockObject):
        pass


    class QAbstractItemModel(QMockObject):
        pass


    class QModelIndex(QMockObject):
        pass


    class QTabWidget(QMockObject):
        pass


    class QWebPage(QMockObject):
        pass


    class QTableView(QMockObject):
        pass


    class QWebView(QMockObject):
        pass


    class QAbstractTableModel(QMockObject):
        pass


    class Qt(QMockObject):
        DisplayRole = None


    class QWidget(QMockObject):
        pass


    class QPushButton(QMockObject):
        pass


    class QDoubleSpinBox(QMockObject):
        pass


    class QListWidget(QMockObject):
        pass


    class QDialog(QMockObject):
        pass


    class QSize(QMockObject):
        pass


    class QTableWidget(QMockObject):
        pass


    class QMainWindow(QMockObject):
        pass


    class QTreeWidget(QMockObject):
        pass


    class QAbstractItemDelegate(QMockObject):
        pass


    class QColor(QMockObject):
        pass


    class QGraphicsItemGroup(QMockObject):
        pass


    class QGraphicsItem(QMockObject):
        pass


    class QGraphicsPathItem(QMockObject):
        pass


    class QGraphicsTextItem(QMockObject):
        pass


    class QGraphicsRectItem(QMockObject):
        pass


    class QGraphicsScene(QMockObject):
        pass


    class QGraphicsView(QMockObject):
        pass

    app = None
