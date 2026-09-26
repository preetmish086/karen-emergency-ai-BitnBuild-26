import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import pandas as pd


class LocationReportTracker:
    """
    Spatio-Temporal Location Report Tracker.
    Tracks and counts reports arriving from the SAME location AND WITHIN THE SAME TIME WINDOW (e.g., 30 minutes).

    Solves the bottleneck where morning and evening reports at the same location are NOT conflated.
    """

    def __init__(self, window_minutes: int = 30):
        self.window_minutes = window_minutes
        self.location_window_counts: Dict[str, int] = {}

    def normalize_location_key(self, text_loc: Optional[str], lat: Optional[float], lon: Optional[float]) -> str:
        if text_loc and text_loc.strip():
            return text_loc.strip().lower()
        if lat is not None and lon is not None:
            return f"{round(lat, 3)},{round(lon, 3)}"
        return "unknown"

    def get_time_window_bucket(self, timestamp_str: Optional[str]) -> int:
        """
        Buckets an ISO timestamp string into a discrete time window index (e.g. 30-minute blocks).
        """
        if not timestamp_str:
            # If no timestamp provided, use current UTC time window
            now = datetime.now(timezone.utc)
            epoch_seconds = int(now.timestamp())
        else:
            try:
                # Replace 'Z' with +00:00 for python fromisoformat compatibility
                ts_clean = timestamp_str.replace("Z", "+00:00")
                dt = datetime.fromisoformat(ts_clean)
                epoch_seconds = int(dt.timestamp())
            except Exception:
                now = datetime.now(timezone.utc)
                epoch_seconds = int(now.timestamp())

        window_seconds = self.window_minutes * 60
        return epoch_seconds // window_seconds

    def get_spatio_temporal_key(
        self,
        text_loc: Optional[str],
        lat: Optional[float],
        lon: Optional[float],
        timestamp_str: Optional[str]
    ) -> str:
        loc_key = self.normalize_location_key(text_loc, lat, lon)
        if loc_key == "unknown":
            return "unknown"

        window_bucket = self.get_time_window_bucket(timestamp_str)
        return f"{loc_key}__win_{window_bucket}"

    def register_report(
        self,
        text_loc: Optional[str],
        lat: Optional[float],
        lon: Optional[float],
        timestamp_str: Optional[str] = None
    ) -> int:
        """
        Registers a report and returns the count for the SAME location AND SAME time window.
        """
        key = self.get_spatio_temporal_key(text_loc, lat, lon, timestamp_str)
        if key == "unknown":
            return 1

        self.location_window_counts[key] = self.location_window_counts.get(key, 0) + 1
        return self.location_window_counts[key]

    def get_count(
        self,
        text_loc: Optional[str],
        lat: Optional[float],
        lon: Optional[float],
        timestamp_str: Optional[str] = None
    ) -> int:
        key = self.get_spatio_temporal_key(text_loc, lat, lon, timestamp_str)
        return self.location_window_counts.get(key, 1)

    def build_from_dataframe(self, df: pd.DataFrame, location_col: str = "location", timestamp_col: str = "timestamp"):
        """
        Pre-computes spatio-temporal report counts across a batch dataframe.
        """
        if location_col in df.columns:
            for idx, row in df.iterrows():
                loc_val = str(row[location_col]) if pd.notna(row[location_col]) else None
                ts_val = str(row[timestamp_col]) if timestamp_col in df.columns and pd.notna(row[timestamp_col]) else None
                lat_val = float(row["latitude"]) if "latitude" in df.columns and pd.notna(row["latitude"]) else None
                lon_val = float(row["longitude"]) if "longitude" in df.columns and pd.notna(row["longitude"]) else None

                self.register_report(text_loc=loc_val, lat=lat_val, lon=lon_val, timestamp_str=ts_val)
