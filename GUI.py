import sys
import segyio
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QSlider, QHBoxLayout, QStatusBar)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Function to load a SEGY file and return the data cube and axes details
def load_segy_file(file_path):
    with segyio.open(file_path, iline=segyio.tracefield.TraceField.SourceEnergyDirectionExponent, 
                     xline=segyio.tracefield.TraceField.CDP) as f:
        il, xl, t = f.ilines, f.xlines, f.samples
        d = segyio.cube(f)
    return d, il, xl, t

# Main GUI Application
class SeismicInversionGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.d, self.il, self.xl, self.t = None, None, None, None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Seismic Inversion GUI')
        self.setGeometry(100, 100, 1000, 600)  # Adjusted for better proportion

        layout = QVBoxLayout()

        # File loading
        self.loadButton = QPushButton('Load SEGY File', self)
        self.loadButton.clicked.connect(self.loadFile)
        layout.addWidget(self.loadButton)

        # Display area for SEGY file data
        self.canvas = FigureCanvas(Figure(figsize=(8, 6)))  # Adjusted figure size
        layout.addWidget(self.canvas)

        # Slider for adjusting X-axis width
        self.xAxisSlider = QSlider(Qt.Horizontal)
        self.xAxisSlider.setMinimum(10)
        self.xAxisSlider.setMaximum(100)
        self.xAxisSlider.setValue(50)  # Default value
        self.xAxisSlider.valueChanged[int].connect(self.updatePlot)
        layout.addWidget(self.xAxisSlider)

        # Status Bar for information
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

    def loadFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open SEGY File", "", "SEGY Files (*.segy)")
        if fileName:
            self.d, self.il, self.xl, self.t = load_segy_file(fileName)
            self.plot_data()
            self.statusBar.showMessage(f"Inline: {len(self.il)}, Crossline: {len(self.xl)}, Time Interval: {self.t[1] - self.t[0]}ms")

    def plot_data(self):
        if self.d is not None:
            ax = self.canvas.figure.subplots()
            ax.clear()
            seismic_plot = ax.imshow(self.d[len(self.il)//2].T, cmap='seismic', aspect='auto', extent=(self.xl[0], self.xl[-1], self.t[-1], self.t[0]))
            ax.set_title('Seismic data')
            ax.set_xlabel('Crossline')
            ax.set_ylabel('Time (s)')
            self.canvas.figure.colorbar(seismic_plot, ax=ax, orientation='vertical')
            self.canvas.draw()

    def updatePlot(self, value):
        if self.d is not None:
            self.canvas.figure.set_size_inches(value / 10.0, 6)
            self.plot_data()

# Run the application
app = QApplication(sys.argv)
ex = SeismicInversionGUI()
ex.show()
sys.exit(app.exec_())
