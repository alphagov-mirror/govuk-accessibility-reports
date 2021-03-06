from typing import Union
import pandas as pd


def get_attachment_counts_or_percents(df: pd.DataFrame,
                                      index: Union[str, list],
                                      values: str,
                                      date: list = None) -> pd.DataFrame:
    """
    Calculates the counts or percentages for each attachment type and pivots the df for easy reading.

    :param df: Dataframe to transform.
    :param index: String of column to group on alongside a column called 'attachment_type' not pivot on.
    :param values: String of whether you want counts or percents. Only takes one of following ("counts", "percents").
    :param date: List of the two dates to inclusively filter df between, [a, b], where a < b.
    :return: Dataframe of attachment percentages pivoted for easy viewing.
    """
    if isinstance(index, str):
        indices = [index, "attachment_type"]
    elif isinstance(index, list):
        indices = index.append("attachment_type")

    if values == "counts":
        values = "counts_attachments"
    elif values == "percents":
        values = "percentage_attachments"
    else:
        print(f"{values} is an invalid input. Please enter 'counts' or 'percents'.")

    if date is not None:
        mask = (pd.to_datetime(df["first_published_at"]) >= date[0]) & \
                (pd.to_datetime(df["first_published_at"]) <= date[1])  # noqa: E126
        df = df.loc[mask, :]

    # calculate counts and percentages for each `attachment_type`
    df_counts = df.value_counts(subset=indices, sort=False).reset_index()
    df_totals = df.value_counts(subset=[index], sort=False).reset_index()
    df_percent = df_counts.merge(right=df_totals,
                                 how='left',
                                 on=[index],
                                 validate="many_to_one")
    df_percent = df_percent.rename(columns={"0_x": "counts_attachments",
                                            "0_y": "total_pages"})
    df_percent["percentage_attachments"] = df_percent["counts_attachments"] / df_percent["total_pages"]

    # pivot and sort df for easy reading
    df_percent = pd.pivot_table(data=df_percent,
                                index=[index],
                                columns="attachment_type",
                                values=values).reset_index()
    df_percent = df_percent.sort_values(by=index)

    return df_percent
