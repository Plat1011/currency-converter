import { convert } from "./api.js";

const amountInput = document.getElementById("amount");
const fromSelect = document.getElementById("fromCurrency");
const toSelect = document.getElementById("toCurrency");
const convertButton = document.getElementById("convertBtn");
const resultBlock = document.getElementById("result");

convertButton.addEventListener("click", async () => {
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
