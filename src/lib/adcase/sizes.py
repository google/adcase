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
"""User creatives sizes helper."""
from flask import jsonify
from lib.adcase import db
from lib.adcase import helper as f


def run(req):
  """frontend for sizes module.

  Args:
    req: flask request

  Returns:
    details from each function
  """
  if not req.values.get("format_id"):
    out = get_user_sizes(req)
  else:
    out = save_user_sizes(req)
  return jsonify(out)


def save_user_sizes(req):
  """Saves user sizes in DB.

  Args:
    req: flask request

  Returns:
    updated user sizes
  """
  user_id = f.get_user_id(req)
  format_id = req.values.get("format_id")
  field_name = req.values.get("field_name")
  values = req.values.get("values")

  exists_sql = db.res(
      "select 1 from sizes where user_id= %s and format_id = "
      "%s and field_name = %s", (user_id, format_id, field_name))
  if exists_sql:
    db.query(
        "UPDATE sizes set data_values = %s where user_id = %s and "
        "format_id = %s and field_name = %s",
        (values.strip(), user_id, format_id, field_name))
  else:
    db.query(
        "INSERT into sizes set data_values=%s, user_id=%s, format_id = "
        "%s, field_name = %s", (values.strip(), user_id, format_id, field_name))

  return get_user_sizes(req)


def get_user_sizes(req):
  """Reads user sizes from DB.

  Args:
    req: flask request

  Returns:
    object with all user sizes from DB
  """
  user_id = f.get_user_id(req)
  sizes = {}
  rows = db.full_res("select format_id, field_name, data_values from sizes "
                     "where user_id is null")
  for row in rows:
    sizes[str(row["format_id"]) + "-" +
          str(row["field_name"])] = row["data_values"].strip()

  rows = db.full_res(
      "select format_id, field_name, data_values "
      "from sizes where user_id=%s", (user_id))
  for row in rows:
    sizes[str(row["format_id"]) + "-" +
          str(row["field_name"])] = row["data_values"].strip()

  return {"sizes": sizes}
