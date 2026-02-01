// ---------- CONFIG ----------
const API_BASE = "https://real-time-crypto-tracker-rzxk.onrender.com";

// ---------- ELEMENTS ----------
const tableBody = document.getElementById("cryptoTable");
const currencySelect = document.getElementById("currency");
const limitSelect = document.getElementById("limit");
const refreshBtn = document.getElementById("refreshBtn");

// ---------- FETCH ----------
async function fetchCryptoData() {
  const currency = currencySelect.value;
  const limit = limitSelect.value;

  tableBody.innerHTML = `
    <tr>
      <td colspan="4">Loading...</td>
    </tr>
  `;

  try {
    const res = await fetch(
      `${API_BASE}/prices?currency=${currency}&limit=${limit}`
    );

    const result = await res.json();

    if (!result.data || result.data.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="4">⚠️ Data temporarily unavailable</td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = "";

    result.data.forEach((coin) => {
      const change = coin.change_24h;
      const changeClass = change >= 0 ? "positive" : "negative";

      tableBody.innerHTML += `
        <tr>
          <td>${coin.name} (${coin.symbol.toUpperCase()})</td>
          <td>${coin.price.toLocaleString()}</td>
          <td class="${changeClass}">${change.toFixed(2)}%</td>
          <td>${coin.market_cap.toLocaleString()}</td>
        </tr>
      `;
    });

  } catch (err) {
    console.error(err);
    tableBody.innerHTML = `
      <tr>
        <td colspan="4">❌ Backend not reachable</td>
      </tr>
    `;
  }
}

// ---------- EVENTS ----------
refreshBtn.addEventListener("click", fetchCryptoData);
limitSelect.addEventListener("change", fetchCryptoData);

// ---------- INITIAL LOAD ----------
setTimeout(fetchCryptoData, 800);
