from .base import ToolBase
from ..ui import ConfigPanel, QFolderLineEdit, QFileOpenLineEdit
from ..globals import settings
from ..qt import *
from .. import utils
import padua

LEVELS = ["Group", "Replicate", "Technical", "Timepoint"]

class CorrelationConfig(ConfigPanel):

    def __init__(self, parent, *args, **kwargs):
        super(CorrelationConfig, self).__init__(parent, *args, **kwargs)

        self.v = parent
        gb = QGroupBox('Correlation')
        gd = QGridLayout()

        valid_levels = QListWidget()
        for l in LEVELS:
            valid_levels.addItem(l)
        valid_levels.setSelectionMode(QAbstractItemView.ExtendedSelection)
        gd.addWidget(QLabel('Levels'), 0, 0)
        gd.addWidget(valid_levels, 0, 1)
        self.config.add_handler('correlation_levels', valid_levels)

        labels = QComboBox()
        labels.addItems(LEVELS)
        gd.addWidget(QLabel('Labels'), 0, 2)
        gd.addWidget(labels, 0, 3)
        self.config.add_handler('labels', labels)

        vmin = QDoubleSpinBox()
        vmin.setRange(0,1)
        self.config.add_handler('vmin', vmin)
        gd.addWidget(QLabel("Minima"), 2, 0)
        gd.addWidget(vmin, 2, 1)

        show_scatter = QCheckBox("Show scatter plots?")
        gd.addWidget(show_scatter, 3, 1)
        self.config.add_handler('show_scatter', show_scatter)

        gb.setLayout(gd)
        self.layout.addWidget(gb)

        self.finalise()



class Correlation(ToolBase):

    name = "Correlation"
    description = "Sample-wise correlation plot"
    icon = 'correlation.png'

    shortname = 'correlation'

    is_manual_runnable = False
    is_auto_runnable = True
    is_auto_rerunnable = False
    is_disableable = False

    def __init__(self, *args, **kwargs):
        super(Correlation, self).__init__(*args, **kwargs)

        self.config.set_defaults({
            'vmin': 0.0,
            'labels': 'Group',
            'correlation_levels': ['Group','Replicate'],
            'show_scatter': False,
        })

        self.addConfigPanel(CorrelationConfig)
        self.addButtonBar(self.defaultButtons())

    def run_manual(self):
        self.run( self.correlation )

    @staticmethod
    def correlation(df, config, progress_callback, **kwargs):
        import padua
        import numpy as np

        dfm = df.copy()
        dfm = dfm.median(axis=1, level=config['correlation_levels'])

        labels = config['labels'] if config['labels'] and dfm.shape[1] < 50 else None

        fig = padua.visualize.correlation(dfm,
                                          show_scatter=config['show_scatter'],
                                          labels=labels,
                                          vmin=config['vmin'],
                                          vmax=1)

        return {'data': {'df': df, **kwargs}, 'fig': fig}
