from Task4 import Ui_MainWindow
from PyQt5 import QtGui, QtWidgets
import sys , qdarkstyle , logging
import numpy as np
from Spectrogram import Spectrogram
from Sound import Sound
from database import Database

logging.basicConfig(filename='logger.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger()
#ناقص حوار مقارنة الفيتشرز كلهاوال weights

class Main(Ui_MainWindow):

    def __init__(self,MainWindow):
        super(Main,self).setupUi(MainWindow)
        self.Loadbtns = [self.Opensong1, self.Opensong2]
        self.audFiles = [None, None]    # List Containing both songs
        self.SamplingRate = [0, 0]
        self.similarityResults = []
        for i in range(2):
            self.Loadbtns[i].clicked.connect(lambda checked, i=i:self.loadFile(i))
        self.Mix.clicked.connect(self.Searching)
        self.Mixing_Slider.valueChanged.connect(self.updateratio)
    
    def updateratio(self):
        self.Percentage.setText("{s} : {n}".format(
            n=self.Mixing_Slider.value(), s=(100-self.Mixing_Slider.value())))

    def loadFile(self,flag):
        self.statusbar.showMessage("Loading Song {}".format(flag+1))
        audFile,_ = QtWidgets.QFileDialog.getOpenFileName(None, "Load Song {}".format(flag+1),
                                                                   filter="*.mp3")
        logger.info("Song {} Loaded".format(flag+1))

        if audFile == "":
            logger.info("loading cancelled")
            self.statusbar.showMessage("Loading cancelled")
        else:
            logger.info("starting extraction of data")
            try:
               audData , audRate = Sound.ReadFile(audFile)
               
            except:
                self.statusbar.showMessage("Error Uploading File")
                logger.warning("Error Uploading File")
                return
                
            logger.info("extraction successful")
            self.audFiles[flag] = audData
            self.SamplingRate[flag] = audRate
            self.Loadbtns[flag].setText(audFile.split('/')[-1])
            self.statusbar.showMessage("Loading Done")
            logger.info("Loading done")
            self.Mix.setEnabled(True)
            if all(type(element) == np.ndarray for element in self.audFiles):
                self.Mixing_Slider.setEnabled(True)
                self.Percentage.show()


    def Searching(self):

        self.statusbar.showMessage("Finding Matches ...")
        logger.info("starting searching process")
        if any(type(element) != np.ndarray for element in self.audFiles):
            for i in range(2): 
                if self.audFiles[i] is not None:
                    logger.info("loaded only one song")
                    self.audMix = self.audFiles[i]    

        elif all(type(element) == np.ndarray for element in self.audFiles):
            logger.info("loaded 2 songs")
            logger.info("starting Mixing")
            self.audMix = Sound.mix(self.audFiles, max(self.SamplingRate), self.Mixing_Slider.value()/100)


        self.spectrogram = Spectrogram.Features(self.audMix, max(self.SamplingRate))[0]
        self.testHash = Spectrogram.Hash(self.spectrogram)
        logger.info("Mixing Done")
        self.statusbar.clearMessage()
        self.check_similarity()

    def check_similarity(self):
        self.similarityResults.clear()
        logger.info("Searching similarities")
        self.statusbar.showMessage("Searching Similarities")
        for songName, songHashes in Database.read("DataBase.json"):
            spectroDiff = Spectrogram.getSimilarity(
                songHashes["spectrogram_hash"], self.testHash)
            self.similarityResults.append((songName, spectroDiff*100))

        self.similarityResults.sort(key=lambda x: x[1], reverse=True)
        # print(self.similarityResults)
        logger.info("Searching and getting similarities Done")
        self.statusbar.showMessage("Getting Similarities Done")
        logger.info("Searching similarities Done")
        self.statusbar.showMessage("Searching Similarities Done")
        self.fill_table()

    def fill_table(self):
        self.Similarity_Results.clear()
        self.Similarity_Results.setRowCount(0)
        self.Similarity_Results.setHorizontalHeaderLabels(
            ["Matches Found", "Similarity Percentage"])

        logger.info("Showing Results")
        self.statusbar.showMessage("Showing Results")
        for row in range(len(self.similarityResults)):
            self.Similarity_Results.insertRow(row)

            self.Similarity_Results.setItem(row, 0, QtWidgets.QTableWidgetItem(
                self.similarityResults[row][0]))
            self.Similarity_Results.setItem(row, 1, QtWidgets.QTableWidgetItem(
                str(round(self.similarityResults[row][1], 2))+"%"))

        for col in range(2):
            self.Similarity_Results.horizontalHeader().setSectionResizeMode(
                col, QtWidgets.QHeaderView.Stretch)
            self.Similarity_Results.horizontalHeaderItem(
                col).setBackground(QtGui.QColor(57, 65, 67))
        self.similarityResults.clear()

        logger.info("Results Done")
        self.statusbar.showMessage("Results Done")



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow = QtWidgets.QMainWindow()
    ui = Main(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())