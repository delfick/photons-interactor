from whirlwind.request_handlers.base import Simple

import time

favicon = """
AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAABILAAASCwAAAAAAAAAAA
ACsj+j/XSTR/2Uv1P9kLdP/ZC3T/2Qt0/9kLdP/ZC3T/2Qt0/9kLdP/ZC3T/2Qt0/9kLdP/ZS/U/10k0v
+ad+P/YjLT/zUAxv89Asn/PADI/zwAyP88AMj/PADI/zwAyP88AMj/PADI/zwAyP88AMj/PADI/z0Cyf8
2AMf/Xi3S/2Qv1P89AMn/RAPL/0MCyv9DAsr/QwLK/0MCyv9DAsr/QwLK/0MCyv9DAsr/QwLK/0MCyv9E
A8v/PQDJ/2Uv1P9kLtP/PADI/0MCyv9CAMr/QgDK/0IAyv9CAMr/QgDK/0IAyv9CAMr/QgDK/0IAyv9CA
Mr/QwLK/zwAyP9kLdP/ZC3T/zwAyP9DAsr/QgDK/0IAyv9CAMr/QgDK/0IAyv9CAMr/QgDK/0IAyv9CAM
r/QgDK/0MCyv88AMj/ZC3T/2Qt0/88AMj/QwLK/0IAyv9CAMr/QgDK/0IAyv9CAMr/QgDK/0IAyv9CAMr
/QgDK/0IAyv9DAsr/PADI/2Qt0/9kLdP/PADI/0MCyv9CAMr/QgDK/0IAyv9CAMr/QgDK/0IAyv9CAMr/
QgDK/0IAyv9CAMr/QwLK/zwAyP9kLdP/ZC3T/zwAyP9DAsr/QgDK/0IAyv9CAMr/QgDK/0IAyv9CAMr/Q
gDK/0IAyv9CAMr/QgDK/0MCyv88AMj/ZC3T/2Qt0/88AMj/QwLK/0IAyv9CAMr/QgDK/0IAyv9CAMr/Qg
DK/0IAyv9CAMr/QgDK/0IAyv9DAsr/PADI/2Qt0/9kLdP/PADI/0MCyv9CAMr/QgDK/0IAyv9CAMr/QgD
K/0IAyv9CAMr/QgDK/0IAyv9CAMr/QwLK/zwAyP9kLdP/ZC3T/zwAyP9DAsr/QgDK/0IAyv9CAMr/QgDK
/0IAyv9CAMr/QgDK/0IAyv9CAMr/QgDK/0MCyv88AMj/ZC3T/2Qt0/88AMj/QwLK/0IAyv9CAMr/QgDK/
0IAyv9CAMr/QgDK/0IAyv9CAMr/QgDK/0IAyv9DAsr/PADI/2Qt0/9kLtT/PADI/0MCyv9CAMr/QgDK/0
IAyv9CAMr/QgDK/0IAyv9CAMr/QgDK/0IAyv9CAMr/QwLK/zwAyP9kLdP/ZC/T/z4Ayf9EA8v/QwLK/0M
Cyv9DAsr/QwLK/0MCyv9DAsr/QwLK/0MCyv9DAsr/QwLK/0QDy/89AMn/ZS/U/2Q10/80AMb/PgLJ/zwA
yP88AMj/PADI/zwAyP88AMj/PADI/zwAyP88AMj/PADI/zwAyP89Asn/NQDG/14u0v+8pOz/YyzT/2Qu0
/9kLtT/ZC3T/2Qt0/9kLdP/ZC3T/2Qt0/9kLdP/ZC3T/2Qt0/9kLtP/ZC7U/2Eq0/+rjuj/AAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==
""".replace(
    "\n", ""
).strip()

template = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Photons Interactor</title>
    <link rel="icon" type="image/x-icon" href="data:image/x-icon;base64,{favicon}">
    <link rel="stylesheet" type="text/css" href="/static/main.css?{timestamp}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
  </head>

  <body>
    <div id="page"></div>

    <script src="/static/vendors~main.app.js?{timestamp}"></script>
    <script src="/static/app.js?{timestamp}"></script>

    <script>
        ReactDOM.render(Page, document.getElementById("page"));
    </script>
  </body>
</html>
""".strip()


class Index(Simple):
    def initialize(self):
        self.timestamp = time.time()

    async def do_get(self):
        return template.format(favicon=favicon, timestamp=self.timestamp)
