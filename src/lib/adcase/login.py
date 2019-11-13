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
"""Login helper."""
import json
import random
import string
from flask import jsonify
from lib.adcase import db
import requests


def run(req, action):
  """frontend for login module.

  Args:
    req: flask request
    action: action to run

  Returns:
    details from each function
  """
  if action == "register_token":
    out = register_token(req)

  return jsonify(out)


def register_token(req):
  """Register new login token.

  Args:
    req: flask request

  Returns:
    object with logged user data
  """
  import hashlib 
  
  user = do_login(req.args.get("token"))
  if user["logged"]:

    #user["email"] = str(hashlib.md5(user["email"].encode('utf-8')).hexdigest()) 
    #user["name"] = "Logged"
    #ser["full"] = ""

    # save to DB
    n = 256
    user["hash"] = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=n))
    user_id = "0"
    # get user id
    user_id = db.res("SELECT id from users where email=%s", (user["email"]))

    if not user_id:
      db.query(
          "INSERT into users set email=%s,short_name=%s,name=%s,"
          "valid_until='2100-01-01',status=1",
          (user["email"], user["name"], user["full"]))
      user_id = db.res("SELECT id from users where email=%s", (user["email"]))

    # save session
    db.query(
        "INSERT into sessions set email=%s,name=%s,full=%s,"
        "created_date=now(),enabled=1,hash=%s,user_id=%s",
        (user["email"], user["name"], user["full"], user["hash"], user_id))

  return {"user": user}


def do_login(token):
  """Validates login token with oauth server.

  Args:
    token: login sent from frontend

  Returns:
    object with logged user data
  """
  r = requests.get("https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=" +
                   token)
  jdata = r.content
  user = {}

  user["email"] = json.loads(jdata)["email"]
  user["name"] = json.loads(jdata)["given_name"]
  user["full"] = json.loads(jdata)["name"]
  user["logged"] = True

  # except:
  #  user["logged"] = False
  return user
