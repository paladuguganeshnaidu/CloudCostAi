document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('prediction-form');
  const cpuSlider = document.querySelector('input[name="cpu"]');
  const memorySlider = document.querySelector('input[name="memory"]');
  const cpuValue = document.getElementById('cpu-value');
  const memoryValue = document.getElementById('memory-value');
  const categoryData = {
    service: ['AI Platform','BigQuery','Cloud Armor','Cloud Build','Cloud CDN','Cloud Data Fusion','Cloud Dataproc','Cloud Endpoints','Cloud Functions','Cloud Interconnect','Cloud Load Balancing','Cloud Memorystore','Cloud NAT','Cloud Run','Cloud SQL','Cloud Spanner','Cloud Storage','Cloud VPC','Cloud VPN','Compute Engine','Container Registry','Dataflow','Firestore','Kubernetes Engine','Pub/Sub'],
    region: ['asia-east1','asia-northeast1','asia-southeast1','australia-southeast1','europe-north1','europe-west1','europe-west3','northamerica-northeast1','southamerica-east1','us-central1','us-east1','us-west1'],
    unit: ['GB','Hours','Requests']
  };
  if (form) {
    form.addEventListener('submit', function () {
      const btn = document.getElementById('predict-button');
      if (btn) {
        btn.setAttribute('disabled', 'disabled');
        const spinner = btn.querySelector('.spinner');
        const thinking = btn.querySelector('.thinking-pill');
        const label = btn.querySelector('.btn-label');
        if (spinner) spinner.classList.remove('d-none');
        if (thinking) thinking.classList.remove('d-none');
        if (label) label.textContent = 'Analyzing';
      }
    });
  }

  if (cpuSlider && cpuValue) {
    const syncValue = () => {
      cpuValue.textContent = `${cpuSlider.value}%`;
    };
    syncValue();
    cpuSlider.addEventListener('input', syncValue);
  }

  if (memorySlider && memoryValue) {
    const syncValue = () => {
      memoryValue.textContent = `${memorySlider.value}%`;
    };
    syncValue();
    memorySlider.addEventListener('input', syncValue);
  }

  if (window.lucide) {
    window.lucide.createIcons();
  }

  function initSearchSelect(inputId, hiddenName, optionsId, values) {
    const input = document.getElementById(inputId);
    const hidden = document.querySelector(`input[name="${hiddenName}"]`);
    const dropdown = document.getElementById(optionsId);
    if (!input || !hidden || !dropdown) return;

    function renderOptions(query = '') {
      const normalized = query.toLowerCase();
      const filtered = values.filter((value) => value.toLowerCase().includes(normalized));
      dropdown.innerHTML = filtered.length ? filtered.map((value) => `<button type="button" class="select-option" data-value="${value}">${value}</button>`).join('') : '<span class="select-empty">No matching option</span>';
      dropdown.style.display = filtered.length ? 'block' : 'block';
      input.setAttribute('aria-expanded', 'true');
      input.setAttribute('aria-activedescendant', filtered[0] ? filtered[0] : '');
    }

    input.addEventListener('focus', () => renderOptions(input.value));
    input.addEventListener('input', () => renderOptions(input.value));
    input.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        dropdown.style.display = 'none';
        input.setAttribute('aria-expanded', 'false');
        return;
      }
      if (event.key === 'Enter') {
        event.preventDefault();
        const firstOption = dropdown.querySelector('.select-option');
        if (firstOption) {
          const selectedValue = firstOption.getAttribute('data-value');
          input.value = selectedValue;
          hidden.value = selectedValue;
          dropdown.style.display = 'none';
          input.setAttribute('aria-expanded', 'false');
        }
      }
    });

    dropdown.addEventListener('click', (event) => {
      const option = event.target.closest('.select-option');
      if (!option) return;
      const selectedValue = option.getAttribute('data-value');
      input.value = selectedValue;
      hidden.value = selectedValue;
      dropdown.style.display = 'none';
      input.setAttribute('aria-expanded', 'false');
    });

    document.addEventListener('click', (event) => {
      if (!input.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.style.display = 'none';
        input.setAttribute('aria-expanded', 'false');
      }
    });

    input.addEventListener('blur', () => {
      setTimeout(() => {
        dropdown.style.display = 'none';
        input.setAttribute('aria-expanded', 'false');
      }, 120);
    });
  }

  initSearchSelect('service-search', 'service_name', 'service-options', categoryData.service);
  initSearchSelect('region-search', 'region', 'region-options', categoryData.region);
  initSearchSelect('unit-search', 'usage_unit', 'unit-options', categoryData.unit);

  const themeToggle = document.getElementById('theme-toggle');
  const savedTheme = localStorage.getItem('cloudcostai-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = savedTheme || (prefersDark ? 'dark' : 'light');
  document.body.setAttribute('data-theme', theme);
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.body.setAttribute('data-theme', current);
      localStorage.setItem('cloudcostai-theme', current);
      if (window.lucide) window.lucide.createIcons();
    });
  }
});

function clearPredictionForm() {
  const form = document.getElementById('prediction-form');
  if (!form) return;
  form.reset();
}

export {};

// Admin delete button handling
document.addEventListener('click', async (e) => {
  const target = e.target;
  if (target && target.classList && target.classList.contains('delete-btn')) {
    const id = target.getAttribute('data-id');
    if (!id) return;
    if (!confirm('Delete this prediction?')) return;
    try {
      target.setAttribute('disabled', 'disabled');
      const res = await fetch(`/api/delete/${id}`, { method: 'DELETE' });
      if (res.ok) {
        const row = target.closest('tr');
        if (row) row.remove();
        alert('Prediction deleted');
      } else {
        const data = await res.json();
        alert('Delete failed: ' + (data.message || res.statusText));
      }
    } catch (err) {
      alert('Delete failed: ' + err);
    } finally {
      target.removeAttribute('disabled');
    }
  }
});

// Utility: format number as INR
function formatINR(value) {
  try {
    return '₹ ' + Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  } catch (e) {
    return value;
  }
}

// Update table rows from JSON rows
function updateHistoryTable(rows) {
  const tbody = document.getElementById('history-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  if (!rows || rows.length === 0) {
    const tr = document.createElement('tr');
    tr.id = 'no-predictions-row';
    tr.innerHTML = '<td colspan="6" class="text-center text-muted">No predictions available.</td>';
    tbody.appendChild(tr);
    return;
  }
  rows.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.id}</td>
      <td>${item.timestamp}</td>
      <td>${item.service_name}</td>
      <td>${item.region}</td>
      <td>${formatINR(item.predicted_cost)}</td>
      <td><button class="row-action delete-btn" data-id="${item.id}">Delete</button></td>
    `;
    tbody.appendChild(tr);
  });
}

// Fetch history and update table
async function fetchAndUpdateHistory(query) {
  const q = query || document.getElementById('search-input')?.value || '';
  const res = await fetch(`/history?q=${encodeURIComponent(q)}`);
  if (!res.ok) return;
  const data = await res.json();
  updateHistoryTable(data.predictions || []);
}

// Search button handler
document.getElementById('search-button')?.addEventListener('click', (e) => {
  fetchAndUpdateHistory();
});

// Export CSV for current filter
document.getElementById('export-csv')?.addEventListener('click', async () => {
  const q = document.getElementById('search-input')?.value || '';
  const url = `/download?q=${encodeURIComponent(q)}`;
  const a = document.createElement('a');
  a.href = url;
  a.download = 'cloudcostai_predictions.csv';
  document.body.appendChild(a);
  a.click();
  a.remove();
});

// Chart click handlers: drilldown by label
function bindChartDrilldown(chart, type) {
  chart.options.onClick = async (evt, elements) => {
    if (!elements || !elements.length) return;
    const idx = elements[0].index;
    const label = chart.data.labels[idx];
    let q = '';
    if (type === 'daily') q = label;
    if (type === 'service') q = label;
    if (type === 'region') q = label;
    document.getElementById('search-input').value = q;
    await fetchAndUpdateHistory(q);
  };
}

// After charts created, bind drilldown
window.addEventListener('load', () => {
  if (window.dailyChart) bindChartDrilldown(window.dailyChart, 'daily');
  if (window.serviceChart) bindChartDrilldown(window.serviceChart, 'service');
  if (window.regionChart) bindChartDrilldown(window.regionChart, 'region');
});
