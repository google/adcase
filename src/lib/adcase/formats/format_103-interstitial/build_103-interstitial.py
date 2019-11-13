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
  current_path = os.path.dirname(__file__)

  errors = []
  v = {}
  if "zipfile" not in req.files:
    return {"errors": ["No uploaded file"]}

  zfile = req.files["zipfile"]
  ext = f.get_ext(req.files["zipfile"].filename)

  # unzip to temp dir
  tdir = "/tmp/" + f.get_tmp_file_name()

  if ext == "zip":
    if not f.extract_zip(zfile, tdir):
      return {"errors": ["Incorrect Zip file"]}
    else:
      index = f.file_get_contents(tdir + "/index.html")
      if not index:
        return {"errors": ["No index.html in Zip file"]}

    if index.find("<head>") < 0:
      errors.append("No <head> tag")
    if index.find("</body>") < 0:
      errors.append("No </body> tag")

    index = replace_html(index)

  else:
    index = f.file_get_contents(current_path + "/index_103-interstitial.html")
    f.save_file(req.files["zipfile"], tdir + "/image." + ext)
    v["image_ext"] = ext

  v["autoclose"] = str(f.get_int_param("autoclose"))
  v["close_button"] = f.get_param("close_button")
  v["close_button_width"] = f.get_param("close_button_width")
  v["close_button_height"] = f.get_param("close_button_height")
  v["bgcolor"] = f.get_param("bgcolor")
  v["openTimeout"] = str(f.get_int_param("open_timeout")*1000)

  return {"errors": errors, "dir": tdir, "index": index, "vars": v}


def replace_html(index):
  """Formats html.

  Args:
    index: index html content

  Returns:
    Modified index.html content
  """

  body = """  [[clicktag_layer]]
<script>
  var clickTag = "[[clicktag_url]]";
  console.log("adcase creative '.$folder.'");

  window.top.postMessage( {
    msg: "adcase", format:"interstitial",
    params:{
    backgroundColor: "[[bgcolor]]",
    autoclose: [[autoclose]],
    close_button: "[[close_button]]",
    close_button_width: "[[close_button_width]]",
    close_button_height: "[[close_button_height]]",
    width:[[width]],
    height:[[height]]
     }
   }
     , "*");

window.addEventListener("message", _rm_Message, false);
function _rm_Message(e) {
  if(e.data && e.data.width && e.data.height) {
    document.body.style.width = e.data.width;
    document.body.style.height = e.data.height;
  }
}
</script>
<script data-exports-type="dclk-quick-preview">if(typeof studio !== "undefined" && studio.Enabler) { studio.Enabler.setRushSimulatedLocalEvents(true); }
</script>
</body>"""

  head = "<head><meta name='ad.size' content='width=[[width]],height=[[height]]'>"

  index = index.replace("<meta name=\"ad.size\"", "<meta name=\"old.adsize\"")
  index = index.replace("<head>", head)
  index = index.replace("</body>", body)
  index = index.replace("<meta name=\"GCD\"", "<meta name=\"old.GCD\"")

  return index
