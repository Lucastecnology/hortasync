document.addEventListener("DOMContentLoaded", () => {
    fetch('data/hortas.json')
        .then(response => response.json())
        .then(data => {
            const sortedHortas = data.sort((a, b) => {
                const scoreA = (a.clicks + a.donations) / 2;
                const scoreB = (b.clicks + b.donations) / 2;
                return scoreB - scoreA;
            });
            renderCards(sortedHortas);
        });
});

function renderCards(hortas) {
    const cardsContainer = document.querySelector('.cards');
    cardsContainer.innerHTML = "";
    hortas.forEach(horta => {
        const card = document.createElement('div');
        card.className = 'card';
        card.id = horta.id;
        card.innerHTML = `
            <img src="${horta.image}" alt="Imagem da horta">
            <div class="card-content">
                <h2>${horta.name}</h2>
                <p>${horta.category}</p>
                <p>Arrecadado: R$ ${horta.raised}</p>
                <div class="progress-bar">
                    <div class="progress" style="width: ${(horta.raised / horta.goal) * 100}%;"></div>
                </div>
                <p>Meta: R$ ${horta.goal}</p>
            </div>
        `;
        cardsContainer.appendChild(card);
    });
}