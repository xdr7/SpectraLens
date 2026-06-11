"""
Main Window - SpectraLens GUI
===============================
PyQt5-based GUI with embedded matplotlib visualizations for WiFi frequency scanning.

Creator : Asmaul Asni Subegi, S.Kom
Email   : sabayonx@gmail.com
"""

import sys
import os
import numpy as np
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QTextEdit, QFileDialog,
    QMessageBox, QGroupBox, QGridLayout, QSpinBox, QDoubleSpinBox,
    QStatusBar, QAction, QToolBar,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QSplitter, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor

from scanner.wifi_scanner import WiFiScanner
from scanner.data_collector import DataCollector
from interpolation.idw import IDWInterpolator
from interpolation.grid_builder import GridBuilder
from visualization.heatmap_2d import Heatmap2D
from visualization.surface_3d import Surface3D
from visualization.spectrum_analyzer import SpectrumAnalyzer
from visualization.signal_propagation import SignalPropagation
from storage.database import Database

# Matplotlib embedded in PyQt5
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ScanWorker(QThread):
    """Worker thread for WiFi scanning to keep GUI responsive."""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.scanner = WiFiScanner()

    def run(self):
        try:
            networks = self.scanner.scan()
            self.finished.emit(networks)
        except Exception as e:
            self.error.emit(str(e))


class MplCanvas(FigureCanvas):
    """Matplotlib canvas widget for embedding plots in PyQt5."""
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setMinimumSize(400, 300)


class MplCanvas3D(FigureCanvas):
    """Matplotlib canvas widget for embedding 3D plots in PyQt5."""
    def __init__(self, parent=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setMinimumSize(400, 300)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.xaxis.pane.set_facecolor('#2a2a2a')
        self.ax.yaxis.pane.set_facecolor('#2a2a2a')
        self.ax.zaxis.pane.set_facecolor('#2a2a2a')
        self.ax.xaxis.pane.set_edgecolor('#444')
        self.ax.yaxis.pane.set_edgecolor('#444')
        self.ax.zaxis.pane.set_edgecolor('#444')
        self.ax.tick_params(colors='#aaa')
        self.ax.xaxis.label.set_color('#aaa')
        self.ax.yaxis.label.set_color('#aaa')
        self.ax.zaxis.label.set_color('#aaa')
        self.ax.title.set_color('#ddd')


class SpectraLensGUI(QMainWindow):
    """
    Main SpectraLens GUI Window with embedded visualizations.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SpectraLens - WiFi Frequency Visualization Tool")
        self.setMinimumSize(1400, 850)
        
        # Core components
        self.scanner = WiFiScanner()
        self.data_collector = DataCollector()
        self.database = Database()
        self.interpolator = IDWInterpolator(power=2, k=5)
        self.grid_builder = None
        
        # Data storage
        self.networks = []
        self.measurement_points = []
        self.current_session = None
        
        # Realtime scan state
        self.realtime_running = False
        self.realtime_timer = QTimer()
        self.realtime_timer.timeout.connect(self._realtime_scan)
        
        # Setup UI
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        
        # Apply dark theme
        self._apply_dark_theme()
        
        # Show welcome
        self.statusBar().showMessage("Ready | SpectraLens v1.0.0", 5000)
    
    def _apply_dark_theme(self):
        """Apply a modern dark theme to the GUI."""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(50, 50, 50))
        dark_palette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.Text, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.Button, QColor(50, 50, 50))
        dark_palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 100, 100))
        dark_palette.setColor(QPalette.Highlight, QColor(0, 150, 200))
        dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(dark_palette)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QTabWidget::pane { background-color: #2a2a2a; border: 1px solid #3a3a3a; }
            QTabBar::tab { background-color: #333; color: #ccc; padding: 8px 16px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #007acc; color: white; }
            QGroupBox { color: #ddd; border: 1px solid #444; border-radius: 4px; margin-top: 10px; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QPushButton { background-color: #007acc; color: white; border: none; padding: 6px 14px; border-radius: 3px; }
            QPushButton:hover { background-color: #0098e6; }
            QPushButton:pressed { background-color: #005f99; }
            QPushButton:disabled { background-color: #555; color: #888; }
            QTableWidget { background-color: #252525; color: #ddd; gridline-color: #3a3a3a; border: 1px solid #3a3a3a; }
            QTableWidget::item:selected { background-color: #007acc; }
            QHeaderView::section { background-color: #333; color: #ddd; padding: 4px; border: 1px solid #444; }
            QTextEdit { background-color: #1e1e1e; color: #ddd; border: 1px solid #3a3a3a; }
            QProgressBar { background-color: #333; border: 1px solid #444; border-radius: 3px; text-align: center; color: #ddd; }
            QProgressBar::chunk { background-color: #007acc; border-radius: 2px; }
            QStatusBar { background-color: #252525; color: #aaa; border-top: 1px solid #3a3a3a; }
            QToolBar { background-color: #252525; border-bottom: 1px solid #3a3a3a; spacing: 4px; }
            QMenuBar { background-color: #252525; color: #ddd; }
            QMenuBar::item:selected { background-color: #007acc; }
            QMenu { background-color: #2a2a2a; color: #ddd; border: 1px solid #444; }
            QMenu::item:selected { background-color: #007acc; }
            QSplitter::handle { background-color: #3a3a3a; width: 2px; }
        """)
    
    def _setup_ui(self):
        """Setup the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)
        
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Segoe UI", 10))
        main_layout.addWidget(self.tabs)
        
        self._create_dashboard_tab()
        self._create_scanner_tab()
        self._create_visualization_tab()
        self._create_data_tab()
        self._create_recording_tab()
        self._create_realtime_tab()
        self._create_spectrum_tab()
        self._create_propagation_tab()
    
    def _setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        import_action = QAction("Import CSV...", self)
        import_action.triggered.connect(self._import_csv)
        file_menu.addAction(import_action)
        
        export_action = QAction("Export CSV...", self)
        export_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        scan_action = QAction("Scan WiFi", self)
        scan_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        tools_menu.addAction(scan_action)
        
        viz_action = QAction("Visualizations", self)
        viz_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        tools_menu.addAction(viz_action)
        
        realtime_action = QAction("Realtime Monitor", self)
        realtime_action.triggered.connect(lambda: self.tabs.setCurrentIndex(4))
        tools_menu.addAction(realtime_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About SpectraLens", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Setup the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        btn_scan = QAction("Scan", self)
        btn_scan.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        toolbar.addAction(btn_scan)
        
        btn_viz = QAction("Visualize", self)
        btn_viz.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        toolbar.addAction(btn_viz)
        
        btn_realtime = QAction("Realtime", self)
        btn_realtime.triggered.connect(lambda: self.tabs.setCurrentIndex(4))
        toolbar.addAction(btn_realtime)
        
        toolbar.addSeparator()
        
        btn_import = QAction("Import CSV", self)
        btn_import.triggered.connect(self._import_csv)
        toolbar.addAction(btn_import)
        
        btn_sample = QAction("Sample Data", self)
        btn_sample.triggered.connect(self._load_sample_data)
        toolbar.addAction(btn_sample)
    
    def _setup_statusbar(self):
        """Setup the status bar."""
        self.statusBar().showMessage("Ready")
    
    # =====================================================================
    # DASHBOARD TAB
    # =====================================================================
    def _create_dashboard_tab(self):
        """Create the dashboard/home tab with overview."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        header = QLabel("SpectraLens - WiFi Frequency Visualization")
        header.setFont(QFont("Segoe UI", 18))
        header.setStyleSheet("color: #00b4d8; padding: 10px; font-weight: bold;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel('"Making the invisible visible, one frequency at a time."')
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #888; padding-bottom: 10px; font-style: italic;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QGridLayout(actions_group)
        actions_layout.setSpacing(10)
        
        btn_scan = QPushButton("Scan WiFi Networks")
        btn_scan.setMinimumHeight(50)
        btn_scan.setFont(QFont("Segoe UI", 11))
        btn_scan.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        actions_layout.addWidget(btn_scan, 0, 0)
        
        btn_visualize = QPushButton("View Visualizations")
        btn_visualize.setMinimumHeight(50)
        btn_visualize.setFont(QFont("Segoe UI", 11))
        btn_visualize.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        actions_layout.addWidget(btn_visualize, 0, 1)
        
        btn_realtime = QPushButton("Realtime Monitor")
        btn_realtime.setMinimumHeight(50)
        btn_realtime.setFont(QFont("Segoe UI", 11))
        btn_realtime.clicked.connect(lambda: self.tabs.setCurrentIndex(4))
        actions_layout.addWidget(btn_realtime, 0, 2)
        
        btn_data = QPushButton("Data Collection")
        btn_data.setMinimumHeight(50)
        btn_data.setFont(QFont("Segoe UI", 11))
        btn_data.clicked.connect(lambda: self.tabs.setCurrentIndex(3))
        actions_layout.addWidget(btn_data, 1, 0)
        
        btn_import = QPushButton("Import CSV")
        btn_import.setMinimumHeight(50)
        btn_import.setFont(QFont("Segoe UI", 11))
        btn_import.clicked.connect(self._import_csv)
        actions_layout.addWidget(btn_import, 1, 1)
        
        btn_sample = QPushButton("Load Sample Data")
        btn_sample.setMinimumHeight(50)
        btn_sample.setFont(QFont("Segoe UI", 11))
        btn_sample.clicked.connect(self._load_sample_data)
        actions_layout.addWidget(btn_sample, 1, 2)
        
        layout.addWidget(actions_group)
        
        # Stats overview
        stats_group = QGroupBox("System Overview")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(8)
        
        self.lbl_scan_count = QLabel("Networks Scanned: 0")
        self.lbl_scan_count.setFont(QFont("Segoe UI", 11))
        stats_layout.addWidget(self.lbl_scan_count, 0, 0)
        
        self.lbl_data_points = QLabel("Data Points: 0")
        self.lbl_data_points.setFont(QFont("Segoe UI", 11))
        stats_layout.addWidget(self.lbl_data_points, 0, 1)
        
        self.lbl_sessions = QLabel("Saved Sessions: 0")
        self.lbl_sessions.setFont(QFont("Segoe UI", 11))
        stats_layout.addWidget(self.lbl_sessions, 0, 2)
        
        self.lbl_status = QLabel("Status: Idle")
        self.lbl_status.setFont(QFont("Segoe UI", 11))
        self.lbl_status.setStyleSheet("color: #888;")
        stats_layout.addWidget(self.lbl_status, 1, 0)
        
        self.lbl_scanner_backend = QLabel("Scanner: " + self.scanner.get_backend_name())
        self.lbl_scanner_backend.setFont(QFont("Segoe UI", 11))
        stats_layout.addWidget(self.lbl_scanner_backend, 1, 1)
        
        layout.addWidget(stats_group)
        
        # Info text
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(150)
        info_text.setFont(QFont("Consolas", 9))
        info_text.setStyleSheet("background-color: #1a1a1a; color: #aaa;")
        info_text.setText(
            "SpectraLens v1.0.0\n"
            "====================\n\n"
            "A WiFi frequency visualization tool that transforms wireless signals\n"
            "into beautiful 2D heatmaps and 3D surface visualizations.\n\n"
            "Features:\n"
            "  - Scan nearby WiFi networks and view signal strength\n"
            "  - Generate 2D heatmaps of signal distribution\n"
            "  - Create interactive 3D surface plots\n"
            "  - Real-time WiFi signal monitoring\n"
            "  - Import/export measurement data (CSV)\n"
            "  - Database storage for historical analysis\n\n"
            "Creator: Asmaul Asni Subegi, S.Kom\n"
            "Email: sabayonx@gmail.com"
        )
        layout.addWidget(info_text)
        
        layout.addStretch()
        self.tabs.addTab(tab, "Dashboard")
    
    # =====================================================================
    # SCANNER TAB
    # =====================================================================
    def _create_scanner_tab(self):
        """Create the WiFi scanner tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)
        
        # Control bar
        control_bar = QHBoxLayout()
        
        self.btn_scan = QPushButton("Scan Now")
        self.btn_scan.setMinimumHeight(40)
        self.btn_scan.setFont(QFont("Segoe UI", 11))
        self.btn_scan.setStyleSheet("font-weight: bold;")
        self.btn_scan.clicked.connect(self._start_scan)
        control_bar.addWidget(self.btn_scan)
        
        self.scan_progress = QProgressBar()
        self.scan_progress.setMaximumWidth(200)
        self.scan_progress.setMaximumHeight(20)
        self.scan_progress.setVisible(False)
        control_bar.addWidget(self.scan_progress)
        
        control_bar.addStretch()
        
        lbl_count = QLabel("Networks Found:")
        lbl_count.setFont(QFont("Segoe UI", 10))
        control_bar.addWidget(lbl_count)
        
        self.lbl_network_count = QLabel("0")
        self.lbl_network_count.setFont(QFont("Segoe UI", 12))
        self.lbl_network_count.setStyleSheet("color: #00b4d8; font-weight: bold;")
        control_bar.addWidget(self.lbl_network_count)
        
        layout.addLayout(control_bar)
        
        # Splitter: table + chart
        splitter = QSplitter(Qt.Vertical)
        
        # Network table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        table_label = QLabel("WiFi Networks")
        table_label.setFont(QFont("Segoe UI", 10))
        table_label.setStyleSheet("font-weight: bold;")
        table_layout.addWidget(table_label)
        
        self.network_table = QTableWidget()
        self.network_table.setColumnCount(6)
        self.network_table.setHorizontalHeaderLabels(["SSID", "BSSID", "Signal (dBm)", "Quality", "Channel", "Frequency"])
        header = self.network_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.network_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.network_table.setAlternatingRowColors(True)
        self.network_table.setEditTriggers(QTableWidget.NoEditTriggers)
        table_layout.addWidget(self.network_table)
        
        splitter.addWidget(table_widget)
        
        # Chart area
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        
        chart_label = QLabel("Signal Strength Visualization")
        chart_label.setFont(QFont("Segoe UI", 10))
        chart_label.setStyleSheet("font-weight: bold;")
        chart_layout.addWidget(chart_label)
        
        self.scan_canvas = MplCanvas(self, width=10, height=3, dpi=100)
        self.scan_canvas.fig.patch.set_facecolor('#2a2a2a')
        self.scan_ax = self.scan_canvas.fig.add_subplot(111)
        self.scan_ax.set_facecolor('#1e1e1e')
        self.scan_ax.tick_params(colors='#aaa')
        self.scan_ax.xaxis.label.set_color('#aaa')
        self.scan_ax.yaxis.label.set_color('#aaa')
        self.scan_ax.title.set_color('#ddd')
        for spine in self.scan_ax.spines.values():
            spine.set_color('#444')
        self.scan_ax.set_xlabel('Signal Strength (dBm)')
        self.scan_ax.set_title('WiFi Networks Signal Strength')
        chart_layout.addWidget(self.scan_canvas)
        
        splitter.addWidget(chart_widget)
        splitter.setSizes([300, 250])
        
        layout.addWidget(splitter)
        
        self.tabs.addTab(tab, "Scanner")
    
    def _start_scan(self):
        """Start WiFi scanning in background thread."""
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("Scanning...")
        self.scan_progress.setVisible(True)
        self.scan_progress.setRange(0, 0)
        self.statusBar().showMessage("Scanning for WiFi networks...")
        
        self.scan_worker = ScanWorker()
        self.scan_worker.finished.connect(self._on_scan_complete)
        self.scan_worker.error.connect(self._on_scan_error)
        self.scan_worker.start()
    
    def _on_scan_complete(self, networks):
        """Handle scan completion."""
        self.networks = networks
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("Scan Now")
        self.scan_progress.setVisible(False)
        
        if networks:
            self._update_network_table(networks)
            self._update_scan_chart(networks)
            self.lbl_network_count.setText(str(len(networks)))
            self.lbl_scan_count.setText("Networks Scanned: " + str(len(networks)))
            self.statusBar().showMessage("Scan complete: " + str(len(networks)) + " networks found", 5000)
        else:
            self.statusBar().showMessage("No WiFi networks found", 5000)
    
    def _on_scan_error(self, error_msg):
        """Handle scan error."""
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("Scan Now")
        self.scan_progress.setVisible(False)
        self.statusBar().showMessage("Scan error: " + str(error_msg))
        QMessageBox.warning(self, "Scan Error", "Failed to scan: " + str(error_msg))
    
    def _update_network_table(self, networks):
        """Update the network table with scan results."""
        self.network_table.setRowCount(len(networks))
        
        for i, net in enumerate(networks):
            ssid = net.get('ssid', 'Unknown')
            bssid = net.get('bssid', 'N/A')
            rssi = net.get('rssi', 0)
            channel = net.get('channel', 0)
            frequency = net.get('frequency', 0)
            
            quality = self._rssi_to_quality(rssi)
            
            self.network_table.setItem(i, 0, QTableWidgetItem(str(ssid)))
            self.network_table.setItem(i, 1, QTableWidgetItem(str(bssid)))
            
            rssi_item = QTableWidgetItem(str(rssi))
            rssi_item.setForeground(self._signal_color(rssi))
            self.network_table.setItem(i, 2, rssi_item)
            
            quality_item = QTableWidgetItem(str(quality) + "%")
            quality_item.setForeground(self._signal_color(rssi))
            self.network_table.setItem(i, 3, quality_item)
            
            self.network_table.setItem(i, 4, QTableWidgetItem(str(channel)))
            
            freq_str = str(frequency) + " MHz" if frequency > 0 else "N/A"
            self.network_table.setItem(i, 5, QTableWidgetItem(freq_str))
    
    def _update_scan_chart(self, networks):
        """Update the bar chart with scan results."""
        self.scan_ax.clear()
        self.scan_ax.set_facecolor('#1e1e1e')
        
        if not networks:
            self.scan_ax.text(0.5, 0.5, 'No networks found', 
                            ha='center', va='center', color='#888', fontsize=14)
            self.scan_canvas.draw()
            return
        
        sorted_nets = sorted(networks, key=lambda x: x['rssi'])
        ssids = [net['ssid'][:25] for net in sorted_nets]
        rssis = [net['rssi'] for net in sorted_nets]
        colors = [self._rssi_to_hex_color(r) for r in rssis]
        
        self.scan_ax.barh(range(len(ssids)), rssis, color=colors, edgecolor='#555', linewidth=0.5)
        self.scan_ax.set_yticks(range(len(ssids)))
        self.scan_ax.set_yticklabels(ssids, fontsize=9, color='#ddd')
        self.scan_ax.set_xlabel('Signal Strength (dBm)', color='#aaa')
        self.scan_ax.set_title('WiFi Networks Signal Strength', color='#ddd', fontweight='bold')
        self.scan_ax.invert_yaxis()
        
        for i, (rssi, net) in enumerate(zip(rssis, sorted_nets)):
            label = str(rssi) + ' dBm | Ch ' + str(net.get("channel", "?"))
            self.scan_ax.text(rssi + 0.5, i, label, va='center', fontsize=8, color='#aaa')
        
        min_rssi = min(rssis) - 15 if rssis else -100
        max_rssi = max(rssis) + 10 if rssis else -30
        self.scan_ax.set_xlim(min_rssi, max_rssi + 5)
        
        self.scan_ax.grid(axis='x', alpha=0.15, linestyle='--', color='#555')
        for spine in self.scan_ax.spines.values():
            spine.set_color('#444')
        self.scan_ax.tick_params(colors='#aaa')
        
        self.scan_canvas.draw()
    
    # =====================================================================
    # VISUALIZATION TAB
    # =====================================================================
    def _create_visualization_tab(self):
        """Create the visualization tab with embedded heatmap and 3D surface."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)
        
        # Control bar
        control_bar = QHBoxLayout()
        
        self.btn_gen_heatmap = QPushButton("Generate Heatmap")
        self.btn_gen_heatmap.setMinimumHeight(35)
        self.btn_gen_heatmap.clicked.connect(self._generate_heatmap)
        control_bar.addWidget(self.btn_gen_heatmap)
        
        self.btn_gen_surface = QPushButton("Generate 3D Surface")
        self.btn_gen_surface.setMinimumHeight(35)
        self.btn_gen_surface.clicked.connect(self._generate_surface)
        control_bar.addWidget(self.btn_gen_surface)
        
        self.btn_gen_interactive = QPushButton("Interactive 3D (Browser)")
        self.btn_gen_interactive.setMinimumHeight(35)
        self.btn_gen_interactive.clicked.connect(self._generate_interactive)
        control_bar.addWidget(self.btn_gen_interactive)
        
        control_bar.addStretch()
        
        control_bar.addWidget(QLabel("Resolution:"))
        self.resolution_spin = QSpinBox()
        self.resolution_spin.setRange(10, 200)
        self.resolution_spin.setValue(50)
        self.resolution_spin.setMinimumWidth(60)
        control_bar.addWidget(self.resolution_spin)
        
        layout.addLayout(control_bar)
        
        # Splitter: canvas (left) + info (right)
        splitter = QSplitter(Qt.Horizontal)
        
        # LEFT: Stacked canvas area (heatmap / 3D)
        display_widget = QWidget()
        display_layout = QVBoxLayout(display_widget)
        display_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Embedded 2D Heatmap Canvas ---
        self.heatmap_canvas = MplCanvas(self, width=8, height=5, dpi=100)
        self.heatmap_canvas.fig.patch.set_facecolor('#2a2a2a')
        self.heatmap_ax = self.heatmap_canvas.fig.add_subplot(111)
        self.heatmap_ax.set_facecolor('#1e1e1e')
        self.heatmap_ax.tick_params(colors='#aaa')
        self.heatmap_ax.xaxis.label.set_color('#aaa')
        self.heatmap_ax.yaxis.label.set_color('#aaa')
        self.heatmap_ax.title.set_color('#ddd')
        for spine in self.heatmap_ax.spines.values():
            spine.set_color('#444')
        self.heatmap_ax.set_xlabel('X Position (meters)')
        self.heatmap_ax.set_ylabel('Y Position (meters)')
        self.heatmap_ax.set_title('WiFi Signal Strength Heatmap')
        self.heatmap_ax.text(0.5, 0.5, 'Load data & click "Generate Heatmap"',
                            ha='center', va='center', color='#666', fontsize=14,
                            transform=self.heatmap_ax.transAxes)
        display_layout.addWidget(self.heatmap_canvas)
        
        # --- Embedded 3D Surface Canvas ---
        self.surface_canvas = MplCanvas3D(self, width=8, height=5, dpi=100)
        self.surface_canvas.fig.patch.set_facecolor('#2a2a2a')
        self.surface_canvas.ax.set_title('WiFi Signal 3D Surface', color='#ddd', fontweight='bold')
        self.surface_canvas.ax.set_xlabel('X Position (m)')
        self.surface_canvas.ax.set_ylabel('Y Position (m)')
        self.surface_canvas.ax.set_zlabel('Signal (dBm)')
        self.surface_canvas.ax.text2D(0.5, 0.5, 'Load data & click "Generate 3D Surface"',
                                     ha='center', va='center', color='#666', fontsize=14,
                                     transform=self.surface_canvas.ax.transAxes)
        self.surface_canvas.setVisible(False)  # Hide initially
        display_layout.addWidget(self.surface_canvas)
        
        splitter.addWidget(display_widget)
        
        # RIGHT: Info panel
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        info_group = QGroupBox("Visualization Info")
        info_group_layout = QVBoxLayout(info_group)
        
        self.viz_info = QTextEdit()
        self.viz_info.setReadOnly(True)
        self.viz_info.setMaximumWidth(300)
        self.viz_info.setFont(QFont("Consolas", 9))
        self.viz_info.setText("No visualization generated yet.\n\nClick 'Generate Heatmap' or\n'Generate 3D Surface' to start.")
        info_group_layout.addWidget(self.viz_info)
        
        info_layout.addWidget(info_group)
        
        data_group = QGroupBox("Data Points")
        data_group_layout = QVBoxLayout(data_group)
        
        self.lbl_viz_points = QLabel("Points: 0")
        data_group_layout.addWidget(self.lbl_viz_points)
        
        self.lbl_viz_range = QLabel("Signal Range: N/A")
        data_group_layout.addWidget(self.lbl_viz_range)
        
        self.lbl_viz_grid = QLabel("Grid: N/A")
        data_group_layout.addWidget(self.lbl_viz_grid)
        
        info_layout.addWidget(data_group)
        info_layout.addStretch()
        
        splitter.addWidget(info_widget)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
        
        self.tabs.addTab(tab, "Visualization")
    
    def _check_data_for_viz(self):
        """Check if there is data available for visualization."""
        if not self.measurement_points:
            QMessageBox.warning(self, "No Data", 
                "No measurement data available.\n\n"
                "Please add data points in the 'Data Collection' tab\n"
                "or import a CSV file first.")
            return False
        return True
    
    def _get_viz_data(self):
        """Get points and values from measurement data."""
        points = np.array([[p[0], p[1]] for p in self.measurement_points])
        values = np.array([p[2] for p in self.measurement_points])
        return points, values
    
    def _interpolate(self, points, values):
        """Perform IDW interpolation on the data."""
        self.interpolator = IDWInterpolator(power=2, k=5)
        self.interpolator.fit(points, values)
        
        grid_builder = GridBuilder(points)
        resolution = self.resolution_spin.value()
        grid_x, grid_y = grid_builder.create_grid(resolution=resolution)
        grid_z = self.interpolator.interpolate(grid_x, grid_y)
        
        return grid_x, grid_y, grid_z
    
    def _generate_heatmap(self):
        """Generate 2D heatmap visualization embedded in GUI."""
        if not self._check_data_for_viz():
            return
        
        self.statusBar().showMessage("Generating heatmap...")
        QApplication.processEvents()
        
        try:
            points, values = self._get_viz_data()
            grid_x, grid_y, grid_z = self._interpolate(points, values)
            
            # Clear and redraw on embedded heatmap canvas
            self.heatmap_ax.clear()
            self.heatmap_ax.set_facecolor('#1e1e1e')
            
            # Plot contourf
            contour = self.heatmap_ax.contourf(grid_x, grid_y, grid_z, 
                                               levels=50, cmap='RdYlBu_r', alpha=0.85)
            contour_lines = self.heatmap_ax.contour(grid_x, grid_y, grid_z, 
                                                    levels=10, colors='black', 
                                                    linewidths=0.5, alpha=0.3)
            self.heatmap_ax.clabel(contour_lines, inline=True, fontsize=8, fmt='%.0f')
            
            # Overlay points
            scatter = self.heatmap_ax.scatter(points[:, 0], points[:, 1], 
                                             c=values, cmap='RdYlBu_r', 
                                             edgecolors='black', linewidth=1,
                                             s=80, zorder=5, vmin=grid_z.min(), vmax=grid_z.max())
            for i, (x, y) in enumerate(points):
                self.heatmap_ax.annotate(f'{values[i]:.0f}', (x, y), 
                                        xytext=(5, 5), textcoords='offset points',
                                        fontsize=8, fontweight='bold',
                                        bbox=dict(boxstyle='round,pad=0.2', 
                                                facecolor='white', alpha=0.7))
            
            # Colorbar
            cbar = self.heatmap_canvas.fig.colorbar(contour, ax=self.heatmap_ax, 
                                                    label='Signal Strength (dBm)', shrink=0.8)
            cbar.ax.yaxis.label.set_color('#aaa')
            cbar.ax.tick_params(colors='#aaa')
            
            # Labels
            self.heatmap_ax.set_xlabel('X Position (meters)', color='#aaa')
            self.heatmap_ax.set_ylabel('Y Position (meters)', color='#aaa')
            self.heatmap_ax.set_title('WiFi Signal Strength Heatmap', color='#ddd', fontweight='bold')
            self.heatmap_ax.set_aspect('equal')
            self.heatmap_ax.grid(True, alpha=0.3, linestyle='--', color='#555')
            
            # Stats box
            stats_text = (f"Min: {grid_z.min():.0f} dBm | Max: {grid_z.max():.0f} dBm | "
                         f"Avg: {grid_z.mean():.0f} dBm | Grid: {grid_x.shape[0]}×{grid_x.shape[1]}")
            self.heatmap_ax.text(0.02, 0.98, stats_text, transform=self.heatmap_ax.transAxes,
                               fontsize=9, verticalalignment='top',
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            for spine in self.heatmap_ax.spines.values():
                spine.set_color('#444')
            self.heatmap_ax.tick_params(colors='#aaa')
            
            # Show heatmap, hide 3D
            self.heatmap_canvas.setVisible(True)
            self.surface_canvas.setVisible(False)
            self.heatmap_canvas.draw()
            
            self.viz_info.setText(
                "Heatmap generated successfully!\n\n"
                "Points: " + str(len(points)) + "\n"
                "Grid: " + str(grid_x.shape[0]) + "x" + str(grid_x.shape[1]) + "\n"
                "Signal Range: " + str(int(grid_z.min())) + " to " + str(int(grid_z.max())) + " dBm\n"
                "Average: " + str(int(grid_z.mean())) + " dBm"
            )
            self.lbl_viz_points.setText("Points: " + str(len(points)))
            self.lbl_viz_range.setText("Signal Range: " + str(int(grid_z.min())) + " to " + str(int(grid_z.max())) + " dBm")
            self.lbl_viz_grid.setText("Grid: " + str(grid_x.shape[0]) + "x" + str(grid_x.shape[1]))
            
            self.statusBar().showMessage("Heatmap generated successfully", 5000)
            
        except Exception as e:
            self.statusBar().showMessage("Error: " + str(e))
            QMessageBox.warning(self, "Error", "Failed to generate heatmap:\n" + str(e))
    
    def _generate_surface(self):
        """Generate 3D surface visualization embedded in GUI."""
        if not self._check_data_for_viz():
            return
        
        self.statusBar().showMessage("Generating 3D surface...")
        QApplication.processEvents()
        
        try:
            points, values = self._get_viz_data()
            grid_x, grid_y, grid_z = self._interpolate(points, values)
            
            # Clear and redraw on embedded 3D canvas
            self.surface_canvas.ax.clear()
            self.surface_canvas.ax.set_facecolor('#1e1e1e')
            
            # Plot surface
            surf = self.surface_canvas.ax.plot_surface(grid_x, grid_y, grid_z, 
                                                       cmap='RdYlBu_r', alpha=0.9,
                                                       linewidth=0, antialiased=True,
                                                       edgecolor='none')
            
            # Wireframe
            stride = max(1, grid_x.shape[0] // 20)
            self.surface_canvas.ax.plot_wireframe(grid_x, grid_y, grid_z, 
                                                 rstride=stride, cstride=stride,
                                                 color='gray', alpha=0.15, linewidth=0.3)
            
            # Overlay points
            if points is not None and len(points) > 0:
                self.surface_canvas.ax.scatter(points[:, 0], points[:, 1], values,
                                              c=values, cmap='RdYlBu_r', 
                                              s=60, edgecolors='black', linewidth=0.5,
                                              vmin=grid_z.min(), vmax=grid_z.max())
            
            # Labels
            self.surface_canvas.ax.set_xlabel('X Position (m)', color='#aaa', labelpad=8)
            self.surface_canvas.ax.set_ylabel('Y Position (m)', color='#aaa', labelpad=8)
            self.surface_canvas.ax.set_zlabel('Signal (dBm)', color='#aaa', labelpad=8)
            self.surface_canvas.ax.set_title('WiFi Signal 3D Surface', color='#ddd', fontweight='bold', pad=15)
            
            # View angle
            self.surface_canvas.ax.view_init(elev=30, azim=-60)
            
            # Colorbar
            cbar = self.surface_canvas.fig.colorbar(surf, ax=self.surface_canvas.ax, 
                                                    shrink=0.6, aspect=20, pad=0.1)
            cbar.set_label('Signal Strength (dBm)', fontsize=10)
            cbar.ax.yaxis.label.set_color('#aaa')
            cbar.ax.tick_params(colors='#aaa')
            
            # Stats
            stats_text = (f"Peak: {grid_z.max():.0f} dBm\n"
                         f"Lowest: {grid_z.min():.0f} dBm\n"
                         f"Range: {grid_z.max() - grid_z.min():.0f} dB")
            self.surface_canvas.ax.text2D(0.02, 0.98, stats_text, 
                                         transform=self.surface_canvas.ax.transAxes,
                                         fontsize=9, verticalalignment='top',
                                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # Style 3D pane
            self.surface_canvas.ax.xaxis.pane.set_facecolor('#2a2a2a')
            self.surface_canvas.ax.yaxis.pane.set_facecolor('#2a2a2a')
            self.surface_canvas.ax.zaxis.pane.set_facecolor('#2a2a2a')
            self.surface_canvas.ax.xaxis.pane.set_edgecolor('#444')
            self.surface_canvas.ax.yaxis.pane.set_edgecolor('#444')
            self.surface_canvas.ax.zaxis.pane.set_edgecolor('#444')
            self.surface_canvas.ax.tick_params(colors='#aaa')
            
            # Show 3D, hide heatmap
            self.surface_canvas.setVisible(True)
            self.heatmap_canvas.setVisible(False)
            self.surface_canvas.draw()
            
            self.viz_info.setText(
                "3D Surface generated successfully!\n\n"
                "Grid: " + str(grid_x.shape[0]) + "x" + str(grid_x.shape[1]) + "\n"
                "Peak Signal: " + str(int(grid_z.max())) + " dBm\n"
                "Lowest Signal: " + str(int(grid_z.min())) + " dBm\n"
                "Range: " + str(int(grid_z.max() - grid_z.min())) + " dB\n\n"
                "Tip: You can also generate an Interactive 3D\n"
                "plot (opens in browser) for rotation/zoom."
            )
            self.lbl_viz_points.setText("Points: " + str(len(points)))
            self.lbl_viz_range.setText("Signal Range: " + str(int(grid_z.min())) + " to " + str(int(grid_z.max())) + " dBm")
            self.lbl_viz_grid.setText("Grid: " + str(grid_x.shape[0]) + "x" + str(grid_x.shape[1]))
            
            self.statusBar().showMessage("3D Surface generated successfully", 5000)
            
        except Exception as e:
            self.statusBar().showMessage("Error: " + str(e))
            QMessageBox.warning(self, "Error", "Failed to generate 3D surface:\n" + str(e))
    
    def _generate_interactive(self):
        """Generate interactive 3D surface (HTML)."""
        if not self._check_data_for_viz():
            return
        
        self.statusBar().showMessage("Generating interactive 3D...")
        QApplication.processEvents()
        
        try:
            points, values = self._get_viz_data()
            grid_x, grid_y, grid_z = self._interpolate(points, values)
            
            surface = Surface3D()
            filepath = surface.plot_interactive(grid_x, grid_y, grid_z,
                                               title="WiFi Signal - Interactive 3D",
                                               filename="gui_interactive.html",
                                               points=points, values=values)
            
            self.viz_info.setText(
                "Interactive 3D generated!\n\n"
                "File: " + filepath + "\n\n"
                "Open the HTML file in your browser\n"
                "for an interactive 3D experience.\n\n"
                "You can rotate, zoom, and hover\n"
                "to explore the signal landscape."
            )
            
            import webbrowser
            webbrowser.open("file:///" + os.path.abspath(filepath))
            
            self.statusBar().showMessage("Interactive 3D opened in browser", 5000)
            
        except Exception as e:
            self.statusBar().showMessage("Error: " + str(e))
            QMessageBox.warning(self, "Error", "Failed to generate interactive 3D:\n" + str(e))
    
    # =====================================================================
    # DATA COLLECTION TAB
    # =====================================================================
    def _create_data_tab(self):
        """Create the data collection tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)
        
        # Control bar
        control_bar = QHBoxLayout()
        
        self.btn_add_point = QPushButton("Add Data Point")
        self.btn_add_point.setMinimumHeight(35)
        self.btn_add_point.clicked.connect(self._add_data_point)
        control_bar.addWidget(self.btn_add_point)
        
        self.btn_clear_data = QPushButton("Clear All")
        self.btn_clear_data.setMinimumHeight(35)
        self.btn_clear_data.setStyleSheet("background-color: #cc3333;")
        self.btn_clear_data.clicked.connect(self._clear_data)
        control_bar.addWidget(self.btn_clear_data)
        
        control_bar.addStretch()
        
        self.lbl_data_count = QLabel("Points: 0")
        self.lbl_data_count.setFont(QFont("Segoe UI", 10))
        self.lbl_data_count.setStyleSheet("font-weight: bold;")
        control_bar.addWidget(self.lbl_data_count)
        
        layout.addLayout(control_bar)
        
        # Data entry form
        form_group = QGroupBox("Add Measurement Point")
        form_layout = QGridLayout(form_group)
        form_layout.setSpacing(8)
        
        form_layout.addWidget(QLabel("X Position:"), 0, 0)
        self.spin_x = QSpinBox()
        self.spin_x.setRange(-100, 100)
        self.spin_x.setValue(0)
        form_layout.addWidget(self.spin_x, 0, 1)
        
        form_layout.addWidget(QLabel("Y Position:"), 0, 2)
        self.spin_y = QSpinBox()
        self.spin_y.setRange(-100, 100)
        self.spin_y.setValue(0)
        form_layout.addWidget(self.spin_y, 0, 3)
        
        form_layout.addWidget(QLabel("Signal (dBm):"), 0, 4)
        self.spin_signal = QSpinBox()
        self.spin_signal.setRange(-100, 0)
        self.spin_signal.setValue(-50)
        form_layout.addWidget(self.spin_signal, 0, 5)
        
        form_layout.addWidget(QLabel("SSID:"), 0, 6)
        self.edit_ssid = QLabel("Manual Point")
        form_layout.addWidget(self.edit_ssid, 0, 7)
        
        layout.addWidget(form_group)
        
        # Data table
        table_label = QLabel("Measurement Points")
        table_label.setFont(QFont("Segoe UI", 10))
        table_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(table_label)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(4)
        self.data_table.setHorizontalHeaderLabels(["X", "Y", "Signal (dBm)", "SSID"])
        header = self.data_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.data_table)
        
        self.tabs.addTab(tab, "Data Collection")
    
    def _add_data_point(self):
        """Add a manual data point."""
        x = self.spin_x.value()
        y = self.spin_y.value()
        signal = self.spin_signal.value()
        ssid = "Manual Point"
        
        self.measurement_points.append((x, y, signal, ssid, 0))
        self._update_data_table()
        self.lbl_data_count.setText("Points: " + str(len(self.measurement_points)))
        self.lbl_data_points.setText("Data Points: " + str(len(self.measurement_points)))
        self.statusBar().showMessage("Data point added: (" + str(x) + ", " + str(y) + ") = " + str(signal) + " dBm", 3000)
    
    def _clear_data(self):
        """Clear all measurement data."""
        reply = QMessageBox.question(self, "Clear Data", 
            "Are you sure you want to clear all measurement data?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.measurement_points = []
            self.data_table.setRowCount(0)
            self.lbl_data_count.setText("Points: 0")
            self.lbl_data_points.setText("Data Points: 0")
            # Reset embedded canvases
            self.heatmap_ax.clear()
            self.heatmap_ax.set_facecolor('#1e1e1e')
            self.heatmap_ax.text(0.5, 0.5, 'Load data & click "Generate Heatmap"',
                                ha='center', va='center', color='#666', fontsize=14,
                                transform=self.heatmap_ax.transAxes)
            self.heatmap_canvas.draw()
            self.surface_canvas.ax.clear()
            self.surface_canvas.ax.set_facecolor('#1e1e1e')
            self.surface_canvas.ax.text2D(0.5, 0.5, 'Load data & click "Generate 3D Surface"',
                                         ha='center', va='center', color='#666', fontsize=14,
                                         transform=self.surface_canvas.ax.transAxes)
            self.surface_canvas.draw()
            self.viz_info.setText("No visualization generated yet.\n\nClick 'Generate Heatmap' or\n'Generate 3D Surface' to start.")
            self.lbl_viz_points.setText("Points: 0")
            self.lbl_viz_range.setText("Signal Range: N/A")
            self.lbl_viz_grid.setText("Grid: N/A")
            self.statusBar().showMessage("Data cleared", 3000)
    
    def _update_data_table(self):
        """Update the data table."""
        self.data_table.setRowCount(len(self.measurement_points))
        for i, point in enumerate(self.measurement_points):
            self.data_table.setItem(i, 0, QTableWidgetItem(str(point[0])))
            self.data_table.setItem(i, 1, QTableWidgetItem(str(point[1])))
            self.data_table.setItem(i, 2, QTableWidgetItem(str(point[2])))
            self.data_table.setItem(i, 3, QTableWidgetItem(str(point[3])))
    
    # =====================================================================
    # RECORDING TAB (Mode Rekam Jalan Langsung)
    # =====================================================================
    def _create_recording_tab(self):
        """Create the live recording tab for walk-around data collection."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        # Recording state
        self.recording_active = False
        self.recording_points = []
        self.recording_path_x = []
        self.recording_path_y = []
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self._recording_step)
        self.recording_position = [0, 0]
        self.recording_step_size = 1.0

        # Control bar
        control_bar = QHBoxLayout()

        self.btn_record = QPushButton("Start Recording")
        self.btn_record.setMinimumHeight(40)
        self.btn_record.setFont(QFont("Segoe UI", 11))
        self.btn_record.setStyleSheet("font-weight: bold; background-color: #cc3333;")
        self.btn_record.clicked.connect(self._toggle_recording)
        control_bar.addWidget(self.btn_record)

        self.btn_record_export = QPushButton("Export Recording")
        self.btn_record_export.setMinimumHeight(35)
        self.btn_record_export.clicked.connect(self._export_recording)
        control_bar.addWidget(self.btn_record_export)

        self.btn_record_clear = QPushButton("Clear Recording")
        self.btn_record_clear.setMinimumHeight(35)
        self.btn_record_clear.setStyleSheet("background-color: #666;")
        self.btn_record_clear.clicked.connect(self._clear_recording)
        control_bar.addWidget(self.btn_record_clear)

        control_bar.addStretch()

        # Position controls
        pos_group = QGroupBox("Position Control")
        pos_layout = QHBoxLayout(pos_group)

        pos_layout.addWidget(QLabel("X:"))
        self.record_spin_x = QSpinBox()
        self.record_spin_x.setRange(-100, 100)
        self.record_spin_x.setValue(0)
        pos_layout.addWidget(self.record_spin_x)

        pos_layout.addWidget(QLabel("Y:"))
        self.record_spin_y = QSpinBox()
        self.record_spin_y.setRange(-100, 100)
        self.record_spin_y.setValue(0)
        pos_layout.addWidget(self.record_spin_y)

        self.btn_set_pos = QPushButton("Set Position")
        self.btn_set_pos.setMinimumHeight(30)
        self.btn_set_pos.clicked.connect(self._set_recording_position)
        pos_layout.addWidget(self.btn_set_pos)

        pos_layout.addWidget(QLabel("Step (m):"))
        self.record_step_spin = QDoubleSpinBox()
        self.record_step_spin.setRange(0.1, 10.0)
        self.record_step_spin.setValue(1.0)
        self.record_step_spin.setSingleStep(0.1)
        pos_layout.addWidget(self.record_step_spin)

        control_bar.addWidget(pos_group)

        layout.addLayout(control_bar)

        # Status bar for recording
        record_status = QHBoxLayout()

        self.lbl_record_status = QLabel("Status: Idle")
        self.lbl_record_status.setFont(QFont("Segoe UI", 10))
        self.lbl_record_status.setStyleSheet("color: #888; font-weight: bold;")
        record_status.addWidget(self.lbl_record_status)

        self.lbl_record_count = QLabel("Points: 0")
        self.lbl_record_count.setFont(QFont("Segoe UI", 10))
        record_status.addWidget(self.lbl_record_count)

        self.lbl_record_pos = QLabel("Position: (0, 0)")
        self.lbl_record_pos.setFont(QFont("Segoe UI", 10))
        record_status.addWidget(self.lbl_record_pos)

        self.lbl_record_signal = QLabel("Signal: N/A")
        self.lbl_record_signal.setFont(QFont("Segoe UI", 10))
        record_status.addWidget(self.lbl_record_signal)

        record_status.addStretch()

        layout.addLayout(record_status)

        # Splitter: canvas (left) + table (right)
        splitter = QSplitter(Qt.Horizontal)

        # LEFT: Recording canvas with path visualization
        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout(canvas_widget)
        canvas_layout.setContentsMargins(0, 0, 0, 0)

        canvas_label = QLabel("Recording Path & Signal Map")
        canvas_label.setFont(QFont("Segoe UI", 10))
        canvas_label.setStyleSheet("font-weight: bold;")
        canvas_layout.addWidget(canvas_label)

        self.record_canvas = MplCanvas(self, width=8, height=5, dpi=100)
        self.record_canvas.fig.patch.set_facecolor('#2a2a2a')
        self.record_ax = self.record_canvas.fig.add_subplot(111)
        self.record_ax.set_facecolor('#1e1e1e')
        self.record_ax.tick_params(colors='#aaa')
        self.record_ax.xaxis.label.set_color('#aaa')
        self.record_ax.yaxis.label.set_color('#aaa')
        self.record_ax.title.set_color('#ddd')
        for spine in self.record_ax.spines.values():
            spine.set_color('#444')
        self.record_ax.set_xlabel('X Position (meters)')
        self.record_ax.set_ylabel('Y Position (meters)')
        self.record_ax.set_title('Live Recording - Walk Path')
        self.record_ax.set_xlim(-15, 15)
        self.record_ax.set_ylim(-15, 15)
        self.record_ax.grid(True, alpha=0.15, linestyle='--', color='#555')
        self.record_ax.text(0.5, 0.5, 'Set position and click "Start Recording"\nto begin walk-around data collection',
                           ha='center', va='center', color='#666', fontsize=12,
                           transform=self.record_ax.transAxes)
        canvas_layout.addWidget(self.record_canvas)

        splitter.addWidget(canvas_widget)

        # RIGHT: Recording data table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)

        table_label = QLabel("Recorded Points")
        table_label.setFont(QFont("Segoe UI", 10))
        table_label.setStyleSheet("font-weight: bold;")
        table_layout.addWidget(table_label)

        self.record_table = QTableWidget()
        self.record_table.setColumnCount(5)
        self.record_table.setHorizontalHeaderLabels(["X", "Y", "Signal (dBm)", "SSID", "Channel"])
        header = self.record_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.record_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.record_table.setAlternatingRowColors(True)
        self.record_table.setEditTriggers(QTableWidget.NoEditTriggers)
        table_layout.addWidget(self.record_table)

        splitter.addWidget(table_widget)
        splitter.setSizes([700, 300])

        layout.addWidget(splitter)

        self.tabs.addTab(tab, "Recording")

    def _toggle_recording(self):
        """Toggle recording on/off."""
        if self.recording_active:
            # Stop recording
            self.recording_active = False
            self.recording_timer.stop()
            self.btn_record.setText("Start Recording")
            self.btn_record.setStyleSheet("font-weight: bold; background-color: #cc3333;")
            self.lbl_record_status.setText("Status: Stopped")
            self.lbl_record_status.setStyleSheet("color: #888; font-weight: bold;")
            self.statusBar().showMessage("Recording stopped. " + str(len(self.recording_points)) + " points collected", 5000)
        else:
            # Start recording
            self.recording_active = True
            self.recording_step_size = self.record_step_spin.value()
            interval = 3000  # 3 seconds between scans
            self.recording_timer.start(interval)
            self.btn_record.setText("Stop Recording")
            self.btn_record.setStyleSheet("font-weight: bold; background-color: #008800;")
            self.lbl_record_status.setText("Status: Recording...")
            self.lbl_record_status.setStyleSheet("color: #00cc00; font-weight: bold;")
            self.statusBar().showMessage("Recording started - move to new positions and recording will auto-scan", 5000)

    def _set_recording_position(self):
        """Manually set the current recording position."""
        x = self.record_spin_x.value()
        y = self.record_spin_y.value()
        self.recording_position = [float(x), float(y)]
        self.lbl_record_pos.setText("Position: (" + str(x) + ", " + str(y) + ")")
        self._update_recording_canvas()
        self.statusBar().showMessage("Position set to (" + str(x) + ", " + str(y) + ")", 3000)

    def _recording_step(self):
        """Perform one recording step: scan WiFi at current position."""
        x, y = self.recording_position
        self.statusBar().showMessage("Recording at position (" + str(x) + ", " + str(y) + ")...")

        try:
            networks = self.scanner.scan()

            if networks:
                # Find strongest network
                strongest = max(networks, key=lambda n: n.get('rssi', -100))
                ssid = strongest.get('ssid', 'Unknown')
                rssi = strongest.get('rssi', -100)
                channel = strongest.get('channel', 0)

                # Record the point
                self.recording_points.append((x, y, rssi, ssid, channel))
                self.measurement_points.append((x, y, rssi, ssid, channel))

                # Update UI
                self._update_recording_table()
                self._update_recording_canvas()
                self.lbl_record_count.setText("Points: " + str(len(self.recording_points)))
                self.lbl_record_signal.setText("Signal: " + str(rssi) + " dBm (" + ssid[:15] + ")")
                self.lbl_record_signal.setStyleSheet("color: " + self._rssi_to_hex_color(rssi) + ";")

                # Auto-increment position for next step
                self.recording_position[0] += self.recording_step_size
                self.record_spin_x.setValue(int(round(self.recording_position[0])))
                self.lbl_record_pos.setText("Position: (" + str(int(round(self.recording_position[0]))) + ", " + str(int(round(self.recording_position[1]))) + ")")

                self.statusBar().showMessage("Recorded: (" + str(x) + ", " + str(y) + ") = " + str(rssi) + " dBm", 3000)
            else:
                self.statusBar().showMessage("No networks found at position (" + str(x) + ", " + str(y) + ")", 3000)

        except Exception as e:
            self.statusBar().showMessage("Recording error: " + str(e))

    def _update_recording_canvas(self):
        """Update the recording canvas with path and signal data."""
        self.record_ax.clear()
        self.record_ax.set_facecolor('#1e1e1e')

        if not self.recording_points:
            self.record_ax.set_xlim(-15, 15)
            self.record_ax.set_ylim(-15, 15)
            self.record_ax.set_xlabel('X Position (meters)', color='#aaa')
            self.record_ax.set_ylabel('Y Position (meters)', color='#aaa')
            self.record_ax.set_title('Live Recording - Walk Path', color='#ddd', fontweight='bold')
            self.record_ax.grid(True, alpha=0.15, linestyle='--', color='#555')
            self.record_ax.text(0.5, 0.5, 'Start recording to collect data points',
                               ha='center', va='center', color='#666', fontsize=12,
                               transform=self.record_ax.transAxes)
            for spine in self.record_ax.spines.values():
                spine.set_color('#444')
            self.record_ax.tick_params(colors='#aaa')
            self.record_canvas.draw()
            return

        # Extract data
        xs = [p[0] for p in self.recording_points]
        ys = [p[1] for p in self.recording_points]
        signals = [p[2] for p in self.recording_points]

        # Plot path line
        self.record_ax.plot(xs, ys, '-', color='#00b4d8', linewidth=2, alpha=0.7, label='Walk Path')

        # Plot points colored by signal
        scatter = self.record_ax.scatter(xs, ys, c=signals, cmap='RdYlBu_r',
                                        s=120, edgecolors='black', linewidth=1,
                                        vmin=-100, vmax=-30, zorder=5)

        # Add signal labels
        for i, (x, y, s) in enumerate(zip(xs, ys, signals)):
            self.record_ax.annotate(f'{s:.0f}', (x, y),
                                   xytext=(3, 3), textcoords='offset points',
                                   fontsize=8, fontweight='bold',
                                   bbox=dict(boxstyle='round,pad=0.2',
                                           facecolor='white', alpha=0.7))

        # Mark start and end
        if len(self.recording_points) > 0:
            sx, sy = xs[0], ys[0]
            self.record_ax.plot(sx, sy, 'o', color='green', markersize=12,
                               markeredgecolor='white', markeredgewidth=2, zorder=10)
            self.record_ax.text(sx, sy - 1.5, 'Start', ha='center', va='top',
                               fontsize=9, fontweight='bold', color='green')

        if len(self.recording_points) > 1:
            ex, ey = xs[-1], ys[-1]
            self.record_ax.plot(ex, ey, 's', color='red', markersize=12,
                               markeredgecolor='white', markeredgewidth=2, zorder=10)
            self.record_ax.text(ex, ey + 1.5, 'Current', ha='center', va='bottom',
                               fontsize=9, fontweight='bold', color='red')

        # Colorbar
        cbar = self.record_canvas.fig.colorbar(scatter, ax=self.record_ax,
                                               label='Signal (dBm)', shrink=0.8)
        cbar.ax.yaxis.label.set_color('#aaa')
        cbar.ax.tick_params(colors='#aaa')

        # Auto-adjust limits with padding
        all_x = xs + [self.recording_position[0]]
        all_y = ys + [self.recording_position[1]]
        x_min, x_max = min(all_x) - 2, max(all_x) + 2
        y_min, y_max = min(all_y) - 2, max(all_y) + 2
        x_range = max(x_max - x_min, 10)
        y_range = max(y_max - y_min, 10)
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        half_range = max(x_range, y_range) / 2
        self.record_ax.set_xlim(x_center - half_range, x_center + half_range)
        self.record_ax.set_ylim(y_center - half_range, y_center + half_range)

        self.record_ax.set_xlabel('X Position (meters)', color='#aaa')
        self.record_ax.set_ylabel('Y Position (meters)', color='#aaa')
        self.record_ax.set_title('Live Recording - Walk Path', color='#ddd', fontweight='bold')
        self.record_ax.grid(True, alpha=0.15, linestyle='--', color='#555')
        self.record_ax.legend(loc='upper right', fontsize=8, facecolor='#2a2a2a',
                             edgecolor='#444', labelcolor='#ddd')

        for spine in self.record_ax.spines.values():
            spine.set_color('#444')
        self.record_ax.tick_params(colors='#aaa')
        self.record_canvas.draw()

    def _update_recording_table(self):
        """Update the recording data table."""
        self.record_table.setRowCount(len(self.recording_points))
        for i, point in enumerate(self.recording_points):
            self.record_table.setItem(i, 0, QTableWidgetItem(str(point[0])))
            self.record_table.setItem(i, 1, QTableWidgetItem(str(point[1])))
            signal_item = QTableWidgetItem(str(point[2]))
            signal_item.setForeground(self._signal_color(point[2]))
            self.record_table.setItem(i, 2, signal_item)
            self.record_table.setItem(i, 3, QTableWidgetItem(str(point[3])))
            self.record_table.setItem(i, 4, QTableWidgetItem(str(point[4])))

    def _export_recording(self):
        """Export recording data to CSV."""
        if not self.recording_points:
            QMessageBox.warning(self, "No Data", "No recording data to export.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Recording", "recording.csv", "CSV Files (*.csv);;All Files (*)")

        if not filepath:
            return

        try:
            import csv
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['x', 'y', 'signal', 'ssid', 'channel'])
                for point in self.recording_points:
                    writer.writerow(point)

            self.statusBar().showMessage("Exported " + str(len(self.recording_points)) + " recording points to " + filepath, 5000)

        except Exception as e:
            QMessageBox.warning(self, "Export Error", "Failed to export recording:\n" + str(e))

    def _clear_recording(self):
        """Clear all recording data."""
        reply = QMessageBox.question(self, "Clear Recording",
            "Clear all recording data?\n\nThis will not affect other data points.",
            QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.recording_points = []
            self.recording_position = [0, 0]
            self.record_spin_x.setValue(0)
            self.record_spin_y.setValue(0)
            self.record_table.setRowCount(0)
            self.lbl_record_count.setText("Points: 0")
            self.lbl_record_pos.setText("Position: (0, 0)")
            self.lbl_record_signal.setText("Signal: N/A")
            self._update_recording_canvas()
            self.statusBar().showMessage("Recording data cleared", 3000)

    # =====================================================================
    # REALTIME TAB
    # =====================================================================
    def _create_realtime_tab(self):
        """Create the realtime monitoring tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)
        
        # Control bar
        control_bar = QHBoxLayout()
        
        self.btn_realtime = QPushButton("Start Realtime Monitor")
        self.btn_realtime.setMinimumHeight(40)
        self.btn_realtime.setFont(QFont("Segoe UI", 11))
        self.btn_realtime.setStyleSheet("font-weight: bold;")
        self.btn_realtime.clicked.connect(self._toggle_realtime)
        control_bar.addWidget(self.btn_realtime)
        
        control_bar.addWidget(QLabel("Interval (s):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(5)
        control_bar.addWidget(self.interval_spin)
        
        control_bar.addStretch()
        
        self.lbl_realtime_status = QLabel("Status: Stopped")
        self.lbl_realtime_status.setFont(QFont("Segoe UI", 10))
        self.lbl_realtime_status.setStyleSheet("color: #888;")
        control_bar.addWidget(self.lbl_realtime_status)
        
        layout.addLayout(control_bar)
        
        # Realtime chart
        chart_label = QLabel("Realtime Signal Monitor")
        chart_label.setFont(QFont("Segoe UI", 10))
        chart_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(chart_label)
        
        self.realtime_canvas = MplCanvas(self, width=10, height=4, dpi=100)
        self.realtime_canvas.fig.patch.set_facecolor('#2a2a2a')
        self.realtime_ax = self.realtime_canvas.fig.add_subplot(111)
        self.realtime_ax.set_facecolor('#1e1e1e')
        self.realtime_ax.tick_params(colors='#aaa')
        self.realtime_ax.xaxis.label.set_color('#aaa')
        self.realtime_ax.yaxis.label.set_color('#aaa')
        self.realtime_ax.title.set_color('#ddd')
        for spine in self.realtime_ax.spines.values():
            spine.set_color('#444')
        self.realtime_ax.set_xlabel('Time')
        self.realtime_ax.set_ylabel('Signal Strength (dBm)')
        self.realtime_ax.set_title('Realtime WiFi Signal Monitor')
        layout.addWidget(self.realtime_canvas)
        
        # Realtime data storage
        self.realtime_history = {}  # ssid -> list of (time, rssi)
        self.realtime_counter = 0
        
        self.tabs.addTab(tab, "Realtime")
    
    def _toggle_realtime(self):
        """Toggle realtime monitoring on/off."""
        if self.realtime_running:
            self.realtime_running = False
            self.realtime_timer.stop()
            self.btn_realtime.setText("Start Realtime Monitor")
            self.btn_realtime.setStyleSheet("")
            self.lbl_realtime_status.setText("Status: Stopped")
            self.lbl_realtime_status.setStyleSheet("color: #888;")
            self.statusBar().showMessage("Realtime monitoring stopped", 3000)
        else:
            self.realtime_running = True
            interval = self.interval_spin.value() * 1000
            self.realtime_timer.start(interval)
            self.btn_realtime.setText("Stop Realtime Monitor")
            self.btn_realtime.setStyleSheet("background-color: #cc3333;")
            self.lbl_realtime_status.setText("Status: Running")
            self.lbl_realtime_status.setStyleSheet("color: #2d8a2d;")
            self.statusBar().showMessage("Realtime monitoring started (interval: " + str(interval) + "ms)", 3000)
    
    def _realtime_scan(self):
        """Perform a realtime scan and update chart."""
        self.realtime_counter += 1
        self.statusBar().showMessage("Realtime scan #" + str(self.realtime_counter) + "...")
        
        try:
            networks = self.scanner.scan()
            
            # Update history
            for net in networks:
                ssid = net.get('ssid', 'Unknown')
                rssi = net.get('rssi', -100)
                
                if ssid not in self.realtime_history:
                    self.realtime_history[ssid] = []
                
                self.realtime_history[ssid].append((self.realtime_counter, rssi))
                
                # Keep last 20 points
                if len(self.realtime_history[ssid]) > 20:
                    self.realtime_history[ssid] = self.realtime_history[ssid][-20:]
            
            # Update chart
            self._update_realtime_chart()
            
            self.statusBar().showMessage("Realtime scan #" + str(self.realtime_counter) + " complete", 2000)
            
        except Exception as e:
            self.statusBar().showMessage("Realtime scan error: " + str(e))
    
    def _update_realtime_chart(self):
        """Update the realtime chart."""
        self.realtime_ax.clear()
        self.realtime_ax.set_facecolor('#1e1e1e')
        
        if not self.realtime_history:
            self.realtime_ax.text(0.5, 0.5, 'Waiting for data...', 
                                ha='center', va='center', color='#888', fontsize=14)
            self.realtime_canvas.draw()
            return
        
        # Plot each network
        colors = ['#00b4d8', '#ff6b6b', '#51cf66', '#ffd43b', '#cc5de8', '#ff922b', '#20c997', '#f06595']
        color_idx = 0
        
        for ssid, history in self.realtime_history.items():
            if len(history) < 2:
                continue
            
            times = [h[0] for h in history]
            signals = [h[1] for h in history]
            color = colors[color_idx % len(colors)]
            color_idx += 1
            
            self.realtime_ax.plot(times, signals, '-o', color=color, label=ssid[:20], linewidth=1.5, markersize=4)
        
        self.realtime_ax.set_xlabel('Scan #', color='#aaa')
        self.realtime_ax.set_ylabel('Signal Strength (dBm)', color='#aaa')
        self.realtime_ax.set_title('Realtime WiFi Signal Monitor', color='#ddd', fontweight='bold')
        self.realtime_ax.legend(loc='upper right', fontsize=8, facecolor='#2a2a2a', edgecolor='#444', labelcolor='#ddd')
        self.realtime_ax.grid(alpha=0.15, linestyle='--', color='#555')
        self.realtime_ax.set_ylim(-100, -20)
        for spine in self.realtime_ax.spines.values():
            spine.set_color('#444')
        self.realtime_ax.tick_params(colors='#aaa')
        
        self.realtime_canvas.draw()
    
    # =====================================================================
    # SPECTRUM ANALYZER TAB
    # =====================================================================
    def _create_spectrum_tab(self):
        """Create the spectrum analyzer tab with channel analysis, waterfall, and utilization."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        # Control bar
        control_bar = QHBoxLayout()

        self.btn_spectrum_scan = QPushButton("Scan & Analyze Spectrum")
        self.btn_spectrum_scan.setMinimumHeight(35)
        self.btn_spectrum_scan.setStyleSheet("font-weight: bold;")
        self.btn_spectrum_scan.clicked.connect(self._spectrum_scan)
        control_bar.addWidget(self.btn_spectrum_scan)

        self.btn_spectrum_waterfall = QPushButton("Generate Waterfall")
        self.btn_spectrum_waterfall.setMinimumHeight(35)
        self.btn_spectrum_waterfall.clicked.connect(self._spectrum_waterfall)
        control_bar.addWidget(self.btn_spectrum_waterfall)

        self.btn_spectrum_utilization = QPushButton("Channel Utilization")
        self.btn_spectrum_utilization.setMinimumHeight(35)
        self.btn_spectrum_utilization.clicked.connect(self._spectrum_utilization)
        control_bar.addWidget(self.btn_spectrum_utilization)

        control_bar.addStretch()

        self.lbl_spectrum_status = QLabel("Ready")
        self.lbl_spectrum_status.setStyleSheet("color: #888;")
        control_bar.addWidget(self.lbl_spectrum_status)

        layout.addLayout(control_bar)

        # Spectrum canvas
        self.spectrum_canvas = MplCanvas(self, width=10, height=5, dpi=100)
        self.spectrum_canvas.fig.patch.set_facecolor('#2a2a2a')
        self.spectrum_ax = self.spectrum_canvas.fig.add_subplot(111)
        self.spectrum_ax.set_facecolor('#1e1e1e')
        self.spectrum_ax.tick_params(colors='#aaa')
        self.spectrum_ax.xaxis.label.set_color('#aaa')
        self.spectrum_ax.yaxis.label.set_color('#aaa')
        self.spectrum_ax.title.set_color('#ddd')
        for spine in self.spectrum_ax.spines.values():
            spine.set_color('#444')
        self.spectrum_ax.set_xlabel('WiFi Channel')
        self.spectrum_ax.set_ylabel('Signal Strength (dBm)')
        self.spectrum_ax.set_title('WiFi Spectrum Analyzer')
        self.spectrum_ax.text(0.5, 0.5, 'Click "Scan & Analyze Spectrum" to begin',
                            ha='center', va='center', color='#666', fontsize=14,
                            transform=self.spectrum_ax.transAxes)
        layout.addWidget(self.spectrum_canvas)

        # Info panel
        info_group = QGroupBox("Spectrum Info")
        info_layout = QVBoxLayout(info_group)

        self.spectrum_info = QTextEdit()
        self.spectrum_info.setReadOnly(True)
        self.spectrum_info.setMaximumHeight(120)
        self.spectrum_info.setFont(QFont("Consolas", 9))
        self.spectrum_info.setText("No spectrum data yet.\n\nScan WiFi networks to analyze the frequency spectrum.")
        info_layout.addWidget(self.spectrum_info)

        layout.addWidget(info_group)

        # Initialize spectrum analyzer
        self.spectrum_analyzer = SpectrumAnalyzer(max_history=30)

        self.tabs.addTab(tab, "Spectrum Analyzer")

    def _spectrum_scan(self):
        """Scan WiFi and show spectrum bar chart directly on canvas."""
        self.lbl_spectrum_status.setText("Scanning...")
        self.statusBar().showMessage("Scanning for spectrum analysis...")
        QApplication.processEvents()

        try:
            networks = self.scanner.scan()
            if not networks:
                self.lbl_spectrum_status.setText("No networks found")
                self.statusBar().showMessage("No networks found for spectrum analysis", 3000)
                return

            # Update spectrum analyzer
            self.spectrum_analyzer.update(networks)

            # Clear and draw directly on embedded canvas
            self.spectrum_ax.clear()
            self.spectrum_ax.set_facecolor('#1e1e1e')

            # Separate 2.4 GHz and 5 GHz networks
            nets_2ghz = [n for n in networks if n.get('channel', 0) <= 14]
            nets_5ghz = [n for n in networks if n.get('channel', 0) > 14]

            # Group by channel
            channel_data = {}
            for net in networks:
                ch = net.get('channel', 0)
                if ch > 0:
                    if ch not in channel_data:
                        channel_data[ch] = []
                    channel_data[ch].append(net)

            if channel_data:
                channels = sorted(channel_data.keys())
                ch_indices = list(range(len(channels)))
                rssi_values = []
                labels = []

                for ch in channels:
                    nets = channel_data[ch]
                    best_rssi = max(n.get('rssi', -100) for n in nets)
                    rssi_values.append(best_rssi)
                    ssids = [n.get('ssid', '?')[:10] for n in nets]
                    labels.append(f"Ch {ch}")

                # Color bars by signal strength
                colors = []
                for r in rssi_values:
                    if r >= -50: colors.append('#d32f2f')
                    elif r >= -60: colors.append('#f57c00')
                    elif r >= -70: colors.append('#fbc02d')
                    elif r >= -80: colors.append('#7cb342')
                    else: colors.append('#1565c0')

                bars = self.spectrum_ax.bar(ch_indices, rssi_values, color=colors,
                                           edgecolor='#555', linewidth=0.5, alpha=0.9)
                self.spectrum_ax.set_xticks(ch_indices)
                self.spectrum_ax.set_xticklabels(labels, fontsize=9, rotation=45, color='#ddd')

                # Add SSID labels on bars
                for i, ch in enumerate(channels):
                    nets = channel_data[ch]
                    ssid_text = "\n".join([n.get('ssid', '?')[:12] for n in nets])
                    self.spectrum_ax.text(i, rssi_values[i] + 0.5, ssid_text,
                                         ha='center', va='bottom', fontsize=7, color='#aaa')

                # Noise floor line
                self.spectrum_ax.axhline(y=-90, color='red', linestyle='--', alpha=0.3, linewidth=0.5)
                self.spectrum_ax.text(len(channels)-0.5, -90, 'Noise Floor (~-90 dBm)',
                                     fontsize=7, color='red', alpha=0.5, ha='right', va='bottom')

                self.spectrum_ax.set_ylim(min(rssi_values) - 15, max(rssi_values) + 15)
            else:
                self.spectrum_ax.text(0.5, 0.5, 'No channel data available',
                                     ha='center', va='center', color='#666', fontsize=14,
                                     transform=self.spectrum_ax.transAxes)

            self.spectrum_ax.set_xlabel('WiFi Channel', color='#aaa')
            self.spectrum_ax.set_ylabel('Signal Strength (dBm)', color='#aaa')
            self.spectrum_ax.set_title('WiFi Spectrum - Channel Analysis', color='#ddd', fontweight='bold')
            self.spectrum_ax.grid(axis='y', alpha=0.15, linestyle='--', color='#555')
            for spine in self.spectrum_ax.spines.values():
                spine.set_color('#444')
            self.spectrum_ax.tick_params(colors='#aaa')
            self.spectrum_canvas.draw()

            # Update info
            n_2ghz = len(nets_2ghz)
            n_5ghz = len(nets_5ghz)
            channels_list = sorted(channel_data.keys())

            info_text = (
                f"Spectrum Analysis Complete\n"
                f"{'='*30}\n"
                f"Total Networks: {len(networks)}\n"
                f"2.4 GHz: {n_2ghz} networks\n"
                f"5 GHz: {n_5ghz} networks\n"
                f"Active Channels: {', '.join(str(c) for c in channels_list)}\n"
                f"Channels in use: {len(channels_list)}"
            )
            self.spectrum_info.setText(info_text)
            self.lbl_spectrum_status.setText(f"Complete - {len(networks)} networks")
            self.statusBar().showMessage("Spectrum analysis complete", 3000)

        except Exception as e:
            self.lbl_spectrum_status.setText("Error")
            self.statusBar().showMessage("Spectrum scan error: " + str(e))
            QMessageBox.warning(self, "Error", "Spectrum scan failed:\n" + str(e))

    def _spectrum_waterfall(self):
        """Generate waterfall spectrogram from history."""
        if not self.spectrum_analyzer.last_networks:
            QMessageBox.warning(self, "No Data", "Please scan networks first.")
            return

        self.lbl_spectrum_status.setText("Generating waterfall...")
        self.statusBar().showMessage("Generating waterfall spectrogram...")
        QApplication.processEvents()

        try:
            # Build history from multiple scans
            for _ in range(5):
                networks = self.scanner.scan()
                self.spectrum_analyzer.update(networks)

            # Get channel history data
            channel_history = self.spectrum_analyzer.channel_history
            if not channel_history:
                self.lbl_spectrum_status.setText("No history data")
                return

            # Clear and draw directly on canvas
            self.spectrum_ax.clear()
            self.spectrum_ax.set_facecolor('#1e1e1e')

            # Build waterfall matrix
            channels = sorted(ch for ch in channel_history.keys() if ch <= 14)
            if not channels:
                channels = sorted(channel_history.keys())

            n_times = max(len(h) for h in channel_history.values())
            n_channels = len(channels)

            waterfall = np.full((n_times, n_channels), -100.0)
            for t in range(n_times):
                for j, ch in enumerate(channels):
                    history = list(channel_history[ch])
                    if t < len(history):
                        waterfall[t, j] = history[-(t+1)]

            # Plot waterfall
            im = self.spectrum_ax.imshow(waterfall, aspect='auto', cmap='inferno',
                                        interpolation='bilinear',
                                        extent=[0, n_channels, n_times, 0],
                                        vmin=-100, vmax=-30)

            self.spectrum_ax.set_xticks(range(n_channels))
            self.spectrum_ax.set_xticklabels([f"Ch {ch}" for ch in channels],
                                             fontsize=8, rotation=45, color='#ddd')
            self.spectrum_ax.set_ylabel('Time Steps', color='#aaa')
            self.spectrum_ax.set_title('Waterfall Spectrogram', color='#ddd', fontweight='bold')

            cbar = self.spectrum_canvas.fig.colorbar(im, ax=self.spectrum_ax, shrink=0.8)
            cbar.set_label('Signal Strength (dBm)', fontsize=9)
            cbar.ax.yaxis.label.set_color('#aaa')
            cbar.ax.tick_params(colors='#aaa')

            for spine in self.spectrum_ax.spines.values():
                spine.set_color('#444')
            self.spectrum_ax.tick_params(colors='#aaa')
            self.spectrum_canvas.draw()

            self.spectrum_info.setText(
                "Waterfall Spectrogram generated!\n\n"
                "Shows signal strength changes over time\n"
                f"for {n_channels} WiFi channels.\n\n"
                f"History: {n_times} scans\n"
                "Brighter colors = stronger signal"
            )
            self.lbl_spectrum_status.setText("Waterfall generated")
            self.statusBar().showMessage("Waterfall spectrogram generated", 3000)

        except Exception as e:
            self.lbl_spectrum_status.setText("Error")
            self.statusBar().showMessage("Waterfall error: " + str(e))

    def _spectrum_utilization(self):
        """Generate channel utilization chart directly on canvas."""
        if not self.spectrum_analyzer.last_networks:
            QMessageBox.warning(self, "No Data", "Please scan networks first.")
            return

        self.lbl_spectrum_status.setText("Generating utilization...")
        self.statusBar().showMessage("Generating channel utilization chart...")
        QApplication.processEvents()

        try:
            networks = self.spectrum_analyzer.last_networks

            # Count networks per channel
            channel_counts = {}
            for net in networks:
                ch = net.get('channel', 0)
                if ch > 0:
                    channel_counts[ch] = channel_counts.get(ch, 0) + 1

            if not channel_counts:
                self.lbl_spectrum_status.setText("No channel data")
                return

            channels = sorted(channel_counts.keys())
            counts = [channel_counts[ch] for ch in channels]

            # Clear and draw directly on canvas
            self.spectrum_ax.clear()
            self.spectrum_ax.set_facecolor('#1e1e1e')

            # Bar chart
            colors = plt.cm.RdYlBu_r([c / max(counts) for c in counts])
            self.spectrum_ax.bar(range(len(channels)), counts, color=colors,
                                edgecolor='white', linewidth=0.5)
            self.spectrum_ax.set_xticks(range(len(channels)))
            self.spectrum_ax.set_xticklabels([f"Ch {ch}" for ch in channels],
                                             fontsize=9, rotation=45, color='#ddd')
            self.spectrum_ax.set_ylabel('Number of Networks', color='#aaa')
            self.spectrum_ax.set_title('Channel Utilization', color='#ddd', fontweight='bold')
            self.spectrum_ax.grid(axis='y', alpha=0.15, linestyle='--', color='#555')

            # Add count labels
            for i, count in enumerate(counts):
                self.spectrum_ax.text(i, count + 0.1, str(count), ha='center', va='bottom',
                                     fontsize=10, color='#aaa')

            # Highlight recommended channels (1, 6, 11)
            for i, ch in enumerate(channels):
                if ch in [1, 6, 11]:
                    self.spectrum_ax.text(i, counts[i] + 0.5, '★',
                                         ha='center', fontsize=14, color='#00ff00')

            for spine in self.spectrum_ax.spines.values():
                spine.set_color('#444')
            self.spectrum_ax.tick_params(colors='#aaa')
            self.spectrum_canvas.draw()

            self.spectrum_info.setText(
                "Channel Utilization generated!\n\n"
                "Shows which channels are most congested.\n\n"
                f"Total channels in use: {len(channels)}\n"
                f"Most crowded: Ch {channels[counts.index(max(counts))]} ({max(counts)} networks)\n\n"
                "Tip: Use non-overlapping channels (1, 6, 11)\n"
                "for best performance in 2.4 GHz band."
            )
            self.lbl_spectrum_status.setText("Utilization generated")
            self.statusBar().showMessage("Channel utilization chart generated", 3000)

        except Exception as e:
            self.lbl_spectrum_status.setText("Error")
            self.statusBar().showMessage("Utilization error: " + str(e))

    # =====================================================================
    # SIGNAL PROPAGATION TAB
    # =====================================================================
    def _create_propagation_tab(self):
        """Create the signal propagation modeling tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        # Control bar
        control_bar = QHBoxLayout()

        self.btn_prop_curves = QPushButton("Path Loss Curves")
        self.btn_prop_curves.setMinimumHeight(35)
        self.btn_prop_curves.clicked.connect(self._propagation_curves)
        control_bar.addWidget(self.btn_prop_curves)

        self.btn_prop_coverage = QPushButton("Coverage Prediction")
        self.btn_prop_coverage.setMinimumHeight(35)
        self.btn_prop_coverage.clicked.connect(self._propagation_coverage)
        control_bar.addWidget(self.btn_prop_coverage)

        self.btn_prop_gradient = QPushButton("Gradient Vectors")
        self.btn_prop_gradient.setMinimumHeight(35)
        self.btn_prop_gradient.clicked.connect(self._propagation_gradient)
        control_bar.addWidget(self.btn_prop_gradient)

        self.btn_prop_multi_ap = QPushButton("Multi-AP Overlay")
        self.btn_prop_multi_ap.setMinimumHeight(35)
        self.btn_prop_multi_ap.clicked.connect(self._propagation_multi_ap)
        control_bar.addWidget(self.btn_prop_multi_ap)

        control_bar.addStretch()

        self.lbl_prop_status = QLabel("Ready")
        self.lbl_prop_status.setStyleSheet("color: #888;")
        control_bar.addWidget(self.lbl_prop_status)

        layout.addLayout(control_bar)

        # Propagation canvas
        self.prop_canvas = MplCanvas(self, width=10, height=5, dpi=100)
        self.prop_canvas.fig.patch.set_facecolor('#2a2a2a')
        self.prop_ax = self.prop_canvas.fig.add_subplot(111)
        self.prop_ax.set_facecolor('#1e1e1e')
        self.prop_ax.tick_params(colors='#aaa')
        self.prop_ax.xaxis.label.set_color('#aaa')
        self.prop_ax.yaxis.label.set_color('#aaa')
        self.prop_ax.title.set_color('#ddd')
        for spine in self.prop_ax.spines.values():
            spine.set_color('#444')
        self.prop_ax.set_xlabel('Distance (meters)')
        self.prop_ax.set_ylabel('Path Loss (dB)')
        self.prop_ax.set_title('Signal Propagation Models')
        self.prop_ax.text(0.5, 0.5, 'Click a button above to generate propagation visualization',
                        ha='center', va='center', color='#666', fontsize=14,
                        transform=self.prop_ax.transAxes)
        layout.addWidget(self.prop_canvas)

        # Info panel
        info_group = QGroupBox("Propagation Info")
        info_layout = QVBoxLayout(info_group)

        self.prop_info = QTextEdit()
        self.prop_info.setReadOnly(True)
        self.prop_info.setMaximumHeight(120)
        self.prop_info.setFont(QFont("Consolas", 9))
        self.prop_info.setText(
            "Signal Propagation Models\n"
            "=========================\n\n"
            "1. Free Space Path Loss (FSPL)\n"
            "2. Log-Distance Path Loss\n"
            "3. ITU Indoor Propagation\n"
            "4. Two-Ray Ground Reflection\n\n"
            "Select a visualization above."
        )
        info_layout.addWidget(self.prop_info)

        layout.addWidget(info_group)

        # Initialize signal propagation
        self.signal_propagation = SignalPropagation()

        self.tabs.addTab(tab, "Signal Propagation")

    def _propagation_curves(self):
        """Generate path loss comparison curves directly on canvas."""
        self.lbl_prop_status.setText("Generating curves...")
        self.statusBar().showMessage("Generating path loss comparison curves...")
        QApplication.processEvents()

        try:
            # Generate path loss curves directly on canvas
            self.prop_ax.clear()
            self.prop_ax.set_facecolor('#1e1e1e')

            freq_mhz = 2412
            max_distance = 100
            distances = np.linspace(1, max_distance, 200)

            # Free Space Path Loss
            c = 3e8
            f = freq_mhz * 1e6
            fspl = 20 * np.log10(distances) + 20 * np.log10(f) - 147.55

            # Log-Distance models
            ld_20 = fspl + 10 * 2.0 * np.log10(distances)
            ld_30 = fspl + 10 * 3.0 * np.log10(distances)
            ld_35 = fspl + 10 * 3.5 * np.log10(distances)

            # ITU Indoor model
            N = 28
            Lf = 0.05 * distances
            itu = 20 * np.log10(f) + N * np.log10(distances) + Lf - 28

            # Two-Ray Ground Reflection
            ht = 1.5
            hr = 1.5
            d_cross = (4 * np.pi * ht * hr * f) / c
            two_ray = np.where(distances < d_cross,
                              fspl,
                              40 * np.log10(distances) - (20 * np.log10(ht) + 20 * np.log10(hr)))

            # Plot all models
            self.prop_ax.plot(distances, fspl, '-', color='#00b4d8', linewidth=2, label='Free Space (FSPL)')
            self.prop_ax.plot(distances, ld_20, '--', color='#ff6b6b', linewidth=1.5, label='Log-Distance n=2.0')
            self.prop_ax.plot(distances, ld_30, '--', color='#51cf66', linewidth=1.5, label='Log-Distance n=3.0')
            self.prop_ax.plot(distances, ld_35, '--', color='#ffd43b', linewidth=1.5, label='Log-Distance n=3.5')
            self.prop_ax.plot(distances, itu, '-.', color='#cc5de8', linewidth=1.5, label='ITU Indoor')
            self.prop_ax.plot(distances, two_ray, ':', color='#ff922b', linewidth=2, label='Two-Ray Ground')

            # Labels
            self.prop_ax.set_xlabel('Distance (meters)', color='#aaa')
            self.prop_ax.set_ylabel('Path Loss (dB)', color='#aaa')
            self.prop_ax.set_title('Signal Propagation Models Comparison', color='#ddd', fontweight='bold')
            self.prop_ax.legend(loc='lower right', fontsize=8, facecolor='#2a2a2a', edgecolor='#444', labelcolor='#ddd')
            self.prop_ax.grid(alpha=0.15, linestyle='--', color='#555')
            self.prop_ax.set_xlim(0, max_distance)
            self.prop_ax.set_ylim(30, 130)

            for spine in self.prop_ax.spines.values():
                spine.set_color('#444')
            self.prop_ax.tick_params(colors='#aaa')
            self.prop_canvas.draw()

            self.prop_info.setText(
                "Path Loss Curves generated!\n\n"
                "Models shown:\n"
                "- Free Space (FSPL)\n"
                "- Log-Distance (n=2.0, 3.0, 3.5)\n"
                "- ITU Indoor Propagation\n"
                "- Two-Ray Ground Reflection\n\n"
                "Frequency: 2.412 GHz (WiFi Ch1)"
            )
            self.lbl_prop_status.setText("Curves generated")
            self.statusBar().showMessage("Path loss curves generated", 3000)

        except Exception as e:
            self.lbl_prop_status.setText("Error")
            self.statusBar().showMessage("Curves error: " + str(e))

    def _propagation_coverage(self):
        """Generate coverage prediction map directly on canvas."""
        if not self.measurement_points:
            QMessageBox.warning(self, "No Data",
                "No measurement data available.\n\n"
                "Please add data points in the 'Data Collection' tab\n"
                "or import a CSV file first.")
            return

        self.lbl_prop_status.setText("Generating coverage...")
        self.statusBar().showMessage("Generating coverage prediction...")
        QApplication.processEvents()

        try:
            points, values = self._get_viz_data()
            grid_x, grid_y, grid_z = self._interpolate(points, values)

            # Find approximate AP position (point with strongest signal)
            max_idx = np.argmax(values)
            ap_pos = (points[max_idx, 0], points[max_idx, 1])

            # Draw coverage prediction directly on canvas
            self.prop_ax.clear()
            self.prop_ax.set_facecolor('#1e1e1e')

            # Plot interpolated signal as background
            contour = self.prop_ax.contourf(grid_x, grid_y, grid_z, levels=30, cmap='RdYlBu_r', alpha=0.85)
            contour_lines = self.prop_ax.contour(grid_x, grid_y, grid_z, levels=10, colors='black', linewidths=0.5, alpha=0.3)
            self.prop_ax.clabel(contour_lines, inline=True, fontsize=8, fmt='%.0f')

            # Mark AP position
            self.prop_ax.plot(ap_pos[0], ap_pos[1], '^', color='red', markersize=15, 
                            markeredgecolor='white', markeredgewidth=2, zorder=10)
            self.prop_ax.text(ap_pos[0], ap_pos[1] + 1, 'AP', ha='center', va='bottom',
                            fontsize=10, fontweight='bold', color='white',
                            bbox=dict(boxstyle='round', facecolor='red', alpha=0.8))

            # Coverage edge at -85 dBm
            cs = self.prop_ax.contour(grid_x, grid_y, grid_z, levels=[-85], 
                                     colors='red', linewidths=2, linestyles='--')
            self.prop_ax.clabel(cs, inline=True, fontsize=9, fmt='%.0f dBm')

            # Overlay measurement points
            self.prop_ax.scatter(points[:, 0], points[:, 1], c=values, cmap='RdYlBu_r',
                               edgecolors='black', linewidth=1, s=60, zorder=5,
                               vmin=grid_z.min(), vmax=grid_z.max())

            # Colorbar
            cbar = self.prop_canvas.fig.colorbar(contour, ax=self.prop_ax, label='Signal Strength (dBm)', shrink=0.8)
            cbar.ax.yaxis.label.set_color('#aaa')
            cbar.ax.tick_params(colors='#aaa')

            self.prop_ax.set_xlabel('X Position (meters)', color='#aaa')
            self.prop_ax.set_ylabel('Y Position (meters)', color='#aaa')
            self.prop_ax.set_title('WiFi Coverage Prediction', color='#ddd', fontweight='bold')
            self.prop_ax.set_aspect('equal')
            self.prop_ax.grid(alpha=0.15, linestyle='--', color='#555')
            for spine in self.prop_ax.spines.values():
                spine.set_color('#444')
            self.prop_ax.tick_params(colors='#aaa')
            self.prop_canvas.draw()

            self.prop_info.setText(
                "Coverage Prediction generated!\n\n"
                f"AP Position: ({ap_pos[0]:.1f}, {ap_pos[1]:.1f})\n"
                f"TX Power: 20 dBm\n"
                f"Frequency: 2.412 GHz\n"
                f"Model: Log-Distance (n=3.0)\n\n"
                "Red dashed line shows coverage edge\n"
                "at -85 dBm receiver sensitivity."
            )
            self.lbl_prop_status.setText("Coverage generated")
            self.statusBar().showMessage("Coverage prediction generated", 3000)

        except Exception as e:
            self.lbl_prop_status.setText("Error")
            self.statusBar().showMessage("Coverage error: " + str(e))

    def _propagation_gradient(self):
        """Generate gradient vector visualization directly on canvas."""
        if not self.measurement_points:
            QMessageBox.warning(self, "No Data",
                "No measurement data available.\n\n"
                "Please add data points in the 'Data Collection' tab\n"
                "or import a CSV file first.")
            return

        self.lbl_prop_status.setText("Generating gradients...")
        self.statusBar().showMessage("Generating gradient vectors...")
        QApplication.processEvents()

        try:
            points, values = self._get_viz_data()
            grid_x, grid_y, grid_z = self._interpolate(points, values)

            # Draw gradient vectors directly on canvas
            self.prop_ax.clear()
            self.prop_ax.set_facecolor('#1e1e1e')

            # Plot signal heatmap as background
            self.prop_ax.contourf(grid_x, grid_y, grid_z, levels=30, cmap='RdYlBu_r', alpha=0.7)

            # Compute gradient
            dy, dx = np.gradient(grid_z)
            magnitude = np.sqrt(dx**2 + dy**2)

            # Subsample for quiver
            stride = 3
            x_sub = grid_x[::stride, ::stride]
            y_sub = grid_y[::stride, ::stride]
            dx_sub = dx[::stride, ::stride]
            dy_sub = dy[::stride, ::stride]
            mag_sub = magnitude[::stride, ::stride]

            # Normalize arrows
            norm = np.sqrt(dx_sub**2 + dy_sub**2)
            norm[norm == 0] = 1
            dx_norm = dx_sub / norm
            dy_norm = dy_sub / norm

            # Quiver plot with color by magnitude
            quiv = self.prop_ax.quiver(x_sub, y_sub, dx_norm, dy_norm, mag_sub,
                                      cmap='plasma', scale=25, width=0.008,
                                      headwidth=4, headlength=5, alpha=0.9)

            # Overlay measurement points
            self.prop_ax.scatter(points[:, 0], points[:, 1], c=values, cmap='RdYlBu_r',
                               edgecolors='black', linewidth=1, s=60, zorder=5)

            # Colorbar for gradient magnitude
            cbar = self.prop_canvas.fig.colorbar(quiv, ax=self.prop_ax, label='Gradient Magnitude', shrink=0.8)
            cbar.ax.yaxis.label.set_color('#aaa')
            cbar.ax.tick_params(colors='#aaa')

            self.prop_ax.set_xlabel('X Position (meters)', color='#aaa')
            self.prop_ax.set_ylabel('Y Position (meters)', color='#aaa')
            self.prop_ax.set_title('Signal Gradient Vectors', color='#ddd', fontweight='bold')
            self.prop_ax.set_aspect('equal')
            self.prop_ax.grid(alpha=0.15, linestyle='--', color='#555')
            for spine in self.prop_ax.spines.values():
                spine.set_color('#444')
            self.prop_ax.tick_params(colors='#aaa')
            self.prop_canvas.draw()

            self.prop_info.setText(
                "Gradient Vectors generated!\n\n"
                "Arrows show direction of increasing signal.\n"
                "Arrow color = gradient magnitude.\n\n"
                "Bright areas = rapid signal change."
            )
            self.lbl_prop_status.setText("Gradients generated")
            self.statusBar().showMessage("Gradient vectors generated", 3000)

        except Exception as e:
            self.lbl_prop_status.setText("Error")
            self.statusBar().showMessage("Gradient error: " + str(e))

    def _propagation_multi_ap(self):
        """Generate multi-AP overlay visualization directly on canvas."""
        if not self.measurement_points:
            QMessageBox.warning(self, "No Data",
                "No measurement data available.\n\n"
                "Please add data points in the 'Data Collection' tab\n"
                "or import a CSV file first.")
            return

        self.lbl_prop_status.setText("Generating multi-AP...")
        self.statusBar().showMessage("Generating multi-AP overlay...")
        QApplication.processEvents()

        try:
            points, values = self._get_viz_data()
            grid_x, grid_y, grid_z = self._interpolate(points, values)

            # Create simulated APs from data
            n_aps = min(3, len(points))
            ap_positions = []
            ap_names = []
            ap_powers = []

            # Pick strongest points as AP positions
            sorted_indices = np.argsort(values)[::-1]
            for i in range(n_aps):
                idx = sorted_indices[i]
                ap_positions.append((points[idx, 0], points[idx, 1]))
                ap_names.append(f"AP-{i+1}")
                ap_powers.append(20.0 - i * 2)  # Decreasing power

            # Draw multi-AP overlay directly on canvas
            self.prop_ax.clear()
            self.prop_ax.set_facecolor('#1e1e1e')

            # Plot interpolated signal as background
            self.prop_ax.contourf(grid_x, grid_y, grid_z, levels=30, cmap='RdYlBu_r', alpha=0.5)

            # Colors for each AP
            ap_colors = ['#ff4444', '#4488ff', '#44ff44', '#ffaa00', '#cc44ff']

            # Plot each AP's coverage
            for i, (ap_pos, ap_name, ap_power) in enumerate(zip(ap_positions, ap_names, ap_powers)):
                color = ap_colors[i % len(ap_colors)]

                # Calculate distance from this AP
                ap_x, ap_y = ap_pos
                dist_from_ap = np.sqrt((grid_x - ap_x)**2 + (grid_y - ap_y)**2)

                # Simple path loss model for this AP
                freq_mhz = 2412
                f = freq_mhz * 1e6
                c = 3e8
                fspl = 20 * np.log10(dist_from_ap + 0.1) + 20 * np.log10(f) - 147.55
                ap_signal = ap_power - fspl

                # Contour lines for this AP at specific thresholds
                thresholds = [-80, -70, -60, -50]
                cs = self.prop_ax.contour(grid_x, grid_y, ap_signal, levels=thresholds,
                                         colors=[color], linewidths=1.5, linestyles='--', alpha=0.7)
                self.prop_ax.clabel(cs, inline=True, fontsize=8, fmt='%.0f dBm', colors=[color])

                # Mark AP position
                self.prop_ax.plot(ap_x, ap_y, 'o', color=color, markersize=12,
                                markeredgecolor='white', markeredgewidth=2, zorder=10)
                self.prop_ax.text(ap_x, ap_y + 0.5, ap_name, ha='center', va='bottom',
                                fontsize=9, fontweight='bold', color='white',
                                bbox=dict(boxstyle='round', facecolor=color, alpha=0.8))

            # Overlay measurement points
            self.prop_ax.scatter(points[:, 0], points[:, 1], c=values, cmap='RdYlBu_r',
                               edgecolors='black', linewidth=1, s=50, zorder=5)

            self.prop_ax.set_xlabel('X Position (meters)', color='#aaa')
            self.prop_ax.set_ylabel('Y Position (meters)', color='#aaa')
            self.prop_ax.set_title('Multi-AP Signal Overlay', color='#ddd', fontweight='bold')
            self.prop_ax.set_aspect('equal')
            self.prop_ax.grid(alpha=0.15, linestyle='--', color='#555')
            for spine in self.prop_ax.spines.values():
                spine.set_color('#444')
            self.prop_ax.tick_params(colors='#aaa')
            self.prop_canvas.draw()

            ap_info = "\n".join([f"{name}: ({pos[0]:.1f}, {pos[1]:.1f}) @ {pwr} dBm"
                               for name, pos, pwr in zip(ap_names, ap_positions, ap_powers)])

            self.prop_info.setText(
                "Multi-AP Overlay generated!\n\n"
                f"Access Points ({n_aps}):\n{ap_info}\n\n"
                "Dashed contour lines show signal strength\n"
                "for each AP at -80, -70, -60, -50 dBm."
            )
            self.lbl_prop_status.setText("Multi-AP generated")
            self.statusBar().showMessage("Multi-AP overlay generated", 3000)

        except Exception as e:
            self.lbl_prop_status.setText("Error")
            self.statusBar().showMessage("Multi-AP error: " + str(e))

    # =====================================================================
    # HELPER METHODS
    # =====================================================================
    def _rssi_to_quality(self, rssi):
        """Convert RSSI to percentage quality."""
        if rssi >= -50:
            return 100
        elif rssi <= -100:
            return 0
        else:
            return int(2 * (rssi + 100))
    
    def _signal_color(self, rssi):
        """Return QColor based on signal strength."""
        if rssi >= -50:
            return QColor(0, 200, 0)  # Green - excellent
        elif rssi >= -70:
            return QColor(200, 200, 0)  # Yellow - good
        elif rssi >= -85:
            return QColor(200, 150, 0)  # Orange - fair
        else:
            return QColor(200, 0, 0)  # Red - poor
    
    def _rssi_to_hex_color(self, rssi):
        """Return hex color string based on signal strength."""
        if rssi >= -50:
            return '#00cc00'
        elif rssi >= -70:
            return '#cccc00'
        elif rssi >= -85:
            return '#cc8800'
        else:
            return '#cc0000'
    
    def _import_csv(self):
        """Import measurement data from CSV file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import CSV", "", "CSV Files (*.csv);;All Files (*)")
        
        if not filepath:
            return
        
        try:
            import csv
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                
                count = 0
                for row in reader:
                    if len(row) >= 3:
                        try:
                            x = float(row[0])
                            y = float(row[1])
                            signal = float(row[2])
                            ssid = row[3] if len(row) > 3 else "Imported"
                            channel = int(row[4]) if len(row) > 4 else 0
                            self.measurement_points.append((x, y, signal, ssid, channel))
                            count += 1
                        except (ValueError, IndexError):
                            continue
            
            self._update_data_table()
            self.lbl_data_count.setText("Points: " + str(len(self.measurement_points)))
            self.lbl_data_points.setText("Data Points: " + str(len(self.measurement_points)))
            self.statusBar().showMessage("Imported " + str(count) + " data points from " + filepath, 5000)
            
        except Exception as e:
            QMessageBox.warning(self, "Import Error", "Failed to import CSV:\n" + str(e))
    
    def _export_csv(self):
        """Export measurement data to CSV file."""
        if not self.measurement_points:
            QMessageBox.warning(self, "No Data", "No data to export.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "measurements.csv", "CSV Files (*.csv);;All Files (*)")
        
        if not filepath:
            return
        
        try:
            import csv
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['x', 'y', 'signal', 'ssid', 'channel'])
                for point in self.measurement_points:
                    writer.writerow(point)
            
            self.statusBar().showMessage("Exported " + str(len(self.measurement_points)) + " data points to " + filepath, 5000)
            
        except Exception as e:
            QMessageBox.warning(self, "Export Error", "Failed to export CSV:\n" + str(e))
    
    def _load_sample_data(self):
        """Load sample measurement data."""
        sample_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_measurements.csv')
        
        if not os.path.exists(sample_file):
            # Generate sample data
            self._generate_sample_data()
            return
        
        try:
            import csv
            with open(sample_file, 'r') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                
                self.measurement_points = []
                for row in reader:
                    if len(row) >= 3:
                        try:
                            x = float(row[0])
                            y = float(row[1])
                            signal = float(row[2])
                            ssid = row[3] if len(row) > 3 else "Sample"
                            channel = int(row[4]) if len(row) > 4 else 0
                            self.measurement_points.append((x, y, signal, ssid, channel))
                        except (ValueError, IndexError):
                            continue
            
            self._update_data_table()
            self.lbl_data_count.setText("Points: " + str(len(self.measurement_points)))
            self.lbl_data_points.setText("Data Points: " + str(len(self.measurement_points)))
            self.statusBar().showMessage("Loaded " + str(len(self.measurement_points)) + " sample data points", 5000)
            
        except Exception as e:
            QMessageBox.warning(self, "Load Error", "Failed to load sample data:\n" + str(e))
    
    def _generate_sample_data(self):
        """Generate sample measurement data for demonstration."""
        import random
        random.seed(42)
        
        self.measurement_points = []
        
        # Simulate a WiFi router at center with some noise
        for i in range(30):
            x = random.uniform(-10, 10)
            y = random.uniform(-10, 10)
            dist = (x**2 + y**2)**0.5
            signal = -30 - dist * 5 + random.uniform(-5, 5)
            signal = max(-100, min(-20, signal))
            self.measurement_points.append((x, y, signal, "Sample Router", 6))
        
        self._update_data_table()
        self.lbl_data_count.setText("Points: " + str(len(self.measurement_points)))
        self.lbl_data_points.setText("Data Points: " + str(len(self.measurement_points)))
        self.statusBar().showMessage("Generated " + str(len(self.measurement_points)) + " sample data points", 5000)
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About SpectraLens",
            "<h2>SpectraLens v1.0.0</h2>"
            "<p>WiFi Frequency Visualization Tool</p>"
            "<p>Transforms wireless signals into beautiful "
            "2D heatmaps and 3D surface visualizations.</p>"
            "<hr>"
            "<p><b>Creator:</b> Asmaul Asni Subegi, S.Kom</p>"
            "<p><b>Email:</b> sabayonx@gmail.com</p>"
            "<hr>"
            "<p>Built with Python, PyQt5, Matplotlib, and NumPy</p>"
        )
    
    def resizeEvent(self, event):
        """Handle window resize to update visualization display."""
        super().resizeEvent(event)
        # Canvas-based visualizations auto-resize via FigureCanvas


