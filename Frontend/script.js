// ---------- CONFIG ----------
const API_BASE = "https://YOUR_BACKEND_URL.onrender.com";



// ---------- ELEMENTS ----------
const tableBody = document.getElementById("cryptoTable");
const currencySelect = document.getElementById("currency");
const limitSelect = document.getElementById("limit");
const refreshBtn = document.getElementById("refreshBtn");

// ---------- FETCH ----------
async function fetchCryptoData() {
  const currency = currencySelect.value;
  const limit = limitSelect.value;

  tableBody.innerHTML = `<tr><td colspan="4">Loading...</td></tr>`;

  try {
    const res = await fetch(
      `${API_BASE}/prices?currency=${currency}&limit=${limit}`
    );

    const result = await res.json();

    if (!result.data || result.data.length === 0) {
      tableBody.innerHTML =
        `<tr><td colspan="4">⚠️ Data temporarily unavailable</td></tr>`;
      return;
    }

    tableBody.innerHTML = "";

    result.data.forEach((coin) => {
      const change = coin.change_24h;

      const changeText =
        change !== null && change !== undefined
          ? `${change.toFixed(2)}%`
          : "N/A";

      const changeClass =
        change === null || change === undefined
          ? ""
          : change >= 0
          ? "positive"
          : "negative";

      tableBody.innerHTML += `
        <tr>
          <td>${coin.name} (${coin.symbol.toUpperCase()})</td>
          <td>${coin.price}</td>
          <td class="${changeClass}">${changeText}</td>
          <td>${coin.market_cap.toLocaleString()}</td>
        </tr>
      `;
    });

  } catch (err) {
    console.error(err);
    tableBody.innerHTML =
      `<tr><td colspan="4">Backend not reachable</td></tr>`;
  }
}

// ---------- EVENTS ----------
refreshBtn.addEventListener("click", fetchCryptoData);
currencySelect.addEventListener("change", fetchCryptoData);
limitSelect.addEventListener("change", fetchCryptoData);

// ---------- AUTO ----------
setTimeout(fetchCryptoData, 500);
// setInterval(fetchCryptoData, 60000);
