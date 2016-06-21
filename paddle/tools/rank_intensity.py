from .base import ToolBase
from ..ui import ConfigPanel, QFolderLineEdit, QFileOpenLineEdit
from ..globals import settings
from ..qt import *
from .. import utils
import padua

class RankIntensityConfig(ConfigPanel):

    def __init__(self, parent, *args, **kwargs):
        super(RankIntensityConfig, self).__init__(parent, *args, **kwargs)

        self.v = parent
        gb = QGroupBox('Rank intensity')
        gd = QGridLayout()

        show_go = QCheckBox("Show GO enrichment?")
        gd.addWidget(show_go, 0, 1)
        self.config.add_handler('show_go', show_go)

        gb.setLayout(gd)
        self.layout.addWidget(gb)

        self.finalise()



class RankIntensity(ToolBase):

    name = "Rank intensity"
    description = "Generate rank intensity plot"
    icon = 'rank_intensity.png'

    shortname = 'rank_intensity'

    is_manual_runnable = False
    is_auto_runnable = True
    is_auto_rerunnable = False
    is_disableable = False

    def __init__(self, *args, **kwargs):
        super(RankIntensity, self).__init__(*args, **kwargs)

        self.config.set_defaults({
            'show_go': False,
            #'rank_intensity_prob': 0.75,
        })

        self.addConfigPanel(RankIntensityConfig)
        self.addButtonBar(self.defaultButtons())

    def run_manual(self):
        self.run( self.rank_intensity )

    @staticmethod
    def rank_intensity(df, config, progress_callback):
        from matplotlib.pyplot import Figure
        import padua
        # data is None here
        df = df.copy()

        fig = padua.visualize.rankintensity(df, show_go_enrichment=config['show_go'], progress_callback=progress_callback).figure

        return {'data': {'df': df}, 'fig': fig}
