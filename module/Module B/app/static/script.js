// 1. LOGIN FUNCTION
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
    // Save the JWT token to local storage
    localStorage.setItem("session_token", data["session token"]);
    document.getElementById("login-error").innerText = "";
    loadPortfolio();
  } else {
    document.getElementById("login-error").innerText = data.error;
  }
}

// 2. LOAD PORTFOLIO
// 2. LOAD PORTFOLIO
async function loadPortfolio() {
  const token = localStorage.getItem("session_token");
  if (!token) return;

  // 1. Check Authentication
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

  // 2. Fetch Data
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

    // 3. REVEAL THE DASHBOARD
    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("portfolio-section").classList.remove("hidden");

    // THE CLEANUP CREW (Prevents Ghost Data)
    document.querySelectorAll(".admin-tab-content").forEach((tab) => tab.classList.add("hidden"));
    if (document.getElementById("admin-results")) document.getElementById("admin-results").innerHTML = "";
    if (document.getElementById("admin-complaints-results")) document.getElementById("admin-complaints-results").innerHTML = "";

    // 4. POPULATE HEADER & DETAILS
    if (document.getElementById("display-name")) document.getElementById("display-name").innerText = profile.First_Name || "User";
    if (document.getElementById("display-role")) document.getElementById("display-role").innerText = tokenPayload.role || "Member";

    document.getElementById("port-email").innerText = profile.Email || "N/A";
    document.getElementById("port-contact").innerText = profile.Contact_Number || "N/A";

    const eId = document.getElementById("port-hostel-id");
    const eH = document.getElementById("port-hostel");
    const eR = document.getElementById("port-room");
    if (eId) eId.innerText = profile.Hostel_ID || "Unassigned";
    if (eH) eH.innerText = profile.Hostel_Name || "Unassigned";
    if (eR) eR.innerText = profile.Room_Number || "N/A";

    // 5. HANDLE IMAGE
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

    // Populate Payments
    let payHtml = portData.payments.length > 0 ? "<ul>" : "<p>No payments found.</p>";
    portData.payments.forEach((p) => {
      payHtml += `<li><strong>${p.Fee_Name}</strong>: $${p.Amount_Paid} on ${p.Payment_Date} (${p.Payment_Status})</li>`;
    });
    if (portData.payments.length > 0) payHtml += "</ul>";
    document.getElementById("port-payments").innerHTML = payHtml;

    // Populate Complaints
    let compHtml = portData.complaints.length > 0 ? "<ul>" : "<p>No complaints found.</p>";
    portData.complaints.forEach((c) => {
      compHtml += `<li><strong>${c.Type_Name}</strong>: ${c.Description} - <em>Status: ${c.Status}</em></li>`;
    });
    if (portData.complaints.length > 0) compHtml += "</ul>";
    document.getElementById("port-complaints").innerHTML = compHtml;

    // ==========================================
    // 6. RBAC (UI Gatekeeping) - UPDATED
    // ==========================================
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

    // --- THE NUCLEAR RESET ---
    const allSections = [studentSections, raiseComplaintBox, adminStatsCard, adminSection, securitySection, securityTabs, securityStatsCard];
    allSections.forEach(el => {
        if (el) {
            el.classList.add('hidden');
            el.style.setProperty('display', 'none', 'important');
        }
    });

    [liHostelId, liHostelName, liRoom].forEach(li => {
        if (li) li.style.setProperty('display', 'list-item', 'important');
    });

    // Hide ALL action buttons globally first
    document.querySelectorAll('.shared-btn, .admin-only, .warden-only').forEach(btn => {
        btn.style.setProperty('display', 'none', 'important');
    });

    // --- APPLY ROLE-SPECIFIC LOGIC ---
    if (role === "admin") {
        if (adminStatsCard) {
            adminStatsCard.classList.remove("hidden");
            adminStatsCard.style.setProperty("display", "block", "important");
        }
        if (overviewTitle) overviewTitle.innerText = "📊 Overall System Overview";
        if (liHostelId) liHostelId.style.setProperty("display", "none", "important");
        if (liHostelName) liHostelName.style.setProperty("display", "none", "important");
        if (liRoom) liRoom.style.setProperty("display", "none", "important");
        
        if (adminSection) {
            adminSection.classList.remove("hidden");
            adminSection.style.setProperty("display", "block", "important");
        }

        // Show Admin & Shared, Hide Warden
        document.querySelectorAll(".shared-btn").forEach((btn) => btn.style.setProperty("display", "inline-block", "important"));
        document.querySelectorAll(".admin-only").forEach((btn) => btn.style.setProperty("display", "inline-block", "important"));
        
        fetchAdminStats();

    } else if (role === "warden") {
        if (adminStatsCard) {
            adminStatsCard.classList.remove("hidden");
            adminStatsCard.style.setProperty("display", "block", "important");
        }
        if (overviewTitle) overviewTitle.innerText = "📊 Warden Overview";
        if (liRoom) liRoom.style.setProperty("display", "none", "important");
        
        if (adminSection) {
            adminSection.classList.remove("hidden");
            adminSection.style.setProperty("display", "block", "important");
        }

        // Show Warden & Shared, Hide Admin
        document.querySelectorAll(".shared-btn").forEach((btn) => btn.style.setProperty("display", "inline-block", "important"));
        document.querySelectorAll(".warden-only").forEach((btn) => btn.style.setProperty("display", "inline-block", "important"));
        
        fetchAdminStats();

    } else if (role === "security") {
        if (securitySection) {
            securitySection.classList.remove("hidden");
            securitySection.style.setProperty("display", "block", "important");
        }
        if (overviewTitle) overviewTitle.innerText = "🛡️ Security Gate Management";

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
        // Student logic
        if (overviewTitle) overviewTitle.innerText = "🏠 Student Dashboard";
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


// ADMIN: FETCH ALL MEMBERS
async function fetchAllMembers() {
  const token = localStorage.getItem("session_token");

  const response = await fetch("/admin/members", {
    headers: { Authorization: "Bearer " + token },
  });

  const data = await response.json();

  if (response.ok) {
    let html =
      "<table border='1' width='100%' style='border-collapse: collapse; text-align: left; background: white;'>";

    html +=
      "<tr style='background-color: #f2f2f2;'><th>ID</th><th>Name</th><th>Email</th><th>Hostel</th><th>Room</th><th>Status</th><th>Action</th></tr>";

    data.members.forEach((m) => {
      let statusColor = m.Status === "Active" ? "green" : "red";

      html += `<tr>
                            <td>${m.Member_ID}</td>
                            <td>${m.First_Name} ${m.Last_Name || ""}</td>
                            <td>${m.Email}</td>
                            <td><strong>${m.Hostel_Name || '<span style="color:gray;">Unassigned</span>'}</strong></td>
                            <td><strong>${m.Room_Number || '<span style="color:gray;">N/A</span>'}</strong></td>
                            
                            <td style="color: ${statusColor}; font-weight: bold;">${m.Status}</td>
                            <td>
                                <button onclick="openEditForm(${m.Member_ID}, '${m.Contact_Number}', '${m.Status}')" style="background: #f39c12; color: white; padding: 4px 8px; font-size: 12px; border: none; cursor: pointer; border-radius: 3px;">Edit</button>
                            </td>
                         </tr>`;
    });
    html += "</table>";
    document.getElementById("admin-results").innerHTML = html;
  } else {
    alert("Security Block: " + data.error);
  }
}

// ADMIN: Open the Edit Form
function openEditForm(id, contact, status) {
  // Show the form
  document.getElementById("update-member-form").classList.remove("hidden");
  // Hide the add form if it's open so it doesn't look messy
  document.getElementById("add-member-form").classList.add("hidden");

  // Populate the fields with the student's current data
  document.getElementById("update-id").value = id;
  document.getElementById("update-contact").value = contact;
  document.getElementById("update-status").value = status;

  window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
}

// ADMIN: Submit the Update
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

// ADMIN: View Complaints
async function fetchComplaints() {
  const token = localStorage.getItem("session_token");
  const response = await fetch("/admin/complaints", {
    headers: { Authorization: "Bearer " + token },
  });
  const data = await response.json();

  if (response.ok) {
    let html =
      "<table border='1' width='100%' style='border-collapse: collapse; text-align: left; background: white;'>";

    html +=
      "<tr style='background-color: #f2f2f2;'><th>Date</th><th>Submitted By</th><th>Hostel</th><th>Room</th><th>Type</th><th>Description</th><th>Status</th><th>Action</th></tr>";

    data.complaints.forEach((c) => {
      // Safely format the date
      let formattedDate = new Date(c.Submission_Date).toLocaleDateString(
        "en-GB",
      );

      // Create the Status Dropdown
      let statusDropdown = `
                    <select onchange="updateComplaintStatus(${c.Complaint_ID}, this.value)" style="color: ${c.Status === "Pending" ? "red" : "green"}; font-weight: bold; padding: 4px;">
                        <option value="Pending" ${c.Status === "Pending" ? "selected" : ""}>Pending</option>
                        <option value="In Progress" ${c.Status === "In Progress" ? "selected" : ""}>In Progress</option>
                        <option value="Resolved" ${c.Status === "Resolved" ? "selected" : ""}>Resolved</option>
                    </select>
                `;

      // The Data Rows
      html += `<tr>
                            <td>${formattedDate}</td>
                            <td>${c.First_Name} ${c.Last_Name || ""}</td>
                            <td><strong>${c.Hostel_Name || '<span style="color:gray;">Unassigned</span>'}</strong></td>
                            <td><strong>${c.Room_Number || '<span style="color:gray;">N/A</span>'}</strong></td>
                            <td>${c.Type_Name}</td>
                            <td>${c.Description}</td>
                            <td>${statusDropdown}</td>
                            <td>
                                <button onclick="deleteComplaint(${c.Complaint_ID})" style="background: #e74c3c; color: white; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer;">Delete</button>
                            </td>
                         </tr>`;
    });

    html += "</table>";

    document.getElementById("admin-complaints-results").innerHTML = html;
  } else {
    alert("Error loading complaints: " + data.error);
  }
}

// ADMIN: Add New Member
async function submitNewMember() {
  // Check if the form is valid before sending
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
    contact: document.getElementById("new-contact").value, // Standard backend field name
    email: email,
    emergency_contact: document.getElementById("emergency-contact").value,
    role_id: document.getElementById("new-role").value,
    hostel_id: document.getElementById("new-hostel-id").value,
    room_number: room,
  };

  const token = localStorage.getItem("session_token");

  try {
    // Updated URL to match the common admin route
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

      // Matches your HTML ID: tab-add-member
      document.getElementById("tab-add-member").classList.add("hidden");

      // Clear the form fields
      document.getElementById("new-fname").value = "";
      document.getElementById("new-lname").value = "";
      document.getElementById("new-email").value = "";
      document.getElementById("new-contact").value = "";
      document.getElementById("new-room-number").value = "";

      // Refresh the member list immediately
      if (typeof fetchAllMembers === "function") fetchAllMembers();
    } else {
      alert("Error: " + (data.error || "Failed to save member"));
    }
  } catch (error) {
    console.error("Save error:", error);
    alert("Server connection failed. Make sure your backend is running.");
  }
}

// STUDENT: Submit a New Complaint
function updateSubcategories() {
  const category = document.getElementById("complaint-category").value;
  const subSelect = document.getElementById("new-complaint-type");

  // Clear current options
  subSelect.innerHTML = '<option value="">Select Subcategory</option>';

  // Mapping based on the SQL table we have created
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
      opt.value = item.id; // This matches the Complaint_Type_ID in DB
      opt.innerText = item.label;
      subSelect.appendChild(opt);
    });
  }
}
// STUDENT: Submit a New Complaint
async function submitComplaint() {
  const typeId = document.getElementById("new-complaint-type").value;
  const description = document.getElementById("new-complaint-desc").value;

  // 1. Validate Subcategory
  if (!typeId) {
    alert("Please select a valid Category and Subcategory.");
    return;
  }

  // 2. Validate Description
  if (!description.trim()) {
    alert("Please provide a description for your complaint.");
    return;
  }

  // 3. Prepare the Data
  const payload = {
    type_id: typeId,
    description: description,
  };

  // 4. Send to Python Backend
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
      document.getElementById("new-complaint-desc").value = ""; // Clear the text box
      window.location.reload(); // Refresh to show the new complaint!
    } else {
      alert("Backend Error: " + data.error);
    }
  } catch (error) {
    console.error("Fetch error:", error);
    alert("Network error. Please check your console.");
  }
}

// LOGOUT FUNCTION
function logout() {
  // 1. Delete the security token
  localStorage.removeItem("session_token");

  // 2. Force a full page reload
  window.location.reload();
}

window.onload = () => {
  if (localStorage.getItem("session_token")) {
    loadPortfolio();
  }
};

// ADMIN: Delete a Complaint
async function deleteComplaint(complaintId) {
  // 1. Ask for confirmation before doing anything destructive!
  if (
    !confirm(
      "Are you sure you want to delete this complaint? This action cannot be undone.",
    )
  ) {
    return;
  }

  const token = localStorage.getItem("session_token");

  // 2. Send the DELETE request to the backend
  const response = await fetch("/admin/complaints/" + complaintId, {
    method: "DELETE",
    headers: {
      Authorization: "Bearer " + token,
    },
  });

  const data = await response.json();

  // 3. Handle the result
  if (response.ok) {
    alert("Success! The complaint has been deleted.");
    fetchComplaints(); // Refresh the table so the deleted row disappears instantly
  } else {
    alert("Error: " + data.error);
  }
}

// DMIN: Update Complaint Status
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
    // Refresh the table to update the text colors instantly
    fetchComplaints();
  } else {
    alert("Error: " + data.error);
    // If it fails, refresh to revert the dropdown to its real database value
    fetchComplaints();
  }
}

// ADMIN TAB SWITCHER
function openAdminTab(tabName) {
  const targetTab = document.getElementById("tab-" + tabName);

  // 1. Check if the tab they clicked is ALREADY open
  const isAlreadyOpen = !targetTab.classList.contains("hidden");

  // 2. Hide ALL tabs first
  const allTabs = document.querySelectorAll(".admin-tab-content");
  allTabs.forEach((tab) => {
    tab.classList.add("hidden");
  });

  // Also hide the edit form to keep the screen clean
  const updateForm = document.getElementById("update-member-form");
  if (updateForm) {
    updateForm.classList.add("hidden");
  }

  // 3. If it wasn't open before, show it!
  if (!isAlreadyOpen) {
    targetTab.classList.remove("hidden");
  }
}

// FETCH ADMIN DASHBOARD STATS
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

// ==========================================
// NEW WARDEN, ADMIN & SECURITY FETCH FUNCTIONS
// ==========================================

async function fetchSecurityDashboard() {
  const token = localStorage.getItem("session_token");
  const response = await fetch("/api/security/dashboard", {
    headers: { Authorization: "Bearer " + token },
  });
  const data = await response.json();

  if (response.ok) {
    // 1. Update Hostel Name and Stats
    document.getElementById("sec-hostel-name-stat").innerText =
      data.hostel_name;
    document.getElementById("stat-sec-visitors").innerText =
      data.active_visitors.length;
    document.getElementById("stat-sec-outside").innerText =
      data.outside_students.length;

    // 2. Build Visitors Table
    // 2. Build Visitors Table
    let visHtml =
      "<table border='1' width='100%' style='border-collapse: collapse; text-align: left; background: white;'><tr style='background-color: #f2f2f2;'><th>Visitor</th><th>Visiting</th><th>Room</th><th>Purpose</th><th>Entry Time</th><th>Action</th></tr>";

    data.active_visitors.forEach((v) => {
      visHtml += `<tr>
                <td style="padding:8px;">${v.Visitor_Name}</td>
                <td style="padding:8px;">${v.Visiting_Student}</td>
                <td style="padding:8px;">${v.Room_Number}</td>
                <td style="padding:8px;">${v.Purpose}</td>
                <td style="padding:8px;">${new Date(v.Entry_Time).toLocaleString("en-GB")}</td>
                <td style="padding:8px; text-align:center;">
                    <button onclick="markVisitorExited(${v.Log_ID})" style="background: #e74c3c; color: white; padding: 5px 10px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;">
                        Sign Out
                    </button>
                </td>
            </tr>`;
    });

    visHtml += "</table>";
    document.getElementById("sec-visitors-table").innerHTML =
      data.active_visitors.length > 0
        ? visHtml
        : "<p>No visitors currently inside.</p>";
    // 3. Build Students Outside Table
    // 3. Build Students Outside Table
    let outHtml =
      "<table border='1' width='100%' style='border-collapse: collapse; text-align: left; background: white;'><tr style='background-color: #f2f2f2;'><th>Student Name</th><th>Contact</th><th>Exit Time</th><th>Purpose</th><th>Action</th></tr>";

    data.outside_students.forEach((s) => {
      outHtml += `<tr>
                <td style="padding:8px;">${s.First_Name} ${s.Last_Name || ""}</td>
                <td style="padding:8px;">${s.Contact_Number}</td>
                <td style="padding:8px;">${new Date(s.Exit_Time).toLocaleString("en-GB")}</td>
                <td style="padding:8px;">${s.Purpose}</td>
                <td style="padding:8px; text-align:center;">
                    <button onclick="markStudentReturned(${s.Log_ID})" style="background: #27ae60; color: white; padding: 5px 10px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;">
                        Sign In
                    </button>
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
      "<table border='1' width='100%' style='border-collapse: collapse; text-align: left; background: white;'><tr style='background-color: #f2f2f2;'><th>Asset Type</th><th>Total Quantity</th><th>Status</th></tr>";
    data.forEach((item) => {
      let status =
        item.Needs_Repair > 0
          ? `<span style="color:red; font-weight:bold;">⚠️ ${item.Needs_Repair} Damaged</span>`
          : `<span style="color:green; font-weight:bold;">✅ Good</span>`;
      html += `<tr><td style="padding:8px;"><strong>${item.Item_Name}</strong></td><td style="padding:8px;">${item.Total_Quantity} units</td><td style="padding:8px;">${status}</td></tr>`;
    });
    html += `</table>`;
    document.getElementById("warden-furniture-results").innerHTML = html;
  }
}

// --- Mark Visitor Exited ---
async function markVisitorExited(logId) {
  if (!confirm("Are you sure you want to sign this visitor out?")) {
    return;
  }

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
      // Instantly refresh the dashboard to remove the visitor from the table
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
    // 1. Added the "Action" header to the table
    let html = "<table border='1' width='100%' style='border-collapse: collapse; text-align: left; background: white;'><tr style='background-color: #f2f2f2;'><th>Student</th><th>Room</th><th>Exit Time</th><th>Return Time</th><th>Purpose</th><th>Action</th></tr>";
    
    data.forEach((log) => {
      let returnTime = log.Entry_Time
        ? new Date(log.Entry_Time).toLocaleString("en-GB")
        : '<span style="color:red; font-weight:bold;">Currently Outside</span>';
      
      // 2. Logic to show the button ONLY if the student is currently outside
      let actionBtn = "";
      if (!log.Entry_Time) {
        // If they are outside, show the green Sign In button
        // NOTE: Make sure 'log.Log_ID' matches the primary key name in your database!
        actionBtn = `<button onclick="markStudentReturned(${log.Log_ID})" style="background: #27ae60; color: white; padding: 5px 10px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 12px;">Sign In</button>`;
      } else {
        // If they are already back, just show plain text
        actionBtn = `<span style="color: gray; font-size: 12px;">Returned</span>`;
      }

      html += `<tr>
        <td style="padding:8px;">${log.First_Name} ${log.Last_Name || ""}</td>
        <td style="padding:8px;">${log.Room_Number}</td>
        <td style="padding:8px;">${new Date(log.Exit_Time).toLocaleString("en-GB")}</td>
        <td style="padding:8px;">${returnTime}</td>
        <td style="padding:8px;">${log.Purpose}</td>
        <td style="padding:8px; text-align:center;">${actionBtn}</td>
      </tr>`;
    });
    
    html += `</table>`;
    document.getElementById("warden-movement-results").innerHTML = html;
  }
}
// --- Mark Student Returned ---
async function markStudentReturned(logId) {
    if (!confirm("Confirm this student has returned to the hostel?")) {
        return;
    }

    const token = localStorage.getItem('session_token');
    
    try {
        const response = await fetch(`/api/movement/${logId}/return`, {
            method: 'PUT',
            headers: { 
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            // Check which dashboard the user is on to refresh the right data
            const role = localStorage.getItem('user_role');
            if (role === 'security') {
                fetchSecurityDashboard();
            } else if (role === 'warden' || role === 'admin') {
                // If you add this button to the Warden's table later, this ensures it refreshes!
                if (typeof fetchWardenMovement === 'function') fetchWardenMovement();
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
    title = "🛏️ Global Furniture Overview";
  }
  if (type === "visitors") {
    url = "/api/admin/all_visitors";
    title = "👥 Global Visitor Logs";
  }
  if (type === "movement") {
    url = "/api/admin/all_movement";
    title = "🌍 Global Student Movements";
  }

  document.getElementById("admin-global-title").innerText = title;

  const token = localStorage.getItem("session_token");
  const response = await fetch(url, {
    headers: { Authorization: "Bearer " + token },
  });
  const data = await response.json();

  if (response.ok) {
    let html =
      "<table border='1' width='100%' style='border-collapse: collapse; text-align: left; background: white;'>";
    if (data.length > 0) {
      html += `<tr style='background-color: #f2f2f2;'>`;
      Object.keys(data[0]).forEach(
        (key) =>
          (html += `<th style="padding:8px;">${key.replace(/_/g, " ")}</th>`),
      );
      html += `</tr>`;
      data.forEach((row) => {
        html += `<tr>`;
        Object.values(row).forEach((val) => {
          let displayVal =
            val === null
              ? '<span style="color:red; font-weight:bold;">Pending / Inside</span>'
              : val;
          if (typeof val === "string" && val.includes("GMT")) {
            displayVal = new Date(val).toLocaleString("en-GB");
          }
          html += `<td style="padding:8px;">${displayVal}</td>`;
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
  // Hide both first just in case
  document.getElementById("sec-modal-visitors").classList.add("hidden");
  document.getElementById("sec-modal-students").classList.add("hidden");

  if (type === "visitors") {
    document.getElementById("sec-modal-visitors").classList.remove("hidden");
  } else if (type === "students") {
    document.getElementById("sec-modal-students").classList.remove("hidden");
  }

  // Refresh data whenever a modal is opened
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
        // Join room numbers with commas
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

// --- Modal Controls ---
function openAddVisitorModal() {
  const modal = document.getElementById("modal-add-visitor");
  modal.classList.remove("hidden");
  modal.style.setProperty("display", "flex", "important"); // Safe flexbox toggle
}

function closeAddVisitorModal() {
  const modal = document.getElementById("modal-add-visitor");
  modal.classList.add("hidden");
  modal.style.setProperty("display", "none", "important");
}

// --- Live Student Search ---
let searchTimeout = null;

async function searchStudent() {
    const query = document.getElementById('vis-student-search').value;
    const resultsDiv = document.getElementById('student-search-results');
    
    // Clear the hidden ID if they start typing something new
    document.getElementById('vis-host-id').value = '';

    // Only search if they typed at least 2 characters
    if (query.length < 2) {
        resultsDiv.style.display = 'none';
        return;
    }

    // Delay the search by 300ms to avoid overloading the database
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        const token = localStorage.getItem('session_token');
        try {
            const response = await fetch(`/api/security/search-student?q=${encodeURIComponent(query)}`, {
                headers: { 'Authorization': 'Bearer ' + token }
            });
            const data = await response.json();

            if (response.ok && data.length > 0) {
                resultsDiv.innerHTML = ''; // Clear old results
                
                data.forEach(student => {
                    const fullName = `${student.First_Name} ${student.Last_Name || ''}`.trim();
                    const div = document.createElement('div');
                    
                    // Style the dropdown row
                    div.style.padding = '10px';
                    div.style.cursor = 'pointer';
                    div.style.borderBottom = '1px solid #eee';
                    div.style.transition = 'background 0.2s';
                    div.innerHTML = `<strong style="color:#2c3e50;">${fullName}</strong> (Room: ${student.Room_Number}) <br><small style="color:#7f8c8d;">📞 ${student.Contact_Number}</small>`;
                    
                    // Add Hover Effect
                    div.onmouseover = () => div.style.background = '#f2f9ff';
                    div.onmouseout = () => div.style.background = 'white';
                    
                    // Click Event: Fill the input and save the ID
                    div.onclick = () => {
                        document.getElementById('vis-student-search').value = `${fullName} (Room ${student.Room_Number})`;
                        document.getElementById('vis-host-id').value = student.Member_ID;
                        resultsDiv.style.display = 'none'; // Hide dropdown
                    };
                    
                    resultsDiv.appendChild(div);
                });
                resultsDiv.style.display = 'block';
            } else {
                resultsDiv.innerHTML = '<div style="padding:10px; color:#e74c3c; text-align:center;">No active students found.</div>';
                resultsDiv.style.display = 'block';
            }
        } catch (err) {
            console.error("Search error:", err);
        }
    }, 300);
}

// --- Submit Function ---
async function submitNewVisitor() {
  // 1. Gather the data
  const payload = {
    visitor_name: document.getElementById("vis-name").value,
    contact: document.getElementById("vis-contact").value,
    id_type: document.getElementById("vis-id-type").value,
    id_number: document.getElementById("vis-id-num").value,
    host_id: document.getElementById("vis-host-id").value,
    purpose: document.getElementById("vis-purpose").value,
  };

  // 2. Simple Validation
  if (!payload.visitor_name || !payload.id_number || !payload.host_id) {
    alert("Please fill in all required fields.");
    return;
  }

  // 3. Send to Python Backend
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

      // Clean up the form
      document.getElementById("vis-name").value = "";
      document.getElementById("vis-contact").value = "";
      document.getElementById("vis-id-num").value = "";
      document.getElementById("vis-host-id").value = "";
      document.getElementById("vis-purpose").value = "";

      closeAddVisitorModal();

      // Immediately refresh the Security Dashboard tables!
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
