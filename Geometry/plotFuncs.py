from matplotlib import pyplot as plt


def initPlot(self):
        """
        Initializes the plot for vertical geometry measurements.
        """
        plt.figure()
        plt.title('Vertical Geometry Measurements')
        plt.xlabel('Frame Number')
        plt.ylabel('Length (pixels)')
        ax = plt.gca()
        ax.set_ylim(0, 500)
        lines = []
        for i in range(self._numVerticalROIs):
            lines.append(plt.plot(range(len(self._verticalGeometryHistory)), self._verticalGeometryHistory[:,i], label=f'ROI {i+1}'))
        plt.legend()
        return ax, lines
def updatePlot(self, ax, lines):
    """
    Updates the plot with the latest vertical geometry measurements.
    """
    for i in range(len(lines)):
        lines[i][0].set_data(range(len(self._verticalGeometryHistory)), self._verticalGeometryHistory[:, i])
    ax.set_xlim(max(0, len(self._verticalGeometryHistory)-501), len(self._verticalGeometryHistory)-1)
    
    plt.draw()
    plt.pause(0.01)
