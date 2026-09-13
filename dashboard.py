import streamlit as st
import pandas as pd
from datetime import datetime
from paper_portfolio import PaperPortfolio
import config

st.set_page_config(
    page_title="Polymarket Copy Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📈 Polymarket Copy Trading Bot")
    st.caption("Paper Trading Dashboard • Sports + BTC Short-term")

    with st.sidebar:
        st.header("Controls")
        st.write(f"**Mode:** 🟢 PAPER")
        st.write(f"**Copy ratio:** {config.COPY_RATIO*100:.0f}%")
        st.write(f"**Max trade:** ${config.MAX_TRADE_USD:.0f}")
        st.divider()
        st.subheader("Target Wallets")
        if config.TARGETS:
            for i, w in enumerate(config.TARGETS, 1):
                st.code(f"{i}. {w[:10]}...{w[-6:]}")
        else:
            st.info("No targets yet.\nAdd them later in config.py")
        st.divider()
        st.caption("This is the online paper dashboard")

    portfolio = PaperPortfolio(starting_cash=1000.0, state_file=config.STATE_FILE)
    metrics = portfolio.summary_dict()

    st.subheader("Portfolio Overview")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Equity", f"${metrics['equity']:,.2f}", delta=f"{metrics['return_pct']:+.2f}%")
    c2.metric("Cash", f"${metrics['cash']:,.2f}")
    c3.metric("Positions Value", f"${metrics['position_value']:,.2f}")
    c4.metric("Total PnL", f"${metrics['total_pnl']:+,.2f}")
    c5.metric("Realized PnL", f"${metrics['realized_pnl']:+,.2f}")
    c6.metric("Unrealized PnL", f"${metrics['unrealized_pnl']:+,.2f}")

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"Open Positions ({metrics['open_positions']})")
        pos_data = portfolio.positions_list()
        if pos_data:
            st.dataframe(pd.DataFrame(pos_data), use_container_width=True, hide_index=True)
        else:
            st.info("No open positions yet.")

    with col2:
        st.subheader("Quick Stats")
        st.metric("Starting Capital", f"${metrics['starting_cash']:,.2f}")
        st.metric("Total Trades", metrics['total_trades'])
        st.metric("Open Positions", metrics['open_positions'])

    st.divider()
    st.subheader("Recent Trades")
    trades = portfolio.trades_list(limit=30)
    if trades:
        st.dataframe(pd.DataFrame(trades), use_container_width=True, hide_index=True)
    else:
        st.info("No trades yet.")

    st.caption(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC • Paper mode")

if __name__ == "__main__":
    main()
