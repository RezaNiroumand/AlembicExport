# -*- coding: UTF-8 -*-
# @date: 17/05/2023
# @file: MMO_SweepA Trails Alembic Cache Tool
# @version:1.0.0
# description: Export alembic Cache for SweepA Character and Repath the VRayMesh cache with the exported the abc.


__author__ = ['Kian_Hao', 'Sumesh']

import os
import sys
import maya.cmds as cmds
from __builtin__ import long
from PySide2 import QtCore, QtGui, QtUiTools, QtWidgets
from maya import OpenMayaUI as omu
import maya.OpenMaya as OM
from shiboken2 import wrapInstance

mainObject = omu.MQtUtil.mainWindow()
mayaMainWind = wrapInstance(long(mainObject), QtWidgets.QWidget)


class SweepATrailAbcExport(QtWidgets.QWidget):
    def __init__(self, parent=mayaMainWind):
        # import UI
        ui_path = os.path.abspath(os.path.dirname(__file__) + '/ui/alembic_export_ui.ui')
        super(SweepATrailAbcExport, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('MMO_SweepA Trails Alembic Cache Tool')
        self.ui = ui_path
        loader = QtUiTools.QUiLoader()
        uiFile = QtCore.QFile(self.ui)
        uiFile.open(QtCore.QFile.ReadOnly)
        self.theMainWidget = loader.load(uiFile)
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(2, 2, 2, 4)
        mainLayout.addWidget(self.theMainWidget)
        self.setLayout(mainLayout)

        try:
            show = "T:/dwtv/mmo/Maya_MMO/scenes/Animation"
            # show = "D:/WTP/Cache"
            # projectName = MMO
            self.projectName = os.environ["PROJNAME"]
            # Season = S01
            self.season = (cmds.file(q=True, sn=True)).split("/")[6]
            # episode = 101
            self.episode = (cmds.file(q=True, sn=True)).split("/")[7]
            # shotfiele = 010_001
            self.shotfile = (cmds.file(q=True, sn=True)).split("/")[8]
            self.cachefolder = "Cache/Fx/abc"
            # EX path = T:\dwtv\mmo\Maya_MMO\scenes\Animation\S_01\106\010_001\Cache\Fx\abc
            self.export_path = os.path.join(show, self.season, self.episode, self.shotfile, self.cachefolder)
        except:
            print("[INFO] Not in MMO scene file")

        # Find Widget
        self.open_cache_btn = self.theMainWidget.findChild(QtWidgets.QPushButton, "pushButton")
        self.exp_all_cache_btn = self.theMainWidget.findChild(QtWidgets.QPushButton, "pushButton_3")
        self.exp_sel_cache_btn = self.theMainWidget.findChild(QtWidgets.QPushButton, "pushButton_2")
        self.repath_vray_CB = self.theMainWidget.findChild(QtWidgets.QCheckBox, "checkBox")
        self.actionTutorial = self.theMainWidget.findChild(QtWidgets.QAction, "actionTutorial")

        # create singal
        self.open_cache_btn.clicked.connect(self.openAlembicFolder)
        self.exp_sel_cache_btn.clicked.connect(self.expo_sel)
        self.exp_all_cache_btn.clicked.connect(self.expo_all)
        self.actionTutorial.triggered.connect(self.openDoc)

    def expo_sel(self):
        abc_sel_geo = cmds.ls(sl=1)
        if abc_sel_geo:
            for geo in abc_sel_geo:
                expo_obj = geo.split(':')[-1]
                self.export_geo_alembic(expo_obj, geo)
                render_geo = geo.replace('_Mesh', '_Render_Mesh')
                if self.repath_vray_CB.isChecked():
                    self.vray_repath(render_geo, self.exportabc)
            QtWidgets.QMessageBox.information(self, 'Success!', 'AlemebicExported') 
        else:
            QtWidgets.QMessageBox.warning(self, 'Failed!', 'Select Mesh') 
        
        
        
    def vray_repath(self, obj, export):
        vrray_cache_query = cmds.listRelatives(obj, c=1)
        for vray in vrray_cache_query:
            if cmds.objectType(vray) == 'mesh':
                pp_value = cmds.listConnections(vray + '.inMesh', d=False, s=True)
                for pp in pp_value:
                    if cmds.objectType(pp) == 'VRayMesh':
                        cmds.setAttr(pp + ".fileName", export, type='string')

    def expo_all(self):
        parent_grp = cmds.ls('*:MMO_SweepsA_Fx:FX_Trail_MASH_Grp')
        if parent_grp:
            for grp in parent_grp:
                child_mesh = cmds.listRelatives(grp, c=1)
                for geo in child_mesh:
                    expo_obj = geo.split(':')[-1]
                    self.export_geo_alembic(expo_obj, geo)
                    render_geo = geo.replace('_Mesh', '_Render_Mesh')
                    if self.repath_vray_CB.isChecked():
                        self.vray_repath(render_geo, self.exportabc)
            QtWidgets.QMessageBox.information(self, 'Success!', 'AlemebicExported')
        else:
            QtWidgets.QMessageBox.warning(self, 'Failed!', 'No SweepA Fx mesh found')        
         
        
    def export_geo_alembic(self, obj, geo):
        minTime = cmds.playbackOptions(q=True, min=True)
        maxTime = cmds.playbackOptions(q=True, max=True)
        if not os.path.exists(self.export_path):
            os.makedirs(self.export_path)
        shotname = self.projectName + "_" + self.episode + "_" + self.shotfile
        self.exportabc = self.export_path + "/" + obj + ".abc"
        self.exportabc = self.exportabc.replace('\\', '/')
        ac_command = "-frameRange " + str(int(minTime)) + " " + str(
            int(maxTime)) + " -stripNamespaces -uvWrite -worldSpace -root " + geo + " -file " + self.exportabc
        if cmds.ogs(q=True, pause=True):
            pass
        else:
            cmds.ogs(pause=True)
        cmds.AbcExport(j=ac_command)
        # cmds.ogs(pause=True)
        OM.MGlobal.displayInfo("[INFO] exported" + self.exportabc)
        return self.exportabc

    def openDoc(self):
        #filepath = 
        os.startfile(os.path.abspath(os.path.dirname(__file__) + '/doc/Alembic_Cache_Tool.pdf'))
                     
    def openAlembicFolder(self):
        ex = self.export_path
        if os.path.exists(ex):
            os.startfile(ex)
        else:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Missing Alembic Folder Please Export And Try')

###########################################
if __name__ == '__main__':
    main()