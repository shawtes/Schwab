"""
Institutional Trading Application - Desktop GUI
Professional-grade trading platform with stock screening, analysis, and portfolio management
Built for Blackstone-level institutional trading
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# PyQt5/PySide6 imports - IMPORTANT: Only use ONE, not both!
# Having both installed causes conflicts on macOS (segmentation faults)
QT_VERSION = None
PYQT_AVAILABLE = False

# Check if both are installed (warning)
try:
    import PySide6
    has_pyside6 = True
except ImportError:
    has_pyside6 = False

try:
    import PyQt5
    has_pyqt5 = True
except ImportError:
    has_pyqt5 = False

if has_pyside6 and has_pyqt5:
    print("=" * 60)
    print("WARNING: Both PySide6 and PyQt5 are installed!")
    print("=" * 60)
    print("This can cause conflicts and crashes on macOS.")
    print("\nRecommended: Uninstall PyQt5 and use only PySide6")
    print("  pip uninstall PyQt5")
    print("\nOr uninstall PySide6 and use only PyQt5")
    print("  pip uninstall PySide6")
    print("=" * 60)
    print("\nProceeding with PySide6 (preferred)...")
    print("=" * 60)

# Try PySide6 first (preferred)
if has_pyside6:
    try:
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
            QGroupBox, QSplitter, QProgressBar, QMessageBox, QFileDialog,
            QHeaderView, QMenuBar, QMenu, QStatusBar, QToolBar,
            QCheckBox, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox
        )
        # QAction moved to QtGui in Qt6/PySide6
        from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QAction
        from PySide6.QtCore import Qt, QThread, Signal as pyqtSignal, QTimer, QSize
        QT_VERSION = "PySide6"
        PYQT_AVAILABLE = True
    except ImportError as e:
        print(f"Warning: PySide6 import failed: {e}")

# Fallback to PyQt5 only if PySide6 failed
if not PYQT_AVAILABLE and has_pyqt5:
    try:
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
            QGroupBox, QSplitter, QProgressBar, QMessageBox, QFileDialog,
            QHeaderView, QMenuBar, QMenu, QStatusBar, QToolBar, QAction,
            QCheckBox, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox
        )
        from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
        from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPixmap
        QT_VERSION = "PyQt5"
        PYQT_AVAILABLE = True
    except ImportError as e:
        print(f"Warning: PyQt5 import failed: {e}")

# Final check
if not PYQT_AVAILABLE:
    print("=" * 60)
    print("ERROR: Neither PySide6 nor PyQt5 is available.")
    print("=" * 60)
    print("\nPlease install one of them in your current environment:")
    print("  pip install PySide6  (recommended)")
    print("  OR")
    print("  pip install PyQt5")
    print("\nIf you're using conda:")
    print("  conda install -c conda-forge pyside6")
    print("  OR")
    print("  conda install -c conda-forge pyqt")
    print("\nCurrent Python:", sys.executable)
    print("=" * 60)
    sys.exit(1)

# Matplotlib integration
import matplotlib
if QT_VERSION == "PySide6":
    matplotlib.use('Qt5Agg')  # PySide6 also uses Qt5 backend
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
else:
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# Project imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import schwabdev
from stock_screener import StockScreener
from ensemble_trading_model import EnsembleTradingModel, SchwabDataFetcher
from live_chart import LiveChartTab

load_dotenv()


class DataFetchThread(QThread):
    """Thread for fetching stock data without blocking UI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, screener, symbols, periodType='year', period=1, frequencyType='daily', frequency=1):
        super().__init__()
        self.screener = screener
        self.symbols = symbols
        self.periodType = periodType
        self.period = period
        self.frequencyType = frequencyType
        self.frequency = frequency
    
    def run(self):
        try:
            self.progress.emit("Fetching stock data...")
            results = self.screener.fetch_stocks(
                self.symbols,
                periodType=self.periodType,
                period=self.period,
                frequencyType=self.frequencyType,
                frequency=self.frequency
            )
            self.progress.emit("Calculating indicators...")
            self.screener.calculate_indicators()
            self.progress.emit("Fetching quotes...")
            self.screener.get_current_quotes(self.symbols)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class ChartWidget(QWidget):
    """Custom widget for displaying stock charts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.axes = {}
    
    def plot_stock(self, screener, symbol, indicators=['RSI', 'MACD', 'BB', 'Volume']):
        """Plot stock chart with indicators"""
        if symbol not in screener.stock_features:
            return
        
        self.figure.clear()
        features_df = screener.stock_features[symbol]
        
        # Determine subplot layout
        n_plots = 1 + sum([
            'RSI' in indicators,
            'MACD' in indicators,
            'BB' in indicators,
            'Volume' in indicators
        ])
        
        plot_idx = 0
        
        # Price chart
        ax1 = self.figure.add_subplot(n_plots, 1, plot_idx + 1)
        plot_idx += 1
        
        ax1.plot(features_df.index, features_df['close'], label='Close', linewidth=2, color='#1f77b4')
        if 'ma_20' in features_df.columns:
            ax1.plot(features_df.index, features_df['ma_20'], label='MA 20', alpha=0.7)
        if 'ma_50' in features_df.columns:
            ax1.plot(features_df.index, features_df['ma_50'], label='MA 50', alpha=0.7)
        
        if 'BB' in indicators and 'bb_upper_20' in features_df.columns:
            ax1.plot(features_df.index, features_df['bb_upper_20'], 'r--', alpha=0.5, label='BB Upper')
            ax1.plot(features_df.index, features_df['bb_lower_20'], 'r--', alpha=0.5, label='BB Lower')
        
        ax1.set_title(f'{symbol} - Price Chart', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        # RSI
        if 'RSI' in indicators and 'rsi' in features_df.columns:
            ax = self.figure.add_subplot(n_plots, 1, plot_idx + 1)
            plot_idx += 1
            ax.plot(features_df.index, features_df['rsi'], 'purple', linewidth=2)
            ax.axhline(y=70, color='r', linestyle='--', alpha=0.5)
            ax.axhline(y=30, color='g', linestyle='--', alpha=0.5)
            ax.set_ylabel('RSI')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
        
        # MACD
        if 'MACD' in indicators and 'macd' in features_df.columns:
            ax = self.figure.add_subplot(n_plots, 1, plot_idx + 1)
            plot_idx += 1
            ax.plot(features_df.index, features_df['macd'], 'blue', linewidth=2, label='MACD')
            if 'macd_signal' in features_df.columns:
                ax.plot(features_df.index, features_df['macd_signal'], 'orange', label='Signal')
            if 'macd_hist' in features_df.columns:
                colors = ['green' if x >= 0 else 'red' for x in features_df['macd_hist']]
                ax.bar(features_df.index, features_df['macd_hist'], alpha=0.6, color=colors)
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax.set_ylabel('MACD')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # Volume
        if 'Volume' in indicators and 'volume' in features_df.columns:
            ax = self.figure.add_subplot(n_plots, 1, plot_idx + 1)
            plot_idx += 1
            colors = ['green' if features_df['close'].iloc[i] >= features_df['close'].iloc[i-1] 
                     else 'red' for i in range(len(features_df))]
            ax.bar(features_df.index, features_df['volume'], alpha=0.6, color=colors)
            ax.set_ylabel('Volume')
            ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()


class StockScreenerTab(QWidget):
    """Stock Screener Tab"""
    
    def __init__(self, screener, parent=None):
        super().__init__(parent)
        self.screener = screener
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Top controls
        controls = QHBoxLayout()
        
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Enter symbols (comma-separated): AAPL, MSFT, GOOGL")
        self.symbol_input.setText("AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, JPM, V, JNJ")
        
        self.fetch_btn = QPushButton("Fetch & Analyze")
        self.fetch_btn.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 8px;")
        self.fetch_btn.clicked.connect(self.fetch_stocks)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        
        controls.addWidget(QLabel("Symbols:"))
        controls.addWidget(self.symbol_input)
        controls.addWidget(self.fetch_btn)
        controls.addWidget(self.progress)
        
        # Filter controls
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout()
        
        self.rsi_min = QDoubleSpinBox()
        self.rsi_min.setRange(0, 100)
        self.rsi_min.setValue(30)
        self.rsi_max = QDoubleSpinBox()
        self.rsi_max.setRange(0, 100)
        self.rsi_max.setValue(70)
        
        self.macd_positive = QCheckBox("Positive MACD Hist")
        
        self.volume_min = QDoubleSpinBox()
        self.volume_min.setRange(0, 10)
        self.volume_min.setValue(1.0)
        self.volume_min.setSingleStep(0.1)
        
        filter_layout.addWidget(QLabel("RSI:"))
        filter_layout.addWidget(self.rsi_min)
        filter_layout.addWidget(QLabel("to"))
        filter_layout.addWidget(self.rsi_max)
        filter_layout.addWidget(self.macd_positive)
        filter_layout.addWidget(QLabel("Volume Ratio >"))
        filter_layout.addWidget(self.volume_min)
        
        self.apply_filter_btn = QPushButton("Apply Filters")
        self.apply_filter_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.apply_filter_btn)
        
        filter_group.setLayout(filter_layout)
        
        # Sort controls
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Sort by:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Alpha_Sharpe_20", "RSI", "MACD_Hist", "Momentum_20",
            "Volume_Ratio", "Returns_21d", "Current_Price"
        ])
        self.sort_ascending = QCheckBox("Ascending")
        self.sort_btn = QPushButton("Sort")
        self.sort_btn.clicked.connect(self.sort_stocks)
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addWidget(self.sort_ascending)
        sort_layout.addWidget(self.sort_btn)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Symbol", "Price", "RSI", "MACD", "MACD Hist", 
            "Volume Ratio", "Momentum", "Alpha Sharpe", "Returns 21d", "Signal"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemDoubleClicked.connect(self.on_row_double_clicked)
        
        # Layout
        layout.addLayout(controls)
        layout.addWidget(filter_group)
        layout.addLayout(sort_layout)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def fetch_stocks(self):
        symbols_text = self.symbol_input.text().strip()
        if not symbols_text:
            QMessageBox.warning(self, "Warning", "Please enter stock symbols")
            return
        
        symbols = [s.strip().upper() for s in symbols_text.split(',')]
        
        self.fetch_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Indeterminate
        
        self.thread = DataFetchThread(self.screener, symbols)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_fetch_complete)
        self.thread.error.connect(self.on_fetch_error)
        self.thread.start()
    
    def update_progress(self, message):
        self.progress.setFormat(message)
    
    def on_fetch_complete(self, results):
        self.fetch_btn.setEnabled(True)
        self.progress.setVisible(False)
        self.update_table()
        QMessageBox.information(self, "Success", f"Fetched data for {len(results)} stocks")
    
    def on_fetch_error(self, error_msg):
        self.fetch_btn.setEnabled(True)
        self.progress.setVisible(False)
        QMessageBox.critical(self, "Error", f"Error fetching data: {error_msg}")
    
    def update_table(self):
        summary_df = self.screener.create_summary_dataframe(include_quotes=True)
        
        if summary_df.empty:
            return
        
        self.table.setRowCount(len(summary_df))
        
        for i, row in summary_df.iterrows():
            self.table.setItem(i, 0, QTableWidgetItem(str(row.get('Symbol', ''))))
            self.table.setItem(i, 1, QTableWidgetItem(f"${row.get('Current_Price', 0):.2f}" if pd.notna(row.get('Current_Price')) else "N/A"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{row.get('RSI', 0):.2f}" if pd.notna(row.get('RSI')) else "N/A"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{row.get('MACD', 0):.4f}" if pd.notna(row.get('MACD')) else "N/A"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{row.get('MACD_Hist', 0):.4f}" if pd.notna(row.get('MACD_Hist')) else "N/A"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{row.get('Volume_Ratio', 0):.2f}" if pd.notna(row.get('Volume_Ratio')) else "N/A"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{row.get('Momentum_20', 0):.2%}" if pd.notna(row.get('Momentum_20')) else "N/A"))
            self.table.setItem(i, 7, QTableWidgetItem(f"{row.get('Alpha_Sharpe_20', 0):.4f}" if pd.notna(row.get('Alpha_Sharpe_20')) else "N/A"))
            self.table.setItem(i, 8, QTableWidgetItem(f"{row.get('Returns_21d', 0):.2%}" if pd.notna(row.get('Returns_21d')) else "N/A"))
            
            # Signal
            signal = self.calculate_signal(row)
            signal_item = QTableWidgetItem(signal)
            if signal == "BUY":
                signal_item.setBackground(QColor(200, 255, 200))
            elif signal == "SELL":
                signal_item.setBackground(QColor(255, 200, 200))
            self.table.setItem(i, 9, signal_item)
        
        self.table.resizeColumnsToContents()
    
    def calculate_signal(self, row):
        """Calculate trading signal based on indicators"""
        rsi = row.get('RSI', 50)
        macd_hist = row.get('MACD_Hist', 0)
        momentum = row.get('Momentum_20', 0)
        
        buy_signals = 0
        sell_signals = 0
        
        if rsi < 40:
            buy_signals += 1
        elif rsi > 60:
            sell_signals += 1
        
        if macd_hist > 0:
            buy_signals += 1
        else:
            sell_signals += 1
        
        if momentum > 0:
            buy_signals += 1
        else:
            sell_signals += 1
        
        if buy_signals >= 2:
            return "BUY"
        elif sell_signals >= 2:
            return "SELL"
        else:
            return "HOLD"
    
    def apply_filters(self):
        summary_df = self.screener.create_summary_dataframe(include_quotes=True)
        
        filters = {}
        filters['RSI'] = (self.rsi_min.value(), self.rsi_max.value())
        
        if self.macd_positive.isChecked():
            filters['MACD_Hist'] = (0, None)
        
        filters['Volume_Ratio'] = (self.volume_min.value(), None)
        
        filtered_df = self.screener.filter_stocks(summary_df, filters=filters)
        
        # Update table with filtered data
        self.table.setRowCount(len(filtered_df))
        for i, row in filtered_df.iterrows():
            self.table.setItem(i, 0, QTableWidgetItem(str(row.get('Symbol', ''))))
            # ... (similar to update_table)
    
    def sort_stocks(self):
        summary_df = self.screener.create_summary_dataframe(include_quotes=True)
        sort_by = self.sort_combo.currentText()
        ascending = self.sort_ascending.isChecked()
        
        sorted_df = self.screener.sort_stocks(summary_df, sort_by=sort_by, ascending=ascending)
        self.update_table()
    
    def on_row_double_clicked(self, item):
        row = item.row()
        symbol = self.table.item(row, 0).text()
        self.parent().parent().show_chart(symbol)


class ChartTab(QWidget):
    """Chart Display Tab"""
    
    def __init__(self, screener, parent=None):
        super().__init__(parent)
        self.screener = screener
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Controls
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Symbol:"))
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Enter symbol (e.g., AAPL)")
        self.symbol_input.returnPressed.connect(self.plot_chart)
        
        self.plot_btn = QPushButton("Plot Chart")
        self.plot_btn.setStyleSheet("background-color: #1976D2; color: white; font-weight: bold; padding: 8px;")
        self.plot_btn.clicked.connect(self.plot_chart)
        
        controls.addWidget(self.symbol_input)
        controls.addWidget(self.plot_btn)
        controls.addStretch()
        
        # Indicator checkboxes
        indicator_layout = QHBoxLayout()
        indicator_layout.addWidget(QLabel("Indicators:"))
        self.rsi_check = QCheckBox("RSI")
        self.rsi_check.setChecked(True)
        self.macd_check = QCheckBox("MACD")
        self.macd_check.setChecked(True)
        self.bb_check = QCheckBox("Bollinger Bands")
        self.volume_check = QCheckBox("Volume")
        self.volume_check.setChecked(True)
        
        indicator_layout.addWidget(self.rsi_check)
        indicator_layout.addWidget(self.macd_check)
        indicator_layout.addWidget(self.bb_check)
        indicator_layout.addWidget(self.volume_check)
        indicator_layout.addStretch()
        
        # Chart widget
        self.chart = ChartWidget()
        
        layout.addLayout(controls)
        layout.addLayout(indicator_layout)
        layout.addWidget(self.chart)
        
        self.setLayout(layout)
    
    def plot_chart(self):
        symbol = self.symbol_input.text().strip().upper()
        if not symbol:
            QMessageBox.warning(self, "Warning", "Please enter a symbol")
            return
        
        if symbol not in self.screener.stock_features:
            QMessageBox.warning(self, "Warning", f"No data available for {symbol}. Please fetch data first.")
            return
        
        indicators = []
        if self.rsi_check.isChecked():
            indicators.append('RSI')
        if self.macd_check.isChecked():
            indicators.append('MACD')
        if self.bb_check.isChecked():
            indicators.append('BB')
        if self.volume_check.isChecked():
            indicators.append('Volume')
        
        self.chart.plot_stock(self.screener, symbol, indicators)


class TradingApplication(QMainWindow):
    """Main Trading Application Window"""
    
    def __init__(self):
        super().__init__()
        self.screener = None
        self.client = None
        self.init_ui()
        self.init_client()
    
    def init_ui(self):
        self.setWindowTitle("Institutional Trading Platform - Blackstone Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        # Menu bar
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('File')
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        tools_menu = menubar.addMenu('Tools')
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
        # Central widget with tabs
        self.tabs = QTabWidget()
        
        # Stock Screener Tab
        if self.screener:
            self.screener_tab = StockScreenerTab(self.screener)
        else:
            self.screener_tab = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Initializing..."))
            self.screener_tab.setLayout(layout)
        
        # Chart Tab
        if self.screener:
            self.chart_tab = ChartTab(self.screener)
        else:
            self.chart_tab = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Initializing..."))
            self.chart_tab.setLayout(layout)
        
        # Live Chart Tab (placeholder until client is initialized)
        self.live_chart_tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Initializing..."))
        self.live_chart_tab.setLayout(layout)
        
        self.tabs.addTab(self.screener_tab, "Stock Screener")
        self.tabs.addTab(self.chart_tab, "Charts")
        self.tabs.addTab(self.live_chart_tab, "Live Charts")
        
        self.setCentralWidget(self.tabs)
        
        # Apply dark theme
        self.apply_dark_theme()
    
    def apply_dark_theme(self):
        """Apply professional dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: white;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QTableWidget {
                background-color: #2d2d2d;
                color: white;
                gridline-color: #3d3d3d;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #3d3d3d;
                color: white;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: white;
            }
            QCheckBox {
                color: white;
            }
        """)
    
    def init_client(self):
        """Initialize Schwab API client"""
        app_key = os.getenv('app_key')
        app_secret = os.getenv('app_secret')
        
        if not app_key or not app_secret:
            QMessageBox.critical(
                self, 
                "Configuration Error",
                "Missing API credentials.\n\nPlease set app_key and app_secret in .env file.\n\nRun: python3 setup_schwab.py"
            )
            return
        
        try:
            self.client = schwabdev.Client(
                app_key,
                app_secret,
                os.getenv('callback_url', 'https://127.0.0.1')
            )
            self.screener = StockScreener(self.client)
            
            # Reinitialize tabs with screener
            self.screener_tab = StockScreenerTab(self.screener)
            self.chart_tab = ChartTab(self.screener)
            self.live_chart_tab = LiveChartTab(self.client)
            
            self.tabs.removeTab(0)
            self.tabs.removeTab(0)
            self.tabs.removeTab(0)
            self.tabs.addTab(self.screener_tab, "Stock Screener")
            self.tabs.addTab(self.chart_tab, "Charts")
            self.tabs.addTab(self.live_chart_tab, "Live Charts")
            
            self.statusBar().showMessage('Connected to Schwab API')
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to Schwab API:\n{str(e)}")
    
    def show_chart(self, symbol):
        """Show chart for symbol"""
        self.tabs.setCurrentIndex(1)  # Switch to chart tab
        self.chart_tab.symbol_input.setText(symbol)
        self.chart_tab.plot_chart()
    
    def show_settings(self):
        QMessageBox.information(self, "Settings", "Settings dialog - Coming soon")
    
    def show_about(self):
        QMessageBox.about(
            self,
            "About",
            "Institutional Trading Platform\n\n"
            "Professional-grade trading application with:\n"
            "- Stock screening and analysis\n"
            "- Technical indicators and alpha factors\n"
            "- Real-time data visualization\n"
            "- Portfolio management\n\n"
            "Version 1.0.0\n"
            "Built for institutional trading"
        )


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = TradingApplication()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

