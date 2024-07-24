import pandas as pd
import pandas.api.types as pdtypes
from air_handling_unit.faults.fault_condition import FaultCondition

class FaultConditionOne(FaultCondition):
    """Class provides the definitions for Fault Condition 1."""

    def __init__(self, dict_):
        """

        :param dict_:
        """
        self.vfd_speed_percent_err_thres = float
        self.vfd_speed_percent_max = float
        self.duct_static_inches_err_thres = float
        self.duct_static_col = str
        self.supply_vfd_speed_col = str
        self.duct_static_setpoint_col = str
        self.troubleshoot_mode = bool  # default should be False

        self.set_attributes(dict_)

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.troubleshoot_mode:
            self.troubleshoot_cols(df)

        # check analog outputs [data with units of %] are floats only
        columns_to_check = [self.supply_vfd_speed_col]
        self.check_analog_pct(df, columns_to_check)

        df['static_check_'] = (
            df[self.duct_static_col] < df[self.duct_static_setpoint_col] - self.duct_static_inches_err_thres)
        df['fan_check_'] = (
            df[self.supply_vfd_speed_col] >= self.vfd_speed_percent_max - self.vfd_speed_percent_err_thres)

        # Combined condition check
        df["combined_check"] = df['static_check_'] & df['fan_check_']

        # Rolling sum to count consecutive trues
        rolling_sum = df["combined_check"].rolling(window=5).sum()
        # Set flag to 1 if rolling sum equals the window size (5)
        df["fc1_flag"] = (rolling_sum == 5).astype(int)

        if self.troubleshoot_mode:
            print("Troubleshoot mode enabled - not removing helper columns")
            del df["static_check_"]
            del df["fan_check_"]
            del df["combined_check"]

        return df
