document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("search-input");
    const suggestions = document.getElementById("search-suggestions");

    if (!input || !suggestions) return;

    let timer = null;

    input.addEventListener("input", () => {
        const query = input.value.trim();

        clearTimeout(timer);

        if (query.length < 2) {
            suggestions.innerHTML = "";
            return;
        }

        timer = setTimeout(() => {
            fetch(`/search/suggest/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    suggestions.innerHTML = "";

                    data.results.forEach(item => {
                        const link = document.createElement("a");
                        link.href = item.url;
                        link.className = "list-group-item list-group-item-action";
                        link.textContent = item.title;
                        suggestions.appendChild(link);
                    });
                })
                .catch(() => {
                    suggestions.innerHTML = "";
                });
        }, 300);
    });

    document.addEventListener("click", (event) => {
        if (!input.contains(event.target) && !suggestions.contains(event.target)) {
            suggestions.innerHTML = "";
        }
    });
});