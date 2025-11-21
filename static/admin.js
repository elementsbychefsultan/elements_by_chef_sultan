// Calculate running totals
function updateTotals() {
  let totalMeal = 0, totalDrinks = 0, totalRevenue = 0;

  document.querySelectorAll("#bookingsTable tbody tr").forEach(row => {
    totalMeal += parseInt(row.children[6].querySelector("input").value) || 0;
    totalDrinks += parseInt(row.children[7].querySelector("input").value) || 0;
    totalRevenue += parseFloat(row.children[8].querySelector("input").value) || 0;
  });

  document.getElementById("totalMeal").textContent = totalMeal;
  document.getElementById("totalDrinks").textContent = totalDrinks;
  document.getElementById("totalRevenue").textContent = "£" + totalRevenue.toFixed(2);
}
updateTotals();

// Save booking
function saveBooking(id) {
  const row = document.querySelector(`tr[data-id='${id}']`);
  const inputs = row.querySelectorAll("input");
  const data = {
    name: inputs[0].value,
    email: inputs[1].value,
    phone: inputs[2].value,
    date: inputs[3].value,
    time: inputs[4].value,
    guests_meal: parseInt(inputs[5].value) || 0,
    guests_drinks: parseInt(inputs[6].value) || 0,
    total: parseFloat(inputs[7].value) || 0
  };

  fetch(`/admin/update/${id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(res => {
    if (res.success) {
      alert("✅ Booking updated!");
      updateTotals();
    } else {
      alert("❌ Error: " + res.message);
    }
  });
}

// Delete booking
function deleteBooking(id) {
  if (!confirm("Are you sure you want to delete this booking?")) return;

  fetch(`/admin/delete/${id}`, { method: "POST" })
    .then(res => res.json())
    .then(res => {
      if (res.success) {
        document.querySelector(`tr[data-id='${id}']`).remove();
        updateTotals();
        alert("🗑 Booking deleted.");
      } else {
        alert("❌ Error: " + res.message);
      }
    });
}

