// --- 1. LOGIN FUNCTION ---
async function login() {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: user, password: pass })
    });

    const data = await response.json();

    if (response.ok) {
        // Save the JWT token to local storage
        localStorage.setItem('session_token', data['session token']);
        document.getElementById('login-error').innerText = "";
        loadPortfolio(); // Fetch the data
    } else {
        document.getElementById('login-error').innerText = data.error;
    }
}


// --- 2. LOAD PORTFOLIO & ENFORCE RBAC ---
async function loadPortfolio() {
    const token = localStorage.getItem('session_token');
    if (!token) return;

    // First, check who is logged in via /isAuth
    const authResponse = await fetch('/isAuth', {
        headers: { 'Authorization': 'Bearer ' + token }
    });
    const authData = await authResponse.json();

    if (!authResponse.ok) {
        logout();
        return;
    }

    // We need the Member ID. Since our /isAuth doesn't return ID yet, 
    // we extract it from the token payload directly in JS for the API call.
    const tokenPayload = JSON.parse(atob(token.split('.')[1]));
    const memberId = tokenPayload.member_id;
    const role = tokenPayload.role;

    // Now, fetch their portfolio data
    const portResponse = await fetch(`/portfolio/${memberId}`, {
        headers: { 'Authorization': 'Bearer ' + token }
    });
    const portData = await portResponse.json();

    if (portResponse.ok) {
        // Hide login, show portfolio
        document.getElementById('login-section').classList.add('hidden');
        document.getElementById('portfolio-section').classList.remove('hidden');

        // Populate the Basic Profile HTML
        document.getElementById('display-name').innerText = portData.profile.First_Name;
        document.getElementById('display-role').innerText = role;
        document.getElementById('port-email').innerText = portData.profile.Email;
        document.getElementById('port-contact').innerText = portData.profile.Contact_Number;
        document.getElementById('port-hostel').innerText = portData.profile.Hostel_Name || 'Unassigned';
        document.getElementById('port-room').innerText = portData.profile.Room_Number || 'Unassigned';

        // Populate Payments
        let payHtml = portData.payments.length > 0 ? "<ul>" : "<p>No payments found.</p>";
        portData.payments.forEach(p => {
            payHtml += `<li><strong>${p.Fee_Name}</strong>: $${p.Amount_Paid} on ${p.Payment_Date} (${p.Payment_Status})</li>`;
        });
        if(portData.payments.length > 0) payHtml += "</ul>";
        document.getElementById('port-payments').innerHTML = payHtml;

        // Populate Complaints
        let compHtml = portData.complaints.length > 0 ? "<ul>" : "<p>No complaints found.</p>";
        portData.complaints.forEach(c => {
            compHtml += `<li><strong>${c.Type_Name}</strong>: ${c.Description} - <em>Status: ${c.Status}</em></li>`;
        });
        if(portData.complaints.length > 0) compHtml += "</ul>";
        document.getElementById('port-complaints').innerHTML = compHtml;


        // RBAC UI ENFORCEMENT: Show admin box only if Admin/Warden
        if (role.toLowerCase() === 'admin' || role.toLowerCase() === 'warden') {
            document.getElementById('admin-section').classList.remove('hidden');
        }
    }
}

// --- 4. ADMIN: FETCH ALL MEMBERS ---
async function fetchAllMembers() {
    const token = localStorage.getItem('session_token');
    
    const response = await fetch('/admin/members', {
        headers: { 'Authorization': 'Bearer ' + token }
    });
    
    const data = await response.json();

    if (response.ok) {
        // Build a simple HTML table to display the members
        let html = "<table border='1' width='100%' style='border-collapse: collapse; text-align: left;'>";
        html += "<tr style='background-color: #f2f2f2;'><th>ID</th><th>Name</th><th>Email</th><th>Status</th></tr>";
        
        data.members.forEach(m => {
            html += `<tr>
                        <td>${m.Member_ID}</td>
                        <td>${m.First_Name} ${m.Last_Name || ''}</td>
                        <td>${m.Email}</td>
                        <td>${m.Status}</td>
                        </tr>`;
        });
        html += "</table>";
        
        document.getElementById('admin-results').innerHTML = html;
    } else {
        alert("Security Block: " + data.error);
    }
}

// --- 3. LOGOUT FUNCTION ---
function logout() {
    localStorage.removeItem('session_token');
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('portfolio-section').classList.add('hidden');
    document.getElementById('admin-section').classList.add('hidden');
}

// Auto-load if token exists on page refresh
window.onload = () => {
    if (localStorage.getItem('session_token')) {
        loadPortfolio();
    }
};
