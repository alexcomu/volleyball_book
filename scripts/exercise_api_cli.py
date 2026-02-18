#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, cast


def _request(
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    query: dict[str, str] | None = None,
) -> int:
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    url = f"{base_url}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"

    body = None
    headers: dict[str, str] = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url=url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request) as response:
            content = response.read().decode("utf-8")
            if content:
                print(content)
            else:
                print(f"HTTP {response.status}")
            return 0
    except urllib.error.HTTPError as error:
        print(error.read().decode("utf-8"), file=sys.stderr)
        return error.code
    except urllib.error.URLError as error:
        print(str(error), file=sys.stderr)
        return 1


def _parse_json_list(raw: str | None) -> list[str] | None:
    if raw is None:
        return None
    parsed = json.loads(raw)
    is_string_list = isinstance(parsed, list) and all(
        isinstance(item, str) for item in parsed
    )
    if not is_string_list:
        raise ValueError("Expected JSON array of strings.")
    return cast(list[str], parsed)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Exercise API CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create an exercise")
    create.add_argument("--name", default="Serve Receive Drill")
    create.add_argument("--description", default="Three pass receive rotation")
    create.add_argument("--tags", default='["serve-receive","team"]')
    create.add_argument("--categories", default='["ricezione","difesa"]')

    list_cmd = subparsers.add_parser("list", help="List exercises")
    list_cmd.add_argument("--include-inactive", action="store_true")

    get_cmd = subparsers.add_parser("get", help="Get exercise by id")
    get_cmd.add_argument("id")

    update = subparsers.add_parser("update", help="Patch exercise fields")
    update.add_argument("id")
    update.add_argument("--name")
    update.add_argument("--description")
    update.add_argument("--tags")
    update.add_argument("--categories")

    delete = subparsers.add_parser("delete", help="Soft delete exercise")
    delete.add_argument("id")

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "create":
        payload = {
            "name": args.name,
            "description": args.description,
            "tags": _parse_json_list(args.tags) or [],
            "categories": _parse_json_list(args.categories) or [],
        }
        return _request("POST", "/api/v1/exercises", payload=payload)

    if args.command == "list":
        query = {"include_inactive": "true"} if args.include_inactive else None
        return _request("GET", "/api/v1/exercises", query=query)

    if args.command == "get":
        return _request("GET", f"/api/v1/exercises/{args.id}")

    if args.command == "update":
        update_payload: dict[str, Any] = {}
        if args.name is not None:
            update_payload["name"] = args.name
        if args.description is not None:
            update_payload["description"] = args.description
        if args.tags is not None:
            update_payload["tags"] = _parse_json_list(args.tags)
        if args.categories is not None:
            update_payload["categories"] = _parse_json_list(args.categories)
        return _request(
            "PATCH",
            f"/api/v1/exercises/{args.id}",
            payload=update_payload,
        )

    if args.command == "delete":
        return _request("DELETE", f"/api/v1/exercises/{args.id}")

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
