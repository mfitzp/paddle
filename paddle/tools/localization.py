from .base import ToolBase
from ..ui import ConfigPanel, QFolderLineEdit, QFileOpenLineEdit
from ..globals import settings
from ..qt import *
from .. import utils
import padua

class LocalizationConfig(ConfigPanel):


    def __init__(self, parent, *args, **kwargs):
        super(LocalizationConfig, self).__init__(parent, *args, **kwargs)

        self.v = parent
        gb = QGroupBox('Localization probability')
        gd = QGridLayout()

        localization_prob = QDoubleSpinBox()
        localization_prob.setRange(0,1)
        localization_prob.setSingleStep (0.25)
        localization_prob.setToolTip('Select localization probability cut-off filter')
        self.config.add_handler('localization_prob', localization_prob)
        gd.addWidget(QLabel('Localization probability'), 0, 0)
        gd.addWidget(localization_prob, 0, 1)

        gb.setLayout(gd)
        self.layout.addWidget(gb)

        self.finalise()



class Localization(ToolBase):

    name = "Localisation probability"
    description = "Filter poorly localized peptides"
    icon = 'localization.png'

    shortname = 'localization'

    is_manual_runnable = True
    is_auto_runnable = False
    is_auto_rerunnable = False
    is_disableable = False

    def __init__(self, *args, **kwargs):
        super(Localization, self).__init__(*args, **kwargs)

        self.config.set_defaults({
            'localization_prob': 0.75,
        })

        self.addConfigPanel(LocalizationConfig)
        self.addButtonBar(self.defaultButtons())

    def run_manual(self):
        self.run( self.localization )

    @staticmethod
    def localization(df, config, progress_callback):
        from matplotlib.pyplot import Figure
        import padua
        df = df.copy()

        fig = padua.visualize.modificationlocalization(df).figure
        df = padua.filters.filter_localization_probability(df, config.get('localization_prob'))

        return {'data': {'df': df}, 'fig': fig}
