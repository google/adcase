# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Get builder form, depending on format.

Returns:
  Json containing an html

  Args:
    fmt: format name to return. i.e. "html5"
"""
import os
from lib.adcase import helper as f


def run(fmt):
  """Module entry point.

  Args:
    fmt: format to return

  Returns:
    Json containing an html
  """
  current_path = os.path.dirname(__file__)
  format_id = fmt.split("-")[0]
  header = f.file_get_contents(current_path + "/../../tpl/header.html")
  header = header.replace("[format_id]", format_id)

  ## get all enabled formats START
  formats = [{
      "format_id": "100",
      "name": "html5",
      "title": "100 - HTML5"
  }, {
      "format_id": "111",
      "name": "html5-tag",
      "title": "111 - HTML5 external tag"
  }, {
      "format_id": "101",
      "name": "push",
      "title": "101 - Push"
  }, {
      "format_id": "102",
      "name": "push-tag",
      "title": "102 - Push-tag"
  }, {
      "format_id": "103",
      "name": "interstitial",
      "title": "103 - Interstitial"
  }, {
      "format_id": "104",
      "name": "interstitial-tag",
      "title": "104 - Interstitial Tag"
  }, {
      "format_id": "105",
      "name": "videobanner",
      "title": "105 - Videobanner"
  }, {
      "format_id": "108",
      "name": "footer",
      "title": "108 - Footer"
  }, {
      "format_id": "109",
      "name": "footer-expand",
      "title": "109 - Footer expand"
  }, {
      "format_id": "112",
      "name": "interstitial-video",
      "title": "112 - Interstitial video"
  }, {
      "format_id": "115",
      "name": "double-top-sticky",
      "title": "115 - Double top sticky"
  }, {
      "format_id": "117",
      "name": "push-onclick",
      "title": "117 - Push onclick"
  }, {
      "format_id": "119",
      "name": "footer-to-interstitial",
      "title": "119 - Footer to interstitial"
  }, {
      "format_id": "124",
      "name": "tab-to-interstitial",
      "title": "124 - Tab to interstitial"
  }]

  menu = ""
  for row in formats:
    if str(format_id) == str(row["format_id"]):
      header = header.replace("[title]", row["title"])
      header = header.replace("[fmt]", fmt)

    menu += ("<li onclick='w.go(`" + str(row["format_id"]) + "-" + row["name"] +
             "`)' " + "id='" + str(row["format_id"]) + "-" + row["name"] +
             "'>" + row["title"] + "</li>")
  header = header.replace("[menu]", menu)

  current_path = os.path.dirname(__file__)

  form_file = (current_path + "/formats/format_" + fmt + "/form_" + fmt +
                             ".html")
  print(form_file)
  form = f.file_get_contents(form_file)


  footer = f.file_get_contents(current_path + "/../../tpl/footer.html")

  return header + form + footer
