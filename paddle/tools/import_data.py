from .base import ToolBase
from ..ui import ConfigPanel, QFolderLineEdit, QFileOpenLineEdit
from ..globals import settings
from ..qt import *
from .. import utils
import padua

class ImportDataConfig(ConfigPanel):


    def __init__(self, parent, *args, **kwargs):
        super(ImportDataConfig, self).__init__(parent, *args, **kwargs)

        self.v = parent
        # gb = QGroupBox('Load data from')
        # gd = QGridLayout()
        #, parent=None, description=tr("Select file"), filename_filter=tr("All Files") + " (*.*);;", **kwargs):

        # load_maxquant = QFileOpenLineEdit(self, 'Select data file', filename_filter="Text Files (*.txt);;All Files (*.*);;",)
        # load_maxquant.setToolTip('Select MaxQuant data file')
        # self.config.add_handler('filename', load_maxquant)
        # gd.addWidget(QLabel('MaxQuant data file'), 0, 0)
        # gd.addWidget(load_maxquant, 0, 1)

        # gb.setLayout(gd)
        # self.addBottomSpacer(gd)
        # self.layout.addWidget(gb)


        gb = QGroupBox('Quality filters')
        gd = QGridLayout()

        reverse = QCheckBox('Remove reverse?')
        reverse.setToolTip('Remove reverse?')
        self.config.add_handler('remove_reverse', reverse)
        gd.addWidget(reverse, 0, 0)

        only_by_site = QCheckBox('Remove only identified by site?')
        only_by_site.setToolTip('Remove peptides only identified by site?')
        self.config.add_handler('remove_identified_by_site', only_by_site)
        gd.addWidget(only_by_site, 1, 0)

        contaminants = QCheckBox('Remove potential contaminants?')
        contaminants.setToolTip('Remove potential contaminants?')
        self.config.add_handler('remove_potential_contaminants', contaminants)
        gd.addWidget(contaminants, 2, 0)

        contaminants = QCheckBox('Remove contaminants?')
        contaminants.setToolTip('Remove contaminants?')
        self.config.add_handler('remove_contaminants', contaminants)
        gd.addWidget(contaminants, 3, 0)

        gb.setLayout(gd)
        self.layout.addWidget(gb)

        self.finalise()



class ImportData(ToolBase):

    name = "Overview"
    description = "Summary & quality filters"
    icon = 'maxquant.png'

    shortname = 'import'

    is_manual_runnable = True
    is_auto_runnable = False
    is_auto_rerunnable = False
    is_disableable = False

    def __init__(self, *args, **kwargs):
        super(ImportData, self).__init__(*args, **kwargs)

        self.config.set_defaults({
            'filename': '',
            # Filters
            'remove_identified_by_site': True,
            'remove_potential_contaminants': True,
            'remove_contaminants': True,
            'remove_reverse': True,
        })

        self.addConfigPanel(ImportDataConfig)
        self.addButtonBar(self.defaultButtons())

    def result(self,*args, **kwargs):
        self.parent().setTitle(data_filename=self.config.get('filename'))
        super(ImportData, self).result(*args, **kwargs)

    def run_manual(self):
        self.run( self.load_data )

    @staticmethod
    def load_data(config, progress_callback, **kwargs):
        from matplotlib.pyplot import Figure
        import padua
        # data is None here
        fn = config['filename']

        df = padua.io.read_maxquant(fn)

        fig = padua.visualize.quality_control(df).figure

        if config['remove_reverse'] and 'Reverse' in df.columns:
            df = padua.filters.remove_reverse(df)

        if config['remove_identified_by_site'] and 'Only identified by site' in df.columns:
            df = padua.filters.remove_only_identified_by_site(df)

        if config['remove_potential_contaminants'] and 'Potential contaminant' in df.columns:
            df = padua.filters.remove_potential_contaminants(df)

        if config['remove_contaminants'] and 'Contaminant' in df.columns:
            df = padua.filters.remove_contaminants(df)

        return {'data': {'df': df}, 'fig': fig}
