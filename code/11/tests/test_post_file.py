import _path
import unittest
import request


class TestAnalysis(unittest.TestCase):
    def test_post_file(self):
        raw_data = b"""
POST /post HTTP/1.1\r
Content-Length: 146\r
Content-Type: multipart/form-data; boundary=c658d3db6b6b409a9a8d33bae8a49e87\r
Host: httpbin.org\r
\r
--c658d3db6b6b409a9a8d33bae8a49e87\r
Content-Disposition: form-data; name="a"; filename="flag"\r
\r
flag{123}\r
\r
--c658d3db6b6b409a9a8d33bae8a49e87--""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post", "http://httpbin.org/post"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"Host": "httpbin.org", "Content-Length": "146", "Content-Type": "multipart/form-data; boundary=c658d3db6b6b409a9a8d33bae8a49e87"})
        self.assertDictEqual(req.cookies, dict())
        self.assertEqual(not req.files, False)
        self.assertEqual(len(req.files), 1)
        files = req.files
        f = files[0]
        self.assertEqual(f.name, "a")
        self.assertEqual(f.filename, "flag")
        self.assertEqual(not f.content_type, True)
        self.assertEqual(f.data, b"flag{123}")

    def test_post_two_file(self):
        raw_data = b"""
POST /post HTTP/1.1\r
Content-Length: 257\r
Content-Type: multipart/form-data; boundary=434465de6b414a7d94485882f3796367\r
Host: httpbin.org\r
\r
--434465de6b414a7d94485882f3796367\r
Content-Disposition: form-data; name="a"; filename="flag"\r
\r
flag{123}\r
\r
--434465de6b414a7d94485882f3796367\r
Content-Disposition: form-data; name="b"; filename="flag2"\r
\r
flag{456}\r
\r
--434465de6b414a7d94485882f3796367--""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post", "http://httpbin.org/post"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"Host": "httpbin.org", "Content-Length": "257", "Content-Type": "multipart/form-data; boundary=434465de6b414a7d94485882f3796367"})
        self.assertDictEqual(req.cookies, dict())
        self.assertEqual(not req.files, False)
        self.assertEqual(len(req.files), 2)
        files = req.files
        f = files[0]
        self.assertEqual(f.name, "a")
        self.assertEqual(f.filename, "flag")
        self.assertEqual(not f.content_type, True)
        self.assertEqual(f.data, b"flag{123}")
        f = files[1]
        self.assertEqual(f.name, "b")
        self.assertEqual(f.filename, "flag2")
        self.assertEqual(not f.content_type, True)
        self.assertEqual(f.data, b"flag{456}")

    def test_post_file_with_cool_boundary(self):
        raw_data = b"""
POST /post HTTP/1.1\r
Content-Length: 108\r
Content-Type: multipart/form-data; boundary="cool boundary"\r
Host: httpbin.org\r
\r
--cool boundary\r
Content-Disposition: form-data; name="a"; filename="flag"\r
\r
flag{123}\r
\r
--cool boundary--""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post", "http://httpbin.org/post"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"Host": "httpbin.org", "Content-Length": "108", "Content-Type": 'multipart/form-data; boundary="cool boundary"'})
        self.assertDictEqual(req.cookies, dict())
        self.assertEqual(not req.files, False)
        self.assertEqual(len(req.files), 1)
        files = req.files
        f = files[0]
        self.assertEqual(f.name, "a")
        self.assertEqual(f.filename, "flag")
        self.assertEqual(not f.content_type, True)
        self.assertEqual(f.data, b"flag{123}")

    def test_post_file_with_error1(self):
        raw_data = b"""
POST /post HTTP/1.1\r
Content-Length: 255\r
Content-Type: multipart/form-data; boundary=434465de6b414a7d94485882f3796367\r
Host: httpbin.org\r
\r
--434465de6b414a7d94485882f3796367\r
Content-Disposition: form-data; name="a"; filename="flag"\r
\r
flag{123}\r
\r
--434465de6b414a7d94485882f3796367\r
Content-Disposition: form-data; name="b"; filename="flag2"\r
\r
flag{456}\r
\r
--434465de6b414a7d94485882f3796367""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)

    def test_post_file_with_error2(self):
        raw_data = b"""
POST /post HTTP/1.1\r
Content-Length: 255\r
Content-Type: multipart/form-data; boundary=434465de6b414a7d94485882f3796367\r
Host: httpbin.org\r
\r
--434465de6b414a7d94485882f3796367\r
Content-Disposition: form-data; name="a"; filename="flag"\r
flag{123}\r
\r
--434465de6b414a7d94485882f3796367\r
Content-Disposition: form-data; name="b"; filename="flag2"\r
\r
flag{456}\r
\r
--434465de6b414a7d94485882f3796367--""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)

    def test_post_file_with_error3(self):
        raw_data = b"""
POST /post HTTP/1.1\r
Content-Length: 255\r
Content-Type: multipart/form-data; boundary=434465de6b414a7d94485882f3796367\r
Host: httpbin.org\r
\r
--434465de6b414a7d94485882f3796367\r
Content-Disposition: form-data; name="a"; filename="flag"\r
\r
flag{123}\r
--434465de6b414a7d94485882f3796367\r
Content-Disposition: form-data; name="b"; filename="flag2"\r
\r
flag{456}\r
\r
--434465de6b414a7d94485882f3796367--""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)

    def test_post_file_with_error4(self):  # long boundary
        raw_data = b"""
POST /post HTTP/1.1\r
Content-Length: 255\r
Content-Type: multipart/form-data; boundary=ahpj7vttnbf9s2f2d3wvx0rml4lf8byu2i4uh2985sajq2skiutjp7mhw9jhb3lqfzin298ubtlwih19\r
Host: httpbin.org\r
\r
--ahpj7vttnbf9s2f2d3wvx0rml4lf8byu2i4uh2985sajq2skiutjp7mhw9jhb3lqfzin298ubtlwih19\r
Content-Disposition: form-data; name="a"; filename="flag"\r
\r
flag{123}\r
\r
--ahpj7vttnbf9s2f2d3wvx0rml4lf8byu2i4uh2985sajq2skiutjp7mhw9jhb3lqfzin298ubtlwih19\r
Content-Disposition: form-data; name="b"; filename="flag2"\r
\r
flag{456}\r
\r
--ahpj7vttnbf9s2f2d3wvx0rml4lf8byu2i4uh2985sajq2skiutjp7mhw9jhb3lqfzin298ubtlwih19--""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)


if __name__ == "__main__":
    unittest.main()
