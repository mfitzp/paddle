from .base import ToolBase
from ..ui import ConfigPanel, QFolderLineEdit, QFileOpenLineEdit
from ..globals import settings
from ..qt import *
from .. import utils
import padua

LEVELS = ["Group", "Replicate", "Technical", "Timepoint"]

class FilterConfig(ConfigPanel):

    def __init__(self, parent, *args, **kwargs):
        super(FilterConfig, self).__init__(parent, *args, **kwargs)

        self.v = parent
        gb = QGroupBox('Filter')
        gd = QGridLayout()

        valid_levels = QListWidget()
        for l in LEVELS:
            valid_levels.addItem(l)
        valid_levels.setSelectionMode(QAbstractItemView.ExtendedSelection)
        gd.addWidget(QLabel('Include levels'), 0, 0)
        gd.addWidget(valid_levels, 0, 1)
        self.config.add_handler('filter_levels', valid_levels)

        filter_n = QSpinBox()
        filter_n.setRange(0, 100)
        gd.addWidget(QLabel('Minimum valid values'), 1, 0)
        gd.addWidget(filter_n, 1, 1)
        self.config.add_handler('filter_n', filter_n)



        gb.setLayout(gd)
        self.layout.addWidget(gb)

        self.finalise()



class Filter(ToolBase):

    name = "Filter valid values"
    description = "Filter N valid values"
    icon = 'filter.png'

    shortname = 'filter'

    is_manual_runnable = True
    is_auto_runnable = False
    is_auto_rerunnable = False
    is_disableable = False

    def __init__(self, *args, **kwargs):
        super(Filter, self).__init__(*args, **kwargs)

        self.config.set_defaults({
            'filter_n': 1,
            'filter_levels': ['Group','Replicate'],
        })

        self.addConfigPanel(FilterConfig)
        self.addButtonBar(self.defaultButtons())

    def run_manual(self):
        self.run( self.filter )

    @staticmethod
    def filter(df, config, progress_callback, **kwargs):
        import padua
        import numpy as np

        df = df.copy()
        dfn = df.copy()

        df = padua.filters.minimum_valid_values_in_any_group(df,
                                                             levels=config['filter_levels'],
                                                             n=config['filter_n'],
                                                             invalid=np.nan)

        fig = padua.visualize.venn(dfn, df, labels=["Total","Remaining"]).figure

        return {'data': {'df': df, **kwargs}, 'fig': fig}
