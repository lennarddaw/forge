
// main.js ist mostly a bunch of dropzone stuff

  const result = document.getElementById("result");
    const dropZone = document.getElementById("dropZone");

    dropZone.addEventListener("dragover", e => {
      e.preventDefault();
      dropZone.classList.add("hover");
    });
    dropZone.addEventListener("dragleave", () => {
      dropZone.classList.remove("hover");
    });
    dropZone.addEventListener("drop", async e => {
      e.preventDefault();
      dropZone.classList.remove("hover");
      const file = e.dataTransfer.files[0];
      if (!file || file.type !== "application/pdf") {
        result.textContent = "Nur PDF-Dateien erlaubt.";
        return;
      }       // Until here: all the Eventlisteners

// Post Request to backend to verify
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("http://127.0.0.1:8000/verify-pdf", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (data.valid) {
        result.innerHTML = `<strong>Gültiges Zertifikat</strong><ul style="margin-top:0.5rem; list-style:none; padding:0;"><li>Name: ${data.data.name || data.data.source}</li><li>Kurs: ${data.data.course || data.data.source}</li><li>Datum: ${data.data.date || "–"}</li><li>Aussteller: ${data.data.issuer || "–"}</li></ul>`;
      } else {
        result.textContent = `Ungültig: ${data.message}`;
      }
    });