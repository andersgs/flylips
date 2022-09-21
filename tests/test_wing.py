from flylips.wing import Wing

def test_parse_data(test_data):
    """
    Test the Wing class parse data method
    """
    w = Wing(test_data)
    w.parse_data()
    assert w.xy.shape == (27, 2)
    assert w.polar.shape == (10, 2)

def test_fit(test_data):
    """
    Test the Wing class fit method
    """
    w = Wing(test_data)
    w.fit()
    assert len(w.params) == 5

def test_residuals(test_data):
    """
    Test the Wing class residuals method
    """
    w = Wing(test_data)
    w.get_residuals()
    assert w.res.shape == (27,)

def test_plot(test_data):
    """
    Test the Wing class plot method
    """
    w = Wing(test_data)
    w.plot()
    assert True

def test_rmse(test_data):
    """
    Test the Wing class rmse method
    """
    w = Wing(test_data)
    w.get_rmse()
    assert w.rmse > 0 

def test_correlation(test_data):
    """
    Test the Wing class correlation method
    """
    w = Wing(test_data)
    w.get_correlation()
    assert w.rcoef > 0 and w.rcoef <=1

def test_polar_coords(test_data):
    """
    Test the Wing class polar_coords method
    """
    w = Wing(test_data)
    w.get_polar_coords()
    print(w.polar_coords)
    assert w.polar_coords.shape == (10, 2)

def test_plot_anchor_points(test_data):
    """
    Test the Wing class plot_anchor_points method
    """
    w = Wing(test_data)
    w.plot_anchor_points()
    assert True

def test_report(test_data):
    """
    Test the Wing class report method
    """
    w = Wing(test_data)
    w.report()

    assert False