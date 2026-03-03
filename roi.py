def calculate_roi(median_income, score):
    &quot;&quot;&quot;
    Mock ROI calculation based on median income and score (%).
    Formula: (score / 10) * (median_income / 80000) * 15
    &quot;&quot;&quot;
    return round((score / 10.0) * (median_income / 80000.0) * 15, 1)