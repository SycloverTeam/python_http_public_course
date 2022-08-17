import unittest
import socket
from urllib import request
import httpRequest
import io
import sys

def stub_stdout(testcase_inst):
	stderr = sys.stderr
	stdout = sys.stdout

	def cleanup():
		sys.stderr = stderr
		sys.stdout = stdout

	testcase_inst.addCleanup(cleanup)
	sys.stderr = io.StringIO()
	sys.stdout = io.StringIO()

class TestHttpRequest(unittest.TestCase):
    def testPath(self):
        stub_stdout(self)
        httpRequest.httpRequest("http://httpbin.org/cookies")
        self.assertIn("\"cookies\"",sys.stdout.getvalue(),"no cookie")
        stub_stdout(self)
    def testNonePath(self):
        stub_stdout(self)
        httpRequest.httpRequest("http://httpbin.org")
        self.assertIn("200 OK",sys.stdout.getvalue(),"path in none is incorrect")
if __name__=='__main__':
    unittest.main()