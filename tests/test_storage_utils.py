"""Test the write utilities for both localfilesystem and S3."""
from unittest import TestCase
from unittest import mock
from utils.storage_utils import write_output_csv
import pandas as pd
import arrow
import os


def to_mock_csv(*args, **kwargs):
    """A placeholder to mock the .to_csv() call of a dataframe."""
    return args, kwargs


def do_nothing(*args, **kwargs):
    """A placeholder for a no action."""
    pass


class TestStorageUtils(TestCase):
    """Test the storage utils functions."""

    @mock.patch("pandas.DataFrame.to_csv")
    @mock.patch("os.makedirs")
    def test_write_output_csv(self, do_nothing, to_mock_csv):
        df = pd.read_csv("tests/test_data/test_triage_results.csv")
        os.environ["BASE_TRIAGE_DIR"] = "test"

        # Check if mocks are setup properly.
        assert pd.DataFrame.to_csv is to_mock_csv
        assert os.makedirs is do_nothing

        start = arrow.now()
        end = arrow.now().shift(days=-7)

        df = write_output_csv(start, end, "bert_torch", "knative", df, False)
        # Check if CSV local creation happens normally.
        to_mock_csv.assert_called_with(
            "test/{}-{}/bert_model_inference_probable_cves_{}-{}_knative.csv".format(
                start.format("YYYYMMDD"),
                end.format("YYYYMMDD"),
                start.format("YYYYMMDD"),
                end.format("YYYYMMDD"),
            ),
            index=False,
        )

        # Check if the list of columns of CSV is properly filtered.
        self.assertSetEqual(
            set(df.columns.to_list()),
            {
                "repo_name",
                "event_type",
                "status",
                "url",
                "security_model_flag",
                "cve_model_flag",
                "triage_feedback_comments",
                "id",
                "number",
                "api_url",
                "created_at",
                "updated_at",
                "closed_at",
                "creator_name",
                "creator_url",
                "ecosystem",
            },
        )

        # Check if ecosystem is properly set.
        self.assertListEqual(df["ecosystem"].unique().tolist(), ["knative"])
