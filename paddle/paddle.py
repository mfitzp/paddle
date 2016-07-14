# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import logging
import json
import datetime as dt
from copy import deepcopy
from . import utils

frozen = getattr(sys, 'frozen', False)
ON_RTD = os.environ.get('READTHEDOCS', None) == 'True'

import matplotlib
# Used to enforce Qt version via matplotlib, etc.
os.environ['QT_API'] = 'pyqt5'
matplotlib.rcParams['backend'] = 'Qt5Agg'

if sys.platform == 'win32' and frozen:
    # Dump all output when running without a console; otherwise will hang
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

if frozen:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

from .qt import *

import time
import requests

from .globals import settings, config

from . import ui


# Translation (@default context)
from .translate import tr


__version__ = 0.1

from . import tools
from .tools import ( import_data, localization, amino_acids, rank_intensity,
                     quantification, enrichment, design,
                     filter, correlation
                     # correlation, export_data
                    )


class MainWindow(QMainWindow):

    updated = pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()

        # Do version upgrade availability check
        # FIXME: Do check for new download here; if not done > 1 weeks
        if settings.get('core/last_checked') and settings.get('core/last_checked') < (int(time.time()) - 604800):  # 1 week in seconds
            try:
                r = requests.get('https://raw.githubusercontent.com/mfitzp/paddle/master/VERSION')
            except:
                pass

            else:
                if r.status_code == 200:
                    settings.set('core/latest_version', r.text)

            settings.set('core/last_checked', int(time.time()))

        #  UI setup etc
        self.menuBars = {
            'file': self.menuBar().addMenu(tr('&File')),
            #'help': self.menuBar().addMenu(tr('&Help')),
        }

        # TOOLBAR

        self.setUnifiedTitleAndToolBarOnMac(True) #; // activate Mac-style toolbar


        self.t = QToolBar('Data')
        self.t.setIconSize(QSize(22, 22))

        load_dataAction = QAction(QIcon(os.path.join(utils.scriptdir, 'icons', 'maxquant.png')), tr('Load MaxQuant quantified data file…'), self)
        load_dataAction.setStatusTip('Load MaxQuant data file')
        load_dataAction.triggered.connect(self.onLoadData)
        self.t.addAction(load_dataAction)
        self.menuBars['file'].addAction(load_dataAction)

        load_mspAction = QAction(QIcon(os.path.join(utils.scriptdir, 'icons', 'maxquant_msp.png')), tr('Load MaxQuant modifiedSpecificPeptides file…'), self)
        load_mspAction.setStatusTip('Load MaxQuant modifiedSpecificPeptides file')
        load_mspAction.triggered.connect(self.onLoadMsp)
        self.t.addAction(load_mspAction)
        self.menuBars['file'].addAction(load_mspAction)

        load_designAction = QAction(QIcon(os.path.join(utils.scriptdir, 'icons', 'design.png')), tr('Load experimental design file…'), self)
        load_designAction.setStatusTip('Load experimental design file')
        load_designAction.triggered.connect(self.onLoadDesign)
        self.t.addAction(load_designAction)
        self.menuBars['file'].addAction(load_designAction)

        self.menuBars['file'].addSeparator()

        save_dataAction = QAction(QIcon(os.path.join(utils.scriptdir, 'icons', 'data-save.png')), tr('Save processed data…'), self)
        save_dataAction.setStatusTip('Save processed data')
        save_dataAction.triggered.connect(self.onSaveData)
        self.t.addAction(save_dataAction)
        self.menuBars['file'].addAction(save_dataAction)


        self.addToolBar(self.t)

        self.t = QToolBar('Images')
        self.t.setIconSize(QSize(22, 22))

        save_imageAction = QAction(QIcon(os.path.join(utils.scriptdir, 'icons', 'image-x-generic.png')), tr('Save current figure…'), self)
        save_imageAction.setStatusTip('Save current figure')
        save_imageAction.triggered.connect(self.onLoadData)
        self.t.addAction(save_imageAction)
        self.menuBars['file'].addAction(save_imageAction)

        save_all_imageAction = QAction(QIcon(os.path.join(utils.scriptdir, 'icons', 'image-x-generic-stack.png')), tr('Save all figures…'), self)
        save_all_imageAction.setStatusTip('Save all figures')
        save_all_imageAction.triggered.connect(self.onSaveAllImage)
        self.t.addAction(save_all_imageAction)
        self.menuBars['file'].addAction(save_all_imageAction)

        self.addToolBar(self.t)


        self.menuBars['file'].addSeparator()

        self.t = QToolBar('Configuration')
        self.t.setIconSize(QSize(22, 22))

        load_configAction = QAction(QIcon(os.path.join(utils.scriptdir, 'icons', 'config-open.png')), tr('Load configuration…'), self)
        load_configAction.setStatusTip('Load tool settings and configuration')
        load_configAction.triggered.connect(self.onLoadConfig)
        self.t.addAction(load_configAction)
        self.menuBars['file'].addAction(load_configAction)

        save_configAction = QAction(QIcon(os.path.join(utils.scriptdir, 'icons', 'config-save.png')), tr('Save configuration…'), self)
        save_configAction.setStatusTip('Save current tool settings and configuration')
        save_configAction.triggered.connect(self.onSaveConfig)
        self.t.addAction(save_configAction)
        self.menuBars['file'].addAction(save_configAction)

        self.addToolBar(self.t)

        # INIT PLUGINS AND TOOLS
        # We pass a copy of main window object in to the plugin manager so it can
        # be available for loading

        self.configstack = QStackedWidget()
        self.configstack.setSizePolicy(
            QSizePolicy.Maximum,
            QSizePolicy.Maximum
        )

        self.toolPanel = ui.ToolListWidget(self)
        self.toolPanel.setMinimumWidth(250)
        self.toolPanel.setMaximumWidth(250)

        self.current_tool = None



        self.tools = [
            tools.import_data.ImportData(self),
            # Mod: Modification localisation probability
            tools.localization.Localization(self),
            # Mod: Modified amino acids (allow filtering?)
            tools.amino_acids.ModifiedAminoAcids(self),
            # Rank intensity plots
            tools.rank_intensity.RankIntensity(self),
            # Transformation, normalisation
            tools.quantification.Quantification(self),
            # Transformation, normalisation
            tools.design.Design(self),
            # Filter by valid values
            tools.filter.Filter(self),
            # Correlation plot
            tools.correlation.Correlation(self),
            # Export processed data

            # tools.export_data.ExportData(self),

                        # Mod: Enrichment
            tools.enrichment.Enrichment(self),
        ]

        # Workflow logic
        # On completion of execution for any tool, clear all subsequent tools data
        # empty outputs and clear figures (hacky); execute next tool
        def on_tool_complete(tn):

            # On completion of load of data, design or msp file generate
            # a activation-deactivation mask for tools that are affected
            # then apply this mask
            if tn == 0:
                import_data = self.tools[0]
                if 'data' in import_data.data and 'df' in import_data.data['data']:

                    df = import_data.data['data']['df']
                    is_mod_data = any('___' in c for c in df.columns)

                    if is_mod_data:
                        enable = [True, True,  True,  True, True, True, True, True, None]
                    else:
                        enable = [True, False, False, True, True, True, True, True, None]

                    for n, s in enumerate(enable):
                        if s is True:
                            self.tools[n].enable()
                        elif s is False:
                            self.tools[n].disable()

            if tn == -1:
                enrichment = self.tools[-1]
                enrichment.enable()

            # Get next active tool, and execute
            t = self.tools[tn].get_next_tool()
            if t is not None:
                t.run_manual()

        def on_tool_status(s, tn):
            if s == 'active':
                # Starting up, clear all subsequent tools
                for n in range(tn+1, len(self.tools)):
                    self.tools[n].setup()


        for n in range(len(self.tools)):
            self.tools[n].status.connect(lambda s, n=n: on_tool_status(s, n))
            self.tools[n].complete.connect(lambda n=n: on_tool_complete(n))


        self.viewStack = QStackedWidget()
        self.viewStack.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        for n, tool in enumerate(self.tools):
            item = QListWidgetItem(QIcon(os.path.join(utils.scriptdir, 'icons', tool.icon)), tool.name)
            item.tool = tool
            item.n = n

            tool.item = item

            item.setData(Qt.UserRole, tool)
            item.setData(Qt.UserRole + 1, tool.description)

            item.setData(Qt.UserRole+2, 0.0)  # Progress
            item.setData(Qt.UserRole+3, 'ready') # Status

            if n != 5:
                self.toolPanel.addItem(item)
                tool.disable()
            else:
                tool.enable()

            self.configstack.addWidget(tool.configPanels)
            self.viewStack.addWidget(tool.view)

            # btn.pressed.connect( lambda t=t: self.configstack.setCurrentWidget(t.configPanels))

        self.toolPanel.currentItemChanged.connect( lambda i: i.tool.activate() )
        self.toolPanel.currentItemChanged.connect( self.update_current_tool_from_item )

        self.main = QWidget()
        self.mainlayout = QHBoxLayout()
        self.centerlayout = QVBoxLayout()
        self.centerlayout.setContentsMargins(0,0,0,0)


        # Set window title and icon
        self.window_title_metadata = {}
        self.setTitle(configuration_filename='Untitled', data_filename='No Data')  # Use default

        # Create status bar
        self.progressBar = QProgressBar(self.statusBar())
        self.progressBar.setMaximumSize(QSize(170, 19))
        self.progressBar.setRange(0, 100)
        self.statusBar().addPermanentWidget(self.progressBar)

        # We need two viewers; one for the scatter plot (PCA) to avoid weird scaling issues
        # when clicking back to spectra

        self.mainlayout.addWidget( self.toolPanel )
        self.centerlayout.addWidget( self.configstack )
        self.centerlayout.addWidget(self.viewStack)

        self.mainlayout.addLayout( self.centerlayout )


        # FIXME: This is an unfortunate required hack to make sure figures all fit
        # Numbers come from manually adjusting window.
        # Should be able to reliably fit/adjust matplotlib figures to a specific canvas size
        self.setFixedSize(QSize(1100, 750))

        self.main.setLayout(self.mainlayout)
        self.setCentralWidget(self.main)

        self.show()

        self.threadpool = QThreadPool()
        logging.info("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())



    # FIXME: fugly wrapper to allow set tool on change
    def update_current_tool_from_item(self, item):
        self.current_tool = item.tool

    def onLoadData(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Load MaxQuant quantified data file', '', "Text Files (*.txt);;All Files (*.*);;")
        if filename:
            self.tools[0].enable()
            self.tools[0].config.set('filename', filename) # Autorun?
            self.tools[0].run_manual()

    def onLoadMsp(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Load modificationSpecificPeptides file', '', "Text Files (*.txt);;All Files (*.*);;")
        if filename:
            self.tools[-1].enable()
            self.tools[-1].config.set('filename_msp', filename) # Autorun?
            self.tools[-1].run_manual()


    def onLoadDesign(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Load experimental design file', '', "CSV Files (*.csv);;Text Files (*.txt);;All Files (*.*);;")
        if filename:
            self.tools[5].enable()
            self.tools[5].config.set('filename_design', filename) # Autorun?
            self.tools[5].run_manual()


    def onSaveData(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save processed data', '', "Pickle Files (*.pickle);;CSV Files (*.csv);;All Files (*.*);;")
        if filename:
            print(filename, _)
            # Get data from the tool 6 (filter) output
            td = self.tools[6].data
            print(td.keys())
            if 'data' in td and 'df' in td['data']:
                df = td['data']['df']
                ext = os.path.splitext(filename)[1]
                save_fn = {
                    '.csv': df.to_csv,
                    '.pickle': df.to_pickle,
                }.get(ext, None)
                if save_fn is not None:
                    save_fn(filename)



    def onSaveConfig(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save configuration', '', "Paddle Config File (*.paddle)")
        if filename:
            '''
            Paddle config file is a JSON format storing the tree export from the configuration for individual tools.
            Structure is as follows

            core/<core.config>
            tools/<tool.identifier>/<tool.config>
            '''
            configuration = {
                'version': __version__,
                'created': dt.datetime.now().strftime("%Y-%m-%dT%H:%M%SZ"),
                # Store core configuration for annotations, etc.
                'core': config.as_dict(),
                # Tool configuration
                'tools': {t.__class__.__name__: t.config.as_dict() for t in self.tools }
            }
            with open(filename, 'w') as f:
                json.dump(configuration, f, indent=4)

            self.setTitle(configuration_filename=filename)

    def onLoadConfig(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Load configuration', '', "Paddle Config File (*.paddle);;All files (*.*)")
        if filename:

            # Build an access list of all current tools for assignments
            # deactivate any tools not mapped (newer tools added since config saved)
            toolmap = {t.__class__.__name__:t for t in self.tools}

            with open(filename, 'rU') as f:
                configuration = json.load(f)

            config.set_many(configuration['core'])
            for t, c in configuration['tools'].items():
                tool = toolmap[t]
                tool.config.set_many(c)

                if tool.config.get('is_active'):
                    tool.enable()
                else:
                    tool.disable()

                del toolmap[t]

            # Deactive any remaining tools
            for t in toolmap.values():
                t.disable()

            self.setTitle(configuration_filename=filename)




    # Init application configuration
    def onResetSettings(self):
        # Reset the QSettings object on the QSettings Manager (will auto-fallback to defined defaults)
        settings.settings.clear()

    def onSaveAsImage(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save current figure', '', "Tagged Image File Format (*.tif);;"
                                                                                   "Portable Network Graphics (*.png);;"
                                                                                   "Scalable Vector Graphics (*.svg)")

        if filename:
            try:
                self.current_tool.data['fig'].savefig(filename, bbox_inches='tight')

            except KeyError:
                pass

    def onSaveAllImage(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save all figures', '', "Tagged Image File Format (*.tif);;"
                                                                                   "Portable Network Graphics (*.png);;"
                                                                                   "Scalable Vector Graphics (*.svg)")

        if filename:
            # We need to split the filename and add a suffix before the extension for the view name
            basename, ext = os.path.splitext(filename)

            for tool in self.tools:
                if tool.status != 'inactive' and tool.data is not None:
                    filename = "%s_(%s)%s" % (basename, tool.name, ext)

                    try:
                        tool.data['fig'].savefig(filename, bbox_inches='tight')

                    except KeyError:
                        pass


    def onAnnotateClasses(self):
        # Present list of sample labels and assigned class (editable ListWidget? Treewidget?)
        # Add/Remove
        # Load from file (CSV, two column)

        # Second list of mapped colours -> class name, QColorButton?
        dlg = ui.AnnotateClasses(self, config=config.as_dict())
        if dlg.exec_():
            # Get result
            config.set('annotation/sample_classes', dlg.config.get('annotation/sample_classes'))
            config.set('annotation/class_colors', dlg.config.get('annotation/class_colors'))

        self.onRefreshCurrentToolPlot()

    def onAnnotatePeaks(self):
        # List of peaks in the spectra to annotate with labels and bars
        # Load from CSV, three column
        # Label, Start, End

        # Second list of mapped colours -> class name, QColorButton?
        dlg = ui.AnnotatePeaks(self, config=config.as_dict())
        if dlg.exec_():
            # Get result
            config.set('annotation/peaks', dlg.config.get('annotation/peaks'))

        self.onRefreshCurrentToolPlot()


    def onRefreshCurrentToolPlot(self, *args, **kwargs):
        self.current_tool.plot()

    def onDoRegister(self):
        # Pop-up a registration window; take an email address and submit to
        # register for update-announce.
        dlg = ui.DialogRegister(self)
        if dlg.exec_():
            # Perform registration
            data = {
                'name': dlg.name.text(),
                'email': dlg.email.text(),
                'country': dlg.country.currentText(),
                'research': dlg.research.text(),
                'institution': dlg.institution.text(),
                'type': dlg.type.currentText(),
                'register': dlg.register.checked(),
            }
            # Send data to server;
            # http://register.pathomx.org POST

    def onAbout(self):
        dlg = ui.DialogAbout(self)
        dlg.exec_()

    def onExit(self):
        self.Close(True)  # Close the frame.

    def setTitle(self, configuration_filename=None, data_filename=None):
        if configuration_filename:
            self.window_title_metadata['configuration_filename'] = configuration_filename
        if data_filename:
            self.window_title_metadata['data_filename'] = data_filename

        self.setWindowTitle('%s - Paddle - %s' % (
            self.window_title_metadata['configuration_filename'],
            self.window_title_metadata['data_filename'],
        ))

def setIcons(app, path, filename):

    if sys.platform == 'win32': # Windows 32/64bit
        import ctypes
        app_identifier = app.organizationDomain() + "." + app.applicationName()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_identifier)

    icon = QIcon()
    for s in [16,32,64,128]:
        fn = os.path.join(path, filename.format(**{'d': s}))
        if os.path.exists(fn):
            icon.addFile(fn, QSize(s,s) )
    app.setWindowIcon(icon)

def main():

    locale = QLocale.system().name()

    # Load base QT translations from the normal place (does not include _nl, or _it)
    translator_qt = QTranslator()
    if translator_qt.load("qt_%s" % locale, QLibraryInfo.location(QLibraryInfo.TranslationsPath)):
        logging.debug(("Loaded Qt translations for locale: %s" % locale))
        app.installTranslator(translator_qt)

    # See if we've got a default copy for _nl, _it or others
    elif translator_qt.load("qt_%s" % locale, os.path.join(utils.scriptdir, 'translations')):
        logging.debug(("Loaded Qt (self) translations for locale: %s" % locale))
        app.installTranslator(translator_qt)

    # Load Paddle specific translations
    translator_mp = QTranslator()
    if translator_mp.load("paddle_%s" % locale, os.path.join(utils.scriptdir, 'translations')):
        logging.debug(("Loaded Paddle translations for locale: %s" % locale))
    app.installTranslator(translator_mp)

    import ctypes
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    window = MainWindow()

    logging.info('Ready.')

    setIcons(app, os.path.join(utils.scriptdir, 'static'), 'icon_{d}x{d}.png')



    app.exec_()  # Enter Qt application main loop


    logging.info('Exiting.')
