/**
 * Frontend script for ESP32-S3 MiniWeb Dashboard
 * Periodically polls /api/status and provides interactive LED ping testing.
 */

document.addEventListener("DOMContentLoaded", () => {
  const dot = document.getElementById("server-status-dot");
  const statusText = document.getElementById("server-status-text");
  const valIp = document.getElementById("val-ip");
  const valUptime = document.getElementById("val-uptime");
  const valHeap = document.getElementById("val-heap");
  const valRssi = document.getElementById("val-rssi");
  const btnPing = document.getElementById("btn-ping");
  const latencyText = document.getElementById("latency-text");
  const logList = document.getElementById("activity-log-list");
  const btnClearLog = document.getElementById("btn-clear-log");

  function formatUptime(seconds) {
    if (typeof seconds !== "number" || isNaN(seconds)) return "--";
    const d = Math.floor(seconds / 86400);
    const h = Math.floor((seconds % 86400) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);

    const parts = [];
    if (d > 0) parts.push(`${d}d`);
    if (h > 0 || d > 0) parts.push(`${h}h`);
    if (m > 0 || h > 0 || d > 0) parts.push(`${m}m`);
    parts.push(`${s}s`);
    return parts.join(" ");
  }

  function formatBytes(bytes) {
    if (typeof bytes !== "number" || isNaN(bytes)) return "--";
    if (bytes >= 1048576) {
      return (bytes / 1048576).toFixed(2) + " MB";
    }
    return (bytes / 1024).toFixed(1) + " KB";
  }

  function addLog(message, isSuccess = true) {
    const time = new Date().toLocaleTimeString();
    const li = document.createElement("li");
    li.className = `log-item ${isSuccess ? "success" : "error"}`;
    li.textContent = `[${time}] ${message}`;
    logList.prepend(li);

    while (logList.children.length > 8) {
      logList.removeChild(logList.lastChild);
    }
  }

  async function fetchStatus(isManualPing = false) {
    const startTime = performance.now();
    try {
      const response = await fetch("/api/status", { cache: "no-store" });
      const elapsed = Math.round(performance.now() - startTime);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      dot.classList.remove("disconnected");
      statusText.textContent = "Online";
      valIp.textContent = data.ip || window.location.hostname;
      valUptime.textContent = formatUptime(data.uptime_s);
      valHeap.textContent = formatBytes(data.free_heap);
      valRssi.textContent = data.rssi !== null && data.rssi !== undefined ? `${data.rssi} dBm` : "N/A";
      latencyText.textContent = `Latency: ${elapsed} ms`;

      if (isManualPing) {
        addLog(`Ping OK &bull; LED pulsed (${elapsed}ms)`);
      }
    } catch (err) {
      dot.classList.add("disconnected");
      statusText.textContent = "Offline";
      latencyText.textContent = "Latency: --";
      if (isManualPing) {
        addLog(`Ping failed: ${err.message}`, false);
      }
    }
  }

  btnPing.addEventListener("click", () => {
    btnPing.disabled = true;
    fetchStatus(true).finally(() => {
      setTimeout(() => {
        btnPing.disabled = false;
      }, 200);
    });
  });

  btnClearLog.addEventListener("click", () => {
    logList.innerHTML = "";
  });

  // Initial fetch and 3-second heartbeat polling
  fetchStatus(false);
  setInterval(() => fetchStatus(false), 3000);
});
