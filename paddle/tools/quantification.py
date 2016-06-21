from .base import ToolBase
from ..ui import ConfigPanel, QFolderLineEdit, QFileOpenLineEdit
from ..globals import settings
from ..qt import *
from .. import utils
import padua

NORMALIZE = {
    'None': None,
    'Subtract column median': 'subtract_column_median',
}

QUANTIFICATION = [
    'Ratio',
    'Intensity',
    'LFQ Intensity',
]


class QuantificationConfig(ConfigPanel):


    def __init__(self, parent, *args, **kwargs):
        super(QuantificationConfig, self).__init__(parent, *args, **kwargs)

        self.v = parent
        gb = QGroupBox("Quantification type")
        gd = QGridLayout()

        quantification = QComboBox()
        quantification.addItems(QUANTIFICATION)
        quantification.setToolTip('Select quantification data type')
        self.config.add_handler('quantification', quantification)
        gd.addWidget(QLabel("Quantification type"), 0, 0)
        gd.addWidget(quantification, 0, 1)

        gb.setLayout(gd)
        self.layout.addWidget(gb)

        gb = QGroupBox('Quantification and normalisation')
        gd = QGridLayout()

        log2_transformation = QCheckBox("Log2 transformation?")
        log2_transformation.setToolTip('Apply log2 transformation to data?')
        self.config.add_handler('log2_transformation', log2_transformation)
        gd.addWidget(log2_transformation, 0, 1)

        normalization = QComboBox()
        normalization.addItems(NORMALIZE)
        normalization.setToolTip('Select normalization to apply to data')
        self.config.add_handler('normalization', normalization, mapper=NORMALIZE)
        gd.addWidget(QLabel("Normalisation type"), 1, 0)
        gd.addWidget(normalization, 1, 1)

        gb.setLayout(gd)
        self.layout.addWidget(gb)

        self.finalise()



class Quantification(ToolBase):

    name = "Quantification"
    description = "Quantification type, transformation and normalization"
    icon = 'quantification.png'

    shortname = 'quantification'

    is_manual_runnable = False
    is_auto_runnable = True
    is_auto_rerunnable = False
    is_disableable = False

    def __init__(self, *args, **kwargs):
        super(Quantification, self).__init__(*args, **kwargs)

        self.config.set_defaults({
            'quantification': 'Intensity',
            'log2_transformation': True,
            'normalization': 'subtract_column_median',
        })

        self.addConfigPanel(QuantificationConfig)
        self.addButtonBar(self.defaultButtons())

    def run_manual(self):
        self.run( self.quantification )

    @staticmethod
    def quantification(df, config, progress_callback):
        import matplotlib.pyplot as plt
        import padua
        import pandas as pd
        import numpy as np

        df = df.copy()

        is_mod_data = any('___' in c for c in df.columns)
        quantification = config['quantification']
        data_filter = '^%s .*'  % quantification

        if is_mod_data:
            # Drop the non__N columns from mod data
            # Drop columns without a space following the quantification word
            dft = df.filter(regex='^(?!%s ).*$' % quantification)
            dfi = df.filter(regex='^(%s ).*__\d$' % quantification)

        else:
            # Drop columns without a space following the quantification word
            dft = df.filter(regex='^(?!%s ).*$' % quantification)
            dfi = df.filter(regex='^(%s ).*$' % quantification)


        df = pd.concat([dft,dfi], axis=1)

        progress_callback(0.1)

        fig = plt.figure(figsize=(12,4))
        ax = fig.add_subplot(3,1,1)

        v = df.filter(regex=data_filter).values.flatten()
        v = v[np.isfinite(v)]
        ax.hist(v, bins=25)
        ax.set_yscale("log", nonposy='clip')

        progress_callback(0.2)

        if config['log2_transformation']:
            df = padua.process.transform_expression_columns(df, np.log2, prefix="%s " % quantification)

        progress_callback(0.4)

        if is_mod_data:
            df = padua.process.expand_side_table(df)

        progress_callback(0.5)

        ax = fig.add_subplot(3,1,2)
        v = df.filter(regex=data_filter).values.flatten()
        v = v[np.isfinite(v)]
        ax.hist(v, bins=25)

        if config['normalization'] == 'subtract_column_median':
            df = padua.normalization.subtract_column_median(df, prefix="%s " % quantification)

        progress_callback(0.7)

        ax = fig.add_subplot(3,1,3)
        v = df.filter(regex=data_filter).values.flatten()
        v = v[np.isfinite(v)]
        ax.hist(v, bins=25)
        xlim = np.max(np.abs(ax.get_xlim()))
        ax.set_xlim(-xlim, xlim)

        # Process data into columns, vs. index
        columns = ['Proteins','Protein IDs','Protein names','Gene names','Positions within proteins','Amino acid','Multiplicity','id']
        df = df.filter(regex='^(%s .*|%s)$' % (quantification, '|'.join(columns)))
        df.set_index([c for c in columns if c in df.columns.values], inplace=True)

        # Drop all complete-nan rows
        df.dropna(how='all', axis=0, inplace=True)

        progress_callback(1.0)

        return {'data': {'df': df, 'quantification_type': quantification}, 'fig': fig}
