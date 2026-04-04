// Login Function
async function login() {
  const user = document.getElementById("username").value;
  const pass = document.getElementById("password").value;

  const response = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user: user, password: pass }),
  });

  const data = await response.json();

  if (response.ok) {
    localStorage.setItem("session_token", data["session token"]);
    document.getElementById("login-error").innerText = "";
    loadPortfolio();
  } else {
    document.getElementById("login-error").innerText = data.error;
  }
}

// Load Portfolio
async function loadPortfolio() {
  const token = localStorage.getItem("session_token");
  if (!token) return;

  const authResponse = await fetch("/isAuth", {
    headers: { Authorization: "Bearer " + token },
  });

  if (!authResponse.ok) {
    logout();
    return;
  }

  const tokenPayload = JSON.parse(atob(token.split(".")[1]));
  const memberId = tokenPayload.member_id;
  const role = tokenPayload.role ? tokenPayload.role.trim().toLowerCase() : "";

  const portResponse = await fetch(`/portfolio/${memberId}`, {
    headers: { Authorization: "Bearer " + token },
  });
  const portData = await portResponse.json();

  if (portResponse.ok) {
    const profile = portData.profile;

    if (!profile) {
      console.error("Data arrived, but 'profile' object is missing!");
      return;
    }

    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("portfolio-section").classList.remove("hidden");

    document
      .querySelectorAll(".admin-tab-content")
      .forEach((tab) => tab.classList.add("hidden"));
    if (document.getElementById("admin-results"))
      document.getElementById("admin-results").innerHTML = "";
    if (document.getElementById("admin-complaints-results"))
      document.getElementById("admin-complaints-results").innerHTML = "";

    if (document.getElementById("display-name"))
      document.getElementById("display-name").innerText =
        profile.First_Name || "User";
    if (document.getElementById("display-role"))
      document.getElementById("display-role").innerText =
        tokenPayload.role || "Member";

    document.getElementById("port-email").innerText = profile.Email || "N/A";
    document.getElementById("port-contact").innerText =
      profile.Contact_Number || "N/A";

    const eId = document.getElementById("port-hostel-id");
    const eH = document.getElementById("port-hostel");
    const eR = document.getElementById("port-room");
    if (eId) eId.innerText = profile.Hostel_ID || "Unassigned";
    if (eH) eH.innerText = profile.Hostel_Name || "Unassigned";
    if (eR) eR.innerText = profile.Room_Number || "N/A";

    const profileImg = document.getElementById("port-profile-pic");
    if (profileImg) {
      const path = profile.Image_Path || "";
      if (path.includes("riya.png")) {
        profileImg.src = "/static/uploads/riya.png";
      } else if (path.startsWith("http")) {
        profileImg.src = path;
      } else {
        profileImg.src = `https://ui-avatars.com/api/?name=${profile.First_Name || "User"}&background=3498db&color=fff`;
      }
    }

    let payHtml =
      portData.payments.length > 0 ? "<ul>" : "<p>No payments found.</p>";
    portData.payments.forEach((p) => {
      payHtml += `<li><strong>${p.Fee_Name}</strong>: $${p.Amount_Paid} on ${p.Payment_Date} (${p.Payment_Status})</li>`;
    });
    if (portData.payments.length > 0) payHtml += "</ul>";
    document.getElementById("port-payments").innerHTML = payHtml;

    let compHtml =
      portData.complaints.length > 0 ? "<ul>" : "<p>No complaints found.</p>";
    portData.complaints.forEach((c) => {
      compHtml += `<li><strong>${c.Type_Name}</strong>: ${c.Description} - <em>Status: ${c.Status}</em></li>`;
    });
    if (portData.complaints.length > 0) compHtml += "</ul>";
    document.getElementById("port-complaints").innerHTML = compHtml;

    // RBAC (UI Gatekeeping)
    const studentSections = document.getElementById("student-only-sections");
    const raiseComplaintBox = document.getElementById("raise-complaint-box");
    const adminStatsCard = document.getElementById("admin-stats-card");
    const adminSection = document.getElementById("admin-section");
    const securitySection = document.getElementById("security-section");
    const securityTabs = document.getElementById("security-tabs");
    const securityStatsCard = document.getElementById("security-stats-card");

    const liHostelId = document.getElementById("li-hostel-id");
    const liHostelName = document.getElementById("li-hostel-name");
    const liRoom = document.getElementById("li-room");
    const overviewTitle = document.getElementById("overview-title");
    const adminOverviewTitle = document.getElementById("admin-overview-title");

    const allSections = [
      studentSections,
      raiseComplaintBox,
      adminStatsCard,
      adminSection,
      securitySection,
      securityTabs,
      securityStatsCard,
    ];

    allSections.forEach((el) => {
      if (el) {
        el.classList.add("hidden");
        el.style.setProperty("display", "none", "important");
      }
    });

    [liHostelId, liHostelName, liRoom].forEach((li) => {
      if (li) li.style.setProperty("display", "list-item", "important");
    });

    document
      .querySelectorAll(".shared-btn, .admin-only, .warden-only")
      .forEach((btn) => {
        btn.style.setProperty("display", "none", "important");
      });

    if (role === "admin") {
      if (adminStatsCard) {
        adminStatsCard.classList.remove("hidden");
        adminStatsCard.style.setProperty("display", "block", "important");
      }
      if (adminOverviewTitle)
        adminOverviewTitle.innerText = "Overall System Overview";

      if (liHostelId)
        liHostelId.style.setProperty("display", "none", "important");
      if (liHostelName)
        liHostelName.style.setProperty("display", "none", "important");
      if (liRoom) liRoom.style.setProperty("display", "none", "important");

      if (adminSection) {
        adminSection.classList.remove("hidden");
        adminSection.style.setProperty("display", "block", "important");
      }

      document
        .querySelectorAll(".shared-btn")
        .forEach((btn) =>
          btn.style.setProperty("display", "inline-block", "important"),
        );
      document
        .querySelectorAll(".admin-only")
        .forEach((btn) =>
          btn.style.setProperty("display", "inline-block", "important"),
        );

      fetchAdminStats();
    } else if (role === "warden") {
      if (adminStatsCard) {
        adminStatsCard.classList.remove("hidden");
        adminStatsCard.style.setProperty("display", "block", "important");
      }
      if (adminOverviewTitle)
        adminOverviewTitle.innerText = " Warden Overview";
      if (liRoom) liRoom.style.setProperty("display", "none", "important");

      if (adminSection) {
        adminSection.classList.remove("hidden");
        adminSection.style.setProperty("display", "block", "important");
      }

      document
        .querySelectorAll(".shared-btn")
        .forEach((btn) =>
          btn.style.setProperty("display", "inline-block", "important"),
        );
      document
        .querySelectorAll(".warden-only")
        .forEach((btn) =>
          btn.style.setProperty("display", "inline-block", "important"),
        );

      fetchAdminStats();
    } else if (role === "security") {
      if (securitySection) {
        securitySection.classList.remove("hidden");
        securitySection.style.setProperty("display", "block", "important");
      }
      if (overviewTitle)
        overviewTitle.innerText = "Security Gate Management";

      if (securityTabs) {
        securityTabs.classList.remove("hidden");
        securityTabs.style.setProperty("display", "flex", "important");
      }

      if (securityStatsCard) {
        securityStatsCard.classList.remove("hidden");
        securityStatsCard.style.setProperty("display", "block", "important");
      }

      if (liRoom) liRoom.style.setProperty("display", "none", "important");

      fetchSecurityDashboard();
    } else {
      if (overviewTitle) overviewTitle.innerText = "Student Dashboard";
      if (studentSections) {
        studentSections.classList.remove("hidden");
        studentSections.style.setProperty("display", "block", "important");
      }
      if (raiseComplaintBox) {
        raiseComplaintBox.classList.remove("hidden");
        raiseComplaintBox.style.setProperty("display", "block", "important");
      }
    }
  }
}

// Admin Fetch All Members
async function fetchAllMembers() {
  const token = localStorage.getItem("session_token");
  const response = await fetch("/admin/members", {
    headers: { Authorization: "Bearer " + token },
  });
  const data = await response.json();

  if (response.ok) {
    let html = "<table class='data-table'>";
    html +=
      "<tr class='table-header'><th>ID</th><th>Name</th><th>Email</th><th>Hostel</th><th>Room</th><th>Status</th><th>Action</th></tr>";

    data.members.forEach((m) => {
      let statusClass =
        m.Status === "Active" ? "status-active" : "status-inactive";

      html += `<tr>
                <td>${m.Member_ID}</td>
                <td>${m.First_Name} ${m.Last_Name || ""}</td>
                <td>${m.Email}</td>
                <td><strong>${m.Hostel_Name || '<span class="text-muted">Unassigned</span>'}</strong></td>
                <td><strong>${m.Room_Number || '<span class="text-muted">N/A</span>'}</strong></td>
                <td class="${statusClass}">${m.Status}</td>
                <td style="text-align: center;">
                    <button class="btn-edit" onclick="openEditForm(${m.Member_ID}, '${m.Contact_Number}', '${m.Status}')">Edit</button>
                </td>
             </tr>`;
    });
    html += "</table>";
    document.getElementById("admin-results").innerHTML = html;
  } else {
    alert("Security Block: " + data.error);
  }
}

// Admin: Edit Form
function openEditForm(id, contact, status) {
  document.getElementById("update-member-form").classList.remove("hidden");
  document.getElementById("tab-add-member").classList.add("hidden");

  document.getElementById("update-id").value = id;
  document.getElementById("update-contact").value = contact;
  document.getElementById("update-status").value = status;
}

// Admin: Submit the Update
async function submitUpdateMember() {
  const memberId = document.getElementById("update-id").value;
  const payload = {
    contact: document.getElementById("update-contact").value,
    status: document.getElementById("update-status").value,
  };

  const token = localStorage.getItem("session_token");
  const response = await fetch("/admin/members/" + memberId, {
    method: "PUT",
    headers: {
      Authorization: "Bearer " + token,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (response.ok) {
    alert("Success! Member details updated.");
    document.getElementById("update-member-form").classList.add("hidden");
    fetchAllMembers();
  } else {
    alert("Error: " + data.error);
  }
}

// Admin: View Complaints
async function fetchComplaints() {
  const token = localStorage.getItem("session_token");
  const response = await fetch("/admin/complaints", {
    headers: { Authorization: "Bearer " + token },
  });
  const data = await response.json();

  if (response.ok) {
    let html = "<table class='data-table'>";
    html +=
      "<tr class='table-header'><th>Date</th><th>Submitted By</th><th>Hostel</th><th>Room</th><th>Type</th><th>Description</th><th>Status</th><th>Action</th></tr>";

    data.complaints.forEach((c) => {
      let formattedDate = new Date(c.Submission_Date).toLocaleDateString(
        "en-GB",
      );
      let textStatusClass =
        c.Status === "Pending" ? "text-danger" : "text-success";

      let statusDropdown = `
        <select class="status-select ${textStatusClass}" onchange="updateComplaintStatus(${c.Complaint_ID}, this.value)">
            <option value="Pending" ${c.Status === "Pending" ? "selected" : ""}>Pending</option>
            <option value="In Progress" ${c.Status === "In Progress" ? "selected" : ""}>In Progress</option>
            <option value="Resolved" ${c.Status === "Resolved" ? "selected" : ""}>Resolved</option>
        </select>
      `;

      html += `<tr>
                <td>${formattedDate}</td>
                <td>${c.First_Name} ${c.Last_Name || ""}</td>
                <td><strong>${c.Hostel_Name || '<span class="text-muted">Unassigned</span>'}</strong></td>
                <td><strong>${c.Room_Number || '<span class="text-muted">N/A</span>'}</strong></td>
                <td>${c.Type_Name}</td>
                <td>${c.Description}</td>
                <td>${statusDropdown}</td>
                <td style="text-align: center;">
                    <button class="btn-delete" onclick="deleteComplaint(${c.Complaint_ID})">Delete</button>
                </td>
             </tr>`;
    });

    html += "</table>";
    document.getElementById("admin-complaints-results").innerHTML = html;
  } else {
    alert("Error loading complaints: " + data.error);
  }
}

// Admin: Add New Member
async function submitNewMember() {
  const firstName = document.getElementById("new-fname").value;
  const email = document.getElementById("new-email").value;
  const room = document.getElementById("new-room-number").value;

  if (!firstName || !email || !room) {
    alert(
      "Please fill in all required fields (First Name, Email, and Room Number).",
    );
    return;
  }

  const payload = {
    first_name: firstName,
    last_name: document.getElementById("new-lname").value,
    gender: document.getElementById("new-gender").value,
    age: document.getElementById("new-age").value,
    contact: document.getElementById("new-contact").value,
    email: email,
    emergency_contact: document.getElementById("emergency-contact").value,
    role_id: document.getElementById("new-role").value,
    hostel_id: document.getElementById("new-hostel-id").value,
    room_number: room,
  };

  const token = localStorage.getItem("session_token");

  try {
    const response = await fetch("/admin/members", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (response.ok) {
      alert("Success! The member has been added to the database.");
      document.getElementById("tab-add-member").classList.add("hidden");

      document.getElementById("new-fname").value = "";
      document.getElementById("new-lname").value = "";
      document.getElementById("new-email").value = "";
      document.getElementById("new-contact").value = "";
      document.getElementById("new-room-number").value = "";

      if (typeof fetchAllMembers === "function") fetchAllMembers();
    } else {
      alert("Error: " + (data.error || "Failed to save member"));
    }
  } catch (error) {
    console.error("Save error:", error);
    alert("Server connection failed. Make sure your backend is running.");
  }
}

function updateSubcategories() {
  const category = document.getElementById("complaint-category").value;
  const subSelect = document.getElementById("new-complaint-type");

  subSelect.innerHTML = '<option value="">Select Subcategory</option>';

  const subTypeMap = {
    Electrical: [
      { id: 1, label: "Fan/Light" },
      { id: 2, label: "Power Socket" },
    ],
    Plumbing: [
      { id: 3, label: "Leakage" },
      { id: 4, label: "Tap Repair" },
    ],
    Civil: [
      { id: 5, label: "Wall Seepage" },
      { id: 6, label: "Door/Lock" },
    ],
    Mechanical: [{ id: 7, label: "Bed/Chair Repair" }],
    Other: [{ id: 8, label: "General Maintenance" }],
  };

  if (subTypeMap[category]) {
    subTypeMap[category].forEach((item) => {
      const opt = document.createElement("option");
      opt.value = item.id;
      opt.innerText = item.label;
      subSelect.appendChild(opt);
    });
  }
}

async function submitComplaint() {
  const typeId = document.getElementById("new-complaint-type").value;
  const description = document.getElementById("new-complaint-desc").value;

  if (!typeId) {
    alert("Please select a valid Category and Subcategory.");
    return;
  }

  if (!description.trim()) {
    alert("Please provide a description for your complaint.");
    return;
  }

  const payload = {
    type_id: typeId,
    description: description,
  };

  const token = localStorage.getItem("session_token");
  try {
    const response = await fetch("/portfolio/complaints", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (response.ok) {
      alert("Success! Your complaint has been submitted.");
      document.getElementById("new-complaint-desc").value = "";
      window.location.reload();
    } else {
      alert("Backend Error: " + data.error);
    }
  } catch (error) {
    console.error("Fetch error:", error);
    alert("Network error. Please check your console.");
  }
}

async function deleteComplaint(complaintId) {
  if (
    !confirm(
      "Are you sure you want to delete this complaint? This action cannot be undone.",
    )
  ) {
    return;
  }
  const token = localStorage.getItem("session_token");
  const response = await fetch("/admin/complaints/" + complaintId, {
    method: "DELETE",
    headers: { Authorization: "Bearer " + token },
  });

  const data = await response.json();
  if (response.ok) {
    alert("Success! The complaint has been deleted.");
    fetchComplaints();
  } else {
    alert("Error: " + data.error);
  }
}

async function updateComplaintStatus(complaintId, newStatus) {
  const token = localStorage.getItem("session_token");
  const response = await fetch("/admin/complaints/" + complaintId, {
    method: "PUT",
    headers: {
      Authorization: "Bearer " + token,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status: newStatus }),
  });

  const data = await response.json();
  if (response.ok) {
    fetchComplaints();
  } else {
    alert("Error: " + data.error);
    fetchComplaints();
  }
}

function openAdminTab(tabName) {
  const targetTab = document.getElementById("tab-" + tabName);
  const isAlreadyOpen = !targetTab.classList.contains("hidden");

  const allTabs = document.querySelectorAll(".admin-tab-content");
  allTabs.forEach((tab) => {
    tab.classList.add("hidden");
  });

  const updateForm = document.getElementById("update-member-form");
  if (updateForm) updateForm.classList.add("hidden");

  if (!isAlreadyOpen) targetTab.classList.remove("hidden");
}

async function fetchAdminStats() {
  const token = localStorage.getItem("session_token");
  if (!token) return;

  try {
    const response = await fetch("/admin/stats", {
      method: "GET",
      headers: { Authorization: "Bearer " + token },
    });
    const data = await response.json();

    if (response.ok) {
      document.getElementById("stat-complaints").innerText =
        data.pending_complaints;
      document.getElementById("stat-residents").innerText =
        data.total_residents;
      document.getElementById("stat-rooms").innerText = data.available_rooms;
    }
  } catch (error) {
    console.error("Error fetching stats:", error);
  }
}

async function fetchSecurityDashboard() {
  const token = localStorage.getItem("session_token");
  const response = await fetch("/api/security/dashboard", {
    headers: { Authorization: "Bearer " + token },
  });
  const data = await response.json();

  if (response.ok) {
    document.getElementById("sec-hostel-name-stat").innerText =
      data.hostel_name;
    document.getElementById("stat-sec-visitors").innerText =
      data.active_visitors.length;
    document.getElementById("stat-sec-outside").innerText =
      data.outside_students.length;

    let visHtml =
      "<table class='data-table'><tr class='table-header'><th>Visitor</th><th>Visiting</th><th>Room</th><th>Purpose</th><th>Entry Time</th><th>Action</th></tr>";

    data.active_visitors.forEach((v) => {
      visHtml += `<tr>
                <td>${v.Visitor_Name}</td>
                <td>${v.Visiting_Student}</td>
                <td>${v.Room_Number}</td>
                <td>${v.Purpose}</td>
                <td>${new Date(v.Entry_Time).toLocaleString("en-GB")}</td>
                <td style="text-align:center;">
                    <button class="btn-action-red" onclick="markVisitorExited(${v.Log_ID})">Sign Out</button>
                </td>
            </tr>`;
    });
    visHtml += "</table>";
    document.getElementById("sec-visitors-table").innerHTML =
      data.active_visitors.length > 0
        ? visHtml
        : "<p>No visitors currently inside.</p>";

    let outHtml =
      "<table class='data-table'><tr class='table-header'><th>Student Name</th><th>Contact</th><th>Exit Time</th><th>Purpose</th><th>Action</th></tr>";

    data.outside_students.forEach((s) => {
      outHtml += `<tr>
                <td>${s.First_Name} ${s.Last_Name || ""}</td>
                <td>${s.Contact_Number}</td>
                <td>${new Date(s.Exit_Time).toLocaleString("en-GB")}</td>
                <td>${s.Purpose}</td>
                <td style="text-align:center;">
                    <button class="btn-action-green" onclick="markStudentReturned(${s.Log_ID})">Sign In</button>
                </td>
            </tr>`;
    });
    outHtml += "</table>";
    document.getElementById("sec-students-table").innerHTML =
      data.outside_students.length > 0
        ? outHtml
        : "<p>All students are safely on campus.</p>";
  } else {
    alert("Security Load Error: " + data.error);
  }
}

async function fetchFurniture() {
  const token = localStorage.getItem("session_token");
  const response = await fetch("/api/warden/furniture", {
    headers: { Authorization: "Bearer " + token },
  });
  const data = await response.json();

  if (response.ok) {
    let html =
      "<table class='data-table'><tr class='table-header'><th>Asset Type</th><th>Total Quantity</th><th>Status</th></tr>";
    data.forEach((item) => {
      let status =
        item.Needs_Repair > 0
          ? `<span class="text-danger">${item.Needs_Repair} Damaged</span>`
          : `<span class="text-success">Good</span>`;
      html += `<tr><td><strong>${item.Item_Name}</strong></td><td>${item.Total_Quantity} units</td><td>${status}</td></tr>`;
    });
    html += `</table>`;
    document.getElementById("warden-furniture-results").innerHTML = html;
  }
}

async function markVisitorExited(logId) {
  if (!confirm("Are you sure you want to sign this visitor out?")) return;

  const token = localStorage.getItem("session_token");
  try {
    const response = await fetch(`/api/security/visitors/${logId}/exit`, {
      method: "PUT",
      headers: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    if (response.ok) {
      fetchSecurityDashboard();
    } else {
      alert("Error signing out visitor: " + data.error);
    }
  } catch (err) {
    console.error(err);
    alert("Network Error: Could not connect to the server.");
  }
}

async function fetchWardenMovement() {
  const token = localStorage.getItem("session_token");
  const response = await fetch("/api/warden/movement", {
    headers: { Authorization: "Bearer " + token },
  });
  const data = await response.json();

  if (response.ok) {
    let html =
      "<table class='data-table'><tr class='table-header'><th>Student</th><th>Room</th><th>Exit Time</th><th>Return Time</th><th>Purpose</th><th>Action</th></tr>";

    data.forEach((log) => {
      let returnTime = log.Entry_Time
        ? new Date(log.Entry_Time).toLocaleString("en-GB")
        : '<span class="text-danger">Currently Outside</span>';

      let actionBtn = "";
      if (!log.Entry_Time) {
        actionBtn = `<button class="btn-action-green" onclick="markStudentReturned(${log.Log_ID})">Sign In</button>`;
      } else {
        actionBtn = `<span class="text-muted text-sm">Returned</span>`;
      }

      html += `<tr>
        <td>${log.First_Name} ${log.Last_Name || ""}</td>
        <td>${log.Room_Number}</td>
        <td>${new Date(log.Exit_Time).toLocaleString("en-GB")}</td>
        <td>${returnTime}</td>
        <td>${log.Purpose}</td>
        <td style="text-align:center;">${actionBtn}</td>
      </tr>`;
    });

    html += `</table>`;
    document.getElementById("warden-movement-results").innerHTML = html;
  }
}

async function markStudentReturned(logId) {
  if (!confirm("Confirm this student has returned to the hostel?")) return;

  const token = localStorage.getItem("session_token");
  try {
    const response = await fetch(`/api/movement/${logId}/return`, {
      method: "PUT",
      headers: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    if (response.ok) {
      const role = localStorage.getItem("user_role"); // Warning: this role lookup might be undefined depending on your login logic, consider pulling from tokenPayload instead
      if (
        document.getElementById("security-section") &&
        !document
          .getElementById("security-section")
          .classList.contains("hidden")
      ) {
        fetchSecurityDashboard();
      } else {
        if (typeof fetchWardenMovement === "function") fetchWardenMovement();
      }
    } else {
      alert("Error: " + data.error);
    }
  } catch (err) {
    console.error(err);
    alert("Network Error: Could not connect to the server.");
  }
}

async function fetchAdminGlobal(type) {
  let url = "";
  let title = "";
  if (type === "furniture") {
    url = "/api/admin/all_furniture";
    title = "Global Furniture Overview";
  }
  if (type === "visitors") {
    url = "/api/admin/all_visitors";
    title = "Global Visitor Logs";
  }
  if (type === "movement") {
    url = "/api/admin/all_movement";
    title = "Global Student Movements";
  }

  document.getElementById("admin-global-title").innerText = title;

  const token = localStorage.getItem("session_token");
  const response = await fetch(url, {
    headers: { Authorization: "Bearer " + token },
  });
  const data = await response.json();

  if (response.ok) {
    let html = "<table class='data-table'>";
    if (data.length > 0) {
      html += `<tr class='table-header'>`;
      Object.keys(data[0]).forEach(
        (key) => (html += `<th>${key.replace(/_/g, " ")}</th>`),
      );
      html += `</tr>`;
      data.forEach((row) => {
        html += `<tr>`;
        Object.values(row).forEach((val) => {
          let displayVal =
            val === null
              ? '<span class="text-danger">Pending / Inside</span>'
              : val;
          if (typeof val === "string" && val.includes("GMT")) {
            displayVal = new Date(val).toLocaleString("en-GB");
          }
          html += `<td>${displayVal}</td>`;
        });
        html += `</tr>`;
      });
    } else {
      html = `<p>No data found.</p>`;
    }
    html += `</table>`;
    document.getElementById("admin-global-results").innerHTML = html;
  }
}

function openSecurityModal(type) {
  document.getElementById("sec-modal-visitors").classList.add("hidden");
  document.getElementById("sec-modal-students").classList.add("hidden");

  if (type === "visitors") {
    document.getElementById("sec-modal-visitors").classList.remove("hidden");
  } else if (type === "students") {
    document.getElementById("sec-modal-students").classList.remove("hidden");
  }

  fetchSecurityDashboard();
}

async function checkAvailableRooms() {
  const hostelId = document.getElementById("new-hostel-id").value;
  const roomsListDiv = document.getElementById("available-rooms-list");
  const roomsDataSpan = document.getElementById("rooms-data");

  if (!hostelId) {
    alert("Please enter a Hostel ID first!");
    return;
  }

  try {
    const token = localStorage.getItem("session_token");
    const response = await fetch(`/api/admin/available-rooms/${hostelId}`, {
      headers: { Authorization: "Bearer " + token },
    });
    const data = await response.json();

    if (response.ok) {
      roomsListDiv.style.display = "block";
      if (data.rooms && data.rooms.length > 0) {
        roomsDataSpan.innerHTML = data.rooms
          .map(
            (r) =>
              `<span style="cursor:pointer; color:#2980b9; text-decoration:underline;" onclick="document.getElementById('new-room-number').value='${r.Room_Number}'">${r.Room_Number}</span>`,
          )
          .join(", ");
      } else {
        roomsDataSpan.innerText =
          "No existing rooms have space. A new one will be created.";
      }
    } else {
      alert("Error: " + data.error);
    }
  } catch (err) {
    alert("Failed to fetch rooms. Check server connection.");
  }
}

function openAddVisitorModal() {
  const modal = document.getElementById("modal-add-visitor");
  modal.classList.remove("hidden");
  modal.style.setProperty("display", "flex", "important");
}

function closeAddVisitorModal() {
  const modal = document.getElementById("modal-add-visitor");
  modal.classList.add("hidden");
  modal.style.setProperty("display", "none", "important");
}

let searchTimeout = null;

async function searchStudent() {
  const query = document.getElementById("vis-student-search").value;
  const resultsDiv = document.getElementById("student-search-results");

  document.getElementById("vis-host-id").value = "";

  if (query.length < 2) {
    resultsDiv.style.display = "none";
    return;
  }

  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(async () => {
    const token = localStorage.getItem("session_token");
    try {
      const response = await fetch(
        `/api/security/search-student?q=${encodeURIComponent(query)}`,
        { headers: { Authorization: "Bearer " + token } },
      );
      const data = await response.json();

      if (response.ok && data.length > 0) {
        resultsDiv.innerHTML = "";

        data.forEach((student) => {
          const fullName =
            `${student.First_Name} ${student.Last_Name || ""}`.trim();
          const div = document.createElement("div");

          // Using our new clean CSS class!
          div.className = "search-result-item";
          div.innerHTML = `<strong class="text-dark-blue">${fullName}</strong> (Room: ${student.Room_Number}) <br><small class="text-muted">📞 ${student.Contact_Number}</small>`;

          div.onclick = () => {
            document.getElementById("vis-student-search").value =
              `${fullName} (Room ${student.Room_Number})`;
            document.getElementById("vis-host-id").value = student.Member_ID;
            resultsDiv.style.display = "none";
          };

          resultsDiv.appendChild(div);
        });
        resultsDiv.style.display = "block";
      } else {
        resultsDiv.innerHTML =
          '<div class="search-no-results">No active students found.</div>';
        resultsDiv.style.display = "block";
      }
    } catch (err) {
      console.error("Search error:", err);
    }
  }, 300);
}

async function submitNewVisitor() {
  const payload = {
    visitor_name: document.getElementById("vis-name").value,
    contact: document.getElementById("vis-contact").value,
    id_type: document.getElementById("vis-id-type").value,
    id_number: document.getElementById("vis-id-num").value,
    host_id: document.getElementById("vis-host-id").value,
    purpose: document.getElementById("vis-purpose").value,
  };

  if (!payload.visitor_name || !payload.id_number || !payload.host_id) {
    alert("Please fill in all required fields.");
    return;
  }

  const token = localStorage.getItem("session_token");
  try {
    const response = await fetch("/api/security/visitors", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (response.ok) {
      alert("Success! Visitor logged into the system.");

      document.getElementById("vis-name").value = "";
      document.getElementById("vis-contact").value = "";
      document.getElementById("vis-id-num").value = "";
      document.getElementById("vis-host-id").value = "";
      document.getElementById("vis-purpose").value = "";

      closeAddVisitorModal();

      if (typeof fetchSecurityDashboard === "function") {
        fetchSecurityDashboard();
      }
    } else {
      alert("Database Error: " + data.error);
    }
  } catch (err) {
    alert("Network Error: Make sure your server is running.");
  }
}

function logout() {
  localStorage.removeItem("session_token");
  window.location.reload();
}

window.onload = () => {
  if (localStorage.getItem("session_token")) {
    loadPortfolio();
  }
};
