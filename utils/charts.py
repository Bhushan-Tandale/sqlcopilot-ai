import plotly.express as px
import streamlit as st


def generate_chart(df):

    """
    Automatically generate charts
    based on query result structure
    """

    columns = df.columns.tolist()

    # Need at least 2 columns
    if len(columns) < 2:
        st.info("Not enough columns for chart generation.")
        return

    x_col = columns[0]
    y_col = columns[1]

    # =========================================
    # LINE CHART
    # =========================================

    if "month" in x_col.lower() or "date" in x_col.lower():

        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            markers=True,
            title=f"{y_col} over {x_col}"
        )

        # Premium purple line
        fig.update_traces(
            line=dict(
                color="#8B5CF6",
                width=4
            ),

            marker=dict(
                size=8,
                color="#C4B5FD",
                line=dict(
                    width=2,
                    color="#8B5CF6"
                )
            )
        )

    # =========================================
    # BAR CHART
    # =========================================

    else:

        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            title=f"{y_col} by {x_col}",

            color_discrete_sequence=[
                "#8B5CF6"
            ]
        )

        fig.update_traces(
            marker_line_width=0
        )

    # =========================================
    # GLOBAL CHART STYLING
    # =========================================

    fig.update_layout(

        paper_bgcolor="#0b1220",
        plot_bgcolor="#08101f",

        hoverlabel=dict(
            bgcolor="#111827",
            bordercolor="#8B5CF6",
            font_size=14
        ),

        

        font=dict(
            color="white",
            family="Inter"
        ),

        title=dict(
            font=dict(
                size=24
            ),
            x=0.02
        ),

        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20
        ),

        height=420,

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False
        ),

        yaxis=dict(
            gridcolor="rgba(255,255,255,0.08)",
            zeroline=False,
            showline=False
        )
    )

    # =========================================
    # DISPLAY CHART
    # =========================================

    st.plotly_chart(
        fig,
        use_container_width=True
    )