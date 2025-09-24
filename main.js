document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-turno");
  const tabela = document.getElementById("tabela-faltando");
  const tbody = tabela.querySelector("tbody");
  const loading = document.getElementById("loading");
  const mensagem = document.getElementById("mensagem");

  const apiURL = "https://raw.githubusercontent.com/msv-stihl/limpeza/master/faltando.json";

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const turno = document.getElementById("turno").value;
      tabela.classList.add("hidden");
      mensagem.textContent = "";
      loading.classList.remove("hidden");

      try {
        const res = await fetch(apiURL);
        const data = await res.json();
        const lista = data[turno] || [];

        if (lista.length > 0) {
          tbody.innerHTML = lista.map(item => `
            <tr>
              <td>${item["Local Instalação"]}</td>
              <td>${item["Arvore Prisma4 / Pro"]}</td>
              <td>${item["Descrição"]}</td>
              <td>${item["Turnos"]}</td>
            </tr>
          `).join("");
          tabela.classList.remove("hidden");
        } else {
          mensagem.textContent = "Nenhum ambiente faltante encontrado.";
        }
      } catch (err) {
        console.error("Erro ao buscar dados:", err);
        mensagem.textContent = "Erro ao buscar dados.";
      } finally {
        loading.classList.add("hidden");
      }
    });
  }
});