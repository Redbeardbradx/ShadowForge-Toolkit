#!/usr/bin/env python3
import unittest
import sys
import subprocess
from src.shadowforge.main import parser  # CLI test

class TestShadowForge(unittest.TestCase):
    def test_help_flag(self):
        result = subprocess.run([sys.executable, '-m', 'src.shadowforge.main', '--help'], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        self.assertIn('usage:', result.stdout)  # No .decode()—str already

    def test_auto_chain(self):
        result = subprocess.run([sys.executable, '-m', 'src.shadowforge.main', 'auto', '--target', 'localhost'], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        self.assertIn('payload', result.stdout)  # Shell JSON tease

    def test_vulns_parse(self):
        result = subprocess.run([sys.executable, '-m', 'src.shadowforge.main', 'vulns', '--target', 'localhost'], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        self.assertIn('cves', result.stdout)  # CVE tease

if __name__ == '__main__':
    unittest.main()