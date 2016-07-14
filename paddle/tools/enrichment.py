from .base import ToolBase
from ..ui import ConfigPanel, QFolderLineEdit, QFileOpenLineEdit
from ..globals import settings
from ..qt import *
from .. import utils
import padua

LEVELS = ["Group", "Replicate", "Technical", "Timepoint"]

class EnrichmentConfig(ConfigPanel):


    def __init__(self, parent, *args, **kwargs):
        super(EnrichmentConfig, self).__init__(parent, *args, **kwargs)

        self.v = parent
        gb = QGroupBox('Enrichment')
        gd = QGridLayout()

        # load_maxquant_msp = QFileOpenLineEdit(self, 'Select modificationSpecificPeptides file', filename_filter="Text Files (*.txt);;All Files (*.*);;",)
        # load_maxquant_msp.setToolTip('Select MaxQuant modificationSpecificPeptides file')
        # self.config.add_handler('filename_msp', load_maxquant_msp)
        # gd.addWidget(QLabel('modificationSpecificPeptides file'), 1, 0)
        # gd.addWidget(load_maxquant_msp, 1, 1)

        enrich_levels = QListWidget()
        for l in LEVELS:
            enrich_levels.addItem(l)
        enrich_levels.setSelectionMode(QAbstractItemView.ExtendedSelection)
        gd.addWidget(QLabel('Enrichment levels'), 0, 0)
        gd.addWidget(enrich_levels, 0, 1)
        self.config.add_handler('enrichment_levels', enrich_levels)


        gb.setLayout(gd)
        self.layout.addWidget(gb)

        self.finalise()



class Enrichment(ToolBase):

    name = "Modification Enrichment"
    description = "Calculate enrichment of modified peptides "
    icon = 'enrichment.png'

    shortname = 'enrichment'

    is_manual_runnable = True
    is_auto_runnable = False
    is_auto_rerunnable = False
    is_disableable = False

    def __init__(self, *args, **kwargs):
        super(Enrichment, self).__init__(*args, **kwargs)

        self.config.set_defaults({
            'filename_msp': "",
            'enrichment_prob': 0.75,
            'enrichment_levels': ['Group']
        })

        self.addConfigPanel(EnrichmentConfig)
        self.addButtonBar(self.defaultButtons())

    def run_manual(self):
        self.run( self.enrichment )

    @staticmethod
    def enrichment(config, progress_callback, design=None, **kwargs):
        import padua
        import pandas as pd

        df_msp = padua.io.read_maxquant(config['filename_msp'])
        dfr = padua.analysis.enrichment_from_msp(df_msp)

        if design is not None:
            print("!!", dfr, design, "!!")
            dfr = padua.process.build_index_from_design(dfr, design, remove=["Intensity "])
            print("OK?")
            if 'REMOVE' in dfr.columns.get_level_values(0):
                dfr = dfr.drop(('REMOVE',), axis=1)

            fig = padua.visualize.enrichment( dfr.median(axis=1, level=config['enrichment_levels']) )[0].figure

        else:
            fig = padua.visualize.enrichment( pd.DataFrame(dfr.mean(axis=1)) )[0].figure

        return {'data': None, 'fig': fig}
