"""
Fama-French five-factor regression for strategy return attribution.
"""

from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import requests
import statsmodels.api as sm


FACTOR_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Research_Data_5_Factors_2x3_CSV.zip"
)

FACTOR_COLUMNS = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"]


def download_fama_french_factors():
    """Download and parse monthly Fama-French five-factor data."""
    response = requests.get(FACTOR_URL, timeout=30)
    response.raise_for_status()

    with ZipFile(BytesIO(response.content)) as archive:
        csv_name = archive.namelist()[0]
        raw_data = archive.read(csv_name).decode("utf-8")

    lines = raw_data.splitlines()
    start = next(
        index for index, line in enumerate(lines)
        if line.startswith(",Mkt-RF")
    )
    end = next(
        index for index, line in enumerate(lines[start + 1:], start + 1)
        if not line.strip() or not line[:6].strip().isdigit()
    )

    factors = pd.read_csv(
        BytesIO("\n".join(lines[start:end]).encode("utf-8")),
        index_col=0,
    )

    factors.index = pd.to_datetime(factors.index.astype(str), format="%Y%m")
    factors.index = factors.index.to_period("M").to_timestamp("M")
    factors.columns = factors.columns.str.strip()
    factors = factors[FACTOR_COLUMNS].apply(pd.to_numeric, errors="coerce") / 100

    return factors.dropna()


def run_factor_regression(results):
    """Estimate monthly strategy excess returns against FF5 factors."""
    strategy_monthly = (
        (1 + results["strategy_return"])
        .resample("ME")
        .prod()
        .sub(1)
    )

    factors = download_fama_french_factors()
    regression_data = pd.concat(
        [strategy_monthly.rename("strategy_return"), factors],
        axis=1,
        join="inner",
    ).dropna()

    excess_returns = regression_data["strategy_return"] - regression_data["RF"]
    regressors = sm.add_constant(regression_data[["Mkt-RF", "SMB", "HML", "RMW", "CMA"]])

    model = sm.OLS(excess_returns, regressors).fit(cov_type="HC3")

    regression_table = pd.DataFrame(
        {
            "coefficient": model.params,
            "t_statistic": model.tvalues,
            "p_value": model.pvalues,
        }
    )
    regression_table.loc["R-squared", "coefficient"] = model.rsquared
    regression_table.loc["Observations", "coefficient"] = model.nobs

    return regression_table, model