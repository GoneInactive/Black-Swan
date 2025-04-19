import dearpygui.dearpygui as dpg
import time
import threading
import os
import sys
from collections import deque

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from clients.kraken_sync_client import KrakenSyncClient


class Plotter:
    def __init__(self):
        self.client = KrakenSyncClient()

    def test_live_plotter(self):
        nsamples = 1000
        data_x = deque(maxlen=nsamples)
        bid_y = deque(maxlen=nsamples)
        ask_y = deque(maxlen=nsamples)
        midpoint_y = deque(maxlen=nsamples)
        moving_avg_y = deque(maxlen=nsamples)  # Moving average of midpoint

        # Create text tags for displaying live bid, ask, spread, and midpoint
        bid_text_tag = 'bid_text'
        ask_text_tag = 'ask_text'
        spread_text_tag = 'spread_text'
        midpoint_text_tag = 'midpoint_text'

        def update_data():
            t0 = time.time()
            while True:
                t = time.time() - t0

                # Get the live bid and ask prices
                bid = self.client.get_bid()
                ask = self.client.get_ask()

                if bid is None or ask is None:
                    continue  # Skip if bid/ask is None

                # Calculate the midpoint between the bid and ask
                midpoint = (bid + ask) / 2

                # Calculate the moving average of the midpoint (SMA)
                moving_avg_y.append(midpoint)
                if len(moving_avg_y) > 1:
                    moving_avg = sum(moving_avg_y) / len(moving_avg_y)
                else:
                    moving_avg = midpoint  # If there's only one value, it is its own average

                # Append the new data
                data_x.append(t)
                bid_y.append(bid)
                ask_y.append(ask)
                midpoint_y.append(midpoint)

                # Update the plot series with the last `nsamples` data points
                dpg.set_value('bid_series', [list(data_x), list(bid_y)])
                dpg.set_value('ask_series', [list(data_x), list(ask_y)])
                #dpg.set_value('midpoint_series', [list(data_x), list(midpoint_y)])
                dpg.set_value('moving_avg_series', [list(data_x), [moving_avg] * len(data_x)])

                # Dynamically adjust axis limits
                max_bid = max(bid_y) if bid_y else 0
                min_bid = min(bid_y) if bid_y else 0
                max_ask = max(ask_y) if ask_y else 0
                min_ask = min(ask_y) if ask_y else 0
                max_midpoint = max(midpoint_y) if midpoint_y else 0
                min_midpoint = min(midpoint_y) if midpoint_y else 0

                # Find the overall min/max for bid, ask, and midpoint
                min_price = min(min_bid, min_ask, min_midpoint)
                max_price = max(max_bid, max_ask, max_midpoint)

                # Update axis data dynamically to ensure bid, ask, and midpoint are within view
                dpg.set_axis_limits('y_axis', min_price - 10, max_price + 10)  # Add a small buffer

                # Fit x axis to time
                dpg.fit_axis_data('x_axis')

                # Calculate and update the spread
                spread = ask - bid

                # Update the live bid, ask, spread, and midpoint text
                dpg.set_value(bid_text_tag, f"Live Bid: ${bid:.2f}")
                dpg.set_value(ask_text_tag, f"Live Ask: ${ask:.2f}")
                dpg.set_value(spread_text_tag, f"Spread: ${spread:.2f}")
                #dpg.set_value(midpoint_text_tag, f"Midpoint: ${midpoint:.2f}")

                # Reduced sleep time for faster updates
                time.sleep(0.1)

        # Initialize DearPyGui context
        dpg.create_context()
        with dpg.window(label='Kraken Bid/Ask Plot', tag='win', width=800, height=600):
            with dpg.plot(label='Live Bid/Ask', height=-1, width=-1):
                # Optionally add a legend
                dpg.add_plot_legend()

                # Create axes with dynamic labels
                x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='Time (s)', tag='x_axis')
                y_axis = dpg.add_plot_axis(dpg.mvYAxis, label='Price (USD)', tag='y_axis')

                # Add three line series for bid, ask, and midpoint
                dpg.add_line_series([], [], label='Bid', parent=y_axis, tag='bid_series')
                dpg.add_line_series([], [], label='Ask', parent=y_axis, tag='ask_series')
                #dpg.add_line_series([], [], label='Midpoint', parent=y_axis, tag='midpoint_series')
                dpg.add_line_series([], [], label='Moving Average', parent=y_axis, tag='moving_avg_series')

            # Add text elements to display the bid, ask, spread, and midpoint
            dpg.add_text(tag=bid_text_tag, default_value="Live Bid: 0.00", pos=(80, 125))
            dpg.add_text(tag=ask_text_tag, default_value="Live Ask: 0.00", pos=(80, 150))
            dpg.add_text(tag=spread_text_tag, default_value="Spread: 0.00", pos=(80, 175))
            #dpg.add_text(tag=midpoint_text_tag, default_value="Midpoint: 0.00", pos=(80, 200))

        # Set up viewport and display
        dpg.create_viewport(title='Kraken Real-Time Bid/Ask', width=850, height=640)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        # Start the data updating thread
        threading.Thread(target=update_data, daemon=True).start()

        # Start the DearPyGui event loop
        dpg.start_dearpygui()

        # Clean up after the event loop ends
        dpg.destroy_context()

if __name__ == "__main__":
    Plotter().test_live_plotter()
