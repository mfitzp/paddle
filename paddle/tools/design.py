from .base import ToolBase
from ..ui import ConfigPanel, QFolderLineEdit, QFileOpenLineEdit
from ..globals import settings
from ..qt import *
from .. import utils
import padua

class DesignConfig(ConfigPanel):


    def __init__(self, parent, *args, **kwargs):
        super(DesignConfig, self).__init__(parent, *args, **kwargs)

        self.v = parent
        gb = QGroupBox('Design')
        gd = QGridLayout()

        design_filename = QFileOpenLineEdit(self, 'Select design file', filename_filter="CSV Files (*.csv);;Text Files (*.txt);;All Files (*.*);;",)
        design_filename.setToolTip('Select design definition CSV file')
        self.config.add_handler('filename_design', design_filename)
        gd.addWidget(QLabel('Experimental design file'), 1, 0)
        gd.addWidget(design_filename, 1, 1)

        gb.setLayout(gd)
        self.layout.addWidget(gb)

        self.finalise()



class Design(ToolBase):

    name = "Experimental Design"
    description = "Define experimental design"
    icon = 'design.png'

    shortname = 'design'

    is_manual_runnable = True
    is_auto_runnable = False
    is_auto_rerunnable = False
    is_disableable = False

    def __init__(self, *args, **kwargs):
        super(Design, self).__init__(*args, **kwargs)

        self.config.set_defaults({
            'filename_design': "",
        })

        self.addConfigPanel(DesignConfig)
        self.addButtonBar(self.defaultButtons())


    def run_manual(self):
        self.run( self.design )

    @staticmethod
    def design(config, progress_callback, df=None, quantification_type="Intensity "):
        import matplotlib.pyplot as plt
        import padua
        import pandas as pd

        # TODO: If no design file specified, build an 'automatic' design, assigning each sample to a different group

        if config['filename_design']:
            design = pd.read_csv(config['filename_design'])

        elif df is not None:
            ls = [l.replace('%s ' % quantification_type, '') for l in df.columns.values]
            design = pd.DataFrame([(l,l,n) for n, l in enumerate(ls)], columns=["Label", "Group","Replicate"])

        else:
            # df is None, and we have no file; design=None
            design = None

        if design is not None and df is not None:
            df = df.copy()
            df = padua.process.build_index_from_design(df, design, remove=['%s ' % quantification_type])

            if 'REMOVE' in df.columns.get_level_values(0):
                df = df.drop(('REMOVE',), axis=1)

        return {'data': {'df': df, 'design': design, 'quantification_type': quantification_type}}
