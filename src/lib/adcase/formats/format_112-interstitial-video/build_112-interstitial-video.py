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

  errors = []
  v = {}
  tdir = "/tmp/" + f.get_tmp_file_name()
  index = get_html()

  ext = f.get_ext(req.files["videofile"].filename)
  if ext != "mp4":
    return {"errors": ["Only mp4 files allowed"]}

  f.save_file(req.files["videofile"], tdir + "/video.mp4")

  v["backgroundColor"] = f.get_param("background_color")
  v["autoclose"] = str(f.get_int_param("autoclose"))

  return {"errors": errors, "dir": tdir, "index": index, "vars": v}


def get_html():
  """Returns html.

  Returns:
    index.html content
  """

  return """
<!DOCTYPE HTML><html lang="en-us">
<head>
  <meta name="ad.size" content="width=[[width]],height=[[height]]">
</head>
<body style='margin:0'>
<div id = 'video'></div>
<script>
var clickTag = "[[clicktag_url]]";
var ads = { };

ads.receiveMessage = function(e) {
  e.data = e.data || {};
  if(e.data.msg && e.data.action) {
    if(e.data.msg == "adcase" && e.data.action == "click") {
      window.open(clickTag);
    }
  }
}

window.addEventListener ? window.addEventListener("message", ads.receiveMessage, !1)
: (window.attachEvent && window.attachEvent("message", ads.receiveMessage));


var href = document.location.href.replace("index.html","");
var videoURL = href + "video.mp4";
var backgroundImage = ("[[backgroundImage]]"=="" ? false : href+"[[backgroundImage]]");

window.top.postMessage({ msg: "adcase", format:112, version: 4, params: { videoURL: videoURL, width:[[width]],
  backgroundImage: backgroundImage, backgroundColor:"[[backgroundColor]]", autoclose: [[autoclose]] } },"*");


</script>
</body>
</html>"""
