import streamlit as st
from streamlit_navigation_bar import st_navbar


def sidebar_ui():
    st.sidebar.title("🧠 Analisis Sentimen Kapten Naratel")
    st.sidebar.markdown("---")
    st.sidebar.markdown("👋 Selamat datang! Gunakan menu di atas untuk menjelajahi aplikasi.")


def page_style(max_width=1250, padding_left="2rem", padding_right="2rem"):
    st.markdown(f"""
        <style>
            .main .block-container {{
                max-width: {max_width}px;
                padding-left: {padding_left};
                padding-right: {padding_right};
            }}
        </style>
    """, unsafe_allow_html=True)

def navbar_style():
    st.set_page_config(initial_sidebar_state="collapsed")

    pages = ["Upload & Scrape", "Analisis Sentimen", "Visualisasi"]
    styles = {
        "nav": {
            "background-color": "rgb(252, 170, 98)",
        },
        "div": {
            "max-width": "32rem",
        },
        "span": {
            "border-radius": "0.5rem",
            "color": "rgb(49, 51, 63)",
            "margin": "0 0.125rem",
            "padding": "0.4375rem 0.625rem",
        },
        "active": {
            "background-color": "rgba(255, 255, 255, 0.25)",
        },
        "hover": {
            "background-color": "rgba(255, 255, 255, 0.35)",
        },
    }

    page = st_navbar(pages, styles=styles)
    return page
