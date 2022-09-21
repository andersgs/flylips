import math
import pathlib
import numpy as np
from scipy import optimize
from skimage.measure import EllipseModel
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.offsetbox import AnchoredText

class Wing(EllipseModel):
    """
    A class to represent a wing data from a fly
    """
    def __init__(self, data: pathlib.Path):
        super().__init__()
        self.data = data
        self.name = self.data.stem 
    def parse_data(self):
        """
        Data is a text file with three columns:
        id, x, y
        One or more rows with x=0 and y=0 indicate the delimiter between
        the coordinates used to estiamte the ellipse and the coordinaates
        for which we want to estimate the polar coordinates.
        Return two numpy arrays, one for the ellipse and one for the
        coordinates for which we want to estimate the polar coordinates.
        """
        with open(self.data) as f:
            lines = f.readlines()
        ellipse = []
        polar = []
        switch = False
        for line in lines:
            try:
                _, x, y = line.strip().split()
            except ValueError:
                continue
            if x == '0' and y == '0':
                switch = True
                continue
            if switch:
                polar.append([int(x), int(y)])
            else:
                ellipse.append([int(x), int(y)])
        self.xy = np.array(ellipse)
        self.polar = np.array(polar)
        if self.xy.shape[0] < 6:
            raise ValueError("Not enough data to fit ellipse. We need at least 6 points.")

    def fit(self):
        if not hasattr(self, 'xy'):
            self.parse_data()
        if self.params is None:
            fit = self.estimate(self.xy)
            if not fit:
                raise ValueError("Could not estimate ellipse")
        _, _, a, b, _ = self.params
        self.size = math.sqrt(a * b)
        self.shape = b / a
        return self.params
    
    def get_polar_coords(self):
        """
        Get polar coordinates from the 10 points along the Ellipse. 

        This implemention is based on the original BASIC code from ASALK.
        """
        if self.params is None:
            self.fit()
        x0, y0, _, _, theta = self.params
        self.trans_coords = []
        for x, y in self.polar:
            xt = (x - x0) * math.cos(-theta) - (y - y0) * math.sin(-theta)
            yt = (x - x0) * math.sin(-theta) + (y - y0) * math.cos(-theta)
            self.trans_coords.append([xt, yt])
        if self.trans_coords[0][0] <= 0:
            self.trans_coords = [-1 * x for x in self.polar_trans]
        if self.trans_coords[0][1] <= 0:
            self.trans_coords = [-1 * y  for y in self.trans_coords]
        dist = [math.sqrt(x**2 + y**2) for x, y in self.trans_coords]
        angle = []
        for x,y in self.trans_coords:
            if x > 0 and y > 0:
                angle.append(math.atan(y/x))
            elif x > 0 and y < 0:
                angle.append(math.atan(y/x) + 2 * math.pi)
            elif x < 0 and y > 0:
                angle.append(math.atan(y/x) + math.pi)
            elif x < 0 and y < 0:
                angle.append(math.atan(y/x) + math.pi)
            else:
                raise ValueError(f"Invalid polar coordinates: x={x}; y={y}")
        self.trans_coords = np.array(self.trans_coords)
        self.polar_coords = np.array([angle, dist]).T
        return self.polar_coords
        
    def plot(self, outfile=None):
        """
        Use matplotlib to plot the ellipse and the XY data
        """
        if self.params is None:
            self.fit()
        if not hasattr(self, 'rcoef'):
            self.get_correlation()
        if outfile is None:
            outfile = self.name + ".png"
        coef_label = f"$\\it{{r}}$ = {self.rcoef:.5f}"
        fig, ax = plt.subplots()
        at = AnchoredText(coef_label, loc='upper left', frameon=True, prop=dict(size=10))
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
        ax.add_artist(at)
        ax.scatter(self.xy[:, 0], self.xy[:, 1])
        ax.scatter(self.polar[:, 0], self.polar[:, 1], color='red')
        ellipse = Ellipse(xy=self.params[0:2], width= 2*self.params[2],
                          height= 2*self.params[3], angle=np.rad2deg(self.params[4]),
                          fill=False)
        ax.add_patch(ellipse)
        plt.title(f"Sample: {self.name}")
        plt.savefig(outfile)
        plt.close()

    def plot_anchor_points(self, outfile=None):
        """
        Plot the anchor points and the residuals
        """
        if self.params is None:
            self.fit()
        if not hasattr(self, 'polar_coords'):
            self.get_polar_coords()
        if outfile is None:
            outfile = self.name + "_anchor.png"
        fig, ax = plt.subplots()
        ellipse = Ellipse(xy=[0,0], width= 2*self.params[2],
                          height= 2*self.params[3], angle=0,
                          fill=False)
        ax.add_patch(ellipse)
        ax.scatter(0, 0, color = "blue", s = 50, zorder = 20)
        for x,y in self.trans_coords:
            ax.plot([0,x], [0,y])
            ax.scatter(x, y)
        plt.title(f"Sample: {self.name}")
        plt.savefig(outfile)
        plt.close()

    def get_residuals(self):
        if not hasattr(self, 'w'):
            self.fit()
        if not hasattr(self, 'res'):
            self.res = self.residuals(self.xy)
        return self.res

    def get_rmse(self):
        """
        Calculate the root mean squared error between the XY data and the closest 
        point on the ellipse
        """
        if self.params is None:
            self.fit()
        if not hasattr(self, 'rmse'):
            self.rmse = np.sqrt(np.mean(self.get_residuals()**2))
        return self.rmse
    
    def get_correlation(self):
        """
        Calculate the correlation between the observed Y and the predicted Y 
        on the ellipse
        """

        if self.params is None:
            self.fit()

        xc, yc, a, b, theta = self.params

        ctheta = math.cos(theta)
        stheta = math.sin(theta)

        x = self.xy[:, 0]
        y = self.xy[:, 1]

        N = self.xy.shape[0]

        def fun(t, xi, yi):
            ct = math.cos(t)
            st = math.sin(t)
            xt = xc + a * ctheta * ct - b * stheta * st
            yt = yc + a * stheta * ct + b * ctheta * st
            return (xi - xt) ** 2 + (yi - yt) ** 2
        
        def pred_y(t):
            ct = math.cos(t)
            st = math.sin(t)
            yt = yc + a * stheta * ct + b * ctheta * st
            return yt

        y_hat = np.empty((N, ), dtype=np.float64)

        # initial guess for parameter t of closest point on ellipse
        t0 = np.arctan2(y - yc, x - xc) - theta

        # determine shortest distance to ellipse for each point
        for i in range(N):
            xi = x[i]
            yi = y[i]
            # faster without Dfun, because of the python overhead
            t, _ = optimize.leastsq(fun, t0[i], args=(xi, yi))
            y_hat[i] = pred_y(t)
        
        # calculate correlation
        self.rcoef = np.corrcoef(y, y_hat)[0, 1]
        return self.rcoef

    def report(self, outfile, include_header=False, sep="\t"):
        """
        Output the estimates of size and shape and the polar coordinates
        of the anchor points
        """
        if self.params is None:
            self.fit()
        if not hasattr(self, 'polar_coords'):
            self.get_polar_coords()
        if not hasattr(self, 'rcoef'):
            self.get_correlation()
        if not hasattr(self, 'rmse'):
            self.get_rmse()
        if include_header:
            print("sample_id", "parameter", "value", sep=sep, file=outfile)
        print(self.name, "semi-major axis", self._format_number(self.params[2]), sep=sep, file=outfile)
        print(self.name, "semi-minor axis", self._format_number(self.params[3]), sep=sep, file=outfile)
        print(self.name, "theta", self._format_number(self.params[4]), sep=sep, file=outfile)
        print(self.name, "correlation", self._format_number(self.rcoef), sep=sep, file=outfile)
        print(self.name, "rmse", self._format_number(self.rmse), sep=sep, file=outfile)
        print(self.name, "size", self._format_number(self.size), sep=sep, file=outfile)
        print(self.name, "shape", self._format_number(self.shape), sep=sep, file=outfile)
        for i, coords in enumerate(self.polar_coords):
            angle, dist = coords
            print(self.name, f"a_{i+1}", self._format_number(np.rad2deg(angle)), sep=sep, file=outfile)
            print(self.name, f"d_{i+1}", self._format_number(dist), sep=sep, file=outfile)

    @staticmethod
    def _format_number(number):
        """
        Format a number to 4 decimal places
        """
        return "{:.4f}".format(number)