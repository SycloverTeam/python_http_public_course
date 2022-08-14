import _path
import json
import unittest
import request


class TestAnalysis(unittest.TestCase):
    def test_post_json(self):
        raw_data = b"""
POST /post HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 0\r
Content-Type: application/json; charset=utf-8\r
Host: httpbin.org\r
\r
{
    "glossary": {
        "title": "example glossary",
        "GlossDiv": {
            "title": "S",
            "GlossList": {
                "GlossEntry": {
                    "ID": "SGML",
                    "SortAs": "SGML",
                    "GlossTerm": "Standard Generalized Markup Language",
                    "Acronym": "SGML",
                    "Abbrev": "ISO 8879:1986",
                    "GlossDef": {
                        "para": "A meta-markup language, used to create markup languages such as DocBook.",
                        "GlossSeeAlso": ["GML", "XML"]
                    },
                    "GlossSee": "markup"
                }
            }
        }
    }
}
""".lstrip()
        req: request.PreparedRequest = request.analysis_request(raw_data)
        json_data = {
            "glossary": {
                "title": "example glossary",
                "GlossDiv": {
                    "title": "S",
                    "GlossList": {
                        "GlossEntry": {
                            "ID": "SGML",
                            "SortAs": "SGML",
                            "GlossTerm": "Standard Generalized Markup Language",
                            "Acronym": "SGML",
                            "Abbrev": "ISO 8879:1986",
                            "GlossDef": {
                                "para": "A meta-markup language, used to create markup languages such as DocBook.",
                                "GlossSeeAlso": ["GML", "XML"]
                            },
                            "GlossSee": "markup"
                        }
                    }
                }
            }
        }

        self.assertIsInstance(req, request.PreparedRequest)
        self.assertEqual(req.method, "POST")
        self.assertIn(
            req.url, {"http://httpbin.org:80/post", "http://httpbin.org/post"})
        self.assertEqual(req.http_version, "HTTP/1.1")
        self.assertDictEqual(req.params, dict())
        self.assertDictEqual(
            req.headers, {"UserAgent": "syclover", "Host": "httpbin.org", "Content-Length": "705", "Content-Type": "application/json; charset=utf-8"})
        self.assertDictEqual(req.cookies, dict())
        self.assertEqual(json.loads(req.body), json_data)

    def test_post_json_with_error1(self):
        raw_data = b"""
POST /post HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 0\r
Content-Type: application/json; charset=utf-8\r
Host: httpbin.org\r
\r
{"a": 1, "b": 2
""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)

    def test_post_json_with_error2(self):
        raw_data = b"""
POST /post HTTP/1.1\r
UserAgent: syclover\r
Content-Length: 0\r
Content-Type: application/json; charset=utf-8\r
Host: httpbin.org\r
\r
{'a': 1, "b": 2}
""".lstrip()
        with self.assertRaises(request.AnalysisError):
            request.analysis_request(raw_data)


if __name__ == "__main__":
    unittest.main()
