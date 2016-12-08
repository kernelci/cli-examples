#!/usr/bin/python
#
# cli-examples
# Copyright (C) 2016 Linaro Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Get all test cases data for a specified test suite name."""

from __future__ import print_function

import argparse
import datetime
import requests

from urlparse import urljoin

BACKEND_URL = "https://api.kernelci.org"
HEADER_FMT = "{:^24s} {:^24} {:^24} {:^6}".format(
    "ID", "Date", "Name", "Status")
TEST_CASE_FMT = "{:<24s} {:^24} {:<24} {:^6}"


def main(args):
    headers = {
        "Authorization": args.token
    }

    params = {
        "sort": "created_on",
        "sort_order": -1,
    }

    if args.limit != "all":
        params["limit"] = args.limit
    if args.name:
        params["name"] = args.name
    if args.board:
        params["board"] = args.name
    if args.defconfig:
        params["defconfig_full"] = args.defconfig
    if args.tree:
        params["job"] = args.tree
    if args.kernel:
        params["kernel"] = args.kernel

    url = urljoin(BACKEND_URL, "/test/suite")
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        results = response.json()["result"]

        if len(results) > 0:
            for res in results:
                test_suite_id = res["_id"]["$oid"]

                print("Test results for test suite: {}\n".format(res["name"]))
                print("    ID       : {}".format(test_suite_id))
                print("    Lab name : {}".format(res["lab_name"]))
                print("    Board    : {}".format(res["board"]))
                print("    Arch     : {}".format(res["arch"]))
                print("    Tree     : {}".format(res["job"]))
                print("    Kernel   : {}".format(res["kernel"]))
                print("    Defconfig: {}".format(res["defconfig_full"]))
                print("")

                url = urljoin(BACKEND_URL, "/test/case")
                params = {
                    "test_suite_id": test_suite_id
                }
                response = requests.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    print(HEADER_FMT)
                    print("-" * 80)

                    test_cases = response.json()["result"]
                    for case in test_cases:
                        created = case["created_on"]["$date"]
                        created = \
                            datetime.datetime.utcfromtimestamp(created / 1000)

                        print(TEST_CASE_FMT.format(
                            case["_id"]["$oid"],
                            created.isoformat(),
                            case["name"][0:22],
                            case["status"]
                        ))
                else:
                    print("Error getting test cases")

                print("=" * 80)
                print("\n")
        else:
            print("No results found")
    else:
        print("Error: {}".format(response.status_code))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--token", required=True, help="The API token to use")
    parser.add_argument("-n", "--name", help="The name of the test suite")
    parser.add_argument("-r", "--tree", help="The name of the tree/job")
    parser.add_argument("-k", "--kernel", help="The kernel version")
    parser.add_argument("-d", "--defconfig", help="The name of the defconfig")
    parser.add_argument("-b", "--board", help="The name of the board")
    parser.add_argument(
        "-l", "--limit",
        default=5,
        help=(
            "How many test suite results to retrieve, use \"all\" to "
            "retrieve all of them"
        )
    )

    main(parser.parse_args())
