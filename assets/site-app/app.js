(() => {
  "use strict";

  const messages = {
    en: {
      documentTitle: "Rhino Site Studio",
      languageLabel: "Language",
      languageEnglish: "English",
      languageChinese: "Chinese",
      brandSubtitle: "OSM + GEE terrain workbench",
      darkMode: "Dark mode",
      lightMode: "Light mode",
      localService: "Local service",
      selectionSaved: "Selection saved",
      offlineMode: "Offline mode",
      mapWorkspace: "Site map workspace",
      mapActions: "Map actions",
      siteControls: "Site controls",
      workspaceView: "Workspace view",
      mapUnavailable: "Map tiles are unavailable",
      mapUnavailableHelp: "Draw or load a GeoJSON boundary from the controls.",
      invalidBoundaryType: "Use a Polygon or MultiPolygon GeoJSON file.",
      noPolygon: "The GeoJSON contains no Polygon or MultiPolygon.",
      noBoundaryCoords: "The GeoJSON boundary has no coordinates.",
      drawPolygon: "Draw a polygon",
      drawRectangle: "Draw a rectangle",
      editLayers: "Edit layers",
      deleteLayers: "Delete layers",
      zoomIn: "Zoom in",
      zoomOut: "Zoom out",
      drawStartPolygon: "Click to start drawing a polygon.",
      drawStartRectangle: "Click and drag to draw a rectangle.",
      drawContinue: "Click to continue drawing the shape.",
      drawFinish: "Click the first point to close this shape.",
      drawCancel: "Cancel drawing",
      editSave: "Save changes",
      editCancel: "Cancel editing",
      editClearAll: "Clear all layers",
      editEdit: "Edit layers",
      editRemove: "Delete layers",
      editDisabled: "No layers to edit",
      removeDisabled: "No layers to delete",
      editTooltip: "Drag handles to edit the boundary.",
      removeTooltip: "Click a boundary to delete it.",
      findView: "Find my view",
      loadGeoJson: "Load GeoJSON",
      tileState: "OSM tiles unavailable. Offline boundaries active.",
      attribution: "OpenStreetMap contributors / Natural Earth",
      selectSite: "Select a working site",
      selectSiteHelp: "Choose a boundary first. Network requests stay local to this service.",
      boundary: "Boundary",
      notSelected: "Not selected",
      readyToSave: "Ready to save",
      west: "West",
      south: "South",
      east: "East",
      north: "North",
      drawBoundaryHelp: "Draw a rectangle or polygon on the map.",
      featureSingle: "{count} feature; approx {width} x {height} km.",
      featurePlural: "{count} features; approx {width} x {height} km.",
      saveBoundary: "Save boundary",
      planOsm: "Plan OSM",
      planDem: "Plan DEM",
      findPlace: "Find a place",
      placePlaceholder: "City, address, or landmark",
      search: "Search",
      osmSource: "OSM source",
      osmOverpass: "Overpass, small areas",
      osmLocal: "Local OSM or PBF",
      osmGeofabrik: "Geofabrik PBF extract",
      osmHelp: "Overpass needs no login. Large sites should use a local PBF.",
      terrainSource: "Terrain source",
      demCopernicus: "Copernicus GLO-30",
      demSrtm: "USGS SRTM 30 m",
      demNasadem: "NASADEM 30 m",
      demLocal: "Local GeoTIFF or ASCII grid",
      geeHelp: "GEE uses your local Earth Engine session and project.",
      geeProject: "GEE project ID",
      optional: "optional",
      terrainPrecision: "Terrain precision",
      draft: "Draft",
      standard: "Standard",
      fine: "Fine",
      draftNote: "30 m sampling target. Fast preview for large extents.",
      standardNote: "10 m sampling target. Source resolution remains the accuracy limit.",
      fineNote: "3 m sampling target. Interpolation is labelled when source data is coarser.",
      contours: "Contours: {value}.",
      credentialsTitle: "Credentials stay outside the skill",
      credentialsHelp: "OSM is public. GEE may ask you to authorize locally and provide a project ID. Tokens are never saved here.",
      map: "Map",
      extent: "Extent",
      readyForBoundary: "Ready for a boundary.",
      boundaryReady: "Boundary ready. Review settings, then save.",
      savingBoundary: "Saving boundary and settings...",
      boundarySaved: "Boundary and settings saved.",
      selectionToast: "Site selection saved to the local data folder.",
      preparingRequest: "Preparing {kind} request...",
      planReady: "{kind} plan ready.",
      planToast: "{kind} plan written to the data folder.",
      searching: "Searching...",
      noPlace: "No place found.",
      placeFound: "Place found.",
      workingExtent: "Working extent",
      extentHelp: "This plane shows only the selected bounds. Terrain appears after DEM acquisition and the Rhino build.",
      backToMap: "Back to map",
      extentPreview: "Selected site extent preview",
      previewEmpty: "Draw a boundary to see the working extent.",
      extentOnly: "EXTENT ONLY",
      demNotLoaded: "DEM not loaded",
      offlineWorld: "Offline world boundaries could not be loaded.",
      tilesUnavailableActivity: "OSM tiles are unavailable. Offline boundaries and local GeoJSON still work.",
      boundaryCleared: "Boundary cleared.",
      geojsonLoaded: "GeoJSON boundary loaded.",
      locationUnavailable: "Location is not available in this browser.",
      locationDenied: "Location permission was not granted.",
      offlineActivity: "Local service is unavailable. You can still draw and export a GeoJSON file.",
      requestFailed: "Request failed: {message}"
    },
    zh: {
      documentTitle: "Rhino 场地工作台",
      languageLabel: "语言",
      languageEnglish: "英文",
      languageChinese: "中文",
      brandSubtitle: "OSM + GEE 地形工作台",
      darkMode: "深色模式",
      lightMode: "浅色模式",
      localService: "本地服务",
      selectionSaved: "选址已保存",
      offlineMode: "离线模式",
      mapWorkspace: "场地地图工作区",
      mapActions: "地图操作",
      siteControls: "场地控制",
      workspaceView: "工作区视图",
      mapUnavailable: "地图瓦片不可用",
      mapUnavailableHelp: "请从控制栏绘制或载入 GeoJSON 边界。",
      invalidBoundaryType: "请选择 Polygon 或 MultiPolygon 类型的 GeoJSON 文件。",
      noPolygon: "GeoJSON 中没有 Polygon 或 MultiPolygon。",
      noBoundaryCoords: "GeoJSON 边界没有坐标。",
      drawPolygon: "绘制多边形",
      drawRectangle: "绘制矩形",
      editLayers: "编辑图层",
      deleteLayers: "删除图层",
      zoomIn: "放大",
      zoomOut: "缩小",
      drawStartPolygon: "点击开始绘制多边形。",
      drawStartRectangle: "点击并拖动绘制矩形。",
      drawContinue: "点击继续绘制形状。",
      drawFinish: "点击起点闭合形状。",
      drawCancel: "取消绘制",
      editSave: "保存修改",
      editCancel: "取消编辑",
      editClearAll: "清除全部图层",
      editEdit: "编辑图层",
      editRemove: "删除图层",
      editDisabled: "没有可编辑的图层",
      removeDisabled: "没有可删除的图层",
      editTooltip: "拖动控制点编辑边界。",
      removeTooltip: "点击边界将其删除。",
      findView: "定位我的视图",
      loadGeoJson: "载入 GeoJSON",
      tileState: "OSM 瓦片不可用，离线边界仍可使用。",
      attribution: "OpenStreetMap 贡献者 / Natural Earth",
      selectSite: "选择工作场地",
      selectSiteHelp: "请先选择边界。网络请求只会发送到本地服务。",
      boundary: "边界",
      notSelected: "未选择",
      readyToSave: "可以保存",
      west: "西",
      south: "南",
      east: "东",
      north: "北",
      drawBoundaryHelp: "请在地图上绘制矩形或多边形。",
      featureSingle: "{count} 个要素，约 {width} x {height} km。",
      featurePlural: "{count} 个要素，约 {width} x {height} km。",
      saveBoundary: "保存边界",
      planOsm: "规划 OSM",
      planDem: "规划 DEM",
      findPlace: "查找地点",
      placePlaceholder: "城市、地址或地标",
      search: "搜索",
      osmSource: "OSM 来源",
      osmOverpass: "Overpass，小范围",
      osmLocal: "本地 OSM 或 PBF",
      osmGeofabrik: "Geofabrik PBF 提取",
      osmHelp: "Overpass 无需登录。大范围场地建议使用本地 PBF。",
      terrainSource: "地形来源",
      demCopernicus: "Copernicus GLO-30",
      demSrtm: "USGS SRTM 30 m",
      demNasadem: "NASADEM 30 m",
      demLocal: "本地 GeoTIFF 或 ASCII 网格",
      geeHelp: "GEE 使用本机 Earth Engine 会话和项目。",
      geeProject: "GEE 项目 ID",
      optional: "可选",
      terrainPrecision: "地形精度",
      draft: "草稿",
      standard: "标准",
      fine: "精细",
      draftNote: "目标采样 30 m，适合大范围快速预览。",
      standardNote: "目标采样 10 m，实际精度受源数据分辨率限制。",
      fineNote: "目标采样 3 m，源数据较粗时会明确标注插值。",
      contours: "等高线：{value}。",
      credentialsTitle: "凭据不进入 skill",
      credentialsHelp: "OSM 是公开数据。GEE 可能要求在本机授权并提供项目 ID。这里不会保存 token。",
      map: "地图",
      extent: "范围",
      readyForBoundary: "等待选择边界。",
      boundaryReady: "边界已就绪。请检查设置后保存。",
      savingBoundary: "正在保存边界和设置...",
      boundarySaved: "边界和设置已保存。",
      selectionToast: "选址已保存到本地数据目录。",
      preparingRequest: "正在准备 {kind} 请求...",
      planReady: "{kind} 计划已就绪。",
      planToast: "{kind} 计划已写入数据目录。",
      searching: "正在搜索...",
      noPlace: "没有找到地点。",
      placeFound: "已找到地点。",
      workingExtent: "工作范围",
      extentHelp: "此平面只显示选定范围。获取 DEM 并完成 Rhino 构建后才会出现地形。",
      backToMap: "返回地图",
      extentPreview: "选定场地范围预览",
      previewEmpty: "绘制边界后查看工作范围。",
      extentOnly: "仅显示范围",
      demNotLoaded: "DEM 尚未载入",
      offlineWorld: "离线世界边界载入失败。",
      tilesUnavailableActivity: "OSM 瓦片不可用，但离线边界和本地 GeoJSON 仍可使用。",
      boundaryCleared: "边界已清除。",
      geojsonLoaded: "GeoJSON 边界已载入。",
      locationUnavailable: "当前浏览器不支持定位。",
      locationDenied: "定位权限未获允许。",
      offlineActivity: "本地服务不可用。仍可绘制并导出 GeoJSON 文件。",
      requestFailed: "请求失败：{message}"
    }
  };
  const precisionInfo = {
    draft: { sample: "30 m", contour: "20 m", noteKey: "draftNote" },
    standard: { sample: "10 m", contour: "10 m", noteKey: "standardNote" },
    fine: { sample: "3 m", contour: "5 m", noteKey: "fineNote" }
  };
  const state = {
    map: null, drawn: null, boundary: null, bbox: null, theme: "auto", saving: false,
    language: "en", activity: { key: "readyForBoundary", kind: "", params: {} },
    connection: "localService", searchMessage: null
  };
  const el = (id) => document.getElementById(id);

  function t(key, params = {}) {
    const template = messages[state.language]?.[key] ?? messages.en[key] ?? key;
    return Object.entries(params).reduce((text, [name, value]) => text.replaceAll(`{${name}}`, String(value)), template);
  }

  function setActivity(key, kind = "", params = {}) {
    state.activity = { key, kind, params };
    const node = el("activity-message");
    node.textContent = t(key, params);
    node.className = `activity-message${kind ? ` is-${kind}` : ""}`;
  }

  function setConnection(key) {
    state.connection = key;
    el("connection-state").textContent = t(key);
  }

  function setSearchMessage(key, params = {}) {
    state.searchMessage = { key, params };
    el("search-message").textContent = t(key, params);
  }

  function toast(key, params = {}) {
    const node = el("toast");
    node.textContent = t(key, params);
    node.hidden = false;
    window.clearTimeout(toast.timer);
    toast.timer = window.setTimeout(() => { node.hidden = true; }, 3800);
  }

  function formatCoord(value) {
    return Number.isFinite(value) ? value.toFixed(5) : "-";
  }

  function boundsFromGeometry(geometry) {
    const bbox = [Infinity, Infinity, -Infinity, -Infinity];
    const visit = (value) => {
      if (!Array.isArray(value) || !value.length) return;
      if (typeof value[0] === "number") {
        bbox[0] = Math.min(bbox[0], value[0]);
        bbox[1] = Math.min(bbox[1], value[1]);
        bbox[2] = Math.max(bbox[2], value[0]);
        bbox[3] = Math.max(bbox[3], value[1]);
        return;
      }
      value.forEach(visit);
    };
    visit(geometry.coordinates);
    return bbox.every(Number.isFinite) ? bbox : null;
  }

  function normalizeBoundary(payload) {
    const source = payload.type === "FeatureCollection"
      ? payload
      : payload.type === "Feature" ? { type: "FeatureCollection", features: [payload] } : null;
    if (!source || !Array.isArray(source.features)) throw new Error("invalidBoundaryType");
    const features = source.features.filter((feature) => ["Polygon", "MultiPolygon"].includes(feature?.geometry?.type));
    if (!features.length) throw new Error("noPolygon");
    const bbox = [Infinity, Infinity, -Infinity, -Infinity];
    features.forEach((feature) => {
      const next = boundsFromGeometry(feature.geometry);
      if (!next) return;
      bbox[0] = Math.min(bbox[0], next[0]); bbox[1] = Math.min(bbox[1], next[1]);
      bbox[2] = Math.max(bbox[2], next[2]); bbox[3] = Math.max(bbox[3], next[3]);
    });
    if (!bbox.every(Number.isFinite)) throw new Error("noBoundaryCoords");
    return { type: "FeatureCollection", features, bbox };
  }

  function boundaryToLayer(featureCollection) {
    if (!state.map || !window.L) return;
    if (state.drawn) state.drawn.clearLayers();
    if (!state.drawn) state.drawn = new L.FeatureGroup().addTo(state.map);
    L.geoJSON(featureCollection, { style: { color: "#3d64d8", weight: 2, fillColor: "#3d64d8", fillOpacity: 0.12 } }).eachLayer((layer) => state.drawn.addLayer(layer));
    const bounds = state.drawn.getBounds();
    if (bounds.isValid()) state.map.fitBounds(bounds.pad(0.2));
  }

  function setBoundary(featureCollection) {
    const normalized = normalizeBoundary(featureCollection);
    state.boundary = { type: "FeatureCollection", features: normalized.features };
    state.bbox = normalized.bbox;
    updateBoundaryReadout();
    ["save-selection", "plan-osm", "plan-dem"].forEach((id) => { el(id).disabled = false; });
    boundaryToLayer(state.boundary);
    drawPreview();
    setActivity("boundaryReady", "success");
  }

  function updateBoundaryReadout() {
    ["west", "south", "east", "north"].forEach((key, index) => {
      el(`bbox-${key}`).textContent = state.bbox ? formatCoord(state.bbox[index]) : "-";
    });
    if (!state.bbox) {
      el("boundary-state").textContent = t("notSelected");
      el("boundary-state").classList.remove("is-ready");
      el("area-readout").textContent = t("drawBoundaryHelp");
      return;
    }
    const width = Math.abs(state.bbox[2] - state.bbox[0]) * 111.32;
    const height = Math.abs(state.bbox[3] - state.bbox[1]) * 110.54;
    const key = state.boundary.features.length === 1 ? "featureSingle" : "featurePlural";
    el("boundary-state").textContent = t("readyToSave");
    el("boundary-state").classList.add("is-ready");
    el("area-readout").textContent = t(key, { count: state.boundary.features.length, width: width.toFixed(1), height: height.toFixed(1) });
  }

  function updatePrecisionNote() {
    const precision = document.querySelector('input[name="precision"]:checked')?.value || "standard";
    const info = precisionInfo[precision];
    el("precision-note").textContent = `${t(info.noteKey)} ${t("contours", { value: info.contour })}`;
  }

  function getSettings() {
    const precision = document.querySelector('input[name="precision"]:checked')?.value || "standard";
    return {
      osm_provider: el("osm-provider").value,
      dem_dataset: el("dem-dataset").value,
      gee_project: el("gee-project").value.trim() || null,
      precision_preset: precision,
      sample_step_m: precisionInfo[precision].sample,
      contour_interval_m: precisionInfo[precision].contour
    };
  }

  async function postJson(path, body) {
    const response = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.message || result.error || `Request failed (${response.status})`);
    return result;
  }

  async function saveSelection() {
    if (!state.boundary || state.saving) return;
    state.saving = true;
    el("save-selection").disabled = true;
    setActivity("savingBoundary");
    try {
      const result = await postJson("/api/selection", { boundary: state.boundary, ...getSettings() });
      setActivity("boundarySaved", "success");
      toast("selectionToast");
      setConnection("selectionSaved");
      return result;
    } catch (error) {
      setActivity("requestFailed", "error", { message: error.message });
      toast("requestFailed", { message: error.message });
      return null;
    } finally {
      state.saving = false;
      el("save-selection").disabled = false;
    }
  }

  async function plan(kind) {
    if (!state.boundary) return;
    const label = kind.toUpperCase();
    setActivity("preparingRequest", "", { kind: label });
    try {
      const saved = await saveSelection();
      if (!saved) return;
      const result = await postJson("/api/plan", { kind, ...getSettings() });
      setActivity("planReady", "success", { kind: label });
      toast("planToast", { kind: label });
    } catch (error) {
      setActivity("requestFailed", "error", { message: error.message });
    }
  }

  async function searchPlace(event) {
    event.preventDefault();
    const query = el("place-search").value.trim();
    if (!query) return;
    setSearchMessage("searching");
    try {
      const response = await fetch(`/api/geocode?q=${encodeURIComponent(query)}`);
      const result = await response.json();
      if (!response.ok || !result.results?.length) throw new Error("noPlace");
      const place = result.results[0];
      const bounds = place.boundingbox?.map(Number);
      if (bounds?.length === 4 && state.map) state.map.fitBounds([[bounds[0], bounds[2]], [bounds[1], bounds[3]]]);
      else if (state.map) state.map.setView([Number(place.lat), Number(place.lon)], 13);
      setSearchMessage(place.display_name || "placeFound");
    } catch (error) {
      setSearchMessage(messages.en[error.message] ? error.message : "requestFailed", messages.en[error.message] ? {} : { message: error.message });
    }
  }

  function drawPreview() {
    const canvas = el("preview-canvas");
    const context = canvas.getContext("2d");
    if (!context) return;
    const width = canvas.width; const height = canvas.height;
    context.clearRect(0, 0, width, height);
    context.fillStyle = "#202a35"; context.fillRect(0, 0, width, height);
    if (!state.bbox) { el("preview-empty").hidden = false; return; }
    el("preview-empty").hidden = true;
    const pad = 72; const cols = 28; const rows = 16;
    const innerW = width - pad * 2; const innerH = height - pad * 2;
    const bboxWidth = Math.max(0.000001, Math.abs(state.bbox[2] - state.bbox[0]));
    const bboxHeight = Math.max(0.000001, Math.abs(state.bbox[3] - state.bbox[1]));
    const aspect = Math.max(0.35, Math.min(2.8, bboxWidth / bboxHeight));
    const project = (x, y) => [width / 2 + (x * aspect - y) * innerW / cols * 0.58, height * 0.66 + (x * aspect + y) * innerH / rows * 0.2];
    for (let y = 0; y < rows; y += 1) {
      for (let x = 0; x < cols; x += 1) {
        const a = project(x - cols / 2, y - rows / 2);
        const b = project(x + 1 - cols / 2, y - rows / 2);
        const c = project(x + 1 - cols / 2, y + 1 - rows / 2);
        const d = project(x - cols / 2, y + 1 - rows / 2);
        context.beginPath(); context.moveTo(...a); context.lineTo(...b); context.lineTo(...c); context.lineTo(...d); context.closePath();
        context.strokeStyle = "rgba(147, 175, 208, .22)"; context.lineWidth = 1; context.stroke();
      }
    }
    context.fillStyle = "#8ca9ff"; context.font = "600 18px Segoe UI, sans-serif";
    context.fillText(t("extentOnly"), 40, 46);
    context.fillStyle = "#a9b9cd"; context.font = "13px Segoe UI, sans-serif";
    context.fillText(`${formatCoord(state.bbox[0])}, ${formatCoord(state.bbox[1])} to ${formatCoord(state.bbox[2])}, ${formatCoord(state.bbox[3])}`, 40, 69);
    context.fillStyle = "rgba(140, 169, 255, .7)"; context.fillRect(40, height - 34, 130, 2);
    context.fillStyle = "#a9b9cd"; context.fillText(t("demNotLoaded"), 182, height - 28);
  }

  function applyLeafletLocale() {
    if (!window.L) return;
    const local = L.drawLocal;
    if (local?.draw?.toolbar?.buttons) Object.assign(local.draw.toolbar.buttons, {
      polygon: t("drawPolygon"), rectangle: t("drawRectangle")
    });
    if (local?.draw?.toolbar?.actions) Object.assign(local.draw.toolbar.actions, {
      title: t("drawCancel"), text: t("drawCancel")
    });
    if (local?.draw?.handlers?.polygon?.tooltip) Object.assign(local.draw.handlers.polygon.tooltip, {
      start: t("drawStartPolygon"), cont: t("drawContinue"), end: t("drawFinish")
    });
    if (local?.draw?.handlers?.rectangle?.tooltip) local.draw.handlers.rectangle.tooltip.start = t("drawStartRectangle");
    if (local?.edit?.toolbar?.actions) Object.assign(local.edit.toolbar.actions, {
      save: { title: t("editSave"), text: t("editSave") },
      cancel: { title: t("editCancel"), text: t("editCancel") },
      clearAll: { title: t("editClearAll"), text: t("editClearAll") }
    });
    if (local?.edit?.toolbar?.buttons) Object.assign(local.edit.toolbar.buttons, {
      edit: t("editEdit"), editDisabled: t("editDisabled"), remove: t("editRemove"), removeDisabled: t("removeDisabled")
    });
    if (local?.edit?.handlers?.edit?.tooltip) Object.assign(local.edit.handlers.edit.tooltip, { text: t("editTooltip") });
    if (local?.edit?.handlers?.remove?.tooltip) local.edit.handlers.remove.tooltip.text = t("removeTooltip");
    const labels = [
      [".leaflet-draw-draw-polygon", "drawPolygon"], [".leaflet-draw-draw-rectangle", "drawRectangle"],
      [".leaflet-draw-edit-edit", "editLayers"], [".leaflet-draw-edit-remove", "deleteLayers"],
      [".leaflet-control-zoom-in", "zoomIn"], [".leaflet-control-zoom-out", "zoomOut"]
    ];
    labels.forEach(([selector, key]) => document.querySelectorAll(selector).forEach((node) => {
      node.title = t(key); node.setAttribute("aria-label", t(key));
      const screenReaderText = node.querySelector(".sr-only");
      if (screenReaderText) screenReaderText.textContent = t(key);
    }));
  }

  function updateThemeToggle() {
    const hasDarkTheme = document.documentElement.dataset.theme === "dark" ||
      (!document.documentElement.dataset.theme && window.matchMedia?.("(prefers-color-scheme: dark)").matches);
    el("theme-toggle").textContent = t(hasDarkTheme ? "lightMode" : "darkMode");
    el("theme-toggle").setAttribute("aria-pressed", String(hasDarkTheme));
  }

  function preferredLanguage() {
    try {
      const stored = window.localStorage.getItem("rhino-site-language");
      if (stored === "en" || stored === "zh") return stored;
    } catch (_) { /* local preference is optional */ }
    return navigator.language?.toLowerCase().startsWith("zh") ? "zh" : "en";
  }

  function applyLanguage(language) {
    state.language = language === "zh" ? "zh" : "en";
    document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
    document.title = t("documentTitle");
    document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t(node.dataset.i18n); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => { node.placeholder = t(node.dataset.i18nPlaceholder); });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((node) => { node.setAttribute("aria-label", t(node.dataset.i18nAriaLabel)); });
    document.querySelectorAll("[data-language]").forEach((node) => {
      const selected = node.dataset.language === state.language;
      const label = node.dataset.language === "zh" ? t("languageChinese") : t("languageEnglish");
      node.classList.toggle("is-active", selected);
      node.setAttribute("aria-pressed", String(selected));
      node.setAttribute("aria-label", label);
      node.title = label;
    });
    setConnection(state.connection);
    setActivity(state.activity.key, state.activity.kind, state.activity.params);
    if (state.searchMessage) setSearchMessage(state.searchMessage.key, state.searchMessage.params);
    updateBoundaryReadout();
    updatePrecisionNote();
    updateThemeToggle();
    applyLeafletLocale();
    drawPreview();
    try { window.localStorage.setItem("rhino-site-language", state.language); } catch (_) { /* optional */ }
  }

  function toggleTheme() {
    const hasDarkTheme = document.documentElement.dataset.theme === "dark" ||
      (!document.documentElement.dataset.theme && window.matchMedia?.("(prefers-color-scheme: dark)").matches);
    document.documentElement.dataset.theme = hasDarkTheme ? "light" : "dark";
    updateThemeToggle();
  }

  function showPreview(show) {
    const workbench = document.querySelector(".workbench");
    const panel = el("preview-panel");
    workbench.hidden = show;
    panel.hidden = !show;
    el("map-tab").classList.toggle("is-active", !show);
    el("preview-tab").classList.toggle("is-active", show);
    el("map-tab").setAttribute("aria-pressed", String(!show));
    el("preview-tab").setAttribute("aria-pressed", String(show));
    if (show) {
      drawPreview();
      el("close-preview").focus();
    } else {
      el("map-tab").focus();
    }
  }

  async function loadExisting() {
    try {
      const response = await fetch("/api/status");
        const result = await response.json();
      if (result.selection?.boundary) setBoundary(result.selection.boundary);
      if (result.selection) {
        if (result.selection.osm_provider) el("osm-provider").value = result.selection.osm_provider;
        if (result.selection.dem_dataset) el("dem-dataset").value = result.selection.dem_dataset;
        if (result.selection.gee_project) el("gee-project").value = result.selection.gee_project;
        if (result.selection.precision_preset) {
          const radio = document.querySelector(`input[name="precision"][value="${result.selection.precision_preset}"]`);
          if (radio) radio.checked = true;
        }
        drawPreview();
      }
    } catch (_) {
      setConnection("offlineMode");
      setActivity("offlineActivity", "error");
    }
  }

  function initMap() {
    if (!window.L) { el("map-fallback").hidden = false; return; }
    applyLeafletLocale();
    state.map = L.map("map", { zoomControl: false, attributionControl: false }).setView([20, 0], 2);
    L.control.zoom({ position: "bottomright" }).addTo(state.map);
    state.map.createPane("worldPane");
    state.map.getPane("worldPane").style.zIndex = "180";
    state.map.getPane("worldPane").style.pointerEvents = "none";
    fetch("/vendor/countries-110m.json")
      .then((response) => response.json())
      .then((topology) => {
        if (!window.topojson) return;
        const world = window.topojson.feature(topology, topology.objects.countries);
        L.geoJSON(world, {
          pane: "worldPane",
          interactive: false,
          style: { color: "#8794a5", weight: 0.65, fillColor: "#c9d3df", fillOpacity: 0.32 }
        }).addTo(state.map);
      })
      .catch(() => setActivity("offlineWorld", "error"));
    const tiles = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19 }).addTo(state.map);
    let tileErrors = 0;
    let tileLoads = 0;
    tiles.on("tileerror", () => {
      tileErrors += 1;
      if (tileErrors === 3 && tileLoads === 0) {
        el("tile-state").hidden = false;
        setActivity("tilesUnavailableActivity", "error");
      }
    });
    tiles.on("tileload", () => { tileLoads += 1; el("tile-state").hidden = true; });
    state.drawn = new L.FeatureGroup().addTo(state.map);
    state.map.addControl(new L.Control.Draw({ position: "bottomleft", edit: { featureGroup: state.drawn }, draw: { polyline: false, circle: false, circlemarker: false, marker: false } }));
    state.map.on(L.Draw.Event.CREATED, (event) => setBoundary(event.layer.toGeoJSON()));
    state.map.on(L.Draw.Event.EDITED, (event) => { event.layers.eachLayer((layer) => setBoundary(layer.toGeoJSON())); });
    state.map.on(L.Draw.Event.DELETED, () => {
      state.boundary = null; state.bbox = null;
      ["save-selection", "plan-osm", "plan-dem"].forEach((id) => { el(id).disabled = true; });
      updateBoundaryReadout(); drawPreview(); setActivity("boundaryCleared");
    });
    applyLeafletLocale();
  }

  function bind() {
    el("search-form").addEventListener("submit", searchPlace);
    el("save-selection").addEventListener("click", saveSelection);
    el("plan-osm").addEventListener("click", () => plan("osm"));
    el("plan-dem").addEventListener("click", () => plan("dem"));
    el("preview-tab").addEventListener("click", () => showPreview(true));
    el("map-tab").addEventListener("click", () => showPreview(false));
    el("close-preview").addEventListener("click", () => showPreview(false));
    el("load-boundary-button").addEventListener("click", () => el("boundary-file").click());
    el("boundary-file").addEventListener("change", async (event) => {
      const file = event.target.files?.[0]; if (!file) return;
      try { setBoundary(JSON.parse(await file.text())); toast("geojsonLoaded"); }
      catch (error) { setActivity(messages.en[error.message] ? error.message : "requestFailed", "error", messages.en[error.message] ? {} : { message: error.message }); }
      event.target.value = "";
    });
    el("locate-button").addEventListener("click", () => {
      if (!state.map || !navigator.geolocation) { toast("locationUnavailable"); return; }
      navigator.geolocation.getCurrentPosition((position) => state.map.setView([position.coords.latitude, position.coords.longitude], 13), () => toast("locationDenied"));
    });
    document.querySelectorAll('input[name="precision"]').forEach((radio) => radio.addEventListener("change", () => { updatePrecisionNote(); drawPreview(); }));
    document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => applyLanguage(button.dataset.language)));
    el("theme-toggle").addEventListener("click", toggleTheme);
  }

  bind(); applyLanguage(preferredLanguage()); initMap(); loadExisting();
})();
