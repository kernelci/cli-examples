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

import argparse
import datetime
import requests

from urlparse import urljoin

BACKEND_URL = "https://api.kernelci.org"
HEADER_FMT = "{:^24s} {:^24} {:^20} {:^12}".format(
    "ID", "Date", "Name", "Status")
TEST_CASE_FMT = "{:<24s} {:^24} {:<20} {:^12}"


def main(args):
    headers = {
        "Authorization": args.token
    }

    params = {
        "limit": args.limit,
        "name": args.name,
        "sort": "created_on",
        "sort_order": -1,
    }

    url = urljoin(BACKEND_URL, "/test/suite")
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        results = response.json()["result"]

        if len(results) > 0:
            for res in results:
                test_suite_id = res["_id"]["$oid"]

                print "Test results for test suite id: {}\n".format(
                    test_suite_id)

                url = urljoin(BACKEND_URL, "/test/case")
                params = {
                    "test_suite_id": test_suite_id
                }
                response = requests.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    print HEADER_FMT
                    print "-" * 80

                    test_cases = response.json()["result"]
                    for case in test_cases:
                        created = case["created_on"]["$date"]
                        created = \
                            datetime.datetime.utcfromtimestamp(created / 1000)

                        print TEST_CASE_FMT.format(
                            case["_id"]["$oid"],
                            created.isoformat(),
                            case["name"],
                            case["status"]
                        )
                else:
                    print "Error getting test cases"

                print "=" * 80
                print "\n"
        else:
            print "No results found"
    else:
        print "Error: {}".format(response.status_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--token", required=True, help="The API token to use")
    parser.add_argument(
        "-n", "--name", required=True, help="The name of the test suite")
    parser.add_argument(
        "-l", "--limit",
        type=int, default=5, help="How many test suite results to retrieve")

    main(parser.parse_args())
