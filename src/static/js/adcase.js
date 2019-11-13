// Copyright 2019 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
adcase.logData = "5.0.1";
adcase.id = {};
adcase.values = adcase.values || {};

adcase.startProcess = function() {
  "use strict";

  var script = document.createElement("script");
  script.async = true;
  script.src = "https://www.googletagservices.com/tag/js/gpt.js";
  document.head.appendChild(script);

};

adcase.instanceAd = function(format) {
  "use strict";
  this.values = {};
  this.set = function(name, value) {
    this.values[name] = value;
    return this;
  };
  this.get = function(name) {
    return(this.values[name] !== null ? this.values[name] : null);
  };
};


adcase.slotRendered = function(event) {
  adcase.adEvents = adcase.adEvents || [];
  adcase.adEvents.push(event);
  var d = event.slot.getSlotElementId();
  var slot = document.getElementById(d);
  var parent = slot.parentElement;
  parent.id = parent.id || d + "_parent";
  var format = slot.dataset.format || "default";
  adcase.id[d] = new adcase.instanceAd(format);
  adcase.id[d].slot = slot;
  adcase.id[d].parentSlot = parent;
  adcase.id[d].parentId = parent.id;
  adcase.id[d].divId = d;
  adcase.id[d].event = event;
  adcase.id[d].format = format;
  if(event.isEmpty) {
    adcase.id[d].width = 0;
    adcase.id[d].height = 0;
  } else {
    slot.style.display = "";
    adcase.id[d].width = event.size[0];
    adcase.id[d].height = event.size[1];
  }

  if(adcase.id[d].rendered) {
    var params = {
      width: event.size[0],
      height: event.size[1],
      event: event
    };
    adcase.id[d].rendered(params);
  }
};
googletag.cmd.push(function() {
  googletag.pubads().addEventListener("slotRenderEnded", function(
    event) {
    adcase.slotRendered(event);
    // force adcase key-value for logs
    if(googletag.pubads().getTargeting("adcase").length === 0) {
      console.log(
        "******   ERROR   ****   Please set adcase key   *******"
      );
      console.log(
        "googletag.pubads().setTargeting('adcase', console.logData);"
      );
      var d = event.slot.getSlotElementId();
      var slot = document.getElementById(d);
      slot.style.display = "none";
      slot.style.height = "0px";
      slot.parentElement.style.display = "none";
      slot.parentElement.style.height = "0px";
    }
  });
});

adcase.getIdFromMsg = function(e) {
  "use strict";
  var i =  null;
  try {
      var messageOrigin = e.source;
      var sourceWin = null;
      var sourceFrame = null;
      for (i = 0; i < window.frames.length; ++i) {
        if (messageOrigin.parent.parent.parent == window.frames[i] ||
            messageOrigin.parent.parent == window.frames[i] ||
            messageOrigin.parent == window.frames[i] ||
            messageOrigin == window.frames[i]) {
          sourceWin = window.frames[i];
          break;
        }
      }
    if (sourceWin) {
      var iframes = document.getElementsByTagName('iframe');
      for (i = 0; i < iframes.length; ++i) {
        if (iframes[i].contentWindow == sourceWin) {
          sourceFrame = iframes[i];
          break;
        }
      }
      return sourceFrame.parentElement.parentElement.id;
    }
  } catch (ex) {
  }
};



adcase.readFormatMessage = function(e) {
  "use strict";

  var msg = (e.data && e.data.msg) ? e.data.msg : "";
  if(msg == "adcase") {
    //var format = (e.data && e.data.format) ? e.data.format : false;
    var params = e.data.params || {};
    var format = e.data.format || false;
    var adId = adcase.getIdFromMsg(e);
    if(adId && adcase.id[adId]) {
      adcase.id[adId].set("window", e.source);
      if(!(e.data.version) || typeof(format) == "string" || !format) {
      // legacy messages
        params = adcase.convertLegacyMessages(adId, e.data);
        format = params.newFormat;
      }

      // version 4, call a singleton for all messages
      adcase.runFormatMessage(adId, format, params);

    }
  }
};

// This is only used by old creatives. Eventually it can be deleted
// it is needed until the builder is updated to V4.
// It maps old message formats to V4
adcase.convertLegacyMessages = function(adId, data) {
  "use strict";
  var params = data.params || {};
  if(data.format == "push") {
    params.newFormat = 101;
  } else if(params.action && params.action == "pushonclick") {
    params.newFormat = 118;
  } else if(data.format == "footerFixed" && params.expandTo &&
      params.expandTo == "layer") {
    params.newFormat = 119;
  } else if(data.format == "interstitial") {
    params.newFormat = 103;
  } else if(data.format == "default" && params.action && params.action ==
    "videobanner") {
    params.newFormat = 105;
  } else if(data.format == "footerFixed" && params.expandOn &&
    params.expandOn == "mouseover") {
    params.newFormat = 109;
  } else if(params.expand || params.collapse) {
    params.newFormat = 109;
  } else if(data.format == "footerFixed" && params.type && params.type ==
    "standard") {
    params.newFormat = 108;
  } else if(data.format == "doubleTopSticky") {
    params.newFormat = 115;

  }
  return params;
};

adcase.runFormatMessage = function(adId, format, params) {
  "use strict";
  var ad = adcase.id[adId];
  if(format == 101 || format == 102) { // push
    adcase.helpers.push(ad, params);
  } else if(format == 103 && params.videoSRC && params.videoSRC!="") {
    adcase.helpers.videoFullscreen(ad, params);
  } else if(format == 103 || format == 104) { // simple ITT
    params.show = true;
    params.transition = false;
    adcase.helpers.itt(ad, params);
  } else if(format == 105) { // videobanner
    adcase.helpers.videobanner(ad);
  } else if(format == 108) { // simple footer
    adcase.helpers.footer(ad, params);
    ad.parentSlot.style.display = "";
  } else if(format == 109) { // footer expand
    adcase.helpers.footerExpand(ad, params);
  } else if(format == 112) { // itt video
    params.show = true;
    params.transition = false;
    adcase.helpers.ittVideo(ad, params);
  } else if(format == 115) { // double top sticky
    adcase.helpers.doubletopsticky(ad, params);
  } else if(format == 118) { // pushonclick
    adcase.helpers.pushonclick(ad, params);
  } else if(format == 119) { // footer expand
    adcase.helpers.footerToITT(ad, params);
  } else if(format == 124) { // footer expand
    adcase.helpers.tabToITT(ad, params);
  } else {
    console.log("************** MSG ERROR: ", adId, format, params);
  }
};

adcase.helpers = {};

// 101, 102
adcase.helpers.push = function(t, p) {
  "use strict";
  // t = this ad slot
  // p = params

  if(document.location.href.indexOf("elfinanciero.com.mx")>0) {
    adcase.styles.push.expandedHeight = 270;
    t.parentSlot.style.padding = "0";
    t.slot.style.padding = "0";
    t.slot.firstChild.style.padding = "0";
  }

  if(t.get("window") && !t.get("stylesSet")) {
    t.set("stylesSet", true);
    t.get("window").postMessage(adcase.styles.push, "*");
  }

  if(p.expandedHeight) {
    t.set("expandedHeight", p.expandedHeight);
  }
  if(p.collapsedHeight) {
    t.set("collapsedHeight", p.collapsedHeight);
  }

  t.parentSlot.style.overflow = "hidden";
  if(p.transition) {
    t.parentSlot.style.transition = "height " + (p.transition / 1000) +
      "s ease-in";
  }

  var height = false;
  if(p.action == "collapse") {
    if(adcase.styles.push && adcase.styles.push.collapsedHeight) {
      height = adcase.styles.push.collapsedHeight;
    }
    if(t.get("collapsedHeight")) {
      height = t.get("collapsedHeight");
    }
    if(!height) {
      height = 90;
    }
    t.parentSlot.style.height = height + "px";
  } else if(p.action == "expand") {
    if(adcase.styles.push && adcase.styles.push.expandedHeight) {
      height = adcase.styles.push.expandedHeight;
    }
    if(t.get("expandedHeight")) {
      height = t.get("expandedHeight");
    }
    if(!height) {
      height = 250;
    }
    t.parentSlot.style.height = height + "px";
  }
};

// 103,104
adcase.helpers.itt = function(t, params) {
  "use strict";
  params.height = params.height || t.height;
  params.width = params.width || t.width;
  params.transition = (params.transition ? params.transition * 1 : 0);

  var div = params.div || t.slot;
  var parent = div.parentElement;
  var parentId = parent.id;

  div.style.position = "fixed";
  div.style.left = "0px";
  div.style.top = "0px";
  if(!params.backgroundColor || params.backgroundColor === "") {
    params.backgroundColor = "white";
  }
  div.style.backgroundColor = params.backgroundColor;
  div.style.width = "100%";
  div.style.height = "100%";
  div.style.zIndex = "1000000";

  var marginLeft = -(params.width / 2) + "px";
  var marginTop = -(params.height / 2) + "px";
  var iconRight = (params.width / 2 - 53) + adcase.styles.interstitial.right;
  var iconTop = -(params.height / 2) + adcase.styles.interstitial.top;

  var iframe = params.iframe || div.getElementsByTagName("iframe")[0];
  var iconDiv = document.createElement("div");

  iframe.style.maxHeight = params.height + "px";
  iframe.style.maxWidth = params.width + "px";

  iconDiv.style.height = "0px";
  iconDiv.style.width = params.width + "px";
  iconDiv.style.left = "50%";
  iconDiv.style.top = "50%";
  iconDiv.style.position = "absolute";
  iconDiv.style.marginLeft = "-55px";
  iconDiv.style.marginTop = "5px";

  iframe.style.top = "50%";
  iframe.style.position = "absolute";
  iframe.dataset.marginTop = marginTop;
  iframe.dataset.marginLeft = marginLeft;
  iframe.dataset.expandedWidth = params.width;
  iframe.dataset.expandedHeight = params.height;
  iframe.parentElement.parentElement.style.display = "none";
  iframe.dataset.transition = params.transition;

  if(params.show) {
    adcase.helpers.ittShow(iframe.id);
  } else {
    adcase.helpers.ittHide(iframe.id);
  }
  if(params.transition) {
    iframe.style.transition = "all 0.25s ease-in";
  }

  iconDiv.innerHTML = "<div id='adcase_ittIcon_" + parentId +
    "' style='position:absolute;display:;" +
    "right:" + iconRight + "px; top:" + iconTop +
    "px;z-index:1000001;cursor:pointer'>" +
    adcase.styles.interstitial.img + "</div>";
  div.appendChild(iconDiv);
  document.getElementById("adcase_ittIcon_" + parentId).onclick = function() {
    adcase.helpers.ittHide(iframe.id);
  };
  if(params.autoclose && params.autoclose>0) {
    window.setTimeout(function() {
      adcase.helpers.ittHide(iframe.id);
    }, params.autoclose * 1000);
  }

  var screenWidth =
    (adcase.device.isMobile ? screen.width : window.innerWidth);
  var screenHeight =
    (adcase.device.isMobile ? screen.height : window.innerHeight);
  if(params.width > (screenWidth - 20) || params.height > (screenHeight - 20)) {
    adcase.helpers.ittFixButtonTopRight("adcase_ittIcon_" + parentId);
  }
};

// todo: ordenar!
adcase.helpers.videoFullscreen = function(t,params) {
  adcase.set("ittClickTag",params.clickTag);
  if(params.closeTimeout && params.closeTimeout>0) {
      adcase.set("ittCloseTimeout", window.setTimeout(adcase.helpers.ittClose, params.closeTimeout));
  }

  adcase.set("previousOverflow",document.body.style.overflow);
  document.body.style.overflow="hidden";

  t.parentSlot.innerHTML = "<video onclick='adcase.helpers.ittClick()' autoplay "+(params.muted&&params.muted=="muted"?"muted":"")+" src='"+params.videoSRC+"' id='adcase_itt_video' style='cursor:pointer;position:fixed;top:0px;left:0px;width:100%;height:100%;z-index:10000;'></video>";
 // window.setTimeout(function() { document.getElementById("adcase_itt_video").play(); },500);

  adcase.set("ittInterval", window.setInterval(adcase.helpers.ittonResize,50));

  var iconDiv = document.createElement("div");
  var r = Math.random();
  iconDiv.innerHTML = "<div id='interstitialIconDiv_"+r+"' style='position:fixed;right:10px;top:10px;z-index:10001;cursor:pointer' onclick='adcase.helpers.ittClose()'>"
      + adcase.styles.interstitial.img + "</div>";
  t.parentSlot.appendChild(iconDiv);

}
adcase.helpers.ittClick=function() {
    window.open(adcase.get("ittClickTag"));
}
adcase.helpers.ittClose = function() {
  window.clearInterval(adcase.get("ittInterval"));
  window.clearInterval(adcase.get("ittCloseTimeout"));
  document.getElementById("adcase_itt_video").parentElement.innerHTML="";
  document.body.style.overflow=adcase.get("previousOverflow");
}
adcase.helpers.ittonResize = function() {
  var myVideo=document.getElementById("adcase_itt_video");
  var w = window.innerHeight / window.innerWidth;
  var v = myVideo.clientHeight / myVideo.clientWidth;
  if (w<=v) {
    myVideo.style.width=window.innerWidth+"px";
    myVideo.style.height="";
    myVideo.style.marginTop = (- (myVideo.clientHeight - window.innerHeight) / 2)+"px";
    myVideo.style.marginLeft = "0px";

  } else {
    myVideo.style.width="";
    myVideo.style.height= window.innerHeight+"px";
    myVideo.style.marginLeft = (- (myVideo.clientWidth - window.innerWidth) / 2)+"px";
    myVideo.style.marginTop = "0px";

  }
}
// end todo: ordenar

adcase.helpers.ittHide = function(containerId) {
  "use strict";
  var c = document.getElementById(containerId);
  c.style.height = 0;
  c.style.width = 0;
  c.style.marginTop = 0;
  c.style.marginLeft = 0;
  c.style.left = 0;
  document.body.style.overflow = "";
  window.setTimeout(function() {
    c.parentElement.parentElement.style.display = "none";
  }, c.dataset.transition);
};

adcase.helpers.ittShow = function(containerId) {
"use strict";
  var c = document.getElementById(containerId);
  window.setTimeout(function() {
    if(c.parentElement.parentElement && c.parentElement.parentElement.parentElement &&
       c.parentElement.parentElement.parentElement.style.display=="none") {
      c.parentElement.parentElement.parentElement.style.display="";
    }
    c.parentElement.parentElement.style.display = "";
    c.style.left = "50%";
    c.style.marginTop = c.dataset.marginTop;
    c.style.marginLeft = c.dataset.marginLeft;
    c.style.width = c.dataset.expandedWidth + "px";
    c.style.height = c.dataset.expandedHeight + "px";
  }, 50);
  document.body.style.overflow = "none";
};

adcase.helpers.ittFixButtonTopRight = function(iconDivId) {
  "use strict";
  var b = document.getElementById(iconDivId);
  b.style.top = "10px";
  b.style.right = "10px";
  b.style.position = "fixed";
};

// 105
adcase.helpers.videobanner = function(t) {
  "use strict";
  t.videoBannerScroll = function() {
    if(t.elementInViewport()) {
      t.play();
    } else if(!t.elementInViewport()) {
      t.pause();
    }
  };
  t.elementInViewport = function() {
    var rect = t.slot.getBoundingClientRect();
    var wh = (window.innerHeight || document.documentElement.clientHeight);
    var rt = Math.ceil(rect.top);
    var view = false;
    if(rt <= wh - (t.height * 0.75) && rt > -(t.height * 0.25)) {
      view = true;
    }
    return view;
  };
  t.play = function() {
    t.set("playing", true);
    t.get("window").postMessage({
      action: "play"
    }, "*");
  };
  t.pause = function() {
    t.set("playing", false);
    t.get("window").postMessage({
      action: "pause"
    }, "*");
  };
  t.onScroll = function() {
    if(t.get("videoBannerScrollEnabled")) {
      t.videoBannerScroll();
    }
  };
  t.set("videoBannerScrollEnabled", true);
  t.get("window").postMessage({
    videoButtons: adcase.styles.videoButtons
  }, "*");

  if(!adcase.get("scrollEnabled")) {
    adcase.enableScroll();
  } else {
    adcase.scroll();
  }
  t.videoBannerScroll();
};

adcase.enableScroll = function() {
  "use strict";

  adcase.set("scrollEnabled", true);
  window.addEventListener("scroll", function() {
    if(adcase.scrollTimeout) {
      adcase.scroll();
    }
  });
};

adcase.scroll = function() {
  "use strict";

  adcase.scrollTimeout = false;
  setTimeout(function() {
    adcase.scrollTimeout = true;
  }, 500);

  Object.keys(adcase.id).forEach(function(i, index) {
    if(adcase.id[i].onScroll) {
      adcase.id[i].onScroll();
    }
    if(adcase.lazy) {
      var d = adcase.id[i];
      if(adcase.elementInViewport(d.slot) && !adcase.printedSlots[d.divId]) {
        adcase.printedSlots[d.divId] = true;

        adcase.refresh(d.divId, {
          changeCorrelator: false
        });
      }
    }
  });
};

adcase.elementInViewport = function(el) {
  "use strict";

  var rect = el.getBoundingClientRect();

  var tooLeft = (rect.left < 0);
  var tooBottom = (rect.top - 300) > (adcase.device.isMobile ? screen.height : (
    window.innerHeight || document.documentElement.clientHeight));
  var tooTop = (rect.bottom < 0);

  var viewable = !tooLeft && !tooBottom && !tooTop;
  return viewable;
};
// END VIDEOBANNER

// 108
adcase.helpers.footer = function(t, p) {
  "use strict";
  if(p.height) {
    t.set("height", p.height);
  }
  var div = t.slot;
  var containerDiv = t.parentSlot;
  containerDiv.style.display = "none";
  containerDiv.style.zIndex = 9000;
  containerDiv.style.background = "none repeat scroll 0 0 transparent";
  containerDiv.style.position = "fixed";
  containerDiv.style.textAlign = "center";
  containerDiv.style.bottom = "0px";
  containerDiv.style.left = "0px";
  containerDiv.style.width = "100%";
  containerDiv.style.minHeight = "0px";
  containerDiv.style.minWidth = "0px";

  var iframe = containerDiv.getElementsByTagName("iframe")[0];
  iframe.style.background = "none repeat scroll 0 0 white";
  iframe.style.margin = "auto";

  var iconMarginRight = -(t.width / 2);
  if(!document.getElementById("adcase_footer_text_c_" + div.id)) {
      var newDiv = document.createElement("div");
      newDiv.id = "adcase_footer_text_c_" + div.id;
      newDiv.innerHTML = "<div id='adcase_footer_text_" + div.id +
        "' style='position:absolute;display:;right:50%;margin-right:" +
        iconMarginRight + "px;top:0px;cursor:pointer;' " +
        "onclick=\"document.getElementById('" + div.id +
        "').parentElement.style.display = 'none'\">" +
        adcase.styles.footerFixed.closeImg + "</div>";
      containerDiv.appendChild(newDiv);
  }
  div.style.marginTop = adcase.styles.footerFixed.iconMarginTop + "px";
  div.style.display = "inline-block";
  containerDiv.style.height = ((t.get("height") * 1) +
    (adcase.styles.footerFixed.iconMarginTop * 1)) + "px";
};

//109
adcase.helpers.footerExpand = function(t, p) {
  "use strict";
  adcase.helpers.footer(t, p);

  if(p.expandedHeight) { t.set("expandedHeight", p.expandedHeight); }
  if(p.collapsedHeight) { t.set("collapsedHeight", p.collapsedHeight); }
  if(p.expandOn) { t.set("expandOn", p.expandOn); }
  if(p.expandMS) { t.set("expandMS", p.expandMS); }
  if(t.get("expandOn") == "mouseover") {
    adcase.helpers.footerExpandMouseOver(t, p);
  } else { // expand on click
    adcase.helpers.footerExpandClick(t, p);
  }
  t.parentSlot.style.display = "";
};
adcase.helpers.footerExpandMouseOver = function(t, p) {
  "use strict";
  var div = t.slot;
  var containerDiv = t.parentSlot;

  if(p.expand) {
    if(document.getElementById("adcase_footer_text_" + div.id)) {
      document.getElementById("adcase_footer_text_" + div.id).style.display =
        "none";
    }
    containerDiv.style.height = t.get("expandedHeight") + "px";
  } else {
    containerDiv.style.height = t.get("collapsedHeight") + "px";
    if(document.getElementById("adcase_footer_text_" + div.id)) {
      document.getElementById("adcase_footer_text_" + div.id).style.display =
        ""; }
  }
};

adcase.helpers.footerExpandClick = function(t, p) {
  "use strict";
  var div = t.slot;
  var containerDiv = t.parentSlot;
  var iconMarginRight = -(t.width / 2);
  var html = "<div id='adcase_footer_text_" + div.id +
    "' style='position:absolute;display:;right:50%;margin-right:" +
    iconMarginRight + "px;top:0px;cursor:pointer;' >" +
    "<div id='adcase_footer_text_close_" + div.id +
    "' style='float:right' " +
    "onclick='adcase.helpers.footerExpandClickCollapse(\"" +
    div.id + "\")'>" + adcase.styles.footerFixed.closeImg + "</div>" +
    "<div id='adcase_footer_text_open_" + div.id +
    "' style='float:right' " +
    " onclick='adcase.helpers.footerExpandClickExpand(\"" +
    div.id + "\")'>" + adcase.styles.footerFixed.openImg + "</div>" +
    "</div>";
  document.getElementById("adcase_footer_text_c_" + div.id).innerHTML = html;

  containerDiv.style.display = "block";
  containerDiv.style.height = ((t.get("collapsedHeight") * 1) + (adcase.styles
    .footerFixed.iconMarginTop * 1)) + "px";
};

adcase.helpers.footerExpandClickExpand = function(adId) {
  "use strict";
  var t = adcase.id[adId];
  var div = t.slot;
  window.setTimeout(function() {
    t.parentSlot.style.height = t.get("expandedHeight") + "px";
  }, 50);
  t.get("window").postMessage({
    expand: true
  }, "*");
  document.getElementById("adcase_footer_text_open_" + div.id).style.display =
    "none";
};

adcase.helpers.footerExpandClickCollapse = function(adId) {
  "use strict";
  var t = adcase.id[adId];
  var div = t.slot;
  if((t.parentSlot.style.height == t.get("collapsedHeight") + "px") ||
    (t.parentSlot.style.height == ((t.get("collapsedHeight") * 1) +
      (adcase.styles.footerFixed.iconMarginTop * 1)) + "px")) {
    t.parentSlot.style.display = "none";
  }
  t.parentSlot.style.height = t.get("collapsedHeight") + "px";
  t.get("window").postMessage({
    collapse: true
  }, "*");
  document.getElementById("adcase_footer_text_open_" + div.id).style.display =
    "";
};

// 119
adcase.helpers.footerToITT = function(t, p) {
  "use strict";
  adcase.helpers.footer(t, p);

  if(p.expandedHeight) { t.set("expandedHeight", p.expandedHeight); }
  if(p.collapsedHeight) { t.set("collapsedHeight", p.collapsedHeight); }
  if(p.expandOn) { t.set("expandOn", p.expandOn); }
  if(p.expandMS) { t.set("expandMS", p.expandMS); }
  if(p.expandedImage) { t.set("expandedImage", p.expandedImage); }

  var i = document.createElement("div");
  i.id = "adcase_itt_c_" + t.slot.id;
  i.style.display = "none";
  t.slot.appendChild(i);

  t.expandTimeout = null;
  t.slot.onmouseover = function() {
    t.expandTimeout = window.setTimeout(function() {
      adcase.helpers.footerToITTExpand(t.slot.id);
    }, t.get("expandMS"));
  };
  t.slot.onmouseout = function() {
    window.clearTimeout(t.expandTimeout);
  };
  t.parentSlot.style.display = "";
};

adcase.helpers.footerToITTExpand = function(adId) {
  "use strict";
  var t = adcase.id[adId];

  if(document.getElementById("adcase_itt_c_" + t.slot.id).style.display ===
    "") {
    return;
  }

  var div = document.getElementById("adcase_itt_c_" + t.slot.id);
  div.innerHTML = "<div id='adcase_itt_c2_" + t.slot.id + "'></div>";

  var i = document.createElement("img");
  i.src = t.get("expandedImage");
  i.id = "adcase_itt_" + t.slot.id;
  i.style.height = t.get("expandedHeight") + "px";
  i.style.width = t.width + "px";
  i.style.cursor = "pointer";
  i.onclick = function() {
    adcase.sendClick(t.slot.id);
  };
  document.getElementById("adcase_itt_c2_" + t.slot.id).appendChild(i);
  var params = {
    div: div,
    iframe: i,
    width: t.width,
    height: t.get("expandedHeight"),
    show: true,
    transition: false
  }

  adcase.helpers.itt(t, params);

  t.slot.style.display = "";
  t.parentSlot.style.display = "";
};

// 112
adcase.helpers.ittVideo = function(t, params) {
  "use strict";
  var div = t.slot;
  div.getElementsByTagName("iframe")[0].style.display = "none";

  var v = document.createElement("video");
  v.muted = "true";
  v.src = params.videoURL;
  v.style.width = "100%";
  v.style.height = "100%";
  v.style.cursor = "pointer";
  v.id = "adcase_ittvideo_" + div.id;
  v.onclick = function() {
    adcase.sendClick(div.id);
  };
  div.appendChild(v);


  params.iframe = document.getElementById(v.id);

  adcase.helpers.itt(t, params);
  params.iframe.play();
};

adcase.sendClick = function(adId) {
  "use strict";
  var t = adcase.id[adId];
  t.get("window").postMessage({
    msg: "adcase",
    action: "click"
  }, "*");
};

// 115
adcase.helpers.doubletopsticky = function(t, p) {
  "use strict";
  if(p.width && p.width > 0) {
    t.set("transition", p.transition);
    t.set("inlineHeight", p.inlineHeight);
    t.set("stickyHeight", p.stickyHeight);
    t.set("maxHeight", Math.max(p.inlineHeight, p.stickyHeight));
    t.set("width", p.width);
    t.set("topMargin", (typeof(p.topMargin) == "undefined" ? 45 : p.topMargin));
    t.slot.parentElement.style.height = t.get("inlineHeight") + "px";
  }

  t.lastScrollTop = 0;

  window.addEventListener("scroll", function() {
    t.doScroll();
  }, false);

  t.doScroll = function() {
    var offsets =
      document.getElementById(t.parentSlot.id).getBoundingClientRect();
    var inlineBottom = offsets.top + (t.get("inlineHeight") * 1);

    var st = window.pageYOffset || document.documentElement.scrollTop;
    if(st > t.lastScrollTop) {
      if(inlineBottom < 0) {
        if(t.get("window") && !t.get("stickyOn")) { t.showSticky(true); }
      } else {
        if(t.get("window") && t.get("stickyOn")) { t.showSticky(false); }
      }
    } else if(st <= t.lastScrollTop) {
      if(t.get("window") && t.get("stickyOn")) { t.showSticky(false); }
    }
    t.lastScrollTop = st;
  };

  t.showSticky = function(stickyOn) {
    if(stickyOn) {
      t.slot.style.transition = "top 0s ease-in-out";
      t.slot.style.position = "fixed";
      t.slot.style.left = "50%";
      t.slot.style.marginLeft = "-" + (t.get("width") / 2) + "px";
      t.slot.style.height = t.get("stickyHeight") + "px";
      t.slot.style.top = '-' + (t.get("stickyHeight") * 2) + 'px';
      window.setTimeout(function() {
        t.slot.style.zIndex = 1200;
        t.slot.style.transition = "top " + (t.get("transition") / 1000) +
          "s ease-in-out";
        t.slot.style.top = t.get("topMargin") + 'px';
      }, 10);
      t.get("window").postMessage({
        sticky: "on"
      }, "*");
    } else {
      t.slot.style.top = '-' + (t.get("stickyHeight") * 2) + 'px';
      window.setTimeout(function() {
        t.slot.style.position = "";
        t.slot.style.left = "";
        t.slot.style.marginLeft = "";
        t.slot.style.height = t.get("inlineHeight") + "px";

        t.slot.style.top = "";
        t.get("window").postMessage({
          sticky: "off"
        }, "*");
      }, t.get("transition"));

    }

    t.set("stickyOn", stickyOn);
  };
  t.fn = function() {
    t.slot.classList.remove("adcase-doubletopsticky");
    t.get("window").postMessage({
      sticky: "off"
    }, "*");
    t.slot.style.display = "block";
    t.slot.style.position = "relative";
    t.slot.style.top = "";
    t.slot.innerHTML = "";
  };
};

// 118
adcase.helpers.pushonclick = function(t, p) {
  "use strict";
  if(p.expandedHeight) { t.set("expandedHeight", p.expandedHeight); }
  if(p.collapsedHeight) { t.set("collapsedHeight", p.collapsedHeight); }

  t.parentSlot.style.display = adcase.startDisplay;

  if(p.expand) {
    t.parentSlot.style.height = t.get("expandedHeight") + "px";
  } else {
    t.parentSlot.style.height = t.get("collapsedHeight") + "px";
  }
};

// 124
adcase.helpers.tabToITT = function(t, p) {
  "use strict";
  t.slot.style.display = "none";
  var parent = document.createElement("div");
  parent.id = "ads-tab2ITT-parent";
  var content = "";
  if(p.expandedImage) {
    content = "<img id='ads-tab2ITT-iframe' src='" + p.urlPrefix +
      p.expandedImage + "' style='width:100%;height:100%;'>";
  } else {
    content = "<iframe id='ads-tab2ITT-iframe' src='" + p.urlPrefix +
     p.expandedURL + "' frameborder=no></iframe>";
  }
  parent.innerHTML = "<div id = 'ads-tab2ITT-div' style='cursor:pointer'>" +
    content + "</div>";
  parent.style.display = "none";
  t.parentSlot.appendChild(parent);
  var div = document.getElementById("ads-tab2ITT-div");
  var iframe = document.getElementById("ads-tab2ITT-iframe");
  var params = {
    t: t,
    div: div,
    parent: parent,
    iframe: iframe,
    height: p.ittHeight,
    width: p.ittWidth,
    backgroundColor: (p.backgroundColor || "white")
  };
  adcase.helpers.itt(t, params);


  iframe.onclick = function() {
    t.get("window").postMessage({
      msg: "adcase",
      action: "click"
    }, "*");
  };
  //t.slot.style.display="none";
  var smallDiv = document.createElement("div");
  smallDiv.innerHTML = '<div class="' + p.tabClass +
    '"><ul><li><a onclick="adcase.helpers.ittShow(\'' + iframe.id + '\')">' +
    '<img src="' + p.urlPrefix + p.tabImage + '" /></a></li></ul></div>';
  t.parentSlot.appendChild(smallDiv);
  t.parentSlot.style.height = "";
  t.parentSlot.style.display = "";
};


////////////////////////////////////////////////////////////////

adcase.setDefaultStyles = function() {
  "use strict";
  adcase.styles.iconClose = adcase.styles.iconClose ||
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAMAAABHPGVmAAACR" +
    "lBMVEUAAAD///////////8AAAABAQH///8DAwP///////8wMDB+fn4EBAQODg4wMDD///+m" +
    "pqYwMDAHBwcvLy8wMDDp6eliYmJfX18wMDAwMDAwMDAwMDAwMDARERH///+xsbF7e3ukpKQ" +
    "EBAQLCwsICAiCgoJWVlYwMDAwMDAwMDAwMDA+Pj4wMDAwMDAwMDAwMDAwMDAwMDAwMDAlJS" +
    "UUFBQmJib4+Pjy8vLs7OzY2NhZWVmTk5OFhYV2dnYwMDAwMDAwMDAwMDAwMDAwMDAwMDAwM" +
    "DAwMDA4ODgeHh5hYWFvb29ISEhCQkJQUFBERES2traOjo5UVFReXl4wMDAwMDAwMDAwMDAw" +
    "MDAwMDAwMDAwMDAwMDDa2tohISEsLCzu7u4iIiJMTEz6+vrk5OQqKio4ODigoKB4eHhcXFz" +
    "GxsaIiIiHh4e5ubmKiop/f39HR0cwMDAwMDAwMDAwMDAwMDDz8/MYGBjp6enl5eVJSUkpKS" +
    "nR0dH8/Pw3NzdmZmYyMjLd3d2+vr6kpKTAwMCurq5qamrKysqYmJhlZWWoqKhFRUXPz8/Ex" +
    "MScnJysrKyPj48wMDAwMDAwMDAwMDAwMDDs7OwvLy9RUVHV1dUbGxtYWFj+/v7c3Nx1dXVY" +
    "WFi8vLxxcXG3t7eNjY1GRkYwMDAwMDAwMDAwMDD29vZ+fn6ZmZkwMDAwMDAwMDAwMDD///8" +
    "xMTEzMzMqKioJCQkoKCggICAtLS0kJCQXFxcREREODg4iIiIGBgYaGhocHBwUFBQAAAALCw" +
    "vyxkBmAAAArnRSTlMA+Pn9/P7z/Pv18u35+e7269r79vTy7u3VNx0ZFPjv7u7r/vn57u7o0" +
    "Mb69JyRfVBKMv769/Xz8/Pw7u3t6sC5oY2DYVs0Cfn18/Ly8vHx8PDw7OTLrqVvV0I/Jvr6" +
    "+PX19PPz8/Lx8fHv7u7t7e3ts4hmRir6+vj49/f29fX08vHx8fDw8O/v7+7u7e3t7OlrIQ0" +
    "FAfv7+fj19PLv7+7t7ezo6N+yqRD58vGolwMaaJUuAAAIQUlEQVRo3q2a9UPbQBTHk9TZ2q" +
    "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";
  adcase.styles.footerFixed = adcase.styles.footerFixed || {};
  adcase.styles.footerFixed.closeImg = adcase.styles.footerFixed.closeImg ||
    "<img height=24 width=24 src='" + adcase.styles.iconClose + "'>";
  adcase.styles.footerFixed.openImg = adcase.styles.footerFixed.openImg ||
    "[OPEN]";
  adcase.styles.footerFixed.iconMarginTop =
    adcase.styles.footerFixed.iconMarginTop || 0;

  adcase.styles.interstitial = adcase.styles.interstitial || {
    img: "<img src='" + adcase.styles.iconClose +
      "' height=54 width=54 border=0>",
    top: -25,
    right: -25
  };
  adcase.styles.push = adcase.styles.push || {
    iconsStyle: "width:45px;position:absolute;left:917px;top:0;border:1px " +
    "solid #ccc;font-family:Arial;font-size:11px;padding:3px;" +
    "background-color:white;text-align:center;",
    openIconHTML: "OPEN",
    closeIconHTML: "CLOSE"
  };
  adcase.styles.videoButtons = adcase.styles.videoButtons ||
    "<div id='overlay' style='width:100%;height:60px;background-color:white;" +
    "opacity:0.9;position:absolute;bottom:0px;z-index:5;display:none'></div>" +
    "<div id='overlay-txt' style='width:100%;height:50px;position:absolute; " +
    "bottom:0px;z-index:6;display:none'>" +
    "<div style='float:left;cursor:pointer;margin:0px 0 4px 40px' " +
    "onclick='replay()'><img src='data:image/png;base64,iVBORw0KGgoAAAANSUhE" +
    "UgAAAGAAAAAeCAYAAADTsBuJAAAEsUlEQVRoge2aTWhcVRTHfxlSVLow4kJcqIOKFWLJ1EL" +
    "FhXRSXOhCzmTjQk2agKWKCzPoQqSaCVLcNWYl2kUnZtwomHdxoYI0U10ZWg0l6sKiU8EPEG" +
    "EWKuLC5+Kc59y+zsebiZln4P1hmHvP133vnHvPPe++BxkyZMiQGkYSyBwCngAeBm4G9hr9d" +
    "+An4AOgBmx0MxKG4eBXmTJGRpK4aUDbXXgPAK8D48DfwMfAFnDJ+HcC9wAPAjngS+Bp4NN2" +
    "xrIA9IcVIAQuojM/10U2ZzIXTWelnVAYhrv2N0zsAc6bI+cG0J8z3fNm61+k7cTdEoAtc+D" +
    "+bdjYbza2fGLaTtwNAaiZ48bb8K4DngHq6Mb7I/CJ0a5tIz9utmoRIW0n/l8DEO0uh4DPgB" +
    "lgNSYzDbxl7a+BTdM7AOzzZGod9O4DNjrdSKlUKvp951y9v1vYHsIwpFQqVYCJIAim2sns5" +
    "CY8av/vAN9ytfNfAU6gzn0B+CHGvxV41fTuAl72eKtAxWznu1zDut8RkSYw6ZzbTHgPfUNE" +
    "ZoGGF+wJoLhT43VDDigAtwHHYrzHUOc/h87muPMBvgceN5mXrO3jmNku9LiORefcCDAFjAH" +
    "PJr+FgXAGz+FBEEwFQXDDDo/ZFqPAcbTOP+vR9wBvA+8BpxLYOYU+N9SAd4G/jH7WbB9Hnx" +
    "G6wjkXiAh4K0ZEKsBh6y475wKP3jTeGNAAys65pvELwEKcZ3oAh61dsTRYDIKgUiqV8sBsJ" +
    "IOW1dUEPhgIOeARYmmA1mqY7sNWJPtkjL5uY/SEOQ3UYYjIEurEhtHXPJkFYImWg2etj4jk" +
    "bdwCumeV0FkPrWDmvXbR7EX0BXQVRuPuGHLAjcCFGH0G3XD/6MPWb6YzE6NfsDG64aiIrAN" +
    "foA4ri8gYMI+mpznn3CQ640ueXt05N+mcmwNeozVzoxR2wDlXBhYjPbMDsOK122E5CIK5IA" +
    "iqPa59W8ihZWQjRt8HfD6AvU3gjhitQftSNS7TtLazNBLNdBGRdQsQtGYtwDmv7Uy44Omum" +
    "d5R4xUT3YWi3ofswBjtQB+0+B0h2QFfHOeccxURWQMWRKTq8TaBy5EcvdNC0/uPB6iX7tAx" +
    "CvzJ1WXiJeDeAewVgG9itLyNkQRlNFUsoGkDNDjVDvLXe20BcM41RKQB5J1zlYTjpoZR4Ff" +
    "gYIxeA5bR1NHLeTehKesr4G7gqRj/oI3RE+a8KprLV9DZv2SVEWhuL3v1+7yIRKtjnla14o" +
    "BZW1HLaHAKsZw/ISLz6N6RGnLA+0B8M3rT/uMPZu1wP1pufogu8Tdi/EkboxPqXJkaFo1WR" +
    "A/3NtEK5gyaVnzZBlr5LJlOGbScNTtFtBqaxfYIb4xopUV26tZuWrvJkFBAc/6RGH3a6L0e" +
    "ih4yuRB4EbjG4x0xeuG/PmcRkdCr6QdG2mdBOVqb3OkYbxU4iS7RALilgw2/VD0JPO/1T5v" +
    "tHTtW2O2IqqBH0cO4aa5MOyfQTbWK5tGfgY/QfBst0Q10ieeAX9BaHrN1O3oYlyEBuh1H70" +
    "VT0QbwHfpuuBuy4+gBkb2QSTkA2SvJlAMQIXspP6QAZJ+lJEBa3wVFyD7MSuG7oAxDwj+s7" +
    "wq9L116HwAAAABJRU5ErkJggg=='></div>" +
    "<div style='float:right;cursor:pointer;margin:0px 40px 4px 0px' " +
    "onclick='goClick()'><img src='data:image/png;base64,iVBORw0KGgoAAAANSUh" +
    "EUgAAAGAAAAAeCAYAAADTsBuJAAACQ0lEQVRoge2X0ZHaMBCGv2RSgNOBr4KQCvBVsFABUE" +
    "GOCsAV3HVwoQK8FWAqwB3gdEAJedBqUC4cl9wY+x72m/HYWsvalbT6JYPjOI7jOI7jOI7TK" +
    "5+GciwiGTACWlVtX7wbAZmq1j3HlANH4ElVl334/NyHkyvsgNUF+xZ47DkWgGeg6WvwYcAJ" +
    "UNUTUAGT1G7ZnwObPuOx7N8D0z79DiZBACIyJ2TdVFUrsz0CD8AdcCKshNyeS1VtrN7abMK" +
    "FrBWRAiisOAZaoCSsuNzKS1U9mRzOrS2AvaqurZ3M4hnbu7JLaRxagiq7S2KbEAa0JUjUBG" +
    "gI+8UuqbciTE77StuF1ZnZ93OCvhdJOcrcyOq2hEldichD4ueHfRPb7YwvXTb2v1j2RRlaJ" +
    "PKzFJEJYWDuVbUWkQ1wEJEiycBaVRdvuLlX1TbJ8qmqNlYurE4DfI+HARE5AN/s3Ygb7gtD" +
    "rwAABTIb8JnZKkLHIWTjjnO2Fsm3+zcbP5+wflm5Scq52U7ARER2InI033nioxCRZ9snOuU" +
    "jTEAqQ6n8RPbJVQJ11wHYfhLlbMNZbrC9oLTYjpYonTGoBMFfMpQBcam3dv/58j/hBoxJ5E" +
    "xEZoS9IMa4FpEn4EBYpdXFVt7B4BNgKOfjaOxcTRiErYiUBElYqerXG/g/EWQmymCOJYDJ3" +
    "56wKjJe3/TfxUeQIAiDXpNku90XhE7HH7M082quD0bLn3J1rVxik03Q/4qzDDWEk9DWnst/" +
    "6I/jOI7jOI7jOI7jOBf5DbA458r1td3dAAAAAElFTkSuQmCC'></div></div>";
  adcase.styles.default = adcase.styles.default || {
    startDisplay: "none"
  };
};

adcase.set = function(k, v) {
  // set a an adcase scope variable
  "use strict";
  adcase.values[k] = v;
};
adcase.get = function(k) {
  // get a an adcase scope value
  "use strict";
  return adcase.values[k] || null;
};

window.addEventListener("message", adcase.readFormatMessage, false);

adcase.device = {
  isMobile: (/Mobi/.test(navigator.userAgent)),
  isTablet: (screen.width < 800 || screen.height < 800),
  isDesktop: !(/Mobi/.test(navigator.userAgent))
};

adcase.setDefaultStyles();
adcase.startProcess();
