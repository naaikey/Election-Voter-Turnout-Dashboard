import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, callback_context

# -------------------------
# Data loading (relative path)
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "1100378_Final_Election_data.xlsx"

try:
    df = pd.read_excel(DATA_PATH)
except FileNotFoundError:
    print(f"Warning: {DATA_PATH} not found. Please ensure the Excel file is in the same directory.")
    df = pd.DataFrame(columns=[
        "Constituency", "State", "Year", "Electors_Total", "Electors_Male", 
        "Electors_Female", "Votes_Polled_Total", "Votes_Polled_Male", "Votes_Polled_Female",
        "Turnout_Ratio_Overall", "Turnout_Ratio_Male", "Turnout_Ratio_Female", "Turnout_Ratio_Postal"
    ])

# Ensure column names are exactly as expected
df.columns = [
    "Constituency",
    "State",
    "Year",
    "Electors_Total",
    "Electors_Male",
    "Electors_Female",
    "Votes_Polled_Total",
    "Votes_Polled_Male",
    "Votes_Polled_Female",
    "Votes_Polled_Postal",
    "Turnout_Ratio_Overall",
    "Turnout_Ratio_Male",
    "Turnout_Ratio_Female",
    "Turnout_Ratio_Postal",
]

# Ensure Year is int and turnout ratios are numeric
if not df.empty:
    df["Year"] = df["Year"].astype(int)
    turnout_cols = [
        "Turnout_Ratio_Overall",
        "Turnout_Ratio_Male",
        "Turnout_Ratio_Female",
        "Turnout_Ratio_Postal",
    ]
    df[turnout_cols] = df[turnout_cols].apply(pd.to_numeric, errors='coerce')
    
    # Ensure raw counts are numeric for KPI calculation
    count_cols = [
        "Electors_Total", "Electors_Male", "Electors_Female",
        "Votes_Polled_Total", "Votes_Polled_Male", "Votes_Polled_Female"
    ]
    df[count_cols] = df[count_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

# -------------------------
# Color settings
# -------------------------
year_orange_palette = ["#FDBE85", "#FD8D3C", "#E6550D"]  # 2014, 2019, 2024
gender_color_map = {
    "Male": "blue",
    "Female": "pink",
}

year_color_map = {
    "2014": year_orange_palette[0],
    "2019": year_orange_palette[1],
    "2024": year_orange_palette[2],
}

# -------------------------
# Helper aggregations
# -------------------------

def aggregate_overall(df_in: pd.DataFrame) -> pd.DataFrame:
    if df_in.empty: return pd.DataFrame(columns=["Year", "Turnout_Ratio_Overall_Agg"])
    agg = (
        df_in.assign(weight=df_in["Electors_Total"])
        .groupby("Year")
        .apply(
            lambda x: np.average(x["Turnout_Ratio_Overall"], weights=x["weight"])
        )
        .reset_index(name="Turnout_Ratio_Overall_Agg")
    )
    return agg

def aggregate_by_gender(df_in: pd.DataFrame) -> pd.DataFrame:
    if df_in.empty: return pd.DataFrame(columns=["Year", "Gender", "Turnout_Ratio"])
    male = (
        df_in.assign(weight=df_in["Electors_Male"])
        .groupby("Year")
        .apply(lambda x: np.average(x["Turnout_Ratio_Male"], weights=x["weight"]))
        .reset_index(name="Turnout_Ratio_Male_Agg")
    )
    female = (
        df_in.assign(weight=df_in["Electors_Female"])
        .groupby("Year")
        .apply(lambda x: np.average(x["Turnout_Ratio_Female"], weights=x["weight"]))
        .reset_index(name="Turnout_Ratio_Female_Agg")
    )

    agg = male.merge(female, on="Year")
    df_long = agg.melt(
        id_vars="Year",
        value_vars=[
            "Turnout_Ratio_Male_Agg",
            "Turnout_Ratio_Female_Agg",
        ],
        var_name="Gender",
        value_name="Turnout_Ratio",
    )
    df_long["Gender"] = (
        df_long["Gender"]
        .str.replace("Turnout_Ratio_", "", regex=False)
        .str.replace("_Agg", "", regex=False)
    )
    return df_long

def constituency_over_time(df_in: pd.DataFrame) -> pd.DataFrame:
    return df_in[["Constituency", "Year", "Turnout_Ratio_Overall"]]

def constituency_by_gender(df_in: pd.DataFrame) -> pd.DataFrame:
    df_long = df_in.melt(
        id_vars=["Constituency", "Year"],
        value_vars=[
            "Turnout_Ratio_Male",
            "Turnout_Ratio_Female",
        ],
        var_name="Gender",
        value_name="Turnout_Ratio",
    )
    df_long["Gender"] = df_long["Gender"].str.replace(
        "Turnout_Ratio_", "", regex=False
    )
    return df_long

# Precompute globals
const_gender = constituency_by_gender(df)

# -------------------------
# Dash app layout
# -------------------------
app = Dash(__name__)

years = sorted(df["Year"].unique()) if not df.empty else []
constituencies = sorted(df["Constituency"].unique()) if not df.empty else []

kpi_style = {
    "border": "1px solid #ddd",
    "borderRadius": "8px",
    "padding": "15px",
    "textAlign": "center",
    "width": "30%",
    "boxShadow": "2px 2px 5px rgba(0,0,0,0.1)",
    "backgroundColor": "#fff"
}

app.layout = html.Div(
    style={
        "fontFamily": "Arial", 
        "backgroundColor": "#f9f9f9", 
        "height": "100vh", 
        "display": "flex", 
        "flexDirection": "column",
        "overflow": "hidden" 
    },
    children=[
        html.Div(
            style={"padding": "20px", "paddingBottom": "0px", "flex": "0 0 auto"},
            children=[
                html.H2("Voter Turnout Dashboard (10 Constituencies, 3 General Elections)", style={"textAlign": "center", "marginTop": "0"}),

                # Filters row
                html.Div(
                    style={"display": "flex", "gap": "20px", "marginBottom": "20px", "justifyContent": "center"},
                    children=[
                        html.Div(
                            children=[
                                html.Label("Select Year:", style={"fontWeight": "bold"}),
                                dcc.Dropdown(
                                    id="year-filter",
                                    options=[{"label": str(y), "value": y} for y in years],
                                    value=None,
                                    placeholder="All years",
                                    clearable=True,
                                ),
                            ],
                            style={"width": "200px"},
                        ),
                        html.Div(
                            children=[
                                html.Label("Select Constituency:", style={"fontWeight": "bold"}),
                                dcc.Dropdown(
                                    id="const-filter",
                                    options=[{"label": c, "value": c} for c in constituencies],
                                    value=None,
                                    placeholder="All constituencies",
                                    clearable=True,
                                ),
                            ],
                            style={"width": "300px"},
                        ),
                    ],
                ),

                # KPI Boxes Row
                html.Div(
                    style={"display": "flex", "justifyContent": "space-around", "marginBottom": "20px"},
                    children=[
                        html.Div(id="kpi-overall", style=kpi_style),
                        html.Div(id="kpi-male", style=kpi_style),
                        html.Div(id="kpi-female", style=kpi_style),
                    ]
                ),
            ]
        ),

        # Hidden state for drill-down
        dcc.Store(id="selected-year"),
        dcc.Store(id="selected-constituency"),

        # Scrollable Charts Section
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gridGap": "20px",
                "overflowY": "auto", 
                "flex": "1",          
                "padding": "20px",
            },
            children=[
                html.Div(
                    children=[
                        html.H4("1. Change in overall turnout ratio over time"),
                        dcc.Graph(id="chart-overall-time", style={"height": "500px"}),
                    ]
                ),
                html.Div(
                    children=[
                        html.H4("2. Change in turnout ratio across genders over time"),
                        dcc.Graph(id="chart-gender-time", style={"height": "500px"}),
                    ]
                ),
                html.Div(
                    children=[
                        html.H4(
                            "3. Turnout distribution across constituencies and time"
                        ),
                        dcc.Graph(id="chart-const-time", style={"height": "500px"}),
                    ]
                ),
                html.Div(
                    children=[
                        html.H4(
                            "4. Turnout distribution across constituencies and genders"
                        ),
                        dcc.Graph(id="chart-const-gender", style={"height": "500px"}),
                    ]
                ),
            ],
        ),
    ],
)

# -------------------------
# Drill-down state management
# -------------------------

@app.callback(
    Output("selected-year", "data"),
    Output("selected-constituency", "data"),
    Input("chart-const-time", "clickData"),
    Input("chart-const-gender", "clickData"),
    Input("chart-overall-time", "clickData"),
    Input("year-filter", "value"),
    Input("const-filter", "value"),
    State("selected-year", "data"),
    State("selected-constituency", "data"),
)
def update_selection(
    click_const_time,
    click_const_gender,
    click_overall,
    year_filter,
    const_filter,
    sel_year,
    sel_const,
):
    trigger = (
        callback_context.triggered[0]["prop_id"].split(".")[0]
        if callback_context.triggered
        else None
    )

    if trigger == "year-filter":
        sel_year = year_filter
    elif trigger == "const-filter":
        sel_const = const_filter
    elif trigger == "chart-const-time" and click_const_time:
        point = click_const_time["points"][0]
        sel_const = point.get("x")
        sel_year = point.get("customdata")
    elif trigger == "chart-const-gender" and click_const_gender:
        point = click_const_gender["points"][0]
        sel_const = point.get("x")
        sel_year = point.get("customdata")
    elif trigger == "chart-overall-time" and click_overall:
        point = click_overall["points"][0]
        sel_year = point.get("x")

    return sel_year, sel_const

# -------------------------
# KPI Callback
# -------------------------
@app.callback(
    Output("kpi-overall", "children"),
    Output("kpi-male", "children"),
    Output("kpi-female", "children"),
    Input("selected-year", "data"),
    Input("selected-constituency", "data"),
)
def update_kpis(selected_year, selected_const):
    dff = df.copy()
    
    # Filter
    if selected_year is not None:
        dff = dff[dff["Year"] == selected_year]
    if selected_const is not None:
        dff = dff[dff["Constituency"] == selected_const]

    if dff.empty:
        return (
            [html.H3("N/A"), html.P("Overall Turnout")],
            [html.H3("N/A"), html.P("Male Turnout")],
            [html.H3("N/A"), html.P("Female Turnout")]
        )

    # Weighted calculation
    total_votes = dff["Votes_Polled_Total"].sum()
    total_electors = dff["Electors_Total"].sum()
    
    male_votes = dff["Votes_Polled_Male"].sum()
    male_electors = dff["Electors_Male"].sum()
    
    female_votes = dff["Votes_Polled_Female"].sum()
    female_electors = dff["Electors_Female"].sum()
    
    overall_pct = (total_votes / total_electors * 100) if total_electors > 0 else 0
    male_pct = (male_votes / male_electors * 100) if male_electors > 0 else 0
    female_pct = (female_votes / female_electors * 100) if female_electors > 0 else 0
    
    def create_content(title, val, color):
        return [
            html.H3(f"{val:.2f}%", style={"margin": "0", "fontSize": "24px", "color": color}),
            html.P(title, style={"margin": "5px 0 0 0", "fontSize": "16px", "color": "#555"})
        ]
        
    return (
        create_content("Overall Turnout", overall_pct, "#E6550D"),
        create_content("Male Turnout", male_pct, "blue"),
        create_content("Female Turnout", female_pct, "deeppink")
    )

# -------------------------
# Chart callbacks
# -------------------------

@app.callback(
    Output("chart-overall-time", "figure"),
    Input("selected-year", "data"),
    Input("selected-constituency", "data"),
)
def update_chart_overall(selected_year, selected_const):
    dff = df.copy()
    title = "Overall Voter Turnout Ratio (All Constituencies)"
    if selected_const:
        dff = dff[dff["Constituency"] == selected_const]
        title = f"Overall Voter Turnout Ratio ({selected_const})"

    data = aggregate_overall(dff)
    
    if data.empty:
        return px.line(title=title)

    fig = px.line(
        data,
        x="Year",
        y="Turnout_Ratio_Overall_Agg",
        markers=True,
        title=title,
        text="Turnout_Ratio_Overall_Agg"
    )
    
    fig.update_traces(
        line_color="#E6550D", 
        marker=dict(size=10),
        texttemplate='%{text:.2f}%', 
        textposition='top center'
    )

    if selected_year is not None:
        fig.add_vline(x=selected_year, line_dash="dash", line_color="red")
        
    fig.update_layout(
        xaxis=dict(
            title="Year",
            tickmode="array",
            tickvals=[2014, 2019, 2024],
            ticktext=["2014", "2019", "2024"],
        ),
        yaxis_title="Turnout ratio (%)",
    )
    return fig

@app.callback(
    Output("chart-gender-time", "figure"),
    Input("selected-year", "data"),
    Input("selected-constituency", "data"),
)
def update_chart_gender(selected_year, selected_const):
    dff = df.copy()
    title = "Voter Turnout Ratio by Gender (All Constituencies)"
    if selected_const:
        dff = dff[dff["Constituency"] == selected_const]
        title = f"Voter Turnout Ratio by Gender ({selected_const})"
        
    data = aggregate_by_gender(dff)

    if data.empty:
        return px.line(title=title)

    fig = px.line(
        data,
        x="Year",
        y="Turnout_Ratio",
        color="Gender",
        markers=True,
        title=title,
        color_discrete_map=gender_color_map,
        text="Turnout_Ratio"
    )
    
    fig.update_traces(
        texttemplate='%{text:.2f}%', 
        textposition='top center'
    )
    
    if selected_year is not None:
        fig.add_vline(x=selected_year, line_dash="dash", line_color="red")
    fig.update_layout(
        xaxis=dict(
            title="Year",
            tickmode="array",
            tickvals=[2014, 2019, 2024],
            ticktext=["2014", "2019", "2024"],
        ),
        yaxis_title="Turnout ratio (%)",
    )
    return fig

@app.callback(
    Output("chart-const-time", "figure"),
    Input("selected-year", "data"),
    Input("selected-constituency", "data"),
)
def update_chart_const_time(selected_year, selected_const):
    data = constituency_over_time(df)
    
    if selected_const:
        data = data[data["Constituency"] == selected_const]
    
    data = data.copy()
    data["Year_str"] = data["Year"].astype(str)

    fig = px.bar(
        data,
        x="Constituency",
        y="Turnout_Ratio_Overall",
        color="Year_str",
        barmode="group",
        title="Voter Turnout Ratio across Constituencies and Time",
        custom_data=["Year"],
        color_discrete_map=year_color_map,
        category_orders={"Year_str": ["2014", "2019", "2024"]},
        labels={"Year_str": "Year"} # Renamed Legend Title
    )

    if selected_year is not None:
        for y_str in ["2014", "2019", "2024"]:
            fig.for_each_trace(
                lambda tr: tr.update(
                    opacity=1.0 if tr.name == str(selected_year) else 0.3
                )
            )

    fig.update_layout(
        xaxis_title="Constituency",
        yaxis_title="Turnout ratio (%)",
    )
    return fig

@app.callback(
    Output("chart-const-gender", "figure"),
    Input("selected-year", "data"),
    Input("selected-constituency", "data"),
)
def update_chart_const_gender(selected_year, selected_const):
    data = const_gender.copy()

    if selected_year is not None:
        data = data[data["Year"] == selected_year]
    if selected_const is not None:
        data = data[data["Constituency"] == selected_const]

    data["Year_str"] = data["Year"].astype(str)

    fig = px.bar(
        data,
        x="Constituency",
        y="Turnout_Ratio",
        color="Gender",
        facet_col="Year_str",
        title="Voter Turnout Ratio across Constituencies and Genders",
        custom_data=["Year"],
        color_discrete_map=gender_color_map,
        barmode="group",
        labels={"Year_str": "Year"} # Renamed Facet Header variable
    )
    fig.update_layout(
        xaxis_title="Constituency",
        yaxis_title="Turnout ratio (%)",
    )
    return fig

# -------------------------
# Run the app
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)