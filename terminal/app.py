import sys
import os
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QGroupBox, QScrollArea, QTextEdit, QListWidget, QFrame,
    QStatusBar, QHeaderView, QSizePolicy, QLineEdit
)
from PyQt6.QtGui import QPalette, QColor, QFont, QFontDatabase, QPixmap, QIcon

PRIMARY_COLOR = "#4285f4"
SECONDARY_COLOR = "#ffffff"  # Changed from black to white
TEXT_COLOR = "#000000"  # Changed from white to black for better contrast
PANEL_BG = "#f5f7fa"  # Lighter panel background

# Global variable for current trading pair
current_pair = "ETHUSD"

class TradeByteTerminal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TradeByte Terminal")
        self.setMinimumSize(1600, 900)
        
        # Set application icon
        icon_path = os.path.join("docs", "images", "tradebyte-small.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setStyleSheet(f"""
            background-color: {SECONDARY_COLOR}; 
            color: {TEXT_COLOR}; 
            font-family: Arial;
        """)

        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(5, 5, 5, 5)
        central_layout.setSpacing(0)

        # Header Bar
        header = QHBoxLayout()
        header.setContentsMargins(10, 5, 10, 5)
        
        # TradeByte logo
        logo = QLabel()
        logo_path = os.path.join("docs", "images", "tradebyte.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaledToHeight(40, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(scaled_pixmap)
        else:
            logo.setText("TradeByte Terminal")
            logo.setStyleSheet(f"""
                color: {PRIMARY_COLOR};
                font-weight: bold;
                font-size: 18px;
            """)
        
        # Market status
        market_status = QLabel("MARKETS OPEN")
        market_status.setStyleSheet(f"""
            color: #00aa00;  /* Darker green for better visibility on white */
            font-weight: bold;
            padding: 0 10px;
        """)
        
        # Search bar
        search_container = QWidget()
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(5)
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet(f"color: {TEXT_COLOR};")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter trading pair (e.g., ETHUSD)")
        self.search_input.setText(current_pair)  # Set default value
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {PANEL_BG};
                border: 1px solid #ddd;
                padding: 5px;
                color: {TEXT_COLOR};
            }}
        """)
        self.search_input.returnPressed.connect(self._handle_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_container.setLayout(search_layout)
        header.addWidget(search_container)
        
        header.addWidget(logo)
        header.addStretch()
        header.addWidget(market_status)
        
        central_layout.addLayout(header)

        # Ticker
        ticker = QLabel()
        ticker.setStyleSheet(f"""
            background: {PANEL_BG};
            color: {TEXT_COLOR};
            padding: 5px;
            font-family: 'Courier New';
            font-size: 14px;
            font-weight: bold;
        """)
        ticker.setFrameShape(QFrame.Shape.StyledPanel)
        ticker.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(ticker)
        
        # Initialize ticker animation
        self.ticker_text = "BTC/USD: $40,000 (+2.5%) | ETH/USD: $2,200 (+1.8%) | XRP/USD: $0.50 (-0.5%) | LTC/USD: $150 (+3.2%) | DOT/USD: $7.50 (+5.1%) | ADA/USD: $0.45 (-1.2%)"
        self.ticker_position = 0
        self.ticker_timer = QTimer()
        self.ticker_timer.timeout.connect(self._update_ticker)
        self.ticker_timer.start(100)  
        self.ticker_label = ticker

        central_layout.addWidget(ticker)

        # Main Content Grid
        main_grid = QGridLayout()
        main_grid.setSpacing(5)
        main_grid.setContentsMargins(0, 5, 0, 0)

        # Price Scanner Grid
        price_grid = self._create_table(["Symbol", "Last Price", "Change", "Change %", "Volume", "Time"])
        self._populate_market_data(price_grid)
        main_grid.addWidget(self._wrap_group("MARKET MOVERS", price_grid, 1), 0, 0, 1, 2)

        # Chart Module
        chart_area = QLabel("[Live Chart Placeholder]")
        chart_area.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid #ddd;")
        chart_area.setFrameShape(QFrame.Shape.StyledPanel)
        chart_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_grid.addWidget(self._wrap_group("CHART - BTC/USD", chart_area, 1), 0, 2, 1, 2)

        # Portfolio
        portfolio = self._create_table(["Asset", "Position", "Avg Cost", "Market Value", "PnL"])
        self._populate_portfolio(portfolio)
        main_grid.addWidget(self._wrap_group("PORTFOLIO", portfolio), 1, 0)

        # Trades
        trades = QListWidget()
        trades.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid #ddd;")
        self._populate_trades(trades)
        main_grid.addWidget(self._wrap_group("RECENT TRADES", trades), 1, 1)

        # Open Orders
        orders = self._create_table(["Symbol", "Side", "Type", "Qty", "Price", "Status"])
        self._populate_orders(orders)
        main_grid.addWidget(self._wrap_group("OPEN ORDERS", orders), 1, 2)

        # Order Book
        order_book = QTextEdit()
        order_book.setStyleSheet(f"background: {PANEL_BG}; border: 1px solid #ddd;")
        order_book.setPlainText(self._generate_order_book())
        order_book.setReadOnly(True)
        main_grid.addWidget(self._wrap_group("ORDER BOOK - BTC/USD", order_book), 1, 3)

        # News Feed and Command Prompt
        news_command_container = QWidget()
        news_command_layout = QHBoxLayout()
        news_command_layout.setSpacing(5)
        news_command_layout.setContentsMargins(0, 0, 0, 0)
        
        # News Feed
        news_feed = QTextEdit()
        news_feed.setStyleSheet(f"""
            QTextEdit {{
                background: {PANEL_BG};
                border: 1px solid #ddd;
                font-family: 'Arial';
                font-size: 14px;
                line-height: 1.5;
            }}
        """)
        news_feed.setPlainText(self._generate_news_feed())
        news_feed.setReadOnly(True)
        
        # Command Prompt
        command_prompt = QLineEdit()
        command_prompt.setPlaceholderText("Enter command...")
        command_prompt.setStyleSheet(f"""
            QLineEdit {{
                background: {PANEL_BG};
                border: 1px solid #ddd;
                padding: 5px;
                font-family: Consolas, monospace;
            }}
        """)
        command_prompt.returnPressed.connect(self._execute_command)
        
        # Add widgets to container
        news_command_layout.addWidget(news_feed, 4)  # 4 parts width
        news_command_layout.addWidget(command_prompt, 1)  # 1 part width
        
        news_command_container.setLayout(news_command_layout)
        main_grid.addWidget(self._wrap_group("TOP NEWS & COMMAND", news_command_container), 2, 0, 1, 4)

        central_layout.addLayout(main_grid)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            background: {PRIMARY_COLOR};
            color: white;
            font-weight: bold;
        """)

        # version status
        self.ver_status = QLabel("Version v1.1.0 ")
        self.ver_status.setStyleSheet("color: #00ff00;")
        
        # Connection status
        self.connection_status = QLabel(" CONNECTED ")
        self.connection_status.setStyleSheet("color: #00ff00;")
        
        # Current date and time
        self.datetime_label = QLabel()
        self._update_datetime()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_datetime)
        self.timer.start(1000)
        
        self.status_bar.addPermanentWidget(self.ver_status)
        self.status_bar.addPermanentWidget(self.connection_status)
        self.status_bar.addPermanentWidget(self.datetime_label)
        
        self.setStatusBar(self.status_bar)

    def _execute_command(self):
        command = self.sender().text()
        print(f"Command executed: {command}")  # Replace with actual command handling
        self.sender().clear()

    def _wrap_group(self, title, widget, header_size=0):
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                background: {PANEL_BG};
                border: 1px solid #ddd;
                margin-top: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        
        if isinstance(widget, QTableWidget):
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            widget.horizontalHeader().setStretchLastSection(True)
            widget.verticalHeader().setVisible(False)
            widget.setStyleSheet(f"""
                QTableWidget {{
                    background: {PANEL_BG};
                    color: {TEXT_COLOR};
                    gridline-color: #ddd;
                    border: 1px solid #ddd;
                }}
                QTableWidget::item {{
                    padding: 5px;
                }}
                QHeaderView::section {{
                    background: {PANEL_BG};
                    color: {PRIMARY_COLOR};
                    padding: 5px;
                    border: none;
                    font-weight: bold;
                }}
            """)
        
        layout.addWidget(widget)
        group.setLayout(layout)
        return group

    def _create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setStyleSheet(f"""
            QTableWidget {{
                background: {PANEL_BG};
                gridline-color: #ddd;
                border: 1px solid #ddd;
            }}
            QHeaderView::section {{
                background-color: {PRIMARY_COLOR};
                color: white;
                padding: 3px;
                border: none;
                font-weight: bold;
            }}
        """)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        return table

    def _update_datetime(self):
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%Y-%m-%d %H:%M:%S"))

    def _populate_market_data(self, table):
        symbols = ["BTC/USD", "ETH/USD", "SOL/USD", "AAPL", "MSFT", "TSLA", "NVDA", "AMZN", "GOOGL", "META"]
        table.setRowCount(len(symbols))
        
        for row, symbol in enumerate(symbols):
            price = 68000 + row * 1200 if "USD" in symbol else 180 + row * 5
            change = (row - 4) * 0.5
            change_pct = change / 100
            volume = f"{(1000 + row * 200):,}"
            
            table.setItem(row, 0, QTableWidgetItem(symbol))
            table.setItem(row, 1, QTableWidgetItem(f"{price:,.2f}"))
            
            change_item = QTableWidgetItem(f"{change:+.2f}")
            change_item.setForeground(QColor("#ff0000" if change < 0 else "#00aa00"))  # Darker green
            table.setItem(row, 2, change_item)
            
            pct_item = QTableWidgetItem(f"{change_pct:+.2%}")
            pct_item.setForeground(QColor("#ff0000" if change_pct < 0 else "#00aa00"))  # Darker green
            table.setItem(row, 3, pct_item)
            
            table.setItem(row, 4, QTableWidgetItem(volume))
            table.setItem(row, 5, QTableWidgetItem(datetime.now().strftime("%H:%M:%S")))
            
            table.resizeColumnsToContents()

    def _populate_portfolio(self, table):
        assets = ["BTC", "ETH", "AAPL", "MSFT", "CASH"]
        table.setRowCount(len(assets))
        
        for row, asset in enumerate(assets):
            position = 1.5 + row * 0.3
            avg_cost = 65000 if asset == "BTC" else 3500 if asset == "ETH" else 150 + row * 10
            market_value = (68000 if asset == "BTC" else 3800 if asset == "ETH" else 180 + row * 5) * position
            pnl = market_value - (avg_cost * position)
            
            table.setItem(row, 0, QTableWidgetItem(asset))
            table.setItem(row, 1, QTableWidgetItem(f"{position:,.4f}"))
            table.setItem(row, 2, QTableWidgetItem(f"{avg_cost:,.2f}"))
            table.setItem(row, 3, QTableWidgetItem(f"{market_value:,.2f}"))
            
            pnl_item = QTableWidgetItem(f"{pnl:+,.2f}")
            pnl_item.setForeground(QColor("#ff0000" if pnl < 0 else "#00aa00"))  # Darker green
            table.setItem(row, 4, pnl_item)
            
        table.resizeColumnsToContents()

    def _populate_trades(self, list_widget):
        trades = [
            "10:23:45 Bought 1.5 BTC @ 67,850.00",
            "10:15:30 Sold 50 AAPL @ 192.50",
            "09:45:12 Bought 2.3 ETH @ 3,780.25",
            "09:30:00 Sold 10 MSFT @ 419.80",
            "09:15:45 Bought 5 SOL @ 178.40"
        ]
        list_widget.addItems(trades)
        list_widget.setStyleSheet(f"""
            QListWidget {{
                background: {PANEL_BG};
                border: 1px solid #ddd;
            }}
            QListWidget::item {{
                padding: 3px;
                border-bottom: 1px solid #ddd;
            }}
        """)

    def _populate_orders(self, table):
        orders = [
            ["BTC/USD", "BUY", "LIMIT", "1.2", "67,500.00", "PENDING"],
            ["ETH/USD", "SELL", "STOP", "3.0", "3,900.00", "ACTIVE"],
            ["AAPL", "BUY", "LIMIT", "100", "190.00", "PENDING"],
            ["TSLA", "SELL", "MARKET", "50", "MARKET", "FILLED"]
        ]
        table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            for col, value in enumerate(order):
                item = QTableWidgetItem(value)
                if col == 1:  # Side column
                    item.setForeground(QColor("#00aa00" if value == "BUY" else "#ff0000"))  # Darker green
                elif col == 5:  # Status column
                    item.setForeground(QColor("#ccaa00" if value == "PENDING" else "#00aa00" if value == "ACTIVE" else "#000000"))  # Adjusted colors
                table.setItem(row, col, item)
                
        table.resizeColumnsToContents()

    def _generate_order_book(self):
        return """\
BIDS                ASKS
Price     Size      Price     Size
------    -----     ------    -----
68,000.0  2.5       68,050.0  1.8
67,950.0  3.2       68,100.0  2.1
67,900.0  1.7       68,150.0  3.5
67,850.0  4.0       68,200.0  2.8
67,800.0  2.3       68,250.0  1.5

Last Price: 68,025.50
24h Volume: 12,450 BTC
"""

    def _generate_news_feed(self):
        return """\
[10:30] FED ANNOUNCES INTEREST RATE DECISION - RATES UNCHANGED AT 5.25-5.50%
[10:15] BITCOIN SURGES PAST $68,000 AS INSTITUTIONAL INTEREST GROWS
[09:45] TESLA RECALLS CYBERTRUCK OVER ACCELERATION CONCERN
[09:30] APPLE UNVEILS NEW AI FEATURES AT DEVELOPER CONFERENCE
[09:00] US INFLATION DATA COMES IN LOWER THAN EXPECTED
[08:45] MICROSOFT HITS RECORD HIGH AFTER AI DEMO
[08:30] JOBLESS CLAIMS FALL TO 8-MONTH LOW
"""

    def _update_ticker(self):
        """Update the ticker with scrolling effect and color coding"""
        if self.ticker_position >= len(self.ticker_text):
            self.ticker_position = 0
            
        # Create HTML formatted text with colors
        display_text = self.ticker_text[self.ticker_position:] + " | " + self.ticker_text[:self.ticker_position]
        
        # Add color coding for price changes
        colored_text = ""
        parts = display_text.split(" | ")
        for part in parts:
            if "(+" in part:
                # Green for positive changes
                colored_text += f'<span style="color: #00aa00">{part}</span> | '
            elif "(-" in part:
                # Red for negative changes
                colored_text += f'<span style="color: #ff0000">{part}</span> | '
            else:
                colored_text += f'{part} | '
        
        # Remove the last " | " and set the HTML text
        self.ticker_label.setText(colored_text[:-3])
        self.ticker_position += 1

    def _handle_search(self):
        """Handle search input and update current pair"""
        global current_pair
        new_pair = self.search_input.text().strip().upper()
        if new_pair:
            current_pair = new_pair
            # Update the order book title
            for i in range(self.main_grid.count()):
                widget = self.main_grid.itemAt(i).widget()
                if isinstance(widget, QGroupBox) and "ORDER BOOK" in widget.title():
                    widget.setTitle(f"ORDER BOOK - {current_pair}")
            # Update market data
            self._update_market_data()
            # Update order book
            self._update_order_book()
            # Update trades
            self._update_trades()

app = QApplication(sys.argv)
window = TradeByteTerminal()
window.show()
sys.exit(app.exec())