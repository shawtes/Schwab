"""
Live Multi-Timeframe Charting System
Professional-grade real-time charting with multiple timeframes
Built for institutional trading platforms
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import deque
import threading
import json
import warnings
warnings.filterwarnings('ignore')

# Qt imports
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
        QLabel, QLineEdit, QCheckBox, QGroupBox, QSpinBox
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QThread, QMutex
    from PySide6.QtGui import QFont, QColor
    QT_VERSION = "PySide6"
except ImportError:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
        QLabel, QLineEdit, QCheckBox, QGroupBox, QSpinBox
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal as Signal, QThread, QMutex
    from PyQt5.QtGui import QFont, QColor
    QT_VERSION = "PyQt5"

# Matplotlib
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# Project imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import schwabdev
from ensemble_trading_model import SchwabDataFetcher

load_dotenv()


class StreamDataThread(QThread):
    """Thread for handling streaming data"""
    data_received = Signal(dict)  # Emits: {'symbol': str, 'price': float, 'volume': int, 'timestamp': datetime}
    
    def __init__(self, client, symbols):
        super().__init__()
        self.client = client
        self.symbols = symbols if isinstance(symbols, list) else [symbols]
        self.streamer = None
        self.running = False
        self.data_queue = deque(maxlen=1000)
        self.mutex = QMutex()
        
    def run(self):
        """Start streaming"""
        try:
            self.streamer = schwabdev.Stream(self.client)
            self.running = True
            
            # Subscribe to level one quotes
            # Field 3 = Last Price
            fields = "0,1,2,3,4,5,6,7,8"  # Multiple fields for comprehensive data
            self.streamer.send(
                self.streamer.level_one_equities(",".join(self.symbols), fields)
            )
            
            def handle_message(message):
                """Process incoming stream messages"""
                try:
                    data = json.loads(message) if isinstance(message, str) else message
                    
                    if 'data' in data:
                        for service in data['data']:
                            if service.get('service') == 'LEVELONE_EQUITIES':
                                content = service.get('content', [])
                                for item in content:
                                    symbol = item.get('key', '')
                                    fields = item
                                    
                                    # Extract price data (field 3 = last price)
                                    price = None
                                    if '3' in fields:
                                        try:
                                            price = float(fields['3'])
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    # Extract volume (field 8 = total volume)
                                    volume = None
                                    if '8' in fields:
                                        try:
                                            volume = int(float(fields['8']))
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    # Extract bid/ask
                                    bid = None
                                    ask = None
                                    if '0' in fields:
                                        try:
                                            bid = float(fields['0'])
                                        except (ValueError, TypeError):
                                            pass
                                    if '1' in fields:
                                        try:
                                            ask = float(fields['1'])
                                        except (ValueError, TypeError):
                                            pass
                                    
                                    if price is not None and symbol in self.symbols:
                                        timestamp = datetime.now()
                                        data_packet = {
                                            'symbol': symbol,
                                            'price': price,
                                            'bid': bid,
                                            'ask': ask,
                                            'volume': volume,
                                            'timestamp': timestamp
                                        }
                                        
                                        self.mutex.lock()
                                        self.data_queue.append(data_packet)
                                        self.mutex.unlock()
                                        
                                        self.data_received.emit(data_packet)
                except Exception as e:
                    print(f"Error processing stream message: {e}")
            
            self.streamer.start(handle_message, daemon=True)
            
            # Keep thread alive
            while self.running:
                self.msleep(100)
                
        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            if self.streamer:
                self.streamer.stop()
    
    def stop(self):
        """Stop streaming"""
        self.running = False
        if self.streamer:
            self.streamer.stop()
        self.quit()
        self.wait()


class LiveChartWidget(QWidget):
    """Professional live charting widget with multiple timeframes"""
    
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.fetcher = SchwabDataFetcher(client)
        self.current_symbol = None
        self.current_timeframe = '1min'
        self.stream_thread = None
        
        # Data storage
        self.price_data = {}  # {timeframe: deque of (timestamp, open, high, low, close, volume)}
        self.live_prices = deque(maxlen=100)  # Live streaming prices
        self.last_update = {}
        
        # Timeframe options
        self.timeframes = {
            '1min': {'periodType': 'day', 'period': 1, 'frequencyType': 'minute', 'frequency': 1},
            '5min': {'periodType': 'day', 'period': 1, 'frequencyType': 'minute', 'frequency': 5},
            '15min': {'periodType': 'day', 'period': 1, 'frequencyType': 'minute', 'frequency': 15},
            '30min': {'periodType': 'day', 'period': 5, 'frequencyType': 'minute', 'frequency': 30},
            '1hour': {'periodType': 'day', 'period': 10, 'frequencyType': 'minute', 'frequency': 60},
            '1day': {'periodType': 'year', 'period': 1, 'frequencyType': 'daily', 'frequency': 1}
        }
        
        self.init_ui()
        
        # Update timer for chart refresh
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_chart)
        self.update_timer.start(1000)  # Update every second
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Top controls
        controls = QHBoxLayout()
        
        # Symbol input
        controls.addWidget(QLabel("Symbol:"))
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Enter symbol (e.g., AAPL)")
        self.symbol_input.returnPressed.connect(self.load_symbol)
        controls.addWidget(self.symbol_input)
        
        # Timeframe selector
        controls.addWidget(QLabel("Timeframe:"))
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(list(self.timeframes.keys()))
        self.timeframe_combo.currentTextChanged.connect(self.on_timeframe_changed)
        controls.addWidget(self.timeframe_combo)
        
        # Load button
        self.load_btn = QPushButton("Load Chart")
        self.load_btn.setStyleSheet("background-color: #1976D2; color: white; font-weight: bold; padding: 8px;")
        self.load_btn.clicked.connect(self.load_symbol)
        controls.addWidget(self.load_btn)
        
        # Start/Stop streaming
        self.stream_btn = QPushButton("Start Live")
        self.stream_btn.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 8px;")
        self.stream_btn.clicked.connect(self.toggle_streaming)
        controls.addWidget(self.stream_btn)
        
        # Indicator checkboxes
        controls.addWidget(QLabel("Indicators:"))
        self.ma20_check = QCheckBox("MA20")
        self.ma50_check = QCheckBox("MA50")
        self.bb_check = QCheckBox("BB")
        self.volume_check = QCheckBox("Volume")
        self.ma20_check.setChecked(True)
        self.ma50_check.setChecked(True)
        self.volume_check.setChecked(True)
        
        controls.addWidget(self.ma20_check)
        controls.addWidget(self.ma50_check)
        controls.addWidget(self.bb_check)
        controls.addWidget(self.volume_check)
        
        controls.addStretch()
        
        # Price display
        self.price_label = QLabel("Price: --")
        self.price_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2;")
        controls.addWidget(self.price_label)
        
        # Chart
        self.figure = Figure(figsize=(14, 10), facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Layout
        layout.addLayout(controls)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
        # Style the figure
        self.figure.patch.set_facecolor('#1e1e1e')
    
    def load_symbol(self):
        """Load historical data for symbol"""
        symbol = self.symbol_input.text().strip().upper()
        if not symbol:
            return
        
        self.current_symbol = symbol
        self.load_btn.setText("Loading...")
        self.load_btn.setEnabled(False)
        
        # Load in background thread
        def load_data():
            try:
                timeframe_params = self.timeframes[self.current_timeframe]
                df = self.fetcher.get_price_history(
                    symbol,
                    **timeframe_params
                )
                
                if df is not None and len(df) > 0:
                    # Convert to candlestick data format
                    data = deque()
                    for idx, row in df.iterrows():
                        data.append((
                            idx,
                            row['open'],
                            row['high'],
                            row['low'],
                            row['close'],
                            row['volume']
                        ))
                    
                    self.price_data[self.current_timeframe] = data
                    self.last_update[self.current_timeframe] = datetime.now()
                    
                    # Update chart on main thread
                    QTimer.singleShot(0, self.update_chart)
            except Exception as e:
                print(f"Error loading data: {e}")
            finally:
                QTimer.singleShot(0, lambda: self.load_btn.setText("Load Chart"))
                QTimer.singleShot(0, lambda: self.load_btn.setEnabled(True))
        
        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()
    
    def on_timeframe_changed(self, timeframe):
        """Handle timeframe change"""
        self.current_timeframe = timeframe
        if self.current_symbol:
            self.load_symbol()
    
    def toggle_streaming(self):
        """Start/stop live streaming"""
        if self.stream_thread and self.stream_thread.isRunning():
            # Stop streaming
            self.stream_thread.stop()
            self.stream_thread = None
            self.stream_btn.setText("Start Live")
            self.stream_btn.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 8px;")
        else:
            # Start streaming
            if not self.current_symbol:
                return
            
            self.stream_thread = StreamDataThread(self.client, [self.current_symbol])
            self.stream_thread.data_received.connect(self.on_stream_data)
            self.stream_thread.start()
            self.stream_btn.setText("Stop Live")
            self.stream_btn.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold; padding: 8px;")
    
    def on_stream_data(self, data):
        """Handle incoming stream data"""
        if data['symbol'] == self.current_symbol:
            self.live_prices.append(data)
            # Update price label
            price = data['price']
            change = ""
            if len(self.live_prices) > 1:
                prev_price = self.live_prices[-2]['price']
                if price > prev_price:
                    change = "↑"
                    color = "#4caf50"
                elif price < prev_price:
                    change = "↓"
                    color = "#f44336"
                else:
                    change = "→"
                    color = "#ff9800"
            else:
                color = "#1976D2"
            
            self.price_label.setText(f"Price: ${price:.2f} {change}")
            self.price_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
    
    def update_chart(self):
        """Update chart display"""
        if self.current_timeframe not in self.price_data:
            return
        
        self.figure.clear()
        data = self.price_data[self.current_timeframe]
        
        if len(data) == 0:
            return
        
        # Extract data
        timestamps = [d[0] for d in data]
        opens = [d[1] for d in data]
        highs = [d[2] for d in data]
        lows = [d[3] for d in data]
        closes = [d[4] for d in data]
        volumes = [d[5] for d in data]
        
        # Determine subplot layout
        n_plots = 2 if self.volume_check.isChecked() else 1
        
        # Main price chart
        ax1 = self.figure.add_subplot(n_plots, 1, 1)
        ax1.set_facecolor('#1e1e1e')
        
        # Plot candlesticks
        self.plot_candlesticks(ax1, timestamps, opens, highs, lows, closes)
        
        # Moving averages
        if self.ma20_check.isChecked():
            ma20 = pd.Series(closes).rolling(20).mean()
            ax1.plot(timestamps, ma20, 'cyan', linewidth=1.5, alpha=0.7, label='MA20')
        
        if self.ma50_check.isChecked():
            ma50 = pd.Series(closes).rolling(50).mean()
            ax1.plot(timestamps, ma50, 'yellow', linewidth=1.5, alpha=0.7, label='MA50')
        
        # Bollinger Bands
        if self.bb_check.isChecked():
            ma = pd.Series(closes).rolling(20).mean()
            std = pd.Series(closes).rolling(20).std()
            upper = ma + (std * 2)
            lower = ma - (std * 2)
            ax1.plot(timestamps, upper, 'r--', alpha=0.5, linewidth=1)
            ax1.plot(timestamps, lower, 'r--', alpha=0.5, linewidth=1)
            ax1.fill_between(timestamps, upper, lower, alpha=0.1, color='red')
        
        # Style
        ax1.set_title(f'{self.current_symbol} - {self.current_timeframe}', 
                     color='white', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', color='white', fontsize=12)
        ax1.tick_params(colors='white', labelsize=9)
        ax1.grid(True, alpha=0.3, color='gray', linestyle='--')
        ax1.legend(loc='upper left', facecolor='#2d2d2d', edgecolor='gray', fontsize=9)
        
        # Dynamic date formatting based on timeframe
        self.setup_date_formatting(ax1, timestamps)
        
        # Volume chart
        if self.volume_check.isChecked() and n_plots > 1:
            ax2 = self.figure.add_subplot(n_plots, 1, 2, sharex=ax1)
            ax2.set_facecolor('#1e1e1e')
            
            # Color bars based on price direction
            colors = ['#4caf50' if closes[i] >= opens[i] else '#f44336' 
                     for i in range(len(closes))]
            ax2.bar(timestamps, volumes, color=colors, alpha=0.6, width=0.8)
            ax2.set_ylabel('Volume', color='white', fontsize=12)
            ax2.tick_params(colors='white', labelsize=9)
            ax2.grid(True, alpha=0.3, color='gray', linestyle='--')
            # Volume chart will share x-axis formatting from ax1
        
        # Enable better zoom/pan interaction
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        self.zoom_start = None
        self.pan_start = None
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_candlesticks(self, ax, timestamps, opens, highs, lows, closes):
        """Plot candlestick chart"""
        if len(timestamps) == 0:
            return
        
        # Convert timestamps to matplotlib dates
        mdates_list = [mdates.date2num(ts) for ts in timestamps]
        
        # Calculate width based on data range
        if len(mdates_list) > 1:
            width = (mdates_list[1] - mdates_list[0]) * 0.6
        else:
            width = 0.0001  # Small default width
        
        for i, (ts, o, h, l, c) in enumerate(zip(timestamps, opens, highs, lows, closes)):
            # Determine color
            color = '#4caf50' if c >= o else '#f44336'  # Green for up, red for down
            
            # Draw wick (high-low line)
            ax.plot([mdates.date2num(ts), mdates.date2num(ts)], [l, h], 
                   color=color, linewidth=1.5, solid_capstyle='round')
            
            # Draw body (open-close rectangle)
            body_height = abs(c - o)
            body_bottom = min(o, c)
            
            # Avoid zero-height bodies
            if body_height < 0.01:
                body_height = 0.01
            
            rect = Rectangle(
                (mdates.date2num(ts) - width/2, body_bottom),
                width,
                body_height,
                facecolor=color,
                edgecolor=color,
                alpha=0.8,
                linewidth=1
            )
            ax.add_patch(rect)
        
        # Set x-axis limits with better margins
        if len(mdates_list) > 0:
            margin = (mdates_list[-1] - mdates_list[0]) * 0.02 if len(mdates_list) > 1 else 0.1
            ax.set_xlim(mdates_list[0] - margin, mdates_list[-1] + margin)
        
        # Enable better zoom interaction
        ax.set_xmargin(0.01)
        ax.set_ymargin(0.02)


    def setup_date_formatting(self, ax, timestamps):
        """Setup dynamic date formatting based on timeframe"""
        if len(timestamps) == 0:
            return
        
        timeframe = self.current_timeframe
        
        # Calculate time span
        time_span = timestamps[-1] - timestamps[0] if len(timestamps) > 1 else timedelta(hours=1)
        total_seconds = time_span.total_seconds()
        
        # Determine appropriate format and interval based on timeframe and data span
        if timeframe == '1min':
            if total_seconds < 3600:  # Less than 1 hour
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
            elif total_seconds < 86400:  # Less than 1 day
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        
        elif timeframe == '5min':
            if total_seconds < 14400:  # Less than 4 hours
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
            elif total_seconds < 86400:  # Less than 1 day
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        
        elif timeframe == '15min':
            if total_seconds < 86400:  # Less than 1 day
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        
        elif timeframe == '30min':
            if total_seconds < 172800:  # Less than 2 days
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        
        elif timeframe == '1hour':
            if total_seconds < 259200:  # Less than 3 days
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        
        elif timeframe == '1day':
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            if total_seconds < 7776000:  # Less than 90 days
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            elif total_seconds < 15552000:  # Less than 180 days
                ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
            else:
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        
        # Rotate labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
        
        # Add minor ticks for better granularity (date-specific)
        # For date axes, use appropriate minor locators based on timeframe
        try:
            if timeframe in ['1min', '5min']:
                # For minute timeframes, add minor ticks every few minutes
                ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=1))
            elif timeframe == '15min':
                ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=5))
            elif timeframe == '30min':
                ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=10))
            elif timeframe == '1hour':
                ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
            elif timeframe == '1day':
                ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        except Exception:
            pass  # Skip if not supported
    
    def on_scroll(self, event):
        """Handle mouse scroll for zooming"""
        if event.inaxes != self.figure.axes[0]:
            return
        
        # Zoom factor
        zoom_factor = 1.2 if event.button == 'up' else 1/1.2
        
        # Get current limits
        cur_xlim = event.inaxes.get_xlim()
        cur_ylim = event.inaxes.get_ylim()
        
        # Get mouse position
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None:
            return
        
        # Calculate new limits centered on mouse position
        x_range = (cur_xlim[1] - cur_xlim[0]) / zoom_factor
        y_range = (cur_ylim[1] - cur_ylim[0]) / zoom_factor
        
        new_xlim = [xdata - x_range/2, xdata + x_range/2]
        new_ylim = [ydata - y_range/2, ydata + y_range/2]
        
        # Apply to all axes
        for ax in self.figure.axes:
            ax.set_xlim(new_xlim)
            if ax != self.figure.axes[0]:  # Only set ylim for price chart
                continue
            ax.set_ylim(new_ylim)
        
        self.canvas.draw()
    
    def on_press(self, event):
        """Handle mouse press for panning"""
        if event.inaxes is None:
            return
        if event.button != 1:  # Left mouse button
            return
        
        self.pan_start = (event.xdata, event.ydata, event.inaxes)
    
    def on_release(self, event):
        """Handle mouse release"""
        self.pan_start = None
    
    def on_motion(self, event):
        """Handle mouse motion for panning"""
        if self.pan_start is None:
            return
        if event.inaxes != self.pan_start[2]:
            return
        
        dx = event.xdata - self.pan_start[0]
        dy = event.ydata - self.pan_start[1] if event.ydata else 0
        
        if dx is None:
            return
        
        # Get current limits
        cur_xlim = event.inaxes.get_xlim()
        cur_ylim = event.inaxes.get_ylim()
        
        # Calculate new limits
        new_xlim = [cur_xlim[0] - dx, cur_xlim[1] - dx]
        
        # Apply to all axes
        for ax in self.figure.axes:
            ax.set_xlim(new_xlim)
            if ax == self.figure.axes[0] and dy is not None:
                new_ylim = [cur_ylim[0] - dy, cur_ylim[1] - dy]
                ax.set_ylim(new_ylim)
        
        self.canvas.draw()
        self.pan_start = (event.xdata, event.ydata, event.inaxes)


class LiveChartTab(QWidget):
    """Tab widget for live charting"""
    
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.chart = LiveChartWidget(self.client)
        layout.addWidget(self.chart)
        self.setLayout(layout)

