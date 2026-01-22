import pandas as pd
import streamlit as st

def highlight_status(row):
    colors = []
    # Name
    colors.append("") 
    # Roles
    colors.append("")
    # Consecutive
    val = row["Consecutive Days"]
    if val >= 6:
        colors.append("background-color: #ffcccc; color: black") # Red warning
    elif val >= 5:
        colors.append("background-color: #ffffcc; color: black") # Yellow warning
    else:
        colors.append("")
    
    # Available
    if row["Available Today?"] == "No":
        colors.append("color: gray")
    else:
        colors.append("color: green; font-weight: bold")
    
    # Shifts
    colors.append("")
    # Reason
    colors.append("")
    
    # Validation
    if len(colors) != len(row):
        print(f"Error: Row has {len(row)} cols, but colors has {len(colors)}")
        
    return colors

# Mock Data
data = [
    {
        "Name": "Test",
        "Roles": "Staff",
        "Consecutive Days": 5,
        "Available Today?": "Yes",
        "Assigned Shifts": "A",
        "Reason (If No)": "-"
    }
]

df = pd.DataFrame(data)
print("Columns:", df.columns.tolist())

# Test Apply
try:
    styler = df.style.apply(highlight_status, axis=1)
    # Trigger rendering (to some extent)
    # In real pandas, we can check .to_html() to force apply
    html = styler.to_html()
    print("Styling logic executed successfully.")
except Exception as e:
    print(f"Styling Error: {e}")
