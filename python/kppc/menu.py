import pya
from pathlib import Path
import kppc
import json
import importlib

import logging
import multiprocessing

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

        self.vbox.addWidget(self.scrollarea)
        self.optionvbox = pya.QVBoxLayout(self.optionswidget)
        categorydict = vars(kppc.settings)

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


def dialog():
    dialog = Dialog(pya.Application.instance().main_window())
    dialog.exec_()


def set_settings():
    kppc.settings.Multithreading._Threads_MAX = multiprocessing.cpu_count()
    kppc._fh.setLevel(logging.getLevelName(kppc.settings.Logging.LogfileLevel[1:][kppc.settings.Logging.LogfileLevel[0]]))
    kppc._ch.setLevel(logging.getLevelName(kppc.settings.Logging.StreamLevel[1:][kppc.settings.Logging.StreamLevel[0]]))