import json
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener

MODELO = "Qwen2.5-0.5B-Instruct Q4_K_M"
REVISAO = "9217f5db79a29953eb74d5343926648285ec7e67"


class ClienteLocal:
    def __init__(self, timeout=25):
        self.timeout = timeout
        self.opener = build_opener(ProxyHandler({}))

    def inferir(self, system, data, schema):
        body = {
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": json.dumps(data, ensure_ascii=False)}],
            "temperature": 0, "seed": 42, "max_tokens": 340,
            "response_format": {"type": "json_schema", "json_schema": {
                "name": "decisao", "strict": True, "schema": schema}},
        }
        request = Request("http://127.0.0.1:18081/v1/chat/completions",
                          data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                return json.load(response)["choices"][0]["message"]["content"]
        except (URLError, OSError, ValueError, KeyError, IndexError, TypeError) as error:
            raise RuntimeError("Falha de inferência local") from error
