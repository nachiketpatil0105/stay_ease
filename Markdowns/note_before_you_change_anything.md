# 📌 StayEase – Project Design Notes  
**(Read Before Making Changes)**

---

## 1️⃣ Derived Data Rule (**VERY IMPORTANT**)
- Room occupancy and hostel occupancy are **derived attributes**.
- **Never store** `Current_Occupancy` or similar fields.
- Always compute using:
```

Room_Allocations WHERE Status = 'Active'

```
👉 Prevents **redundancy** and **inconsistency**.

---

## 2️⃣ Clear Separation of Responsibilities
- **Members ≠ Visitors**
- **Members** → Students, Wardens, Technicians
- **Visitors** → External people only

### Movement Tracking
- `Member_Movement_Logs` → Students going out / coming in
- `Visitor_Logs` → Outsiders entering hostel

👉 **Never mix** members and visitors in the same table.

---

## 3️⃣ Single Source of Truth
A fact must live in **only one table**:

| Fact | Table |
|----|----|
| Room assignment | `Room_Allocations` |
| Complaint state | `Complaints` |
| Complaint actions/history | `Complaint_Logs` |

👉 Other tables must **reference**, not duplicate.

---

## 4️⃣ Status Columns Must Obey Business Logic
Allowed values must be **strictly respected**:

- **Members** → `Active` | `Inactive`
- **Room_Allocations** → `Active` | `Inactive`
- **Payments** → `Success` | `Failed`
- **Complaints** → `Pending` | `In Progress` | `Resolved`

👉 **No free-text statuses** in DB or application code.

---

## 5️⃣ Complaint Resolution Rule
If:
```

Complaints.Status = 'Resolved'

```
Then:
- `Resolved_Date` **must NOT be NULL**
- Resolution action **must exist** in `Complaint_Logs`

👉 Never mark a complaint resolved without:
- a date  
- a log entry  

---

## 6️⃣ One Active Room per Student
- A member can have **only one active room allocation** at a time.
- Enforce via:
  - Application logic **OR**
  - Database constraint later

👉 Prevents **double allocation bugs**.

---

## 7️⃣ Room Identity Rule
- `Room_Number` is **unique per hostel**, not globally.
- Always identify a room using:
```

(Hostel_ID, Room_Number)

```

👉 Prevents ambiguity across multiple hostels.

---

## 8️⃣ Fee Design Principle
- `Fee_Structures` → Defines **what** the fee is
- `Payments` → Defines **when & how much** was paid
- **Never** store due dates inside `Fee_Structures`

👉 Keeps fee definitions reusable across years and students.

---

## 9️⃣ Logs Are Append-Only
The following tables are **append-only**:
- `Visitor_Logs`
- `Member_Movement_Logs`
- `Complaint_Logs`

👉 Logs should **never be updated or deleted**, only inserted.

---

## 🔟 Deletions Must Be Careful
❌ Never delete:
- Members with history
- Complaints with logs

✅ Prefer:
```

Status = 'Inactive'

```

👉 Preserves **auditability** and history.

---

## 1️⃣1️⃣ Normalization Rule (Mental Check)
Before adding a column, ask:
> “Can this be derived from another table?”

- **Yes** → ❌ Don’t store it  
- **No** → ✅ Safe to add  

---

## 1️⃣2️⃣ Schema Change Checklist (Quick)
Before changing the schema, ask:

- Does this introduce redundancy?
- Does it violate separation of concerns?
- Will this break historical data?
- Can this be handled by a log instead?

👉 If **any answer is YES** → **rethink the change**

---

✅ These rules define the **core design philosophy** of StayEase.  
Violating them will lead to **inconsistency, bugs, or audit issues**.
