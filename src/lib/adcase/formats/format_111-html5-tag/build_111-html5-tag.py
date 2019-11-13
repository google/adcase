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
"""Executes a build process for a format.
"""
from lib.adcase import helper as f
# pylint: disable=line-too-long


def build(req):
  """Builder for this format.

  Args:
    req: flask request

  Returns:
    Json containing the creative data
  """
  if "ignore" in req.files:
    pass

  errors = []
  v = {}

  # unzip to temp dir
  tdir = "/tmp/" + f.get_tmp_file_name()

  # get index content
  index = """<!DOCTYPE HTML><html lang="en-us">
<head>
  <meta name="ad.size" content="width=[[width]],height=[[height]]">
</head>
<body style='margin:0'>
  [[html_tag]]
  [[clicktag_layer]]
<script>
  var clickTag = "[[clicktag_url]]";
</script>
<script data-exports-type="dclk-quick-preview">if(typeof studio !== 'undefined' && studio.Enabler) { studio.Enabler.setRushSimulatedLocalEvents(true); }</script>
</body>
</html>
   """

  v["html_tag"] = f.get_param("html_tag")

  return {"errors": errors, "dir": tdir, "index": index, "vars": v}

