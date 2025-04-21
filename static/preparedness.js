document.addEventListener("DOMContentLoaded", function () {
  // const API_BASE = "http://127.0.0.1:5000"; // Update this
  const API_BASE = "http://127.0.0.1:5000/api";


  const stateSelect = document.getElementById("state");
  const disasterSelect = document.getElementById("disaster_type");
  const checklistContainer = document.getElementById("checklistContainer");
  const form = document.getElementById("prepForm");
  const resultBox = document.getElementById("result");

  const defaultStatesAndUTs = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
  ];

  const defaultDisasters = [
    "Flood", "Earthquake", "Landslide", "Drought", "Severe Storm",
    "Cyclone", "Heatwave", "Cold Wave", "Industrial Hazard"
  ];

  const fallbackChecklist = [
    "First Aid Kit", "Water Supply", "Emergency Food", "Flashlight", "Batteries", "Radio"
  ];

  let currentChecklist = [];

  // Populate states dropdown (from API or default)
  fetch(`${API_BASE}/states`)
    .then(res => res.json())
    .then(data => {
      const states = data.states || defaultStatesAndUTs;
      states.forEach(state => {
        const option = document.createElement("option");
        option.value = state;
        option.textContent = state;
        stateSelect.appendChild(option);
      });
    })
    .catch(() => {
      defaultStatesAndUTs.forEach(state => {
        const option = document.createElement("option");
        option.value = state;
        option.textContent = state;
        stateSelect.appendChild(option);
      });
    });

  // Populate disaster types when state is selected
  stateSelect.addEventListener("change", () => {
    const selectedState = stateSelect.value;
    disasterSelect.innerHTML = "";
    checklistContainer.innerHTML = "";
    resultBox.innerHTML = "";

    fetch(`${API_BASE}/disasters?state=${encodeURIComponent(selectedState)}`)
      .then(res => res.json())
      .then(data => {
        const disasters = data.disasters || defaultDisasters;
        disasters.forEach(disaster => {
          const option = document.createElement("option");
          option.value = disaster;
          option.textContent = disaster;
          disasterSelect.appendChild(option);
        });
      })
      .catch(() => {
        defaultDisasters.forEach(disaster => {
          const option = document.createElement("option");
          option.value = disaster;
          option.textContent = disaster;
          disasterSelect.appendChild(option);
        });
      });
  });

  // Load checklist on disaster type change
  disasterSelect.addEventListener("change", () => {
    const disasterType = disasterSelect.value;
    checklistContainer.innerHTML = "";
    resultBox.innerHTML = "";

    fetch(`${API_BASE}/checklist?disaster_type=${encodeURIComponent(disasterType)}`)
      .then(res => res.json())
      .then(data => {
        currentChecklist = data.checklist || fallbackChecklist;
        currentChecklist.forEach(item => {
          const label = document.createElement("label");
          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.name = item;
          checkbox.value = "true";
          label.appendChild(checkbox);
          label.appendChild(document.createTextNode(" " + item));
          checklistContainer.appendChild(label);
          checklistContainer.appendChild(document.createElement("br"));
        });
      })
      .catch(() => {
        currentChecklist = fallbackChecklist;
        currentChecklist.forEach(item => {
          const label = document.createElement("label");
          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.name = item;
          checkbox.value = "true";
          label.appendChild(checkbox);
          label.appendChild(document.createTextNode(" " + item));
          checklistContainer.appendChild(label);
          checklistContainer.appendChild(document.createElement("br"));
        });
      });
  });

  // Handle form submission
  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const checklistItems = document.querySelectorAll('#checklistContainer input');
    const checklistResponses = {};
    checklistItems.forEach(item => {
      checklistResponses[item.name] = item.checked;
    });

    const payload = {
      state: document.getElementById("state").value,
      disaster_type: document.getElementById("disaster_type").value,
      household_size: parseInt(document.getElementById("household_size").value),
      has_kit: document.getElementById("has_kit").checked,
      checklist_responses: checklistResponses
    };

    try {
      const response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error("Prediction request failed");

      const data = await response.json();

      if (data.error) {
        resultBox.innerHTML = `<strong>Error:</strong> ${data.error}`;
        resultBox.style.background = "#ffebee";
        resultBox.style.color = "#b71c1c";
      } else {

        const levelColor = {
          "Needs Urgent Prep": "#E63946",     // red
          "Moderately Prepared": "#F4A261",   // orange
          "Well Prepared": "#2A9D8F"          // green
        };
        
        const progressBar = data.completion_percentage > 0
          ? `<div class="progress-container">
                <div class="progress-bar" style="width: ${data.completion_percentage}%;"></div>
              </div>`
          : ''; // Hide if 0%
        
        resultBox.innerHTML = `
          <div class="result-card" id="resultCard">
            <h2 class="level-heading" style="color: ${levelColor[data.preparedness_level]};">
              🚦 Preparedness Level: ${data.preparedness_level}
            </h2>
            ${progressBar}
        
            <div class="info-box">
              <p><strong>✅ Checklist Completed:</strong> ${data.completion_percentage.toFixed(2)}%</p>
              <p><strong>🧠 Awareness Score:</strong> ${data.awareness_score}</p>
            </div>
        
            <div class="tips-box">
              <h3>📌 <strong>Improvement Tips</strong></h3>
              <ul>${data.improvement_tips.map(t => `<li>🛠 ${t}</li>`).join("")}</ul>
            </div>
        
            <div class="recommendation-box">
              <h3>✅ <strong>Recommended Actions</strong></h3>
              <ul>${data.recommendations.map(t => `<li>📍 ${t}</li>`).join("")}</ul>
            </div>

            <div class="action-buttons">
              <button onclick="copyToClipboard()">📋 Copy</button>
              <button onclick="exportToPDF()">📄 Export as PDF</button>
             </div>
          </div>
        `;
        
      }
    } catch (error) {
      console.error("Error:", error);
      resultBox.innerHTML = `<p>Sorry, something went wrong. Please try again.</p>`;
      resultBox.style.background = "#ffebee";
      resultBox.style.color = "#b71c1c";
    }
  });
});



// 

function copyToClipboard() {
  const card = document.getElementById("resultCard");
  if (!card) return alert("Nothing to copy yet!");
  const text = card.innerText;
  navigator.clipboard.writeText(text).then(() => {
    alert("Copied to clipboard!");
  });
}

function exportToPDF() {
  const element = document.getElementById("resultCard");
  const opt = {
    margin:       0.5,
    filename:     'preparedness_report.pdf',
    image:        { type: 'jpeg', quality: 0.98 },
    html2canvas:  { scale: 2 },
    jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
  };
  html2pdf().from(element).set(opt).save();
}
