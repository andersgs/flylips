from typing import List
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from flylips.wing import Wing


def combined_plot(wings: List[Wing]):
    """
    A function to plot the inferred ellipses for each wing.

    It will take a list of Wing objects and plot the inferred ellipse on the same
    plot. The plot will be saved to the current working directory.
    """
    fig, ax = plt.subplots()
    for wing in wings:
        _, _, a, b, _ = wing.params
        if a < b:
            a, b = b, a
        ellipse = Ellipse(xy=[0,0], width=2*a, height=2*b, angle = 0, fill=False)
        ax.add_patch(ellipse)
    plt.axis('equal')
    plt.savefig('combined.png')
    plt.close()
