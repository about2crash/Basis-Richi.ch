import pandas as pd
import streamlit as st
import datetime
import random
from streamlit_autorefresh import st_autorefresh

# Constants
STARTING_PRICE = 10000
BID_BUTTON_FUNCTIONALITY = True
REFRESH_INTERVAL = 1000  # in milliseconds
IMAGE_PATHS = ['img/img_1.jpg', 'img/img_2.jpg']

# Configure the Streamlit page
st.set_page_config(page_title="Leber zu verkaufen", page_icon="❤️", layout="wide", initial_sidebar_state="expanded")


def read_bids():
    try:
        df = pd.read_csv('emails.csv', names=['Email', 'Bid'], dtype={'Bid': 'float64'})
        max_bid = df['Bid'].max()
        max_bidder = df.loc[df['Bid'] == max_bid, 'Email'].iloc[0]
        return max_bid, max_bidder
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return None, None


def initialize_auction():
    now = datetime.datetime.now()
    next_full_hour = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    max_bid, max_bidder = read_bids()

    defaults = {
        'end_time': next_full_hour + datetime.timedelta(hours=1),
        'start_time': now - datetime.timedelta(days=2),
        'image_index': 0,
        'current_price': max_bid if max_bid is not None else STARTING_PRICE,
        'current_bidder': max_bidder if max_bidder is not None else "No bids yet",
        'last_bid_time': now,
        'bid_count': 0,
        'auto_bidding_active': True,
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    st.sidebar.image("Logo.png")
    sidebar_categories = ["Autos", "Immobilien", "Kleider", "Möbel", "Schmuck", "Technik", "Weiteres Organe"]
    for category in sidebar_categories:
        st.sidebar.text(category)


def display_auction_images():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("Leber-Auktion")
        st.subheader("Leber in gutem Zustand zu verkaufen")
        st.image(IMAGE_PATHS[st.session_state['image_index']], use_column_width=True)

        prev_col, mid_col, next_col = st.columns([0.42, 1.8, 0.42])
        if prev_col.button("← Vorherige"):
            st.session_state['image_index'] = max(0, st.session_state['image_index'] - 1)
        mid_col.write(f"{st.session_state['image_index'] + 1}/{len(IMAGE_PATHS)}")
        if next_col.button("Nächstes →"):
            st.session_state['image_index'] = min(len(IMAGE_PATHS) - 1, st.session_state['image_index'] + 1)


def manage_bids():
    current_time = datetime.datetime.now()
    st.text_input("Enter your email", key="email")
    bid_input = st.number_input("Bid amount", min_value=1000, value=1000, step=50, key="bid")
    enable_button = st.session_state.email.strip() != ""  # Button is enabled only if there is text in the email input
    if st.button("Place bid", disabled=not enable_button, key="bid_button"):
        if bid_input > st.session_state['current_price']:
            st.session_state['current_price'] = bid_input
            st.session_state['current_bidder'] = st.session_state['email']
            st.session_state['last_bid_time'] = current_time
            st.session_state['auto_bidding_active'] = False  # Optionally stop automated bidding upon manual bid
            st.session_state['bid_count'] += 1

            # Append email and bid to CSV
            new_bid = pd.DataFrame([[st.session_state['email'], bid_input]], columns=['Email', 'Bid'])
            new_bid.to_csv('emails.csv', mode='a', header=False, index=False)

    current_price_display = st.session_state['current_price']
    st.metric(label="Current Price", value=f"{current_price_display} CHF")
    st.write(f"Current highest bidder: {st.session_state['current_bidder']}")


def main():
    st_autorefresh(interval=REFRESH_INTERVAL, key="datarefresher")
    initialize_auction()
    display_auction_images()
    manage_bids()


if __name__ == "__main__":
    main()