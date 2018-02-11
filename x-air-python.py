import wpf

from System.Windows import Window

class x_air_python(Window):
    def __init__(self):
        wpf.LoadComponent(self, 'x_air_python.xaml')
