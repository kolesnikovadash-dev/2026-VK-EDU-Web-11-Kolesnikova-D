document.addEventListener("DOMContentLoaded", () => {
    if (!window.CENTRIFUGO_WS_URL || !window.CENTRIFUGO_CHANNEL) return;

    const centrifuge = new Centrifuge(window.CENTRIFUGO_WS_URL);

    const sub = centrifuge.newSubscription(window.CENTRIFUGO_CHANNEL);

    sub.on("publication", function(ctx) {
        const answer = ctx.data;

        if (String(window.CURRENT_ANSWERS_PAGE) !== "1") {
            alert("Появился новый ответ");
            return;
        }

        const answersContainer = document.getElementById("answers-list");

        if (!answersContainer) {
            alert("Появился новый ответ");
            return;
        }

        const item = document.createElement("div");
        item.className = "card mb-3";
        item.id = `answer-${answer.answer_id}`;

        item.innerHTML = `
            <div class="card-body">
                <p>${answer.text}</p>
                <small class="text-muted">
                    answered by ${answer.author} at ${answer.created_at}
                </small>
            </div>
        `;

        answersContainer.prepend(item);
    });

    sub.subscribe();
    centrifuge.connect();
});