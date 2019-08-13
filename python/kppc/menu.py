import pya
from pathlib import Path
import kppc
import json
import importlib

import logging
import multiprocessing
import shutil
from importlib.util import find_spec
from importlib import reload
import subprocess
import kppc

class Dialog(pya.QDialog):

    def __init__(self, parent=None):
        self.settingspath = kppc.settings_path
        self.vbox = pya.QVBoxLayout()
        self.setLayout(self.vbox)
        self.settings = {}
        self.setWindowTitle("KLayoutPhotonicPCells Settings")
        self.setMinimumWidth(300)
        vsize = len(vars(kppc.settings))

        self.scrollarea = pya.QScrollArea(self)
        self.optionswidget = pya.QWidget(self)
        self.scrollarea.setWidget(self.optionswidget)
        self.scrollarea.setWidgetResizable(True)

        #self.vbox.addWidget(self.scrollarea)
        self.optionvbox = pya.QVBoxLayout(self.optionswidget)
        categorydict = vars(kppc.settings)
        
        hbSplitter = pya.QHBoxLayout()        
        vboxbuttons = pya.QVBoxLayout()
        self.vbox.addLayout(hbSplitter)
        hbSplitter.addWidget(self.scrollarea)
        hbSplitter.addLayout(vboxbuttons)
        
        recompileButton = pya.QPushButton('Recompile',self)
        recompileButton.clicked(self.recompile)
        vboxbuttons.addWidget(recompileButton)
        
        resetButton = pya.QPushButton('Restore Defaults',self)
        resetButton.clicked(self.restoreDefaults)
        vboxbuttons.addWidget(resetButton)
        
        vboxbuttons.addStretch()
        
        for i, cat in enumerate(categorydict.keys()):

            groupbox = pya.QGroupBox(cat, self)
            self.optionvbox.addWidget(groupbox)
            vb = pya.QVBoxLayout(groupbox)
            self.settings[cat] = {}

            settingdict = vars(categorydict[cat])

            for j, setting in enumerate(settingdict):
                if setting[0] == '_':
                    continue
                opt = settingdict[setting]
                
                desc_str = f"_{setting}_DESC"
                if desc_str in settingdict:
                    desc = settingdict[desc_str]
                else:
                    desc = setting
                
                if isinstance(opt, bool):
                    v = pya.QCheckBox(desc, self)
                    vb.addWidget(v)
                    v.toggeled = v.setChecked(opt)
                    self.settings[cat][setting] = (v, lambda x: bool(x.checkState.to_i()))
                elif isinstance(opt, int):
                    l = pya.QHBoxLayout()
                    vb.addLayout(l)
                    t = pya.QLabel(desc, self)
                    v = pya.QSpinBox(self)
                    l.addWidget(v)
                    l.addWidget(t)
                    l.addStretch()
                    v.value = opt
                    minset = f"_{setting}_MIN"
                    maxset = f"_{setting}_MAX"
                    if minset in settingdict:
                        v.minimum = settingdict[minset]
                    if maxset in settingdict:
                        v.maximum = settingdict[maxset]
                    self.settings[cat][setting] = (v, lambda x: x.value)
                elif isinstance(opt,list):
                    v = pya.QComboBox(self)
                    l = pya.QHBoxLayout()
                    index = int(opt[0])
                    strs = opt[1:]
                    for i in strs:
                        v.addItem(i)
                    v.currentIndex=index
                    vb.addLayout(l)
                    l.addWidget(v)
                    d = pya.QLabel(desc,self)
                    l.addWidget(d)
                    l.addStretch()
                    self.settings[cat][setting] = (v, lambda x,l=strs: [x.currentIndex] + l)
                else:
                    continue
        self.vbox.addStretch()

        save = pya.QPushButton("Save", self)
        save.clicked = self.save
        abort = pya.QPushButton("Cancel", self)
        abort.clicked = self.abort
        self.hbox = pya.QHBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.hbox.addWidget(abort)
        self.hbox.addStretch()
        self.hbox.addWidget(save)

    def abort(self, checked):
        self.reject()

    def save(self, checked):
        for c in self.settings.keys():
            v = self.settings[c]
            for s in v.keys():
                setattr(getattr(kppc.settings, c), s, self.settings[c][s][1](self.settings[c][s][0]))
        sdict = {}
        for k in kppc.settings.__dict__.keys():
            sdict[k] = {}
            for kk in kppc.settings.__dict__[k].__dict__.keys():
                sdict[k][kk] = kppc.settings.__dict__[k].__dict__[kk]
        with open(self.settingspath, 'w') as f:
            json.dump(sdict, f, indent=4, sort_keys=False)
        importlib.reload(kppc)
        set_settings()
        self.accept()
        
    def restoreDefaults(self,checked):
        dir_path = Path(__file__).parent.parent.parent
        sf = dir_path / "settings.json"
        df = dir_path / "default-settings.json"
        
        msg = pya.QMessageBox(pya.QMessageBox.Warning,
                              "Reload Default Settings",
                              "Restore default Settings?\nThis will close this dialog and reload the default settings.",
                              pya.QMessageBox.StandardButton.Cancel | pya.QMessageBox.StandardButton.Ok,
                              self)
        #msg.setStandardButtons(pya.QMessageBox.StandardButton.Ok | pya.QMessageBox.StandardButton.Cancel)
        res = msg.exec_()
        if res == pya.QMessageBox.Ok.to_i():
            shutil.copy(df,sf)
            kppc.load_settings()
            importlib.reload(kppc.photonics)
            importlib.reload(kppc.drc)
            self.accept()
        else:
            self.reject()
        
    def recompile(self,checked):
    
        dir_path = Path(__file__).parent / "drc"
        cpp_path = dir_path.parent.parent.parent / "cpp"
    
        src_dir = cpp_path / "source"
        kppc.logger.info('Trying to Compile')

        (cpp_path / 'build').mkdir(parents=True, exist_ok=True)

        p1 = subprocess.Popen(['python3', 'setup.py', 'build_ext', '-b', dir_path], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, cwd=src_dir)
        p2 = subprocess.Popen(['python3', 'setup_cc.py', 'build_ext', '-b', dir_path], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, cwd=src_dir)
        p3 = subprocess.Popen(
            ('g++', cpp_path / 'source/CleanerMain.cpp', cpp_path / 'source/CleanerSlave.cpp',
             cpp_path / 'source/DrcSl.cpp', cpp_path / 'source/SignalHandler.cpp', '-o', cpp_path / 'build/cleanermain',
             '-isystem',
             '/usr/include/boost/', '-lboost_system', '-pthread', '-lboost_thread', '-lrt'), stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, cwd=src_dir)
        p1.wait()
        p2.wait()
        p3.wait()
        if p1.returncode == 0 and p2.returncode == 0 and p3.returncode == 0:
            msg = pya.QMessageBox(pya.Application.instance().main_window())
            msg.text = 'The compilation was successful'
            msg.Title = 'Compilation'
            msg.exec_()
            reload(kppc.drc)
        else:
            msg = pya.QMessageBox(pya.Application.instance().main_window())
            msg.text = 'The compilation failed. Please compile manually\n Return Code slcleaner: {}\n Return Code ' \
                       'cleanermaster: {}\n Return Code: {}\n}'.format(p1.returncode, p2.returncode, p3.returncode)
            msg.Title = 'Compilation'
            msg.exec_()
            kppc.logger.error(f'Compilation failed. Return codes: {p1.returncode} , {p2.returncode} {p3.returncode}')


def dialog():
    dialog = Dialog(pya.Application.instance().main_window())
    dialog.exec_()


def set_settings():
    kppc.settings.Multithreading._Threads_MAX = multiprocessing.cpu_count()
    kppc._fh.setLevel(logging.getLevelName(kppc.settings.Logging.LogfileLevel[1:][kppc.settings.Logging.LogfileLevel[0]]))
    kppc._ch.setLevel(logging.getLevelName(kppc.settings.Logging.StreamLevel[1:][kppc.settings.Logging.StreamLevel[0]]))