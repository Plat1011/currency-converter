import { convert, getCurrencies } from "./api.js";

const amountInput = document.getElementById("amount");
const fromSelect = document.getElementById("fromCurrency");
const toSelect = document.getElementById("toCurrency");
const convertButton = document.getElementById("convertBtn");
const resultBlock = document.getElementById("result");

function fillSelect(select, list, selectedCode) {
  select.innerHTML = "";
  for (const { code, name } of list) {
    const option = document.createElement("option");
    option.value = code;
    option.textContent = `${code} — ${name}`;
    if (code === selectedCode) option.selected = true;
    select.appendChild(option);
  }
}

async function init() {
  const data = await getCurrencies();
  const list = Object.entries(data.currencies).map(([code, name]) => ({
    code,
    name,
  }));

  list.sort((a, b) => a.code.localeCompare(b.code));

  fillSelect(fromSelect, list, "USD");
  fillSelect(toSelect, list, "EUR");
}

init().catch((e) => {
  resultBlock.textContent = `Error: ${e.message}`;
});

convertButton.addEventListener("click", async () => {

  const amount = Number(amountInput.value);

  if (!Number.isFinite(amount) || amount <= 0) {
    resultBlock.textContent = "Error: amount must be greater than 0";
    return;
  }

  resultBlock.textContent = "Converting...";

  try {
    const payload = {
      amount: Number(amountInput.value),
      from_currency: fromSelect.value,
      to_currency: toSelect.value,
    };

    const data = await convert(payload);

    resultBlock.textContent = `Rate: ${data.rate}, Result: ${data.result}`;
  } catch (error) {
    resultBlock.textContent = `Error: ${error.message}`;
  }
});
