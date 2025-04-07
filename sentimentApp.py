import streamlit as st
import pandas as pd
from textblob import TextBlob
import io

st.set_page_config(page_title="Sentiment Analyzer", layout="centered")

st.title("🧠 Customer Review Sentiment Analyzer")

# Upload CSV or Excel file
uploaded_file = st.file_uploader("Upload a CSV or Excel file with customer reviews", type=["csv", "xlsx"])

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1]
    
    # Load file
    try:
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Could not read the file: {e}")
        st.stop()
    
    # Find the review column
    review_col = None
    for col in df.columns:
        if "review" in col.lower():
            review_col = col
            break

    if not review_col:
        st.error("No column containing 'review' found. Please make sure the file has a review column.")
        st.stop()

    st.subheader("Preview of Uploaded Data")
    st.dataframe(df[[review_col]].head())

    # Sentiment analysis
    def get_sentiment(text):
        blob = TextBlob(str(text))
        polarity = blob.sentiment.polarity
        if polarity > 0.1:
            return "Positive"
        elif polarity < -0.1:
            return "Negative"
        else:
            return "Neutral"

    df['Sentiment'] = df[review_col].apply(get_sentiment)

    st.subheader("Sentiment Breakdown")
    sentiment_counts = df['Sentiment'].value_counts(normalize=True).round(2) * 100
    st.bar_chart(sentiment_counts)

    # Business summary message
    st.subheader("Business Insight")
    if sentiment_counts.get('Negative', 0) > 50:
        st.warning("""
        **Customer Sentiment Alert**

        More than half of your reviews are negative.
        It might be time to investigate recurring issues, improve customer experience, and address pain points.
        """)
    elif sentiment_counts.get('Positive', 0) > 50:
        st.success("""
        **Kudos!**

        Customers are loving your service. Keep it up!
        Highlight those positive experiences and build momentum.
        """)
    else:
        st.info("Sentiment is mixed. Watch closely for patterns over time.")

    # Download processed file
    st.subheader("Download Processed File")
    output = io.BytesIO()
    if file_type == 'csv':
        df.to_csv(output, index=False)
        st.download_button("Download CSV", data=output.getvalue(), file_name="sentiment_results.csv", mime="text/csv")
    else:
        df.to_excel(output, index=False, engine='openpyxl')
        st.download_button("Download Excel", data=output.getvalue(), file_name="sentiment_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
