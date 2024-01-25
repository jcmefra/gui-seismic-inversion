import sys
import segyio
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLabel, QSlider, QHBoxLayout, QStatusBar, QLineEdit, QProgressBar, QGridLayout)
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
        self.setGeometry(100, 100, 1200, 800)  # Adjusted for better proportion

        mainLayout = QVBoxLayout()

        # File loading
        self.loadButton = QPushButton('Load SEGY File', self)
        self.loadButton.clicked.connect(self.loadFile)
        mainLayout.addWidget(self.loadButton)

        # Display area for SEGY file data
        self.canvas = FigureCanvas(Figure(figsize=(10, 8)))  # Adjusted figure size
        mainLayout.addWidget(self.canvas)

        # Slider for adjusting X-axis width
        self.xAxisSlider = QSlider(Qt.Horizontal)
        self.xAxisSlider.setMinimum(10)
        self.xAxisSlider.setMaximum(100)
        self.xAxisSlider.setValue(50)  # Default value
        self.xAxisSlider.setFixedWidth(180)  # Smaller fixed width for the slider
        self.xAxisSlider.valueChanged[int].connect(self.updatePlot)
        self.xAxisSlider.setVisible(False)  # Hidden until a file is loaded

        # Status Bar for information
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Progress Bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setFixedWidth(180)  # Smaller fixed width for the progress bar
        self.progressBar.setVisible(False)  # Hidden until needed

        # Inline, Crossline, Timeslice inputs and buttons
        inputLayout = QGridLayout()
        self.inlineInput = QLineEdit(self)
        self.crosslineInput = QLineEdit(self)
        self.timesliceInput = QLineEdit(self)
        self.plotInlineButton = QPushButton('Plot Inline', self)
        self.plotCrosslineButton = QPushButton('Plot Crossline', self)
        self.plotTimeSliceButton = QPushButton('Plot Time Slice', self)
        self.plotInlineButton.clicked.connect(lambda: self.plot_data('inline'))
        self.plotCrosslineButton.clicked.connect(lambda: self.plot_data('crossline'))
        self.plotTimeSliceButton.clicked.connect(lambda: self.plot_data('timeslice'))
        inputLayout.addWidget(QLabel('Inline:'), 0, 0)
        inputLayout.addWidget(self.inlineInput, 0, 1)
        inputLayout.addWidget(self.plotInlineButton, 0, 2)
        inputLayout.addWidget(QLabel('Crossline:'), 1, 0)
        inputLayout.addWidget(self.crosslineInput, 1, 1)
        inputLayout.addWidget(self.plotCrosslineButton, 1, 2)
        inputLayout.addWidget(QLabel('Time Slice:'), 2, 0)
        inputLayout.addWidget(self.timesliceInput, 2, 1)
        inputLayout.addWidget(self.plotTimeSliceButton, 2, 2)

        # Add the slider, progress bar, and inputLayout to the bottom of the main layout
        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.progressBar)
        bottomLayout.addLayout(inputLayout)
        bottomLayout.addWidget(self.xAxisSlider)
        mainLayout.addLayout(bottomLayout)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def loadFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open SEGY File", "", "SEGY Files (*.segy)")
        if fileName:
            self.progressBar.setVisible(True)
            self.progressBar.setValue(20)
            self.d, self.il, self.xl, self.t = load_segy_file(fileName)
            self.progressBar.setValue(100)
            self.plot_data('inline')  # Default plot
            self.statusBar.showMessage(f"Loaded file: {fileName} | Total Inlines: {len(self.il)}, Crosslines: {len(self.xl)}, Time Slices: {len(self.t)}")
            self.progressBar.setVisible(False)
            self.xAxisSlider.setVisible(True)  # Show the slider after file is loaded


    def plot_data(self, plot_type):
        if self.d is not None:
            self.canvas.figure.clf()  # Clear the entire figure before plotting a new one
            ax = self.canvas.figure.subplots()

            # Initialize info_message
            info_message = ""

            # Determine what to plot based on the plot_type and provided index values
            if plot_type == 'inline':
                index = int(self.inlineInput.text()) if self.inlineInput.text().isdigit() else len(self.il) // 2
                seismic_slice = self.d[index, :, :].T
                title = f'Seismic Inline {self.il[index]}'
                info_message = f"Plotting Inline: {self.il[index]} | Total Inlines: {len(self.il)}, Crosslines: {len(self.xl)}, Time Slices: {len(self.t)}"
            elif plot_type == 'crossline':
                index = int(self.crosslineInput.text()) if self.crosslineInput.text().isdigit() else len(self.xl) // 2
                seismic_slice = self.d[:, index, :].T
                title = f'Seismic Crossline {self.xl[index]}'
                info_message = f"Plotting Crossline: {self.xl[index]} | Total Inlines: {len(self.il)}, Crosslines: {len(self.xl)}, Time Slices: {len(self.t)}"
            elif plot_type == 'timeslice':
                index = int(self.timesliceInput.text()) if self.timesliceInput.text().isdigit() else len(self.t) // 2
                seismic_slice = self.d[:, :, index].T
                title = f'Seismic Time Slice {self.t[index]} ms'
                info_message = f"Plotting Time Slice: {self.t[index]} ms | Total Inlines: {len(self.il)}, Crosslines: {len(self.xl)}, Time Slices: {len(self.t)}"

            # Plot the selected slice
            seismic_plot = ax.imshow(seismic_slice, cmap='seismic', aspect='auto', 
                                    extent=(self.xl[0], self.xl[-1], self.t[-1], self.t[0]))
            ax.set_title(title)
            ax.set_xlabel('Crossline')
            ax.set_ylabel('Time (ms)')
            self.canvas.figure.colorbar(seismic_plot, ax=ax, orientation='vertical')
            self.canvas.draw()
            
            # Update the status bar with the current viewing slice and the total counts
            self.statusBar.showMessage(info_message)


    def updatePlot(self, value):
        if self.d is not None:
            # Adjust the width of the plot based on the slider value
            new_width = value / 10.0
            self.canvas.figure.set_size_inches(new_width, 8)
            self.plot_data('inline')  # Re-plot the default or current view

# Run the application
app = QApplication(sys.argv)
ex = SeismicInversionGUI()
ex.show()
sys.exit(app.exec_())

