from .base import ToolBase
from ..ui import ConfigPanel, QFolderLineEdit, QFileOpenLineEdit
from ..globals import settings
from ..qt import *
from .. import utils
import padua

class ModifiedAminoAcidsConfig(ConfigPanel):


    def __init__(self, parent, *args, **kwargs):
        super(ModifiedAminoAcidsConfig, self).__init__(parent, *args, **kwargs)

        self.v = parent
        gb = QGroupBox('Modified amino acids')
        gd = QGridLayout()

        #localization_prob = QDoubleSpinBox()
        #localization_prob.setRange(0,1)
        #localization_prob.setSingleStep (0.25)
        #localization_prob.setToolTip('Select amino acids to filter')
        #self.config.add_handler('localization_prob', localization_prob)
        #gd.addWidget(QLabel('Mo probability'), 0, 0)
        #gd.addWidget(localization_prob, 0, 1)

        #gb.setLayout(gd)
        self.layout.addWidget(gb)

        self.finalise()



class ModifiedAminoAcids(ToolBase):

    name = "Modified amino acids"
    description = "Distribution of modified amino acids"
    icon = 'amino_acids.png'

    shortname = 'amino_acids'

    is_manual_runnable = False
    is_auto_runnable = True
    is_auto_rerunnable = False
    is_disableable = False

    def __init__(self, *args, **kwargs):
        super(ModifiedAminoAcids, self).__init__(*args, **kwargs)

        self.config.set_defaults({
        })

        self.addConfigPanel(ModifiedAminoAcidsConfig)
        self.addButtonBar(self.defaultButtons())

    def run_manual(self):
        self.run( self.amino_acids )

    @staticmethod
    def amino_acids(df, config, progress_callback):
        from matplotlib.pyplot import Figure
        import padua
        df = df.copy()

        fig = padua.visualize.modifiedaminoacids(df).figure

        #df = padua.filters.filter_localization_probability(df, config.get('localization_prob'))

        return {'data': {'df': df}, 'fig': fig}
