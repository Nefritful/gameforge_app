(function(){
  // ---------------- modal helpers ----------------
  function qs(sel, root=document){ return root.querySelector(sel); }
  function qsa(sel, root=document){ return Array.from(root.querySelectorAll(sel)); }

  qsa("[data-modal-target]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      const target = btn.getAttribute("data-modal-target");
      const modal = qs(target);
      if(modal) modal.classList.add("is-open");
    });
  });

  qsa("[data-modal-close]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      const modal = btn.closest(".modal");
      if(modal) modal.classList.remove("is-open");
      authReset();
    });
  });

  // auth switching
  const modal = qs("#authModal");
  const loginForm = qs("#loginForm");
  const registerForm = qs("#registerForm");
  const titleEl = qs("[data-auth-title]", modal);
  const backBtn = qs("[data-auth-back]", modal);
  const switchLink = qs("[data-auth-switch='register']", modal);

  function showError(form, msg){
    const err = qs("[data-auth-error]", form);
    if(!err) return;
    err.textContent = msg;
    err.style.display = "block";
  }
  function clearError(form){
    const err = qs("[data-auth-error]", form);
    if(!err) return;
    err.style.display = "none";
    err.textContent = "";
  }

  function authReset(){
    if(!modal) return;
    if(loginForm) { loginForm.style.display = ""; clearError(loginForm); }
    if(registerForm) { registerForm.style.display = "none"; clearError(registerForm); }
    if(titleEl) titleEl.textContent = "Вход";
    if(backBtn) backBtn.style.display = "none";
  }

  if(switchLink){
    switchLink.addEventListener("click", (e)=>{
      e.preventDefault();
      if(loginForm) loginForm.style.display = "none";
      if(registerForm) registerForm.style.display = "";
      if(titleEl) titleEl.textContent = "Регистрация";
      if(backBtn) backBtn.style.display = "";
    });
  }

  if(backBtn){
    backBtn.addEventListener("click", ()=>{
      authReset();
    });
  }

  async function postJson(url, data){
    const res = await fetch(url, {
      method:"POST",
      headers: { "Content-Type":"application/json" },
      body: JSON.stringify(data),
    });
    const j = await res.json().catch(()=>({ok:false, error:"bad json"}));
    if(!res.ok) throw new Error(j.error || "error");
    return j;
  }

  if(loginForm){
    loginForm.addEventListener("submit", async (e)=>{
      e.preventDefault();
      clearError(loginForm);
      const fd = new FormData(loginForm);
      try{
        await postJson("/auth/login/", { email: fd.get("email"), password: fd.get("password") });
        window.location.reload();
      }catch(err){
        showError(loginForm, err.message || "Ошибка входа");
      }
    });
  }

  if(registerForm){
    registerForm.addEventListener("submit", async (e)=>{
      e.preventDefault();
      clearError(registerForm);
      const fd = new FormData(registerForm);
      try{
        await postJson("/auth/register/", { email: fd.get("email"), password: fd.get("password") });
        window.location.href = "/";
      }catch(err){
        showError(registerForm, err.message || "Ошибка регистрации");
      }
    });
  }

  // ---------------- editor page ----------------
  if(!window.GF || !window.GF.projectId) return;

  const projectId = window.GF.projectId;
  const sceneSelect = qs("#sceneSelect");
  const sceneTree = qs("#sceneTree");
  const filesTree = qs("#filesTree");
  const propsPanel = qs("#propsPanel");
  const stage = qs("#stage");
  const canvas = qs("#canvas");
  const saveBtn = qs("#saveSceneBtn");
  const createSceneBtn = qs("#createSceneBtn");
  const addFromTreeBtn = qs("#addFromTreeBtn");

  let state = {
    sceneId: sceneSelect ? sceneSelect.value : "level1",
    scene: { scene_id: "level1", entities: [] },
    selectedIdx: null,
  };

  function uid(prefix="e"){
    return prefix + "_" + Math.random().toString(16).slice(2) + "_" + Date.now().toString(16);
  }

  function safeJsonParse(s, fallback){
    try{ return JSON.parse(s); }catch{ return fallback; }
  }

  async function apiGetFile(key){
    const res = await fetch(`/api/projects/${projectId}/files/get?key=` + encodeURIComponent(key));
    const j = await res.json();
    if(!j.ok) throw new Error(j.error || "get failed");
    return j;
  }
  async function apiSaveFile(key, content){
    const res = await fetch(`/api/projects/${projectId}/files/save`, {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ key, content }),
    });
    const j = await res.json();
    if(!j.ok) throw new Error(j.error || "save failed");
    return j;
  }
  async function apiScenesList(){
    const res = await fetch(`/api/projects/${projectId}/scenes/list`);
    const j = await res.json();
    if(!j.ok) throw new Error(j.error || "list failed");
    return j.scenes || [];
  }
  async function apiSceneCreate(sceneId){
    const res = await fetch(`/api/projects/${projectId}/scenes/create`, {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ scene_id: sceneId }),
    });
    const j = await res.json();
    if(!j.ok) throw new Error(j.error || "create failed");
    return j;
  }

  function renderFilesTree(projectJsonStr){
    const files = [
      { key:"project_json", label:"project.json" },
      { key:`scene:${state.sceneId}`, label:`scene:${state.sceneId}` },
    ];
    filesTree.innerHTML = "";
    files.forEach(f=>{
      const el = document.createElement("div");
      el.className = "file";
      el.innerHTML = `<div class="k">${f.key}</div><div class="muted small">${f.label}</div>`;
      filesTree.appendChild(el);
    });
  }

  function renderSceneTree(){
    sceneTree.innerHTML = "";
    const root = document.createElement("div");
    root.className = "node";
    root.textContent = "SceneRoot";
    sceneTree.appendChild(root);

    state.scene.entities.forEach((e, idx)=>{
      const n = document.createElement("div");
      n.className = "node" + (state.selectedIdx === idx ? " is-active" : "");
      n.textContent = `${e.name || e.type || "Entity"}  (${e.base})`;
      n.addEventListener("click", ()=>{
        selectEntity(idx);
      });
      sceneTree.appendChild(n);
    });
  }

  function renderStage(){
    stage.innerHTML = "";
    state.scene.entities.forEach((e, idx)=>{
      const g = document.createElement("div");
      g.className = "gizmo" + (state.selectedIdx === idx ? " is-active" : "");
      const x = Math.round(e.transform?.x ?? 100);
      const y = Math.round(e.transform?.y ?? 100);
      g.style.left = x + "px";
      g.style.top = (stage.clientHeight - y) + "px"; // имитация Y вверх
      g.textContent = e.name || e.type || e.base;
      g.addEventListener("click", (ev)=>{
        ev.stopPropagation();
        selectEntity(idx);
      });
      stage.appendChild(g);
    });
  }

  function selectEntity(idx){
    state.selectedIdx = idx;
    renderSceneTree();
    renderStage();
    renderProps();
  }

  function updateEntityField(path, value){
    if(state.selectedIdx === null) return;
    const e = state.scene.entities[state.selectedIdx];
    const parts = path.split(".");
    let obj = e;
    for(let i=0;i<parts.length-1;i++){
      const p = parts[i];
      if(!(p in obj) || obj[p] === null) obj[p] = {};
      obj = obj[p];
    }
    obj[parts[parts.length-1]] = value;
    renderSceneTree();
    renderStage();
  }

  function num(v, def=0){
    const n = Number(v);
    return Number.isFinite(n) ? n : def;
  }

  function renderProps(){
    if(state.selectedIdx === null){
      propsPanel.innerHTML = `<div class="muted">Выбери объект на сцене.</div>`;
      return;
    }
    const e = state.scene.entities[state.selectedIdx];
    const t = e.transform || {x:200,y:200,rotation:0,scale:1};
    const v = e.velocity || {vx:0,vy:0};

    propsPanel.innerHTML = `
      <div class="strong">${e.name || e.base}</div>
      <div class="muted small">id: ${e.id}</div>
      <hr>
      <label class="field">
        <span class="field__label">Имя</span>
        <input class="input" value="${(e.name||"")}" data-bind="name">
      </label>

      <div class="grid2">
        <label class="field">
          <span class="field__label">X</span>
          <input class="input" type="number" value="${t.x}" data-bind="transform.x">
        </label>
        <label class="field">
          <span class="field__label">Y</span>
          <input class="input" type="number" value="${t.y}" data-bind="transform.y">
        </label>
      </div>

      <div class="grid2">
        <label class="field">
          <span class="field__label">Rotation</span>
          <input class="input" type="number" value="${t.rotation||0}" data-bind="transform.rotation">
        </label>
        <label class="field">
          <span class="field__label">Scale</span>
          <input class="input" type="number" step="0.1" value="${t.scale||1}" data-bind="transform.scale">
        </label>
      </div>

      <div class="grid2">
        <label class="field">
          <span class="field__label">Vx</span>
          <input class="input" type="number" value="${v.vx||0}" data-bind="velocity.vx">
        </label>
        <label class="field">
          <span class="field__label">Vy</span>
          <input class="input" type="number" value="${v.vy||0}" data-bind="velocity.vy">
        </label>
      </div>

      <label class="field">
        <span class="field__label">Texture ID</span>
        <input class="input" value="${(e.sprite?.texture_id||"")}" data-bind="sprite.texture_id" placeholder="player">
      </label>

      <label class="field">
        <span class="field__label">Base</span>
        <input class="input" value="${e.base}" disabled>
      </label>

      <button class="btn btn--danger btn--small" id="deleteEntityBtn">Удалить</button>
    `;

    propsPanel.querySelectorAll("[data-bind]").forEach(inp=>{
      inp.addEventListener("input", ()=>{
        const key = inp.getAttribute("data-bind");
        let val = inp.value;
        if(inp.type === "number") val = num(val, 0);
        updateEntityField(key, val);
      });
    });

    const delBtn = qs("#deleteEntityBtn", propsPanel);
    if(delBtn){
      delBtn.addEventListener("click", ()=>{
        if(state.selectedIdx === null) return;
        state.scene.entities.splice(state.selectedIdx, 1);
        state.selectedIdx = null;
        renderSceneTree(); renderStage(); renderProps();
      });
    }
  }

  function makeEntity(base){
    // base: Pawn/Object/Area/Ui
    const common = {
      id: uid("ent"),
      base,
      name: base,
      type: base,
      transform: { x: 220, y: 220, rotation: 0, scale: 1 },
      velocity: { vx: 0, vy: 0 },
      physics: {
        body: "dynamic", // dynamic/static/kinematic
        mass: 1.0,
        friction: 0.2,
        restitution: 0.0,
        collider: { shape:"box", w: 64, h: 64 },
      },
      sprite: { texture_id: "", width: 64, height: 64, layer: 1 },
      tags: [],
      components: {},
    };

    if(base === "Pawn"){
      common.player_controller = { enabled: true, speed: 260, scheme:"wasd" };
      common.camera_follow = { enabled: true, target: "self", lerp: 0.12 };
    }
    if(base === "Area"){
      common.physics.body = "static";
      common.area = {
        kind: "trigger", // trigger/light/zone
        trigger: { on_enter: [], on_exit: [] },
        light: { enabled: false, radius: 220, intensity: 1.0 },
      };
      common.sprite = { texture_id: "", width: 96, height: 96, layer: 0 };
    }
    if(base === "Ui"){
      common.ui = {
        widget: "panel", // panel/button/label/image
        anchor: "top_left",
        rect: { x: 20, y: 20, w: 220, h: 90 },
        text: { value: "UI", size: 16 },
        on_click: [],
      };
      // UI не обязана быть в мире (но пока оставим единый список)
      common.physics = { body:"none" };
      common.sprite = { texture_id: "", width: 0, height: 0, layer: 999 };
    }
    return common;
  }

  // ---------------- context menu ----------------
  let cm = null;
  function closeContextMenu(){
    if(cm){ cm.remove(); cm = null; }
  }
  function openContextMenu(x,y, onPick){
    closeContextMenu();
    cm = document.createElement("div");
    cm.className = "contextmenu";
    cm.style.left = x + "px";
    cm.style.top = y + "px";
    const items = ["Pawn","Object","Area","Ui"];
    items.forEach(it=>{
      const el = document.createElement("div");
      el.className = "item";
      el.textContent = "+ " + it;
      el.addEventListener("click", ()=>{
        onPick(it);
        closeContextMenu();
      });
      cm.appendChild(el);
    });
    document.body.appendChild(cm);
  }

  document.addEventListener("click", ()=> closeContextMenu());
  document.addEventListener("keydown", (e)=>{ if(e.key==="Escape") closeContextMenu(); });

  function addEntity(base){
    const e = makeEntity(base);
    state.scene.entities.push(e);
    selectEntity(state.scene.entities.length - 1);
  }

  if(stage){
    stage.addEventListener("contextmenu", (e)=>{
      e.preventDefault();
      openContextMenu(e.clientX, e.clientY, addEntity);
    });
    stage.addEventListener("click", ()=>{
      state.selectedIdx = null;
      renderSceneTree(); renderStage(); renderProps();
    });
  }
  if(addFromTreeBtn){
    addFromTreeBtn.addEventListener("click", (e)=>{
      const r = addFromTreeBtn.getBoundingClientRect();
      openContextMenu(r.left, r.bottom + 6, addEntity);
    });
  }

  if(createSceneBtn){
    createSceneBtn.addEventListener("click", async ()=>{
      const sceneId = prompt("ID новой сцены (например level2):");
      if(!sceneId) return;
      try{
        await apiSceneCreate(sceneId);
        const opt = document.createElement("option");
        opt.value = sceneId;
        opt.textContent = sceneId;
        sceneSelect.appendChild(opt);
        sceneSelect.value = sceneId;
        await loadScene(sceneId);
      }catch(err){
        alert(err.message || "Ошибка создания сцены");
      }
    });
  }

  async function loadScene(sceneId){
    state.sceneId = sceneId;
    const fileKey = `scene:${sceneId}`;
    const res = await apiGetFile(fileKey);
    const scene = safeJsonParse(res.content, { scene_id: sceneId, entities: [] });
    state.scene = scene;
    state.selectedIdx = null;

    renderSceneTree();
    renderStage();
    renderProps();

    // files tree (прочитаем project_json просто чтобы показать файл)
    try{
      const pj = await apiGetFile("project_json");
      renderFilesTree(pj.content);
    }catch{
      renderFilesTree("{}");
    }
  }

  if(sceneSelect){
    sceneSelect.addEventListener("change", async ()=>{
      await loadScene(sceneSelect.value);
    });
  }

  if(saveBtn){
    saveBtn.addEventListener("click", async ()=>{
      try{
        await apiSaveFile(`scene:${state.sceneId}`, state.scene);
        saveBtn.textContent = "Сохранено";
        setTimeout(()=> saveBtn.textContent = "Сохранить", 900);
      }catch(err){
        alert(err.message || "Ошибка сохранения");
      }
    });
  }

  // init
  (async ()=>{
    await loadScene(state.sceneId);
  })();
})();
