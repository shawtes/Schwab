#!/bin/bash

# 🚀 ML Trading System - Interactive Launcher

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║          🤖 ML TRADING SYSTEM - PRODUCTION READY 🚀            ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "What would you like to do?"
echo ""
echo "  1) 🧪 Run Single Paper Trading Cycle (Test)"
echo "  2) 🔄 Start Live Paper Trading (Continuous)"
echo "  3) 📊 View Paper Trading Results"
echo "  4) 📈 Run Full System Backtest"
echo "  5) 🔍 Compare Backtest vs Paper Trading"
echo "  6) 📚 View Documentation"
echo "  7) ❌ Exit"
echo ""
echo -n "Enter your choice [1-7]: "

read choice

case $choice in
    1)
        echo ""
        echo "🧪 Running Single Paper Trading Cycle..."
        echo "This will test the system with one complete cycle"
        echo ""
        ./run_paper_single_cycle.sh
        ;;
    2)
        echo ""
        echo "🔄 Starting Live Paper Trading..."
        echo "Press Ctrl+C to stop"
        echo ""
        ./run_paper_trading.sh
        ;;
    3)
        echo ""
        echo "📊 Loading Paper Trading Results..."
        echo ""
        python view_paper_results.py
        ;;
    4)
        echo ""
        echo "📈 Running Full System Backtest..."
        echo "This may take 10-20 minutes..."
        echo ""
        ./run_full_backtest.sh
        ;;
    5)
        echo ""
        echo "🔍 Comparing Backtest vs Paper Trading..."
        echo ""
        python compare_backtest_paper.py
        ;;
    6)
        echo ""
        echo "📚 Available Documentation:"
        echo ""
        echo "  Quick Start:"
        echo "    - PAPER_TRADING_QUICK_START.md"
        echo "    - QUICK_START.md"
        echo ""
        echo "  Detailed Guides:"
        echo "    - TRADING_SYSTEM_COMPLETE.md (START HERE!)"
        echo "    - PAPER_TRADING_GUIDE.md"
        echo "    - BACKTEST_FULL_SYSTEM_GUIDE.md"
        echo "    - MULTI_TIMEFRAME_EV_SYSTEM.md"
        echo ""
        echo "  Comparisons:"
        echo "    - PAPER_TRADING_COMPARISON.md"
        echo "    - R2_VS_TRADING_PROFITABILITY.md"
        echo ""
        echo "  Architecture:"
        echo "    - FINAL_ARCHITECTURE_AUDIT_2026.md"
        echo "    - ML_TRADING_ARCHITECTURE.md"
        echo ""
        echo "Press Enter to continue..."
        read
        ;;
    7)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run again and select 1-7."
        exit 1
        ;;
esac

echo ""
echo "✅ Complete!"
echo ""
echo "Run './start_here.sh' again for more options"

