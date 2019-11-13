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
import os
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
  data = {"collapsed": {}, "expanded": {}}
  tdir = "/tmp/" + f.get_tmp_file_name()

  if f.get_param("expand_action") == "click":
    index = get_html_click()
  else:
    index = get_html_mouseover()

  if "collapsed_zip" not in req.files:
    return {"errors": ["No collapsed file"]}
  if "expanded_zip" not in req.files:
    return {"errors": ["No expanded file"]}

  ## collapsed
  data["collapsed"]["ext"] = f.get_ext(req.files["collapsed_zip"].filename)
  if data["collapsed"]["ext"] == "zip":
    os.mkdir(tdir)
    if not f.extract_zip(req.files["collapsed_zip"], tdir + "/collapsed"):
      return {"errors": ["Wrong collapsed zip file"]}

    file_name = "index2.html"
    try:
      os.rename(tdir + "/collapsed/index.html", tdir+ "/collapsed/" + file_name)
    except os.FileNotFoundError:
      return {"errors": ["No index.html in collapsed zip"]}
  elif not data["collapsed"]["ext"]:
    return {"errors": ["No collapsed file"]}
  else:
    f.save_file(req.files["collapsed_zip"], tdir + "/collapsed." + data["collapsed"]["ext"])

  ## expanded
  data["expanded"]["ext"] = f.get_ext(req.files["expanded_zip"].filename)
  if data["expanded"]["ext"] == "zip":
    if not f.extract_zip(req.files["expanded_zip"], tdir + "/expanded"):
      return {"errors": ["Wrong expanded zip file"]}

    file_name = "index2.html"
    try:
      os.rename(tdir + "/expanded/index.html", tdir + "/expanded/" + file_name)
    except os.FileNotFoundError:
      return {"errors": ["No index.html in expanded zip"]}
  elif not data["expanded"]["ext"]:
    return {"errors": ["No expanded file"]}
  else:
    f.save_file(req.files["expanded_zip"], tdir + "/expanded." + data["expanded"]["ext"])

  v["expandMS"] = str(f.get_int_param("expand_seconds") * 1000)
  v["width"] = f.get_param("width")
  v["collapsedHeight"] = f.get_param("collapsed_height")
  v["expandedHeight"] = f.get_param("expanded_height")
  v["height"] = v["expandedHeight"]
  v["backgroundColor"] = f.get_param("background_color")
  v["transitionTimeMs"] = str(f.get_int_param("animated_transition") * 250)

  if data["collapsed"]["ext"] == "zip":
    v["collapsedContent"] = "<iframe src='collapsed/index2.html' frameborder=0 style='width:"+v["width"]+"px;height:"+v["collapsedHeight"]+"px' scrolling='no'></iframe>"
  else:
    v["collapsedContent"] = "<img src='collapsed."+data["collapsed"]["ext"]+"' style='border:0;width:"+v["width"]+"px;height:"+v["collapsedHeight"]+"px' />"

  v["expandedURL"] = ""
  if data["expanded"]["ext"] == "zip":
    v["expandedURL"] = "expanded/index2.html"
  else:
    v["expandedImage"] = "expanded."+data["expanded"]["ext"]

  return {"errors": errors, "dir": tdir, "index": index, "vars": v}


def get_html_click():
  """Builder for this format.

  Returns:
    Json containing the creative data
  """

  return """<!DOCTYPE HTML><html lang="en-us">
<head>
  <meta name="ad.size" content="width=[[width]],height=[[expandedHeight]]">
<script>

var clickTag = "[[clicktag_url]]";
var tpl = { expanded: false };

tpl.receiveMessage = function(e) {

    if(e.data && e.data.collapse) {
      tpl.changeSize(false);

    } else if(e.data && e.data.expand) {
      tpl.changeSize(true);

    }
}

tpl.changeSize = function(expanded) {
    if(expanded) {
        document.getElementById("ad_collapsed") && (document.getElementById("ad_collapsed").style.display = "none");
        document.getElementById("ad_expanded") && (document.getElementById("ad_expanded").style.display = "block");
    } else {
        document.getElementById("ad_collapsed") && (document.getElementById("ad_collapsed").style.display = "block");
        document.getElementById("ad_expanded") && (document.getElementById("ad_expanded").style.display = "none");
    }
}
</script>
</head>
<body style='margin:0;cursor:pointer'>
[[clicktag_layer]]
  <div id='ad_collapsed' style=';width:[[width]]px;height:[[collapsedHeight]]px;overflow:hidden;'>
    [[collapsedContent]]
  </div>
  <div id='ad_expanded' style='display:none;width:[[width]]px;height:[[expandedHeight]]px;overflow:hidden;'>
    [[expandedContent]]
  </div>

<script>

window.addEventListener ? window.addEventListener("message", tpl.receiveMessage, !1)
    : (window.attachEvent && window.attachEvent("message", tpl.receiveMessage));

window.top.postMessage({ msg: "adcase", format:"footerFixed",
    params: { expandOn:"click", collapse:true, expandedHeight: [[expandedHeight]], collapsedHeight: [[collapsedHeight]] } } , "*");

</script>
</body></html>"""


def get_html_mouseover():
  """html content for mouseover mode.

  Returns:
    mouseover html
  """

  return """<!DOCTYPE HTML><html lang="en-us">
<head>
  <meta name="ad.size" content="width=[[width]],height=[[collapsedHeight]]">
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

var tpl = { expanded: false };

var url = document.location.href.substring(0,document.location.href.length-10);
var expandedURL = false;
var expandedImage = false;

if("[[expandedURL]]" != "") {
  expandedURL = url + "[[expandedURL]]";
} else {
  expandedImage = url + "[[expandedImage]]";
}

window.top.postMessage({ msg: "adcase", format:"footerFixed",
    params: { expandOn:'mouseover', expandMS:[[expandMS]],
    expandTo:"layer", expandedURL: expandedURL, expandedImage: expandedImage, backgroundColor: '[[backgroundColor]]',
    collapse:true, expandedHeight: [[expandedHeight]], collapsedHeight: [[collapsedHeight]] } } , "*");

</script>
</head>
<body style='margin:0;cursor:pointer'>
[[clicktag_layer]]
<div id='ad_collapsed' style=';width:[[width]]px;height:[[collapsedHeight]]px;overflow:hidden;'>
  [[collapsedContent]]
</div>
</body></html>"""












