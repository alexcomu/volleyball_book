#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    name = sys.argv[1] if len(sys.argv) > 1 else "Serve Receive Drill"
    description = sys.argv[2] if len(sys.argv) > 2 else "Three pass receive rotation"
    tags_arg = sys.argv[3] if len(sys.argv) > 3 else '["serve-receive","team"]'
    categories_arg = sys.argv[4] if len(sys.argv) > 4 else '["ricezione","difesa"]'
    tags = json.loads(tags_arg)
    categories = json.loads(categories_arg)

    payload = {
        "name": name,
        "description": description,
        "tags": tags,
        "categories": categories,
    }
    body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url=f"{base_url}/api/v1/exercises",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            print(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        print(error.read().decode("utf-8"), file=sys.stderr)
        return error.code
    except urllib.error.URLError as error:
        print(str(error), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
