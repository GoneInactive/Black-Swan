import dearpygui.dearpygui as dpg
import math
import time
import collections
import threading
import pdb
import random



class Plotter:
    def __init__(self):
        return None
    
    def test_live_plotter(self):

        nsamples = 10000

        global data_y
        global data_x
        # Can use collections if you only need the last 100 samples
        # data_y = collections.deque([0.0, 0.0],maxlen=nsamples)
        # data_x = collections.deque([0.0, 0.0],maxlen=nsamples)

        # Use a list if you need all the data. 
        # Empty list of nsamples should exist at the beginning.
        # Theres a cleaner way to do this probably.
        data_y = [0.0] * nsamples
        data_x = [0.0] * nsamples
        data_y2 = [0.0] * nsamples

        def update_data():
            sample = 1
            t0 = time.time()
            frequency=1.0
            while True:

                # Get new data sample. Note we need both x and y values
                # if we want a meaningful axis unit.
                t = time.time() - t0
                y = math.sin(t)+(1/2)*t+5**random.uniform(0,1)
                y2 = t
                data_x.append(t)
                data_y.append(y)
                data_y2.append(y2)

                
                #set the series x and y to the last nsamples
                dpg.set_value('series_tag', [list(data_x[-nsamples:]), list(data_y[-nsamples:])])          
                dpg.fit_axis_data('x_axis')
                dpg.fit_axis_data('y_axis')
                
                time.sleep(0.01)
                sample=sample+1
                


        dpg.create_context()
        with dpg.window(label='Tutorial', tag='win',width=800, height=600):

            with dpg.plot(label='Line Series', height=-1, width=-1):
                # optionally create legend
                dpg.add_plot_legend()

                # REQUIRED: create x and y axes, set to auto scale.
                x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='x', tag='x_axis')
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='y', tag='y_axis')


                # series belong to a y axis. Note the tag name is used in the update
                # function update_data
                dpg.add_line_series(x=list(data_x),y=list(data_y), 
                                    label='Temp', parent='y_axis', 
                                    tag='series_tag')
                #dpg.add_line_series(x=list(data_x),y=list(data_y2), 
                #                    label='Temp', parent='y_axis', 
                #                    tag='series_tag')
                
                    
                                    
        dpg.create_viewport(title='Custom Title', width=850, height=640)

        dpg.setup_dearpygui()
        dpg.show_viewport()

        thread = threading.Thread(target=update_data)
        thread.start()
        dpg.start_dearpygui()

        dpg.destroy_context()