from typing import List
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse
from matplotlib.cm import viridis
from flylips.wing import Wing


def combined_plot(wings: List[Wing]):
    """
    A function to plot the inferred ellipses for each wing.

    It will take a list of Wing objects and plot the inferred ellipse on the same
    plot. The plot will be saved to the current working directory.
    """
    fig, ax = plt.subplots()
    colors = np.linspace(0, 1, len(wings))
    custom_legend = []
    labels = []
    for ix,wing in enumerate(wings):
        _, _, a, b, _ = wing.params
        if a < b:
            a, b = b, a
        ellipse = Ellipse(xy=[0,0], width=2*a, height=2*b, angle = 0, fill=False, color=viridis(colors[ix]), label = wing.name)
        custom_legend.append(Line2D([0], [0], color=viridis(colors[ix])))
        labels.append(wing.name)
        ax.add_patch(ellipse)
    plt.axis('equal')
    plt.legend(custom_legend, labels)
    plt.savefig('combined.png')
    plt.close()
