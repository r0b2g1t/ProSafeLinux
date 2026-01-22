#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for ProSafeLinux CLI (Typer implementation)

Uses pytest and typer.testing.CliRunner
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch

from psl_cli_typer import app

runner = CliRunner()


class TestDiscoverCommand:
    """Tests for the discover command."""

    def test_discover_help(self):
        """Test discover command shows help."""
        result = runner.invoke(app, ["discover", "--help"])
        assert result.exit_code == 0
        assert "Search for ProSafe Plus switches" in result.stdout

    @patch("psl_cli_typer.ProSafeLinux")
    def test_discover_no_interface(self, mock_psl_class):
        """Test discover fails gracefully when interface has no address."""
        mock_switch = MagicMock()
        mock_switch.bind.return_value = False
        mock_psl_class.return_value = mock_switch
        
        result = runner.invoke(app, ["discover"])
        assert "Interface has no addresses" in result.stdout

    @patch("psl_cli_typer.ProSafeLinux")
    def test_discover_finds_switches(self, mock_psl_class):
        """Test discover finds switches and prints results."""
        mock_switch = MagicMock()
        mock_switch.bind.return_value = True
        
        mock_entry = MagicMock()
        mock_entry.get_name.return_value = "model"
        mock_switch.discover.return_value = [{mock_entry: "GS108E"}]
        mock_psl_class.return_value = mock_switch
        
        result = runner.invoke(app, ["discover"])
        assert result.exit_code == 0
        assert "Searching for ProSafe Plus Switches" in result.stdout


class TestExploitCommand:
    """Tests for the exploit command."""

    def test_exploit_help(self):
        """Test exploit command shows help."""
        result = runner.invoke(app, ["exploit", "--help"])
        assert result.exit_code == 0
        assert "Set a password without knowing the old one" in result.stdout

    def test_exploit_requires_mac(self):
        """Test exploit requires --mac option."""
        result = runner.invoke(app, ["exploit", "--new-password", "test123"])
        assert result.exit_code != 0

    def test_exploit_requires_new_password(self):
        """Test exploit requires --new-password option."""
        result = runner.invoke(app, ["exploit", "--mac", "AA:BB:CC:DD:EE:FF"])
        assert result.exit_code != 0


class TestQueryCommand:
    """Tests for the query command."""

    def test_query_help(self):
        """Test query command shows help."""
        result = runner.invoke(app, ["query", "--help"])
        assert result.exit_code == 0
        assert "Query values from the switch" in result.stdout

    def test_query_requires_mac(self):
        """Test query requires --mac option."""
        result = runner.invoke(app, ["query", "model"])
        assert result.exit_code != 0

    @patch("psl_cli_typer.ProSafeLinux")
    def test_query_list_options(self, mock_psl_class):
        """Test query list shows available options."""
        mock_switch = MagicMock()
        mock_switch.bind.return_value = True
        
        mock_cmd = MagicMock()
        mock_cmd.get_name.return_value = "model"
        mock_switch.get_query_cmds.return_value = [mock_cmd]
        mock_psl_class.return_value = mock_switch
        
        result = runner.invoke(app, ["query", "--mac", "AA:BB:CC:DD:EE:FF", "list"])
        assert result.exit_code == 0
        assert "Available query options" in result.stdout


class TestQueryRawCommand:
    """Tests for the query_raw command."""

    def test_query_raw_help(self):
        """Test query_raw command shows help."""
        result = runner.invoke(app, ["query-raw", "--help"])
        assert result.exit_code == 0
        assert "Query raw values" in result.stdout

    def test_query_raw_requires_mac(self):
        """Test query_raw requires --mac option."""
        result = runner.invoke(app, ["query-raw"])
        assert result.exit_code != 0


class TestSetCommand:
    """Tests for the set command."""

    def test_set_help(self):
        """Test set command shows help."""
        result = runner.invoke(app, ["set", "--help"])
        assert result.exit_code == 0
        assert "Set values on the switch" in result.stdout

    def test_set_requires_mac(self):
        """Test set requires --mac option."""
        result = runner.invoke(app, ["set", "--passwd", "password"])
        assert result.exit_code != 0

    def test_set_requires_passwd(self):
        """Test set requires --passwd option."""
        result = runner.invoke(app, ["set", "--mac", "AA:BB:CC:DD:EE:FF"])
        assert result.exit_code != 0

    def test_set_shows_options(self):
        """Test set command shows all available options."""
        result = runner.invoke(app, ["set", "--help"])
        assert result.exit_code == 0
        assert "--name" in result.stdout
        assert "--ip" in result.stdout
        assert "--reboot" in result.stdout
        assert "--dhcp" in result.stdout


class TestGlobalOptions:
    """Tests for global CLI options."""

    def test_main_help(self):
        """Test main help shows all commands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "discover" in result.stdout
        assert "exploit" in result.stdout
        assert "query" in result.stdout
        assert "set" in result.stdout

    def test_interface_option(self):
        """Test --interface option is available."""
        result = runner.invoke(app, ["--help"])
        assert "--interface" in result.stdout

    def test_debug_option(self):
        """Test --debug option is available."""
        result = runner.invoke(app, ["--help"])
        assert "--debug" in result.stdout

    def test_timeout_option(self):
        """Test --timeout option is available."""
        result = runner.invoke(app, ["--help"])
        assert "--timeout" in result.stdout


class TestOutputVerification:
    """Tests verifying specific output strings."""

    @patch("psl_cli_typer.ProSafeLinux")
    def test_discover_searching_message(self, mock_psl_class):
        """Test discover shows searching message."""
        mock_switch = MagicMock()
        mock_switch.bind.return_value = True
        mock_switch.discover.return_value = []
        mock_psl_class.return_value = mock_switch
        
        result = runner.invoke(app, ["discover"])
        assert "Searching for ProSafe Plus Switches" in result.stdout

    @patch("psl_cli_typer.ProSafeLinux")
    def test_discover_no_result_message(self, mock_psl_class):
        """Test discover shows no result message when nothing found."""
        mock_switch = MagicMock()
        mock_switch.bind.return_value = True
        mock_switch.discover.return_value = []
        mock_psl_class.return_value = mock_switch
        
        result = runner.invoke(app, ["discover"])
        assert "No result received" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
