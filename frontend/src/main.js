import { convert, getCurrencies, getReceiptPdf } from "./api.js";

const amountInput = document.getElementById("amount");
const fromSelect = document.getElementById("fromCurrency");
const toSelect = document.getElementById("toCurrency");
const convertButton = document.getElementById("convertBtn");
const receiptButton = document.getElementById("receiptBtn");
const resultBlock = document.getElementById("result");

let lastSuccessfulPayload = null;

function resetReceiptState() {
  lastSuccessfulPayload = null;
  receiptButton.disabled = true;
}

function updateConvertButtonState() {
  const amount = Number(amountInput.value);
  const ok = Number.isFinite(amount) && amount > 0;

  convertButton.disabled = !ok;
  receiptButton.disabled = !ok || !lastSuccessfulPayload;

  if (!ok) {
    resetReceiptState();
    resultBlock.textContent = "Enter an amount > 0";
  } else if (resultBlock.textContent === "Enter an amount > 0") {
    resultBlock.textContent = "Ready";
  }
}

function invalidateReceipt() {
  resetReceiptState();
  updateConvertButtonState();
}

amountInput.addEventListener("input", updateConvertButtonState);
amountInput.addEventListener("change", updateConvertButtonState);
fromSelect.addEventListener("change", invalidateReceipt);
toSelect.addEventListener("change", invalidateReceipt);

updateConvertButtonState();

function fillSelect(select, list, selectedCode) {
  select.innerHTML = "";
  for (const { code, name } of list) {
    const option = document.createElement("option");
    option.value = code;
    option.textContent = `${code} - ${name}`;
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
    resetReceiptState();
    resultBlock.textContent = "Error: amount must be greater than 0";
    return;
  }

  resultBlock.textContent = "Converting...";

  try {
    const payload = {
      amount,
      from_currency: fromSelect.value,
      to_currency: toSelect.value,
    };

    const data = await convert(payload);

    lastSuccessfulPayload = payload;
    receiptButton.disabled = false;
    resultBlock.textContent = `Rate: ${data.rate}, Result: ${data.result}`;
  } catch (error) {
    resetReceiptState();
    resultBlock.textContent = `Error: ${error.message}`;
  }
});

receiptButton.addEventListener("click", async () => {
  if (!lastSuccessfulPayload) {
    resultBlock.textContent = "Convert first to issue a receipt";
    return;
  }

  const receiptWindow = window.open("", "_blank");

  try {
    if (receiptWindow) {
      receiptWindow.document.write("<p>Preparing receipt...</p>");
      receiptWindow.document.close();
    }

    const pdfBlob = await getReceiptPdf(lastSuccessfulPayload);
    const pdfUrl = URL.createObjectURL(pdfBlob);

    if (receiptWindow) {
      receiptWindow.location.href = pdfUrl;
    } else {
      window.open(pdfUrl, "_blank");
    }
  } catch (error) {
    if (receiptWindow) {
      receiptWindow.close();
    }
    resultBlock.textContent = `Receipt error: ${error.message}`;
  }
});
