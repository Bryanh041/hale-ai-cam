const els = {
  video: document.getElementById("video"),
  result: document.getElementById("result"),
  canvas: document.getElementById("canvas"),
  overlay: document.getElementById("overlay"),
  startCam: document.getElementById("startCam"),
  capture: document.getElementById("capture"),
  sample: document.getElementById("sample"),
  reset: document.getElementById("reset"),
  faceCount: document.getElementById("faceCount"),
  detectionList: document.getElementById("detectionList"),
  statusDot: document.getElementById("statusDot"),
  statusText: document.getElementById("statusText"),
};

let stream = null;

async function checkHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    if (data.status === "ok") {
      els.statusDot.classList.add("ok");
      els.statusText.textContent = `Online · v${data.version}`;
      return;
    }
    throw new Error("unhealthy");
  } catch (err) {
    els.statusDot.classList.add("err");
    els.statusText.textContent = "API offline";
  }
}

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    els.video.srcObject = stream;
    els.video.hidden = false;
    els.result.hidden = true;
    els.reset.hidden = true;
    els.capture.disabled = false;
    els.startCam.textContent = "Camera running";
    els.startCam.disabled = true;
  } catch (err) {
    alert("Could not access the camera: " + err.message);
  }
}

function showOverlay(show) {
  els.overlay.hidden = !show;
}

function renderResult(data) {
  els.faceCount.textContent = data.count;
  els.detectionList.innerHTML = "";

  if (!data.detections.length) {
    const li = document.createElement("li");
    li.className = "empty";
    li.textContent = "No faces detected in this frame.";
    els.detectionList.appendChild(li);
    return;
  }

  data.detections.forEach((d, i) => {
    const li = document.createElement("li");
    li.innerHTML =
      `<span class="tag">Face ${i + 1}</span> · ` +
      `${d.width}×${d.height}px at (${d.x}, ${d.y}) · ` +
      `<span class="tag">${d.eyes.length}</span> eye(s)`;
    els.detectionList.appendChild(li);
  });
}

function displayAnnotated(dataUrl) {
  els.result.src = dataUrl;
  els.result.hidden = false;
  els.video.hidden = true;
  els.reset.hidden = false;
}

async function analyzeBlob(blob) {
  const form = new FormData();
  form.append("file", blob, "frame.png");
  showOverlay(true);
  try {
    const res = await fetch("/api/detect", { method: "POST", body: form });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    renderResult(data);
    displayAnnotated(data.annotatedImage);
  } catch (err) {
    alert("Detection failed: " + err.message);
  } finally {
    showOverlay(false);
  }
}

function captureFrame() {
  const w = els.video.videoWidth;
  const h = els.video.videoHeight;
  if (!w || !h) {
    alert("Camera is not ready yet.");
    return;
  }
  els.canvas.width = w;
  els.canvas.height = h;
  const ctx = els.canvas.getContext("2d");
  ctx.drawImage(els.video, 0, 0, w, h);
  els.canvas.toBlob((blob) => analyzeBlob(blob), "image/png");
}

async function analyzeSample() {
  showOverlay(true);
  try {
    const res = await fetch("/sample.jpg");
    const blob = await res.blob();
    await analyzeBlob(blob);
  } catch (err) {
    showOverlay(false);
    alert("Could not load sample image: " + err.message);
  }
}

function backToLive() {
  els.result.hidden = true;
  els.reset.hidden = true;
  if (stream) {
    els.video.hidden = false;
  }
}

els.startCam.addEventListener("click", startCamera);
els.capture.addEventListener("click", captureFrame);
els.sample.addEventListener("click", analyzeSample);
els.reset.addEventListener("click", backToLive);

checkHealth();
