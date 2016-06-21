import logging
logging.debug('Loading globals.py')

from .qt import *
from pyqtconfig import QSettingsManager, ConfigManager

try:
    unicode
except:
    unicode = str

# Paddle global variables

STATUS_COLORS = {
    'ready': 'white',
    'active': 'orange',
    'error': 'red',
    'inactive': 'white',
    'complete': 'green'
}

# ReadTheDocs
ON_RTD = os.environ.get('READTHEDOCS', None) == 'True'
if not ON_RTD:

    # Application settings
    settings = QSettingsManager()
    settings.set_defaults({
        'core/is_setup': False,
        'core/current_version': '0.0.1',
        'core/latest_version': '0.0.1',
        'core/last_time_version_checked': 0,
        'core/offered_registration': False,
    })

    # GLobal processing settings (e.g. peak annotations, class groups, etc.)
    config = ConfigManager()
    config.set_defaults({
        'annotation/peaks': [], # [(label, peak, tolerance)
        'annotation/sample_classes': {},  # {'sample_id': 'class_name' }
        'annotation/class_colors': {}, # {'class_name': color }
    })


    STATUS_QCOLORS = {
        'ready': QColor(255, 255, 255),
        'active': QColor(255, 165, 0),
        'error': QColor(255, 0, 0),
        'inactive': QColor(255, 255, 255),
        'complete': QColor(0, 255, 0),
    }

    def _get_QLineEdit(self):
        return self._get_map(self.text())


    def _set_QLineEdit(self, v):
        self.setText(unicode(self._set_map(v)))


    def _event_QLineEdit(self):
        return self.textChanged

    custom_pyqtconfig_hooks = {
        'QFileOpenLineEdit': (_get_QLineEdit, _set_QLineEdit, _event_QLineEdit),
        'QFileSaveLineEdit': (_get_QLineEdit, _set_QLineEdit, _event_QLineEdit),
        'QFolderLineEdit': (_get_QLineEdit, _set_QLineEdit, _event_QLineEdit),
    }

    # Add hooks for custom widgets
    settings.hooks.update(custom_pyqtconfig_hooks.items())

    SPECTRUM_COLOR = QColor(63, 63, 63, 100)
    OUTLIER_COLOR = QColor(255, 0, 0, 255)

    ''' Brewer colors for spectra labelled by class '''
    CLASS_COLORS = [
        QColor(31, 119, 180, 100),
        QColor(255, 127, 14, 100),
        QColor(44, 160, 44, 100),
        QColor(148, 103, 189, 100),
        QColor(140, 86, 75, 100),
        QColor(227, 119, 194, 100),
        QColor(127, 127, 127, 100),
        QColor(188, 189, 34, 100),
        QColor(23, 190, 207),
    ]

else:
    # Shims for ReadTheDocs
    settings = None
    STATUS_QCOLORS = STATUS_COLORS
    SPECTRUM_COLOR = None
    OUTLIER_COLOR = None
    CLASS_COLORS = []
