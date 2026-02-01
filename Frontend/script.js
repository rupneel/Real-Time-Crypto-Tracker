const API_BASE = "https://real-time-crypto-tracker-rzxk.onrender.com";



// ---------- ELEMENTS ----------
const tableBody = document.getElementById("cryptoTable");
const currencySelect = document.getElementById("currency");
const limitSelect = document.getElementById("limit");
const refreshBtn = document.getElementById("refreshBtn");

let isFetching = false; // prevents spam requests


// ---------- FETCH ----------
async function fetchCryptoData() {
  if (isFetching) return; // prevent multiple rapid calls
  isFetching = true;

  const currency = currencySelect.value;
  const limit = limitSelect.value;

  tableBody.innerHTML = `<tr><td colspan="4">Loading...</td></tr>`;

  try {
    const res = await fetch(
      `${API_BASE}/prices?currency=${currency}&limit=${limit}`
    );

    if (!res.ok) {
      throw new Error("Backend error");
    }

    const result = await res.json();

    // Handle backend warning / empty data
    if (!result.data || result.data.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="4">
            ⚠️ Data temporarily unavailable<br/>
            <small>${result.warning || "Please try again in a moment"}</small>
          </td>
        </tr>`;
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
      `<tr><td colspan="4"> Backend not reachable</td></tr>`;
  } finally {
    isFetching = false;
  }
}


// ---------- EVENTS ----------
refreshBtn.addEventListener("click", fetchCryptoData);
currencySelect.addEventListener("change", fetchCryptoData);
limitSelect.addEventListener("change", fetchCryptoData);


// ---------- INITIAL LOAD ----------
setTimeout(fetchCryptoData, 500);

// ❌ DO NOT enable this on free CoinGecko / Render
// setInterval(fetchCryptoData, 60000);
