import httpx as httpx
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

app = FastAPI()
client = httpx.AsyncClient(base_url="https://news.ycombinator.com/")


@app.api_route("/{path_name:path}", methods=["GET"])
async def perform_proxy(request: Request):
    proxy = await client.get(
        httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    )
    # js script that adds tm mark to every word of 6 characters.
    script = bytes(
        r"""<script>
    function replaceInText(element, pattern, replacement) {
        for (let node of element.childNodes) {
            switch (node.nodeType) {
                case Node.ELEMENT_NODE:
                    replaceInText(node, pattern, replacement);
                    break;
                case Node.TEXT_NODE:
                    node.textContent = node.textContent.replace(pattern, replacement);
                    break;
                case Node.DOCUMENT_NODE:
                    replaceInText(node, pattern, replacement);
            }
        }
    }
    replaceInText(document.body, /(?!\/)\b[a-zA-Z]{6}\b(?!\/)/g, matched => matched + "\u2122")
    </script>""",
        "utf-8",
    )
    if "text/html" in proxy.headers["content-type"]:
        # add this script to the bottom of the page.
        idx = proxy.content.index(b"</html>")
        content = proxy.content[:idx] + script + proxy.content[idx:]
    else:
        content = proxy.content
    return Response(
        content, proxy.status_code, {"content-type": proxy.headers["Content-Type"]}
    )
