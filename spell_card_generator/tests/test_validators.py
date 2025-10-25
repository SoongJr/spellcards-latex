"""Tests for spell_card_generator.utils.validators module."""

# pylint: disable=duplicate-code

import pytest

from spell_card_generator.utils.validators import Validators


@pytest.mark.unit
class TestValidators:
    """Test cases for Validators class."""

    def test_validate_class_name_valid(self):
        """Test validation of valid character class names."""
        assert Validators.validate_class_name("sor")  # sorcerer
        assert Validators.validate_class_name("wiz")  # wizard
        assert Validators.validate_class_name("cleric")
        assert Validators.validate_class_name("druid")

    def test_validate_class_name_invalid(self):
        """Test validation of invalid character class names."""
        assert not Validators.validate_class_name("invalid_class")
        assert not Validators.validate_class_name("")
        assert not Validators.validate_class_name("123")

    def test_validate_spell_level_valid(self):
        """Test validation of valid spell levels."""
        assert Validators.validate_spell_level("0")
        assert Validators.validate_spell_level("1")
        assert Validators.validate_spell_level("5")
        assert Validators.validate_spell_level("9")
        assert Validators.validate_spell_level("All")

    def test_validate_spell_level_invalid(self):
        """Test validation of invalid spell levels."""
        assert not Validators.validate_spell_level("10")
        assert not Validators.validate_spell_level("-1")
        assert not Validators.validate_spell_level("abc")
        assert not Validators.validate_spell_level("")

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        assert Validators.sanitize_filename("test.txt") == "test.txt"
        assert Validators.sanitize_filename("my file.txt") == "my file.txt"

    def test_sanitize_filename_problematic_chars(self):
        """Test sanitization of problematic characters."""
        assert Validators.sanitize_filename("file<name>.txt") == "file-name-.txt"
        assert Validators.sanitize_filename('file:name"test') == "file-name-test"
        assert Validators.sanitize_filename("file/path\\test") == "file-path-test"
        assert Validators.sanitize_filename("file|name?test*") == "file-name-test"

    def test_sanitize_filename_multiple_dashes(self):
        """Test that multiple consecutive dashes are collapsed."""
        assert Validators.sanitize_filename("file---name") == "file-name"
        assert Validators.sanitize_filename("a--b--c") == "a-b-c"

    def test_sanitize_filename_leading_trailing_dashes(self):
        """Test removal of leading and trailing dashes."""
        assert Validators.sanitize_filename("-filename-") == "filename"
        assert Validators.sanitize_filename("---test---") == "test"

    def test_sanitize_filename_whitespace(self):
        """Test handling of leading and trailing whitespace."""
        assert Validators.sanitize_filename("  filename  ") == "filename"
        assert Validators.sanitize_filename(" - test - ") == "test"

    def test_sanitize_filename_complex(self):
        """Test complex filename sanitization."""
        result = Validators.sanitize_filename('  My <File>: "Test" | Name.txt  ')
        assert result == "My -File- -Test- - Name.txt"

    def test_validate_url_valid_http(self):
        """Test validation of valid HTTP URLs."""
        assert Validators.validate_url("http://example.com")
        assert Validators.validate_url("http://www.example.com")
        assert Validators.validate_url("http://example.com/path")
        assert Validators.validate_url("http://example.com:8080")

    def test_validate_url_valid_https(self):
        """Test validation of valid HTTPS URLs."""
        assert Validators.validate_url("https://example.com")
        assert Validators.validate_url("https://www.example.com")
        assert Validators.validate_url("https://example.com/path/to/resource")

    def test_validate_url_valid_with_query(self):
        """Test validation of URLs with query parameters."""
        assert Validators.validate_url("https://example.com/page?param=value")
        assert Validators.validate_url("https://example.com/?q=search&p=1")

    def test_validate_url_valid_localhost(self):
        """Test validation of localhost URLs."""
        assert Validators.validate_url("http://localhost")
        assert Validators.validate_url("http://localhost:3000")
        assert Validators.validate_url("http://localhost/path")

    def test_validate_url_valid_ip(self):
        """Test validation of IP address URLs."""
        assert Validators.validate_url("http://192.168.1.1")
        assert Validators.validate_url("http://127.0.0.1:8080")

    def test_validate_url_invalid(self):
        """Test validation of invalid URLs."""
        assert not Validators.validate_url("not a url")
        assert not Validators.validate_url("ftp://example.com")  # Only http/https
        assert not Validators.validate_url("example.com")  # Missing protocol
        assert not Validators.validate_url("")
        assert not Validators.validate_url("http://")
        assert not Validators.validate_url("https://")

    def test_validate_url_case_insensitive(self):
        """Test that URL validation is case-insensitive."""
        assert Validators.validate_url("HTTP://EXAMPLE.COM")
        assert Validators.validate_url("HtTpS://ExAmPlE.cOm")
