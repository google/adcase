This is not an officially supported Google product

## Source Code Headers
Apache header:

    Copyright 2017 Google Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

# Adcase Implementation Guide

## Backend (Python builder) implementation highlights
Configuration file `app.yaml` is made for [Google App Engine](https://cloud.google.com/appengine/docs/standard/python3/config/appref). If'll host this application in any other way, you must adapt this file or create another of your preference.

Modify `tpl/header.html` with correct value for "google-signin-client_id" (OAuth Client ID). This is
important for getting user login to work.

Immediately after deploying the application, access endpoint `/builder/setup` in order to configure the database.




## Frontend (html/javascript) implementation guide

### Step 1:

Replace:
```
<script>
  var googletag = googletag || {cmd:[]};
</script>
<script async="async" src="https://securepubads.g.doubleclick.net/tag/js/gpt.js">
```

With:
```
<script>
  var adcase = { styles: {}, light:true };

  adcase.styles.push = {
    iconsStyle   : "width:62px;position:absolute;left:900px;top:0;border:1px solid #ccc;"
                 + "font-family:Arial;font-size:11px;padding:3px;background-color:white;"
                 + "text-align:center;",
    openIconHTML : "[OPEN]",
    closeIconHTML: "[CLOSE]" };

  var googletag = googletag || {cmd:[]};
</script>
<script async='async' src='[ADCASE.JS LOCATION]'></script>
```

### Step 2:
Replace `[ADCASE.JS LOCATION]` from step 1 with the current location of your adcase.js file, i.e. 
`https://storage.googleapis.com/some-bucket/dist/5/adcase.js`


### Step 3:
Replace:
```
googletag.enableServices();
```


With:
```
googletag.pubads().setTargeting('adcase', adcase.logData);
googletag.enableServices();
```

### Step 4:
Modify slots depending on expected creative types:

* For expanding/push:
```
<div>
  <div id='adslot-push' data-format='push'>
    <script>googletag.cmd.push(function() {
              googletag.display('adslot-push'); });</script>
  </div>
</div>
```

* For footers/sticky:
```
<div style='display:none'>
  <div id='adslot-footer' data-format='footerFixed'>
    <script>googletag.cmd.push(function() {
              googletag.display('adslot-footer'); });</script>
  </div>
</div>
```

* For Interstitials:
```
<div style='display:none'>
  <div id='adslot-itt' data-format='interstitial'>
    <script>googletag.cmd.push(function() {
              googletag.display('adslot-itt'); });</script>
  </div>
</div>
```
